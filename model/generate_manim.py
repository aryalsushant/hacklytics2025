import google.generativeai as genai
from smiles_to_molecule import generate_svg_from_smiles
from drug_info import fetch_drug_information
from config import GEMINI_API_KEY

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def clean_manim_script(script):
    """Extracts only the Manim Python code from the AI-generated response."""

    # Remove Markdown code blocks and trim whitespace
    script = script.strip("```python").strip("```").strip()
    return script.strip() # just trim whitespace at the ends


def generate_manim_code(drug1_svg, drug2_svg, drug1_name, drug2_name, side_effects):
    drug1_info = fetch_drug_information(drug1_name)
    drug2_info = fetch_drug_information(drug2_name)
    """
    Generates a Manim script for drug interaction visualization using pre-generated SVGs.
    
    Parameters:
    drug1_svg (str): SVG filename for first drug
    drug2_svg (str): SVG filename for second drug
    drug1_name (str): Name of first drug
    drug2_name (str): Name of second drug
    drug1_info (str): Information of first drug
    drug2_info (str): Information of second drug
    side_effects (str): Known side effects of the interaction
    """
    
    prompt = f"""
    You are an expert in creating educational animations using Manim.

    Task: Generate a Manim script that visualizes the interaction between {drug1_name} and {drug2_name} in 30 second.
    
    Input Data:
    - Drug 1: {drug1_name} (SVG: {drug1_svg}) (INFO: {drug1_info}))
    - Drug 2: {drug2_name} (SVG: {drug2_svg}) (INFO: {drug2_info}))
    - Known Side Effects: {side_effects}

    Animation Elements:
    1. Title screen with drug names
    2. Display SVG structures of both drugs
    3. Explain their function using voiceover text
    4. Show the drug interaction process
    5. Highlight potential risks and side effects
    6. Provide medical recommendations and safety information

    Voice-Over Requirement:
    - Ensure that each explanatory text is spoken aloud using Manim's VoiceoverScene and GTTSService from manim_voiceover.services.gtts 
    - Use the provided example Manim script and do similarly.

    Requirements:
    - Use the provided SVGs for drug visualization.
    - Implement smooth transitions and professional voiceovers.
    - Use appropriate color coding (RED for warnings, YELLOW for cautions, BLUE for information).
    - Ensure that the generated script includes synchronized text and voice narration.
    - Return ONLY a fully runnable Manim Python script.

    Example working code:
    ```python
    import os
    from manim import *
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.gtts import GTTSService
    from rdkit import Chem
    from rdkit.Chem import rdDepictor
    from rdkit.Chem.Draw import MolDraw2DSVG


    class DrugInteraction(VoiceoverScene):
        def construct(self):
            self.set_speech_service(GTTSService())

            # Introduction
            title = Text("Understanding Drug Interactions:", font_size=48).to_edge(UP, buff=0.5)
            subtitle = Text("Warfarin & Aspirin", font_size=42, color=YELLOW).next_to(title, DOWN)
            
            with self.voiceover(text="Let's explore the important interaction between two common blood-thinning medications: Warfarin and Aspirin."):
                self.play(Write(title), Write(subtitle))
                self.wait(1)

            # Individual Drug Explanations
            warfarin_smiles = "CC(=O)C(C1=CC=CC=C1)C2=CC(=O)OC=C2O"
            aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
            
            warfarin_svg = SVGMobject("warfarin.svg").scale(0.7).move_to(LEFT * 3)
            aspirin_svg = SVGMobject("aspirin.svg").scale(0.7).move_to(RIGHT * 3)

            # Create info boxes for each drug
            warfarin_info = VGroup(
                Text("Warfarin", font_size=36, color=RED),
                Text("• Anticoagulant", font_size=24),
                Text("• Prevents blood clots", font_size=24),
                Text("• Blocks Vitamin K", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

            aspirin_info = VGroup(
                Text("Aspirin", font_size=36, color=BLUE),
                Text("• Anti-platelet", font_size=24),
                Text("• Reduces inflammation", font_size=24),
                Text("• Inhibits platelets", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

            # Create groups for each drug
            warfarin_group = VGroup(warfarin_svg, warfarin_info).arrange(DOWN, buff=0.5)
            aspirin_group = VGroup(aspirin_svg, aspirin_info).arrange(DOWN, buff=0.5)

            # Position the groups
            warfarin_group.to_edge(LEFT, buff=1)
            aspirin_group.to_edge(RIGHT, buff=1)

            with self.voiceover(text="Warfarin is a powerful anticoagulant that works by blocking Vitamin K, preventing blood clots from forming."):
                self.play(FadeOut(subtitle))
                self.play(FadeIn(warfarin_group))
                self.wait(1)

            with self.voiceover(text="Aspirin, on the other hand, works by inhibiting platelets, which are crucial for blood clotting."):
                self.play(FadeIn(aspirin_group))
                self.wait(1)

            # Blood vessel demonstration
            vessel = RoundedRectangle(height=1, width=6, corner_radius=0.5, fill_opacity=0.2, color=RED)
            vessel.move_to(DOWN * 2)
            blood_cells = VGroup(*[Circle(radius=0.1, fill_opacity=1, color=RED) for _ in range(6)])
            for i, cell in enumerate(blood_cells):
                cell.move_to(vessel.get_left() + RIGHT * (i + 0.5))

            with self.voiceover(text="When these medications are combined, they affect blood clotting in different ways:"):
                self.play(Create(vessel), FadeIn(blood_cells))
                self.wait(1)

            # Show interaction effects
            effect_text = VGroup(
                Text("Combined Effects:", font_size=36, color=YELLOW),
                Text("1. Enhanced bleeding risk", font_size=28),
                Text("2. Longer bleeding time", font_size=28),
                Text("3. Higher risk of internal bleeding", font_size=28),
                Text("4. Increased bruising", font_size=28)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            effect_text.next_to(vessel, DOWN, buff=0.5)

            with self.voiceover(text="This dual action significantly increases the risk of bleeding complications."):
                self.play(Write(effect_text))
                self.wait(1)

            # Warning box
            warning_box = VGroup(
                Rectangle(height=2, width=6, fill_opacity=0.1, color=RED),
                Text("⚠ Medical Supervision Required", font_size=32, color=RED),
                Text("Monitor for:", font_size=28),
                Text("• Unusual bleeding", font_size=24),
                Text("• Easy bruising", font_size=24),
                Text("• Dark stools", font_size=24)
            ).arrange(DOWN, buff=0.2)
            
            with self.voiceover(text="Due to these serious risks, this combination requires careful medical supervision and monitoring for signs of bleeding."):
                self.play(
                    FadeOut(vessel),
                    FadeOut(blood_cells),
                    FadeOut(effect_text),
                    FadeIn(warning_box)
                )
                self.wait(1)

            # Conclusion
            conclusion = VGroup(
                Text("Key Takeaways:", font_size=36, color=YELLOW),
                Text("• Always inform your healthcare provider", font_size=28),
                Text("• Regular monitoring is essential", font_size=28),
                Text("• Report any unusual symptoms immediately", font_size=28)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

            with self.voiceover(text="Remember to always inform your healthcare provider about all medications you're taking and follow their monitoring instructions carefully."):
                self.play(
                    FadeOut(warning_box),
                    FadeIn(conclusion)
                )
                self.wait(2)

            # Final fade out
            with self.voiceover(text="Your safety depends on proper medical supervision and careful monitoring of these medications."):
                self.play(
                    FadeOut(title),
                    FadeOut(warfarin_group),
                    FadeOut(aspirin_group),
                    FadeOut(conclusion),
                    run_time=2
                )
                self.wait(1)
     ```

    Generate the complete Manim script below:
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    if response and response.candidates and response.candidates[0].content.parts:
        raw_script = response.candidates[0].content.parts[0].text
        print("Raw Gemini Response:\n", raw_script)  # Print the raw response
        return clean_manim_script(raw_script)
    else:
        print("Error: Gemini did not return a valid response.")
        return None

if __name__ == "__main__":
    # Define drugs
    drug1_smile = "CC(=O)C(C1=CC=CC=C1)C2=CC(=O)OC=C2O"  # Warfarin
    drug2_smile = "CC(=O)OC1=CC=CC=C1C(=O)O"            # Aspirin
    drug1_name = "Warfarin"
    drug2_name = "Aspirin"
    side_effects = "Increased bleeding risk, bruising, potential internal bleeding"

    # Generate SVG files
    drug1_svg = generate_svg_from_smiles(drug1_smile, "warfarin.svg")
    drug2_svg = generate_svg_from_smiles(drug2_smile, "aspirin.svg")

    # Generate Manim script
    manim_script = generate_manim_code(drug1_svg, drug2_svg, drug1_name, drug2_name, side_effects)

    if manim_script:
        with open("drug_interaction_educational2.py", "w") as f:
            f.write(manim_script)
        print("Generated educational Manim script saved to drug_interaction_educational.py")
    else:
        print("Script generation failed. Please try again.")
