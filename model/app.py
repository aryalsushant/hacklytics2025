from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import boto3
from pathlib import Path
import tempfile
import botocore.exceptions  # for catching 404 errors
import subprocess
import time

# Import your modules for SVG and Manim code generation
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

# Initialize R2 client (Cloudflare R2 compatible S3 client)
r2_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

# Define the project root where the fixed files will be stored.
PROJECT_ROOT = Path("/home/ec2-user/hacklytics2025/model")

def render_manim_script(script_filename, scene_name="DrugInteraction", output_filename="drug_interaction.mp4"):
    """
    Runs Manim with the given script and fixed output filename.
    The working directory is set to PROJECT_ROOT so that output files are created predictably.
    '--disable_preview' avoids xdg-open issues on headless servers.
    """
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
        subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT))
        # Manim creates its output at:
        # PROJECT_ROOT/media/videos/<script_stem>/480p15/<output_filename>
        script_stem = Path(script_filename).stem
        media_dir = PROJECT_ROOT / "media/videos" / script_stem / "480p15"
        output_path = media_dir / output_filename
        print("DEBUG: Expecting video at:", output_path)
        if output_path.exists():
            print("DEBUG: Found video file at:", output_path)
            return str(output_path)
        else:
            print("DEBUG: Video file not found.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Manim rendering failed: {e}")
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

        print("DEBUG: drug1_name:", drug1_name)
        print("DEBUG: drug2_name:", drug2_name)
        print("DEBUG: drug1_smiles:", drug1_smiles)
        print("DEBUG: drug2_smiles:", drug2_smiles)
        print("DEBUG: side_effects:", side_effects)

        if not all([drug1_name, drug2_name, drug1_smiles, drug2_smiles]):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate a unique key for the upload while keeping local filenames fixed.
        unique_key = f"{drug1_name.lower()}_{drug2_name.lower()}_{int(time.time())}_interaction.mp4"
        r2_key = f"drug_videos/{unique_key}"

        # Generate SVGs (in a temporary directory)
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

            # Generate the Manim script using the SVG paths
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

        # Write the generated script to a fixed file in PROJECT_ROOT
        fixed_script_path = PROJECT_ROOT / "drug_interaction.py"
        with open(fixed_script_path, "w") as f:
            f.write(manim_script)
        print("DEBUG: Saved Manim script to", fixed_script_path)

        # Render the video; locally it will always be stored as "drug_interaction.mp4"
        video_path = render_manim_script(
            str(fixed_script_path),
            scene_name="DrugInteraction",
            output_filename="drug_interaction.mp4"
        )
        if not video_path:
            return jsonify({"error": "Video generation failed"}), 500

        # Upload the video to R2 with the unique key
        try:
            print("DEBUG: Uploading video to R2")
            r2_client.upload_file(
                video_path,
                "hacklytics",  # Your bucket name
                r2_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            video_url = f"{R2_PUBLIC_URL}/hacklytics/{r2_key}"
            print("DEBUG: Video generated and uploaded successfully:", video_url)
            return jsonify({
                "videoUrl": video_url,
                "message": "Video generated and uploaded successfully"
            }), 200
        except Exception as e:
            return jsonify({"error": f"Failed to upload to R2: {str(e)}"}), 500
        finally:
            # Clean up the local video file
            if video_path and os.path.exists(video_path):
                os.remove(video_path)

    except Exception as e:
        print("DEBUG: Exception in generate_video:", e)
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
