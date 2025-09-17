# 🥗 Food Calories & Proteins Analyzer

An **AI-powered nutrition assistant** that analyzes food images to detect food items, calculate **calories & protein content**, and answer nutrition-related questions.  
Built with **LangGraph, Google Gemini, Nutritionix API, Wikipedia, and Streamlit**.

---

## ✨ Features

- **Food Recognition** – Upload an image, and Gemini identifies visible food items.  
- **Calorie & Protein Calculation** – Nutritionix API provides accurate nutrition facts.  
- **Interactive Q&A** – Ask follow-up questions about the analysis (e.g., *“How much protein is in the rice?”*).  
- **Wikipedia Integration** – Learn nutrition benefits of foods via Wikipedia.  
- **Conversation Memory** – Keeps track of analysis and follow-up questions using `MemorySaver`.  
- **Streamlit UI** – Simple, user-friendly interface for interaction.  
- **MCP Server (Render)** – Nutrition tools are served via a FastAPI MCP server hosted on **Render**.  

---

## 🛠 Tech Stack

- **LangGraph** – Workflow orchestration & memory  
- **Google Gemini** – Vision + LLM for food recognition & reasoning  
- **Nutritionix API** – Nutrition facts (calories, protein, etc.)  
- **Wikipedia API** – Extra nutrition knowledge  
- **Streamlit** – Frontend for interaction  
- **FastAPI + MCP** – Backend tool serving (deployed on **Render**)  

---

## 📂 Project Structure



📂 Project Structure
.
.devcontainer/
├── devcontainer.json       # Main config file
├── backend/                # Backend API & services
│   ├── requirements.txt    # Backend dependencies 
│   ├── server.py           # API server
│
├── frontend/               # Streamlit-based frontend
│   ├── app.py              # Main app
│   ├── client.py           # Connects to backend
│   ├── requirements.txt    # Frontend dependencies
│
├── .env.example            # Example env file 
├── .gitignore              # Git ignore rules
├── .python-version         # Python version
├── pyproject.toml          # Project metadata 
├── README.md               # Project documentation
├── requirements.txt        # Root dependencies
└── uv.lock                 # Lockfile (reproducible builds with uv)

⚡ Setup Instructions
1️⃣ Clone the repository
git clone https://github.com/sunilpowar5/LangGraph-MCP-Nutrition-Analyzer.git
cd LangGraph-MCP-Nutrition-Analyzer

2️⃣ Create virtual environment & install dependencies
python -m venv .venv
# Activate venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

3️⃣ Add environment variables

Create a .env file in the root directory:

GEMINI_API_KEY=your_google_gemini_api_key
NUTRITIONIX_APP_ID=your_nutritionix_app_id
NUTRITIONIX_API_KEY=your_nutritionix_api_key
LANGCHAIN_API_KEY=your_langchain_api_key


(You can use .env.example as a template)

4️⃣ Run the app (Streamlit frontend)
streamlit run frontend/app.py

5️⃣ (Optional) Run backend MCP server
uvicorn backend.server:app --host 0.0.0.0 --port 8000

🎮 Usage

Upload a food image (jpeg/jpg/png).

The system detects food items → Nutritionix fetches calories & protein info.

Ask follow-up questions like:

“Is this meal healthy?”

“What are the benefits of the meal?”

Start a new session anytime.

📌 Example Workflow

Upload image → 🍌 + 🥛 detected

Nutritionix fetch →

Banana: 105 calories, 1.3g protein

Milk: 103 calories, 8g protein

Total: 208 calories, 9.3g protein

Ask: “What are the benefits of milk?”
→ Answer fetched from Wikipedia.

🚀 Roadmap

 Support multi-food image segmentation (bounding boxes).

 Add more nutrition APIs for wider coverage.

 Deploy on Streamlit Cloud / AWS.

 Multi-user history & persistent storage.

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open a PR or report a bug.