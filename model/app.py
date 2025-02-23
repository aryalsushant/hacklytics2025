from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import boto3
from pathlib import Path
import tempfile
import botocore.exceptions  # for catching the 404 when object not found

# Import your existing modules
from .smiles_to_molecule import generate_svg_from_smiles
from .generate_manim import generate_manim_code
from .drug_info import fetch_drug_information
from .config import (
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
    import subprocess
    from pathlib import Path

    # Set project root as working directory.
    project_root = Path("/home/ec2-user/hacklytics2025/model")
    cmd = [
        "manim",
        "-pql",
        script_filename,
        scene_name,
        "-o",
        output_filename,
        "--disable_preview"
    ]
    try:
        print("DEBUG: Running command:", " ".join(cmd))
        subprocess.run(cmd, check=True, cwd=str(project_root))
        media_dir = project_root / "media/videos" / Path(script_filename).stem / "480p15"
        output_path = media_dir / output_filename
        print("DEBUG: Expecting video at:", output_path)
        if output_path.exists():
            print("DEBUG: Found video file at:", output_path)
            return str(output_path)
        else:
            print("DEBUG: Video file not found. Listing contents of 'media/videos':")
            for path in (project_root / "media/videos").rglob("*"):
                print(path)
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

        # Log input
        print("DEBUG: drug1_name:", drug1_name)
        print("DEBUG: drug2_name:", drug2_name)
        print("DEBUG: drug1_smiles:", drug1_smiles)
        print("DEBUG: drug2_smiles:", drug2_smiles)
        print("DEBUG: side_effects:", side_effects)

        if not all([drug1_name, drug2_name, drug1_smiles, drug2_smiles]):
            return jsonify({"error": "Missing required fields"}), 400

        # Construct a unique video filename (you can use a timestamp or UUID for uniqueness)
        import time
        unique_part = str(int(time.time()))
        video_filename = f"{drug1_name.lower()}_{drug2_name.lower()}_{unique_part}_interaction.mp4"
        r2_key = f"drug_videos/{video_filename}"

        # 1. Check if it already exists in R2 (optional if you want caching)
        try:
            r2_client.head_object(Bucket="hacklytics", Key=r2_key)
            existing_video_url = f"{R2_PUBLIC_URL}/{r2_key}"
            return jsonify({
                "videoUrl": existing_video_url,
                "message": "Video already exists, returning cached version."
            }), 200
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != "404":
                return jsonify({"error": f"Failed checking object: {str(e)}"}), 500

        # 2. Generate SVGs in a temporary directory (they don't need to be fixed)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            drug1_svg_path = temp_dir / f"{drug1_name.lower()}.svg"
            drug2_svg_path = temp_dir / f"{drug2_name.lower()}.svg"
            try:
                print("DEBUG: Generating SVG for", drug1_name)
                generate_svg_from_smiles(drug1_smiles, str(drug1_svg_path))
                print("DEBUG: Generating SVG for", drug2_name)
                generate_svg_from_smiles(drug2_smiles, str(drug2_svg_path))
            except Exception as e:
                return jsonify({"error": f"SVG generation failed: {str(e)}"}), 500

            # Generate Manim script
            print("DEBUG: Generating Manim script")
            manim_script = generate_manim_code(
                str(drug1_svg_path),
                str(drug2_svg_path),
                drug1_name,
                drug2_name,
                side_effects
            )
            if not manim_script:
                return jsonify({"error": "Failed to generate Manim script"}), 500

        # 3. Write the generated script to a fixed file in the project root.
        project_root = Path("/home/ec2-user/hacklytics2025/model")
        fixed_script_path = project_root / "drug_interaction.py"
        with open(fixed_script_path, "w") as f:
            f.write(manim_script)

        print("DEBUG: Rendering video with Manim using fixed script at:", fixed_script_path)
        # 4. Render the video; output will be in:
        #    /home/ec2-user/hacklytics2025/model/media/videos/drug_interaction/480p15/drug_interaction.mp4
        video_path = render_manim_script(
            str(fixed_script_path),
            scene_name="DrugInteraction",
            output_filename=video_filename  # unique filename we generated
        )

        if not video_path:
            return jsonify({"error": "Video generation failed"}), 500

        # 5. Upload the video to R2
        try:
            print("DEBUG: Uploading video to R2")
            r2_client.upload_file(
                video_path,
                "hacklytics",  # Your bucket name
                r2_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            video_url = f"{R2_ENDPOINT_URL}/hacklytics/{r2_key}"
            return jsonify({
                "videoUrl": video_url,
                "message": "Video generated and uploaded successfully"
            }), 200
        except Exception as e:
            return jsonify({"error": f"Failed to upload to R2: {str(e)}"}), 500
        finally:
            if video_path and os.path.exists(video_path):
                os.remove(video_path)

    except Exception as e:
        print("DEBUG: Exception in generate_video:", e)
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500
