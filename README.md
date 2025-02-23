# DrugLytics

## 🏆 Hacklytics 2025 Submission | Healthcare, GenAI, and AI for Education

A **GenAI-powered application** that helps users manage the risks of **drug-drug interactions** and **allergic reactions** through a **personalized AI assistant** that generates **text summaries** and **animated videos** explaining potential risks.

---

## 🚀 Inspiration

When taking multiple medications, people often wonder:

- Will these drugs interact negatively?
- What if I consume alcohol with my medication?
- Are there any hidden risks based on my allergies?

Current **online tools** are **complex, text-heavy, and impersonal**. Meanwhile, **doctor consultations take weeks due to high wait times**—even for a **simple medication question**. 

We wanted to **simplify this process** by building an AI-powered platform that is **quick, easy to use, and personalized**.

---

## 🔍 What It Does

1. **User Profile Creation**  
   - Users **input the medications they're currently taking** and **any known allergies**.
   - This profile is **stored for future searches** to provide **more relevant insights**.

2. **Drug Search & Interaction Analysis**  
   - Users **search for a new drug** they want to take.  
   - Our AI analyzes **how it interacts with the user's existing medications** and generates a **simplified text summary**.

3. **AI-Generated Video Explanations**  
   - A **video is created dynamically**, showing:
     - **Visual representations of chemical structures** of the drugs.
     - **A narrated explanation** of potential risks and interactions.

4. **Interactive Chatbot for Further Questions**  
   - Users can **ask follow-up questions** in a chatbot, which provides **real-time explanations**.

---

## 🛠️ How We Built It

### **🗂️ Dataset**
- We used **DrugBank**, a dataset containing **300K+ drug-drug interactions**.

### **🤖 AI-Powered Multi-Agent System**
- **Google Gemini:** Searches the web to augment dataset knowledge and generates interaction videos.  
- **OpenAI API (ChatGPT):** Provides **simplified text summaries** and powers the chatbot.

### **💻 Tech Stack & Tools**
| Component  | Technology Used |
|------------|----------------|
| **Frontend** | Streamlit |
| **Backend** | Flask |
| **LLM APIs** | Google Gemini, OpenAI |
| **Database** | MongoDB Atlas |
| **Cloud Storage** | Cloudflare R2 |
| **Hosting** | AWS EC2 |
| **Molecular Rendering** | RDKit + Manim |
| **Authentication** | Okta Auth0 |

---

## 🔥 Challenges & How We Solved Them

1. **🚀 Handling 300K+ Drug Interactions Efficiently**  
   - **Problem:** Searching through a massive dataset was slow.  
   - **Solution:** We **indexed frequent searches using MongoDB Atlas**, drastically improving response time.

2. **📽️ Generating AI Videos for Every Search**  
   - **Problem:** The dataset stored drug information as **SMILES strings** (text-based molecular data).  
   - **Solution:** We **converted SMILES to 3D chemical structures using RDKit** and rendered animations via **Manim**.

3. **⏳ Reducing Long Processing Times**  
   - **Problem:** Generating video + text summaries on demand was slow.  
   - **Solution:** We **cached past searches** in MongoDB Atlas and stored **previously generated videos in Cloudflare R2**.  
   - **Impact:** Common searches **now load instantly** instead of regenerating from scratch.

4. **🔐 Securing User Data**  
   - **Problem:** Users store personal medication data, requiring security.  
   - **Solution:** We **integrated Okta Auth0 for authentication**, ensuring **secure logins and encrypted user data**.

---

## 🎯 Accomplishments That We’re Proud Of

✅ Successfully **combined AI, molecular visualization, and chatbot functionality** into one seamless application.  
✅ **Optimized our database queries**, making a **300K+ interaction dataset searchable in real-time**.  
✅ **First-time use of Cloudflare R2, AWS EC2, and Okta Auth0** to streamline our infrastructure.  
✅ Built **an intelligent AI video generator** that translates **medical data into simple, animated explanations**.  

---

## 📚 What We Learned

- **Leveraging AI agents** to combine structured medical data with real-world knowledge.  
- **Deploying and caching AI-generated media** for faster response times.  
- **Implementing user authentication and secure database management** with Okta and MongoDB Atlas.  
- **Integrating molecular visualization tools (RDKit, Manim)** for **chemical structure rendering**.  

---

## 🔮 What’s Next for DrugLytics?

🔹 **Enhanced Personalization** – Allow users to input age, gender, and weight for **even more accurate recommendations**.  
🔹 **Medical Report Uploads** – Users can upload PDFs of **medical reports**, and LLMs will **extract key information**.  
🔹 **Fine-Tuned Video Explanations** – Simplify AI-generated **medical descriptions for non-technical users**.  

---

## 🏆 Prize Tracks We're Targeting

✅ **Healthcare Track** 🏥  
✅ **GenAI Track** 🤖  
✅ **Best Use of AI by Reach Capital** (For healthcare and education) 🎓  
✅ **Best Use of Streamlit** 📊  
✅ **Best Use of MongoDB Atlas** 🗄️  
✅ **Best Use of Okta Auth0** 🔐  
✅ **Best Use of AWS** ☁️  
✅ **Best Use of Cloudflare** 🌐  

---

## 📂 Project Structure

```
HACKLYTICS2025/
│── backend/
│   │── database.py
│   │── interactions.py
│   │── chroma_db/
│   │── dataset/
│   │   │── medicine_dataset.csv
│   │   │── twosides_aggregated.csv
│   │── model/
│   │   │── app.py
│   │   │── config.py
│   │   │── drug_info.py
│   │   │── drug_interaction_educational2.py
│   │   │── smiles_to_molecule.py
│   │── generate_manim.py
│   ├── pages/
│   │   │── 2_Profile.py
│   │   │── 3_Chatbot.py
│── templates/chatbot/
│── terraform/
│── venv/
│── .env
│── .gitignore
│── app.py
│── main.py
│── requirements.txt
│── Search.py
│── style.css
```

---

## 🚀 How to Run the Project

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/YOUR-USERNAME/DrugLytics.git
cd DrugLytics
```

### **2️⃣ Set Up a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # MacOS/Linux
venv\Scriptsctivate  # Windows
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Run the Application**
```sh
streamlit run app.py
```

---

## 🤝 Contributing

We welcome contributions!  
Feel free to **open an issue** or **submit a pull request** to improve the project.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👥 Team

🚀 **[Your Team Member Names]**  
💡 **Built at Hacklytics 2025**
