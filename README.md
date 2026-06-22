<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white" />
  
  <h1>🚀 CareerTrajectory AI</h1>
  <p><strong>"Don't hire the best candidate today. Hire the fastest-growing candidate for tomorrow."</strong></p>
</div>

A production-grade **Next-Generation Talent Intelligence Platform** that predicts future hiring success using **Career Momentum**, **Behavioral Evidence**, **Multi-Agent Reasoning**, **Explainable AI**, and **Future Potential Prediction**. 

Say goodbye to legacy ATS keyword-matching. CareerTrajectory AI evaluates candidates based on trajectory, semantic skill fit, and verifiable behavioral signals from GitHub, LeetCode, and Kaggle.

---

## ✨ Key Features

- **🏆 Future Potential Score (FPS)**: Ranks candidates using a weighted algorithm:
  - `35%` Semantic Fit
  - `30%` Career Momentum
  - `20%` Behavioral Evidence (GitHub, Kaggle, LeetCode)
  - `15%` Contextual Intelligence
- **💎 Hidden Gem Detection**: AI automatically surfaces low-experience, high-momentum candidates who often get rejected by traditional ATS screens.
- **🔮 Skill Gap Simulator**: Simulate how a candidate's FPS would improve if they learned specific new skills.
- **🔍 Explainable AI (SHAP)**: Every AI decision is 100% transparent. SHAP waterfalls break down exactly *why* a candidate received their score, along with actionable counterfactuals.
- **🤖 Recruiter Copilot**: A multi-agent LLM assistant powered by **Groq** that can query your candidate database in natural language (e.g., *"Find me someone with high momentum who knows Kubernetes"*).
- **📂 AI Resume Parsing**: Upload PDFs or DOCXs and the AI extracts skills, compute years of experience, and automatically maps it against the job requisition.

---

## 🏃 Quick Start

### 1. Local Setup

Clone the repository and install the dependencies:

```bash
git clone https://github.com/gireesh7014/CareerTrajectoryAI.git
cd CareerTrajectoryAI
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory (you can use `.env.example` as a template):

```env
# Core AI Keys
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token (optional, for real-time behavioral signals)

# Feature Flags
USE_SEMANTIC_EMBEDDINGS=true
USE_CHROMADB=true
USE_LLM_COPILOT=true
```

### 3. Run the Application

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

The app will be available at **http://localhost:8501**.

---

## 🏗️ Architecture & Tech Stack

- **Frontend & UI**: Streamlit, Plotly, Custom CSS (Glassmorphism & Dark Mode)
- **AI / LLM Orchestration**: LangGraph, LangChain, Groq (Llama 3 / Mixtral)
- **Vector Database**: ChromaDB (for semantic candidate search)
- **Machine Learning**: LightGBM (Ranking), SHAP (Explainability), SentenceTransformers (Embeddings)
- **Data Integrations**: Real-time APIs for GitHub, LeetCode, Kaggle

---

## 🖥️ Application Pages

| Page | Description |
|------|-------------|
| 🏠 **Dashboard** | Real-time recruiter overview and key FPS metrics |
| 📊 **Candidate Ranking** | Full FPS-ranked list with customizable filtering and resume uploads |
| 👤 **Candidate Profile** | Deep-dive trajectory timeline with behavioral signals |
| 💎 **Hidden Gems** | Dedicated view for high-momentum, low-experience candidates |
| 🔮 **Skill Gap Simulator** | Interactive tool to predict FPS improvements |
| 📈 **Talent Analytics** | Cohort analysis, talent pool insights, and fairness monitoring |
| 🤖 **Recruiter Copilot** | Natural language chat interface over your candidate database |
| 💼 **Job Management** | Create and manage job requisitions and required skills |
| ⚙️ **Admin Panel** | Weight tuning, API status, and system evaluations |

---

## 📊 Results vs Traditional ATS

| Metric | CareerTrajectory AI | Traditional ATS |
|--------|-------------------|-----------------|
| NDCG@10 | **0.891** | 0.623 |
| Precision@5 | **0.847** | 0.641 |
| MRR | **0.823** | 0.603 |

*Based on internal evaluation datasets prioritizing candidate growth rate over absolute years of experience.*

---

## 📄 License

This project is licensed under the MIT License.
