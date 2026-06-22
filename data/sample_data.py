"""
CareerTrajectory AI — Sample Data
Provides realistic candidate and job data for demo purposes.
"""

import json
import random
from datetime import datetime, timedelta

# ── Sample Candidates ───────────────────────────────────────────────────────

SAMPLE_CANDIDATES = [
    {
        "id": "c001",
        "name": "Arjun Mehta",
        "email": "arjun.mehta@email.com",
        "location": "Bangalore, India",
        "years_of_experience": 3,
        "education": [
            {"degree": "B.Tech Computer Science", "institution": "IIT Delhi", "year": 2021}
        ],
        "skills": {
            "current": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Terraform"],
            "learning": ["Go", "Rust", "eBPF", "Service Mesh"],
            "history": [
                {"skill": "Python", "acquired": "2019-01"},
                {"skill": "Docker", "acquired": "2021-06"},
                {"skill": "Kubernetes", "acquired": "2022-01"},
                {"skill": "AWS", "acquired": "2022-06"},
                {"skill": "Terraform", "acquired": "2023-01"},
                {"skill": "Go", "acquired": "2024-01"},
            ]
        },
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Razorpay",
                "start": "2021-07",
                "end": "2023-06",
                "description": "Built payment processing microservices handling 10M+ transactions/day"
            },
            {
                "title": "Senior Software Engineer",
                "company": "Zepto",
                "start": "2023-07",
                "end": "present",
                "description": "Leading DevOps transformation, reduced deploy time by 70%"
            }
        ],
        "certifications": [
            {"name": "AWS Solutions Architect Professional", "date": "2023-09", "issuer": "Amazon"},
            {"name": "CKA - Certified Kubernetes Administrator", "date": "2024-01", "issuer": "CNCF"}
        ],
        "projects": [
            {
                "name": "K8s Auto-Scaler",
                "description": "Custom HPA controller using custom metrics from Prometheus",
                "skills": ["Kubernetes", "Go", "Prometheus"],
                "url": "https://github.com/arjun/k8s-autoscaler",
                "stars": 234
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "arjunmehta-dev",
                "commit_frequency": 18.5,
                "public_repos": 28,
                "followers": 312,
                "stars_earned": 891,
                "streak_days": 187,
                "top_languages": ["Go", "Python", "Shell"]
            },
            "leetcode": {
                "username": "arjun_codes",
                "problems_solved": 487,
                "contest_rating": 1924,
                "contest_rank_percentile": 85
            },
            "certifications_count": 2,
            "open_source_contributions": 15,
            "stackoverflow_reputation": 2340
        },
        "scores": {
            "semantic_fit": 0.88,
            "career_momentum": 0.91,
            "behavioral_evidence": 0.84,
            "contextual_intelligence": 0.79,
            "fps": 0.873
        },
        "hidden_gem": False,
        "predicted_trajectory": {
            "1_year": "Senior DevOps Engineer",
            "3_years": "Staff Engineer / Platform Lead",
            "5_years": "Engineering Manager / Principal Engineer"
        }
    },
    {
        "id": "c002",
        "name": "Priya Sharma",
        "email": "priya.sharma@email.com",
        "location": "Mumbai, India",
        "years_of_experience": 2,
        "education": [
            {"degree": "B.E. Electronics", "institution": "BITS Pilani", "year": 2022}
        ],
        "skills": {
            "current": ["Python", "TensorFlow", "PyTorch", "NLP", "Transformers", "LangChain"],
            "learning": ["MLOps", "Kubernetes", "Ray"],
            "history": [
                {"skill": "Python", "acquired": "2020-01"},
                {"skill": "TensorFlow", "acquired": "2021-06"},
                {"skill": "PyTorch", "acquired": "2022-01"},
                {"skill": "NLP", "acquired": "2022-06"},
                {"skill": "Transformers", "acquired": "2023-01"},
                {"skill": "LangChain", "acquired": "2023-08"},
            ]
        },
        "experience": [
            {
                "title": "ML Engineer",
                "company": "Sarvam AI",
                "start": "2022-08",
                "end": "present",
                "description": "Building multilingual NLP models for Indian languages, BERT fine-tuning"
            }
        ],
        "certifications": [
            {"name": "Deep Learning Specialization", "date": "2022-03", "issuer": "Coursera/DeepLearning.AI"},
            {"name": "MLOps Zoomcamp", "date": "2023-12", "issuer": "DataTalks.Club"}
        ],
        "projects": [
            {
                "name": "IndoNLP Toolkit",
                "description": "Open-source NLP library for 12 Indian languages with 1K+ GitHub stars",
                "skills": ["Python", "Transformers", "NLP"],
                "url": "https://github.com/priya/indonlp",
                "stars": 1203
            },
            {
                "name": "Multilingual RAG Pipeline",
                "description": "LangChain-based RAG with support for Hindi, Tamil, Bengali",
                "skills": ["LangChain", "ChromaDB", "Python"],
                "url": "https://github.com/priya/multilingual-rag",
                "stars": 567
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "priya-nlp",
                "commit_frequency": 22.3,
                "public_repos": 19,
                "followers": 891,
                "stars_earned": 2340,
                "streak_days": 234,
                "top_languages": ["Python", "Jupyter", "Shell"]
            },
            "kaggle": {
                "username": "priyasharma_ml",
                "competitions": 12,
                "medals": {"gold": 2, "silver": 3, "bronze": 4},
                "ranking_percentile": 92
            },
            "research_papers": 2,
            "certifications_count": 2,
            "open_source_contributions": 43
        },
        "scores": {
            "semantic_fit": 0.76,
            "career_momentum": 0.94,
            "behavioral_evidence": 0.92,
            "contextual_intelligence": 0.81,
            "fps": 0.858
        },
        "hidden_gem": True,
        "predicted_trajectory": {
            "1_year": "Senior ML Engineer",
            "3_years": "Staff ML Engineer / Tech Lead",
            "5_years": "AI Research Lead / Principal Scientist"
        }
    },
    {
        "id": "c003",
        "name": "Rohit Verma",
        "email": "rohit.verma@email.com",
        "location": "Hyderabad, India",
        "years_of_experience": 7,
        "education": [
            {"degree": "M.Tech Computer Science", "institution": "IIT Bombay", "year": 2017}
        ],
        "skills": {
            "current": ["Java", "Spring Boot", "Microservices", "Oracle DB", "Jenkins"],
            "learning": ["React", "TypeScript"],
            "history": [
                {"skill": "Java", "acquired": "2014-01"},
                {"skill": "Spring Boot", "acquired": "2017-01"},
                {"skill": "Oracle DB", "acquired": "2018-01"},
                {"skill": "Jenkins", "acquired": "2019-01"},
                {"skill": "React", "acquired": "2024-01"},
            ]
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Infosys",
                "start": "2017-08",
                "end": "2021-06",
                "description": "Enterprise Java applications for banking clients"
            },
            {
                "title": "Tech Lead",
                "company": "Wipro",
                "start": "2021-07",
                "end": "present",
                "description": "Leading team of 8 engineers building BFSI solutions"
            }
        ],
        "certifications": [
            {"name": "Oracle Java SE 11 Developer", "date": "2020-05", "issuer": "Oracle"}
        ],
        "projects": [
            {
                "name": "Payment Gateway Integration",
                "description": "Integrated 5 payment gateways for a major bank",
                "skills": ["Java", "Spring Boot", "REST"],
                "url": None,
                "stars": 0
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "rohitv",
                "commit_frequency": 3.2,
                "public_repos": 5,
                "followers": 34,
                "stars_earned": 12,
                "streak_days": 14,
                "top_languages": ["Java"]
            },
            "leetcode": {
                "username": "rohit_verma",
                "problems_solved": 89,
                "contest_rating": 1234,
                "contest_rank_percentile": 35
            },
            "certifications_count": 1,
            "open_source_contributions": 1,
            "stackoverflow_reputation": 890
        },
        "scores": {
            "semantic_fit": 0.52,
            "career_momentum": 0.28,
            "behavioral_evidence": 0.31,
            "contextual_intelligence": 0.61,
            "fps": 0.426
        },
        "hidden_gem": False,
        "predicted_trajectory": {
            "1_year": "Tech Lead (Same Domain)",
            "3_years": "Engineering Manager (Traditional Stack)",
            "5_years": "Senior Manager / Architect (BFSI)"
        }
    },
    {
        "id": "c004",
        "name": "Ananya Krishnan",
        "email": "ananya.k@email.com",
        "location": "Chennai, India",
        "years_of_experience": 1,
        "education": [
            {"degree": "B.Sc Mathematics", "institution": "Chennai University", "year": 2023}
        ],
        "skills": {
            "current": ["Python", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Tableau"],
            "learning": ["PyTorch", "MLflow", "Airflow", "dbt"],
            "history": [
                {"skill": "Python", "acquired": "2021-06"},
                {"skill": "SQL", "acquired": "2022-01"},
                {"skill": "Pandas", "acquired": "2022-06"},
                {"skill": "Scikit-Learn", "acquired": "2023-01"},
                {"skill": "Tableau", "acquired": "2023-06"},
                {"skill": "PyTorch", "acquired": "2024-02"},
            ]
        },
        "experience": [
            {
                "title": "Data Analyst Intern",
                "company": "PhonePe",
                "start": "2023-01",
                "end": "2023-06",
                "description": "Built dashboards and ML models for fraud detection"
            },
            {
                "title": "Junior Data Scientist",
                "company": "Darwinbox",
                "start": "2023-07",
                "end": "present",
                "description": "Building people analytics models and HR intelligence features"
            }
        ],
        "certifications": [
            {"name": "Google Data Analytics Certificate", "date": "2022-12", "issuer": "Google"},
            {"name": "IBM Data Science Professional", "date": "2023-05", "issuer": "IBM"},
            {"name": "Kaggle Python & ML Courses", "date": "2023-08", "issuer": "Kaggle"}
        ],
        "projects": [
            {
                "name": "HR Attrition Predictor",
                "description": "Predicts employee attrition with 91% accuracy using ensemble methods",
                "skills": ["Python", "XGBoost", "Scikit-Learn"],
                "url": "https://github.com/ananya/hr-attrition",
                "stars": 89
            },
            {
                "name": "Fraud Detection System",
                "description": "Real-time fraud detection using anomaly detection algorithms",
                "skills": ["Python", "IsolationForest", "Kafka"],
                "url": "https://github.com/ananya/fraud-detect",
                "stars": 156
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "ananya-ds",
                "commit_frequency": 14.7,
                "public_repos": 16,
                "followers": 234,
                "stars_earned": 456,
                "streak_days": 156,
                "top_languages": ["Python", "Jupyter", "R"]
            },
            "kaggle": {
                "username": "ananya_krishnan",
                "competitions": 8,
                "medals": {"gold": 1, "silver": 2, "bronze": 2},
                "ranking_percentile": 88
            },
            "certifications_count": 3,
            "open_source_contributions": 8
        },
        "scores": {
            "semantic_fit": 0.82,
            "career_momentum": 0.89,
            "behavioral_evidence": 0.78,
            "contextual_intelligence": 0.73,
            "fps": 0.825
        },
        "hidden_gem": True,
        "predicted_trajectory": {
            "1_year": "Data Scientist",
            "3_years": "Senior Data Scientist / ML Engineer",
            "5_years": "Lead Data Scientist / ML Platform Engineer"
        }
    },
    {
        "id": "c005",
        "name": "Vikram Nair",
        "email": "vikram.nair@email.com",
        "location": "Pune, India",
        "years_of_experience": 5,
        "education": [
            {"degree": "B.Tech Information Technology", "institution": "VIT University", "year": 2019}
        ],
        "skills": {
            "current": ["React", "Node.js", "TypeScript", "GraphQL", "MongoDB", "Redis", "AWS"],
            "learning": ["Next.js", "tRPC", "Turborepo", "Rust"],
            "history": [
                {"skill": "JavaScript", "acquired": "2018-01"},
                {"skill": "React", "acquired": "2019-06"},
                {"skill": "Node.js", "acquired": "2020-01"},
                {"skill": "TypeScript", "acquired": "2021-01"},
                {"skill": "GraphQL", "acquired": "2021-06"},
                {"skill": "Redis", "acquired": "2022-01"},
                {"skill": "AWS", "acquired": "2022-06"},
                {"skill": "Next.js", "acquired": "2023-06"},
            ]
        },
        "experience": [
            {
                "title": "Frontend Developer",
                "company": "Swiggy",
                "start": "2019-07",
                "end": "2021-06",
                "description": "Built consumer-facing features serving 20M+ users"
            },
            {
                "title": "Full Stack Engineer",
                "company": "CRED",
                "start": "2021-07",
                "end": "2023-06",
                "description": "Architected micro-frontend platform, improved LCP by 45%"
            },
            {
                "title": "Senior Full Stack Engineer",
                "company": "Notion (Remote)",
                "start": "2023-07",
                "end": "present",
                "description": "Working on collaborative editing infrastructure"
            }
        ],
        "certifications": [
            {"name": "AWS Developer Associate", "date": "2022-03", "issuer": "Amazon"},
            {"name": "Meta Frontend Developer", "date": "2023-01", "issuer": "Meta"}
        ],
        "projects": [
            {
                "name": "React Performance Toolkit",
                "description": "Bundle analysis and performance optimization toolkit for React apps",
                "skills": ["React", "TypeScript", "Webpack"],
                "url": "https://github.com/vikram/react-perf",
                "stars": 2341
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "vikramnair",
                "commit_frequency": 16.8,
                "public_repos": 34,
                "followers": 1203,
                "stars_earned": 4567,
                "streak_days": 245,
                "top_languages": ["TypeScript", "JavaScript", "Rust"]
            },
            "leetcode": {
                "username": "vikram_competitive",
                "problems_solved": 312,
                "contest_rating": 1789,
                "contest_rank_percentile": 78
            },
            "certifications_count": 2,
            "open_source_contributions": 67,
            "npm_packages": 3
        },
        "scores": {
            "semantic_fit": 0.71,
            "career_momentum": 0.85,
            "behavioral_evidence": 0.91,
            "contextual_intelligence": 0.76,
            "fps": 0.810
        },
        "hidden_gem": False,
        "predicted_trajectory": {
            "1_year": "Senior Full Stack / Frontend Lead",
            "3_years": "Staff Engineer / Frontend Architect",
            "5_years": "Principal Engineer / VP Engineering"
        }
    },
    {
        "id": "c006",
        "name": "Kavya Reddy",
        "email": "kavya.reddy@email.com",
        "location": "Bangalore, India",
        "years_of_experience": 1.5,
        "education": [
            {"degree": "B.Tech CSE", "institution": "NIT Warangal", "year": 2024}
        ],
        "skills": {
            "current": ["Python", "Rust", "C++", "Systems Programming", "LLVM", "Linux Kernel"],
            "learning": ["eBPF", "Wasm", "RISC-V"],
            "history": [
                {"skill": "C++", "acquired": "2020-06"},
                {"skill": "Python", "acquired": "2021-01"},
                {"skill": "Linux Kernel", "acquired": "2022-06"},
                {"skill": "Rust", "acquired": "2023-01"},
                {"skill": "LLVM", "acquired": "2023-08"},
                {"skill": "eBPF", "acquired": "2024-02"},
            ]
        },
        "experience": [
            {
                "title": "Systems Engineer Intern",
                "company": "ISRO",
                "start": "2023-05",
                "end": "2023-08",
                "description": "Real-time OS development for satellite telemetry systems"
            },
            {
                "title": "Systems Software Engineer",
                "company": "Supra Research (Startup)",
                "start": "2024-07",
                "end": "present",
                "description": "Building high-performance blockchain node in Rust"
            }
        ],
        "certifications": [
            {"name": "Linux Foundation Certified SysAdmin", "date": "2023-06", "issuer": "Linux Foundation"}
        ],
        "projects": [
            {
                "name": "Mini OS Kernel",
                "description": "x86-64 OS kernel written in Rust with basic scheduler and memory management",
                "skills": ["Rust", "x86 Assembly", "Systems"],
                "url": "https://github.com/kavya/rust-kernel",
                "stars": 1876
            },
            {
                "name": "eBPF Network Monitor",
                "description": "Zero-overhead network observability tool using eBPF",
                "skills": ["eBPF", "C", "Python"],
                "url": "https://github.com/kavya/ebpf-monitor",
                "stars": 934
            }
        ],
        "behavioral_signals": {
            "github": {
                "username": "kavyareddy-sys",
                "commit_frequency": 21.4,
                "public_repos": 22,
                "followers": 2341,
                "stars_earned": 5678,
                "streak_days": 312,
                "top_languages": ["Rust", "C", "C++", "Assembly"]
            },
            "codeforces": {
                "handle": "kavya_cp",
                "rating": 1987,
                "rank": "Expert",
                "contests_participated": 89
            },
            "certifications_count": 1,
            "open_source_contributions": 34,
            "kernel_patches": 3
        },
        "scores": {
            "semantic_fit": 0.67,
            "career_momentum": 0.97,
            "behavioral_evidence": 0.95,
            "contextual_intelligence": 0.72,
            "fps": 0.838
        },
        "hidden_gem": True,
        "predicted_trajectory": {
            "1_year": "Systems Software Engineer",
            "3_years": "Senior Systems Engineer / Compiler Engineer",
            "5_years": "Principal Systems Architect / OS/Infra Lead"
        }
    }
]

# ── Sample Jobs ──────────────────────────────────────────────────────────────

SAMPLE_JOBS = [
    {
        "id": "j001",
        "title": "Senior ML Engineer",
        "company": "TechCorp AI",
        "location": "Bangalore, India (Hybrid)",
        "department": "AI Platform",
        "description": """
        We are looking for a Senior ML Engineer to join our AI Platform team.
        You will build and maintain production ML systems that serve millions of users.
        
        Responsibilities:
        - Design and implement ML pipelines using Python and PyTorch/TensorFlow
        - Build MLOps infrastructure using Kubernetes and MLflow
        - Collaborate with research team to productionize models
        - Mentor junior engineers
        
        Requirements:
        - 3+ years of ML Engineering experience
        - Strong Python skills
        - Experience with NLP, Transformers, LLMs preferred
        - Kubernetes/Docker for ML workloads
        - LangChain or similar LLM frameworks
        """,
        "required_skills": ["Python", "PyTorch", "TensorFlow", "NLP", "Transformers", "MLOps"],
        "good_to_have": ["LangChain", "Kubernetes", "Ray", "MLflow", "CUDA"],
        "domain": "Machine Learning / AI",
        "growth_requirements": ["LLMs", "MLOps", "Distributed Training"],
        "level": "Senior",
        "salary_range": "₹40L - ₹70L"
    },
    {
        "id": "j002",
        "title": "DevOps / Platform Engineer",
        "company": "CloudScale Inc",
        "location": "Hyderabad, India (Remote-First)",
        "department": "Platform Engineering",
        "description": """
        CloudScale is hiring a DevOps/Platform Engineer to scale our infrastructure.
        
        Responsibilities:
        - Design and manage Kubernetes clusters at scale
        - Build CI/CD pipelines and developer experience tooling
        - Infrastructure as Code using Terraform
        - Cloud architecture on AWS/GCP
        - On-call for platform reliability
        
        Requirements:
        - 3+ years DevOps/Platform Engineering experience
        - Expert-level Kubernetes
        - AWS or GCP experience
        - Terraform/Pulumi
        - Strong scripting (Python/Go/Shell)
        """,
        "required_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Python"],
        "good_to_have": ["Go", "eBPF", "Istio", "ArgoCD", "Prometheus", "Grafana"],
        "domain": "Platform Engineering / DevOps",
        "growth_requirements": ["Service Mesh", "eBPF", "Multi-Cloud"],
        "level": "Mid-Senior",
        "salary_range": "₹30L - ₹55L"
    },
    {
        "id": "j003",
        "title": "Full Stack Engineer",
        "company": "ProductHouse",
        "location": "Mumbai, India (On-site)",
        "department": "Product Engineering",
        "description": """
        Join our product engineering team building next-generation SaaS products.
        
        Responsibilities:
        - Build full-stack features using React/Next.js and Node.js
        - Design GraphQL APIs
        - Work with MongoDB and Redis
        - Deploy on AWS
        
        Requirements:
        - 3+ years full-stack experience
        - React/TypeScript expert
        - Node.js backend experience
        - GraphQL/REST APIs
        - Cloud deployment experience
        """,
        "required_skills": ["React", "TypeScript", "Node.js", "GraphQL", "MongoDB"],
        "good_to_have": ["Next.js", "Redis", "AWS", "tRPC", "Turborepo"],
        "domain": "Full Stack / Product Engineering",
        "growth_requirements": ["Next.js App Router", "Edge Computing", "AI Integration"],
        "level": "Mid-Senior",
        "salary_range": "₹25L - ₹45L"
    }
]


def get_candidates():
    try:
        import streamlit as st
        from streamlit.runtime import exists
        if not exists():
            return SAMPLE_CANDIDATES
            
        # Only return sample candidates if explicitly toggled on
        if st.session_state.get("use_sample_data", False):
            return SAMPLE_CANDIDATES
        return []
    except Exception:
        # Fallback for non-streamlit scripts
        return SAMPLE_CANDIDATES


def get_jobs():
    return SAMPLE_JOBS


def get_candidate_by_id(candidate_id):
    for c in SAMPLE_CANDIDATES:
        if c["id"] == candidate_id:
            return c
    return None


def get_job_by_id(job_id):
    for j in SAMPLE_JOBS:
        if j["id"] == job_id:
            return j
    return None
