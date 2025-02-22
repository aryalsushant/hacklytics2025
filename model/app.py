from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import boto3
from pathlib import Path
import tempfile
import botocore.exceptions  # for catching the 404 when object not found


# Import your existing modules
from smiles_to_molecule import generate_svg_from_smiles
from generate_manim import generate_manim_code
from drug_info import fetch_drug_information
from config import (
    R2_ACCESS_KEY,
    R2_SECRET_KEY,
    R2_ENDPOINT_URL,
    R2_PUBLIC_URL
)

app = Flask(__name__)
CORS(app)

# Initialize R2 client
r2_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

def render_manim_script(script_filename, scene_name="DrugInteraction", output_filename="interaction.mp4"):
    """
    Renders a Manim script and returns the path to the generated video.
    """
    import subprocess
    
    cmd = [
        "manim",
        "-pql",  # Production quality, medium quality
        script_filename,
        scene_name,
        "-o",
        output_filename
    ]
    
    try:
        subprocess.run(cmd, check=True)

        # Manim's default output location
        media_dir = Path("media/videos") / Path(script_filename).stem / "480p15"
        output_path = media_dir / output_filename
        
        if output_path.exists():
            return str(output_path)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Manim rendering failed: {e}")
        return None

@app.route('/generate-video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json() or request.form
        
        # Extract required fields
        drug1_name = data.get("drug1", "")
        drug2_name = data.get("drug2", "")
        drug1_smiles = data.get("smiles1", "")
        drug2_smiles = data.get("smiles2", "")
        side_effects = data.get("sideEffects", "No specific side effects provided.")

        # Log individual variables
        print("DEBUG: drug1_name:", drug1_name)
        print("DEBUG: drug2_name:", drug2_name)
        print("DEBUG: drug1_smiles:", drug1_smiles)
        print("DEBUG: drug2_smiles:", drug2_smiles)
        print("DEBUG: side_effects:", side_effects)
        
        if not all([drug1_name, drug2_name, drug1_smiles, drug2_smiles]):
            return jsonify({"error": "Missing required fields"}), 400

        # Construct the desired S3 key for your final video
        video_filename = f"{drug1_name.lower()}_{drug2_name.lower()}_interaction.mp4"
        r2_key = f"drug_videos/{video_filename}"
        
        # 1. Check if it already exists in R2
        try:
            r2_client.head_object(Bucket="hacklytics", Key=r2_key)
            # If head_object doesn't raise an exception, the file exists
            existing_video_url = f"{R2_PUBLIC_URL}/{r2_key}"
            return jsonify({
                "videoUrl": existing_video_url,
                "message": "Video already exists, returning cached version."
            }), 200
        except botocore.exceptions.ClientError as e:
            # If a 404 error, object doesn't exist => we generate a new one
            if e.response['Error']['Code'] != "404":
                # Some other error happened
                return jsonify({"error": f"Failed checking object: {str(e)}"}), 500
        
        # 2. Otherwise, we proceed to generate a new video
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Generate SVGs
            drug1_svg_path = temp_dir / f"{drug1_name.lower()}.svg"
            drug2_svg_path = temp_dir / f"{drug2_name.lower()}.svg"
            
            try:
                generate_svg_from_smiles(drug1_smiles, str(drug1_svg_path))
                generate_svg_from_smiles(drug2_smiles, str(drug2_svg_path))
            except Exception as e:
                return jsonify({"error": f"SVG generation failed: {str(e)}"}), 500

            # Generate Manim script
            manim_script = generate_manim_code(
                str(drug1_svg_path),
                str(drug2_svg_path),
                drug1_name,
                drug2_name,
                side_effects
            )
            
            if not manim_script:
                return jsonify({"error": "Failed to generate Manim script"}), 500

            # Write script to temp file
            script_path = temp_dir / f"drug_interaction_{drug1_name.lower()}_{drug2_name.lower()}.py"
            with open(script_path, "w") as f:
                f.write(manim_script)

            # Render Manim video
            video_path = render_manim_script(
                str(script_path),
                scene_name="DrugInteraction",
                output_filename=video_filename
            )
            
            if not video_path:
                return jsonify({"error": "Video generation failed"}), 500

            # 3. Upload the new video to R2
            try:
                r2_client.upload_file(
                    video_path,
                    "hacklytics",  # Your bucket name
                    r2_key,
                    ExtraArgs={'ContentType': 'video/mp4'}
                )
                
                # Generate the new video's URL
                video_url = f"{R2_ENDPOINT_URL}/hacklytics/{r2_key}"
                
                return jsonify({
                    "videoUrl": video_url,
                    "message": "Video generated and uploaded successfully"
                }), 200
                
            except Exception as e:
                return jsonify({"error": f"Failed to upload to R2: {str(e)}"}), 500
            
            finally:
                # Cleanup temporary files
                if video_path and os.path.exists(video_path):
                    os.remove(video_path)

    except Exception as e:
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
