# from drug_info import fetch_drug_information

# def generate_manim_prompt(drug1_name, drug2_name, drug1_svg, drug2_svg, side_effects):
#     """
#     Generates a structured prompt for Google Gemini AI to create a Manim animation script,
#     including voice-over integration, enriched with detailed drug information.
#     """
    
#     # Fetch drug information using the drug_info_agent
#     drug1_info = fetch_drug_information(drug1_name)
#     drug2_info = fetch_drug_information(drug2_name)
    
#     prompt = f"""
#     You are an expert in creating educational animations using Manim.

#     Task: Generate a Manim Python script that visualizes the interaction between {drug1_name} and {drug2_name},
#     incorporating professional voice-over narration.
    
#     Input Data:
#     - Drug 1: {drug1_name} (SVG: {drug1_svg})
#     - Drug 2: {drug2_name} (SVG: {drug2_svg})
#     - Known Side Effects: {side_effects}
#     - Drug 1 Information: {drug1_info}
#     - Drug 2 Information: {drug2_info}
    
#     Animation Elements:
#     1. Title screen with drug names
#     2. Display SVG structures of both drugs
#     3. Explain their function using voice-over text
#     4. Show the drug interaction process with visual effects
#     5. Highlight potential risks and side effects
#     6. Provide medical recommendations and safety information
#     7. Integrate voice-over using Manim’s `TextToSpeech` or external audio sync methods

#     Requirements:
#     - Use the provided SVGs for drug visualization
#     - Implement smooth transitions and professional voiceovers
#     - Use appropriate color coding (RED for warnings, YELLOW for cautions, BLUE for information)
#     - Ensure that the generated script includes synchronized text and voice narration
#     - Return ONLY a fully runnable Manim Python script without extra markdown or comments

#     Generate the complete Manim script below:
#     """
#     return prompt

# test_prompt = generate_manim_prompt("Warfarin", "Aspirin", "warfarin.svg", "aspirin.svg", "Increased bleeding risk, bruising, potential internal bleeding")

# # Print the generated prompt
# print(test_prompt)
