import google.generativeai as genai
from .config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def fetch_drug_information(drug_name):
    """
    Queries Google Gemini AI to scrape the web and retrieve concise drug information,
    limited to 5 bullet points.
    """
    prompt = f"""
    You are a web-scraping assistant specializing in medical research.
    
    Task: Retrieve comprehensive but concise information about the drug {drug_name} from reliable medical sources.
    
    Required Information:
    - What is {drug_name}?
    - What is it used for?
    - How does it affect health positively and negatively?
    - Common side effects and risks.
    - Any notable interactions with other substances.
    
    Provide exactly 5 bullet points, each containing one relevant fact.
    """
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    
    if response and response.candidates and response.candidates[0].content.parts:
        bullet_points = response.candidates[0].content.parts[0].text.split("\n")
        return "\n".join(bullet_points[:5])  # Limit output to exactly 5 bullet points
    else:
        return f"No reliable information found for {drug_name}."

if __name__ == "__main__":
    print(fetch_drug_information("Aspirin"))
