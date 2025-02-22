import os
from smiles_to_molecule import generate_svg_from_smiles
from generate_manim import generate_manim_code

def check_local_video(drug1_name, drug2_name):
    """Checks if the animation for the drug interaction already exists locally."""
    video_filename = f"{drug1_name.lower()}_{drug2_name.lower()}_interaction.mp4"
    
    if os.path.exists(video_filename):
        print(f"Video already exists: {video_filename}")
        return video_filename
    return None

if __name__ == "__main__":
    # Define drugs
    drug1_smile = "CC(=O)C(C1=CC=CC=C1)C2=CC(=O)OC=C2O"  # Warfarin
    drug2_smile = "CC(=O)OC1=CC=CC=C1C(=O)O"            # Aspirin
    drug1_name = "Warfarin"
    drug2_name = "Aspirin"
    side_effects = "Increased bleeding risk, bruising, potential internal bleeding"

    # Check if the video already exists
    existing_video = check_local_video(drug1_name, drug2_name)
    
    if existing_video:
        print(f"Displaying cached video: {existing_video}")
        os.system(f"open {existing_video}")  # Open video on macOS, use `start` on Windows, `xdg-open` on Linux
    else:
        # Generate SVGs
        drug1_svg = generate_svg_from_smiles(drug1_smile, "warfarin.svg")
        drug2_svg = generate_svg_from_smiles(drug2_smile, "aspirin.svg")

        # Generate Manim script
        manim_script = generate_manim_code(drug1_svg, drug2_svg, drug1_name, drug2_name, side_effects)

        if manim_script:
            with open("drug_interaction_educational.py", "w") as f:
                f.write(manim_script)

            print("Generated educational Manim script. Now rendering...")

            # Render Manim animation (this will create an mp4 video)
            video_filename = f"{drug1_name.lower()}_{drug2_name.lower()}_interaction.mp4"
            os.system(f"manim -pql drug_interaction_educational.py DrugInteraction -o {video_filename}")

            # Check if video was successfully generated
            if os.path.exists(video_filename):
                print(f"Video successfully generated: {video_filename}")
                os.system(f"open {video_filename}")  # Automatically play the generated video
            else:
                print("Error: Video file was not created.")
        