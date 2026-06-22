# 🚀 CareerTrajectoryAI

> **"Don't hire the best candidate today. Hire the fastest-growing candidate for tomorrow."**

A production-grade **Next-Generation Talent Intelligence Platform** that predicts future hiring success using Career Momentum, Behavioral Evidence, Multi-Agent Reasoning, Explainable AI, and Future Potential Prediction.

--- 

## ✨ Key Features

*   **Future Potential Score (FPS™):** A proprietary 0-1 score combining Semantic Fit, Career Momentum, Behavioral Evidence, and Contextual Intelligence.
*   **Career Momentum Engine:** Measures skill acquisition velocity and direction alignment to predict growth potential.
*   **Multi-Agent System:** Leverages specialized AI agents for Resume Intelligence, Job Analysis, Candidate Ranking, Behavioral Validation, and Recruiter Copilot.
*   **Explainable AI (SHAP):** Provides transparent, human-readable explanations for candidate rankings.
*   **Live Behavioral Signals:** Integrates with GitHub, LeetCode, and Kaggle APIs for real-time validation of candidate activity.
*   **Semantic Skill Matching:** Uses Sentence Transformers embeddings for nuanced skill comparison, going beyond keyword matching.
*   **Hidden Gem Discovery:** Identifies high-potential candidates with strong momentum but lower experience that traditional ATS might miss.
*   **Skill Gap Simulator:** Predicts FPS improvement based on acquiring specific new skills.
*   **Fairness Monitor:** Actively excludes demographic information from scoring and provides bias mitigation metrics.
*   **Dockerized Deployment:** Includes Docker and Docker Compose configurations for easy setup and scalability.

---

## 🚀 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gireesh7014/CareerTrajectoryAI
    cd CareerTrajectoryAI
    ```

2.  **Set up Environment Variables:**
    Copy `.env.example` to `.env` and fill in your API keys (Groq, GitHub, Kaggle).
    ```bash
    cp .env.example .env
    ```

3.  **Build and Run with Docker:**
    ```bash
    docker-compose up --build
    ```

**Access the application:** Open your browser to `http://localhost:8501`.

--- 

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **AI/ML:** LangGraph, Langchain, Groq SDK, Sentence Transformers, LightGBM, SHAP, Scikit-learn
*   **Data:** Pandas, NumPy, Polars, ChromaDB (Vector Store), PostgreSQL (ORM via SQLAlchemy), Redis
*   **DevOps & Infrastructure:** Docker, Docker Compose, Prometheus, Grafana
*   **Languages:** Python, YAML, Markdown

--- 

## ⚙️ Project Structure

```
CareerTrajectoryAI/
├── .env.example              # Environment variables configuration
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── app.py                    # Main Streamlit application entry point
├── backend/
│   ├── ai/                   # AI Subsystems (LLM, Embeddings, Collectors, Ranking)
│   │   ├── __init__.py
│   │   ├── config.py         # AI configurations and feature flags
│   │   ├── embeddings.py     # Sentence Transformer embedding logic
│   │   ├── feedback_store.py # Recruiter feedback storage
│   │   ├── github_collector.py # GitHub API integration
│   │   ├── kaggle_collector.py # Kaggle API integration
│   │   ├── leetcode_collector.py # LeetCode API integration
│   │   ├── llm_client.py     # Groq LLM client for Llama 3
│   │   ├── orchestrator.py   # LangGraph multi-agent orchestrator
│   │   ├── ranking_model.py  # LightGBM ranking model
│   │   └── vector_store.py   # ChromaDB vector store implementation
│   ├── agents/
│   │   └── agent_01_resume.py # Resume parsing agent (used by resume_parser.py)
│   ├── resume_parser.py    # Resume parsing logic (fallback and agent wrapper)
│   └── scoring_engine.py   # Core FPS, Momentum, Fit calculations
├── data/
│   ├── __init__.py
│   ├── custom_candidates_db.json # Stores manually uploaded candidates
│   ├── database.py         # Utilities for custom candidate DB
│   ├── sample_candidates.json # Sample candidate data for demonstration
│   └── sample_data.py      # Functions to load sample candidates and jobs
├── monitoring/
│   └── prometheus.yml      # Prometheus configuration
├── pages/
│   ├── 01_Dashboard.py     # Main dashboard page
│   ├── 02_Ranking.py       # Candidate ranking and filtering
│   ├── 03_Profile.py       # Detailed candidate profile view
│   ├── 04_HiddenGems.py    # Hidden gem discovery page
│   ├── 05_SkillGap.py      # Skill gap simulation page
│   ├── 06_Analytics.py     # Talent analytics dashboard
│   ├── 07_Copilot.py       # AI Recruiter Copilot interface
│   ├── 08_Jobs.py          # Job requisition management
│   └── 09_Admin.py         # Admin panel for configuration and monitoring
├── ui/
│   ├── __init__.py
│   └── components.py       # Reusable Streamlit UI components and CSS
├── requirements.txt          # Project dependencies for Streamlit app
├── Dockerfile                # Docker configuration for the application
├── docker-compose.yml        # Docker Compose setup for multi-service deployment
└── validate.py               # Validation script for core components
```

--- 

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **AI/ML:** LangGraph, Langchain, Groq SDK, Sentence Transformers, LightGBM, SHAP, Scikit-learn
*   **Data:** Pandas, NumPy, Polars, ChromaDB (Vector Store), PostgreSQL (ORM via SQLAlchemy), Redis
*   **DevOps & Infrastructure:** Docker, Docker Compose, Prometheus, Grafana
*   **Languages:** Python, YAML, Markdown

--- 

## 📚 Installation

To set up the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gireesh7014/CareerTrajectoryAI
    cd CareerTrajectoryAI
    ```

2.  **Set up Environment Variables:**
    Create a `.env` file by copying `.env.example` and filling in your API keys for Groq, GitHub, and Kaggle.
    ```bash
    cp .env.example .env
    # Edit .env with your API keys
    ```

3.  **Install Dependencies:**
    The project uses a requirement file for the Streamlit frontend and the AI backend components. Install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run with Docker Compose:**
    The `docker-compose.yml` file sets up all necessary services (Streamlit UI, PostgreSQL, Redis, Prometheus, Grafana).
    ```bash
    docker-compose up --build
    ```

5.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:8501`.

--- 

## 💡 How to Use

CareerTrajectoryAI provides a suite of tools for recruiters and hiring managers:

1.  **Dashboard (`/pages/01_Dashboard.py`):** Get a real-time overview of your candidate pool, key metrics like Average FPS, number of Hidden Gems, and system activity.
2.  **Candidate Ranking (`/pages/02_Ranking.py`):** View a sortable and filterable list of all candidates ranked by their Future Potential Score (FPS™). You can also upload new resumes or JSON files here to add candidates to the pool.
3.  **Candidate Profile (`/pages/03_Profile.py`):** Dive deep into an individual candidate's profile, including their career timeline, SHAP explanations for their scores, behavioral evidence from external platforms, and predicted future role trajectory.
4.  **Hidden Gems (`/pages/04_HiddenGems.py`):** Discover candidates who might be overlooked by traditional systems due to lower experience but possess high career momentum and strong behavioral signals.
5.  **Skill Gap Simulator (`/pages/05_SkillGap.py`):** Predict how acquiring specific skills would impact a candidate's FPS and ranking for a given job role.
6.  **Talent Analytics (`/pages/06_Analytics.py`):** Access advanced analytics like score distributions, skills heatmaps, cohort analysis (e.g., Momentum by Experience Tier), and fairness monitoring.
7.  **Recruiter Copilot (`/pages/07_Copilot.py`):** Interact with an AI assistant (powered by Llama 3 via Groq in AI mode) to ask natural language questions about your candidate pool, rankings, and specific candidates.
8.  **Job Management (`/pages/08_Jobs.py`):** Create, manage, and view candidate pipelines for different job requisitions.
9.  **Admin Panel (`/pages/09_Admin.py`):** Configure AI subsystems, tune score weights, monitor model evaluation metrics, and view system architecture details.

--- 

## 📈 Project Structure

```
CareerTrajectoryAI/
├── .env.example              # Environment variables configuration
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── app.py                    # Main Streamlit application entry point
├── backend/
│   ├── ai/                   # AI Subsystems (LLM, Embeddings, Collectors, Ranking)
│   │   ├── __init__.py
│   │   ├── config.py         # AI configurations and feature flags
│   │   ├── embeddings.py     # Sentence Transformer embedding logic
│   │   ├── feedback_store.py # Recruiter feedback storage
│   │   ├── github_collector.py # GitHub API integration
│   │   ├── kaggle_collector.py # Kaggle API integration
│   │   ├── leetcode_collector.py # LeetCode API integration
│   │   ├── llm_client.py     # Groq LLM client for Llama 3
│   │   ├── orchestrator.py   # LangGraph multi-agent orchestrator
│   │   ├── ranking_model.py  # LightGBM ranking model
│   │   └── vector_store.py   # ChromaDB vector store implementation
│   ├── agents/
│   │   └── agent_01_resume.py # Resume parsing agent (used by resume_parser.py)
│   ├── resume_parser.py    # Resume parsing logic (fallback and agent wrapper)
│   └── scoring_engine.py   # Core FPS, Momentum, Fit calculations
├── data/
│   ├── __init__.py
│   ├── custom_candidates_db.json # Stores manually uploaded candidates
│   ├── database.py         # Utilities for custom candidate DB
│   ├── sample_candidates.json # Sample candidate data for demonstration
│   └── sample_data.py      # Functions to load sample candidates and jobs
├── monitoring/
│   └── prometheus.yml      # Prometheus configuration
├── pages/
│   ├── 01_Dashboard.py     # Main dashboard page
│   ├── 02_Ranking.py       # Candidate ranking and filtering
│   ├── 03_Profile.py       # Detailed candidate profile view
│   ├── 04_HiddenGems.py    # Hidden gem discovery page
│   ├── 05_SkillGap.py      # Skill gap simulation page
│   ├── 06_Analytics.py     # Talent analytics dashboard
│   ├── 07_Copilot.py       # AI Recruiter Copilot interface
│   ├── 08_Jobs.py          # Job requisition management
│   └── 09_Admin.py         # Admin panel for configuration and monitoring
├── ui/
│   ├── __init__.py
│   └── components.py       # Reusable Streamlit UI components and CSS
├── requirements.txt          # Project dependencies for Streamlit app
├── Dockerfile                # Docker configuration for the application
├── docker-compose.yml        # Docker Compose setup for multi-service deployment
└── validate.py               # Validation script for core components
```

--- 

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **AI/ML:** LangGraph, Langchain, Groq SDK, Sentence Transformers, LightGBM, SHAP, Scikit-learn
*   **Data:** Pandas, NumPy, Polars, ChromaDB (Vector Store), PostgreSQL (ORM via SQLAlchemy), Redis
*   **DevOps & Infrastructure:** Docker, Docker Compose, Prometheus, Grafana
*   **Languages:** Python, YAML, Markdown

--- 

## 📊 Results vs Traditional ATS

| Metric          | CareerTrajectory AI | Traditional ATS |
| :-------------- | :------------------ | :-------------- |
| NDCG@10         | **0.891**           | 0.623           |
| Precision@5     | **0.847**           | 0.641           |
| MRR             | **0.823**           | 0.603           |

--- 

## 🤝 Contributing

Contributions are welcome! Please refer to the `CONTRIBUTING.md` file (if available) or open an issue/pull request on GitHub.

--- 

## 📜 License

This project is likely under a permissive license. Please check the `LICENSE` file in the repository root for specific terms. If no license file is found, it defaults to all rights reserved.

--- 

## 🔗 Important Links

*   **Live Demo:** Not explicitly provided, but the application can be run locally using Docker.
*   **Repository:** [https://github.com/gireesh7014/CareerTrajectoryAI](https://github.com/gireesh7014/CareerTrajectoryAI)

--- 

## 🌟 Footer

Built with ❤️ by the Runtime Terror Team. 
Find us on GitHub: [CareerTrajectoryAI](https://github.com/gireesh7014/CareerTrajectoryAI). 
We encourage you to **Fork**, **Star**, and **Report Issues** if you find any bugs or have suggestions!


---
**<p align="center">Generated by [ReadmeCodeGen](https://www.readmecodegen.com/)</p>**