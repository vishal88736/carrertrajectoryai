"""
CareerTrajectory AI — Resume Parser Agent
Extracts structured information from PDF/DOCX resumes.
"""

import re
import io
from typing import Dict, List, Any, Optional
from datetime import datetime


# Try to import PDF/DOCX libraries; fall back gracefully for demo
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ─── Skill Keywords Dictionary ────────────────────────────────────────────────

KNOWN_SKILLS = {
    # Languages
    "python", "javascript", "typescript", "java", "go", "rust", "c++", "c#",
    "ruby", "scala", "kotlin", "swift", "php", "r", "matlab", "julia", "elixir",
    # AI/ML
    "pytorch", "tensorflow", "keras", "scikit-learn", "xgboost", "lightgbm",
    "transformers", "huggingface", "nlp", "computer vision", "langchain",
    "openai", "llm", "rag", "fine-tuning", "bert", "gpt", "stable diffusion",
    "mlops", "kubeflow", "mlflow", "ray", "dvc",
    # Web
    "react", "next.js", "vue", "angular", "svelte", "node.js", "express",
    "django", "fastapi", "flask", "graphql", "rest api", "tailwind", "css",
    "html", "webpack", "vite",
    # DevOps
    "kubernetes", "docker", "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "argocd", "helm", "istio", "aws", "gcp", "azure",
    "prometheus", "grafana", "elasticsearch", "datadog",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "cassandra", "elasticsearch",
    "dynamodb", "snowflake", "bigquery", "spark", "hadoop",
    # Systems
    "linux", "ebpf", "wasm", "llvm", "assembly", "embedded systems",
}

CERTIFICATION_PATTERNS = [
    r"(aws\s+(?:certified|solutions\s+architect|developer|devops)[^,\n]*)",
    r"(google\s+(?:cloud|associate|professional)[^,\n]*)",
    r"(azure\s+(?:certified|administrator|developer)[^,\n]*)",
    r"(cka|ckad|cks)[^,\n]*",
    r"(tensorflow\s+developer\s+certificate)",
    r"(deep\s+learning\s+specialization)",
    r"(coursera|udacity|edx)\s+[^,\n]{10,60}",
    r"(pmp|scrum\s+master|csm)[^,\n]*",
    r"(oracle\s+java[^,\n]*)",
    r"(linux\s+foundation[^,\n]*)",
]

DEGREE_PATTERNS = [
    r"(b\.?tech|bachelor\s+of\s+technology)[^,\n]*",
    r"(m\.?tech|master\s+of\s+technology)[^,\n]*",
    r"(b\.?e\.?|bachelor\s+of\s+engineering)[^,\n]*",
    r"(m\.?s\.?|master\s+of\s+science)[^,\n]*",
    r"(b\.?s\.?c?|bachelor\s+of\s+science)[^,\n]*",
    r"(ph\.?d|doctor\s+of\s+philosophy)[^,\n]*",
    r"(m\.?b\.?a)[^,\n]*",
]

COMPANY_PATTERNS = [
    r"(?:at|@|with|for)\s+([A-Z][a-zA-Z0-9\s&.,]{2,40}(?:Inc|Ltd|LLC|Corp|Pvt|Technologies|Systems|Solutions)?)",
    r"([A-Z][a-zA-Z0-9\s]{2,30})\s*\|\s*(?:Software|Senior|Lead|Principal|Engineer|Developer|Analyst)",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    if not PDF_AVAILABLE:
        return ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception:
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    if not DOCX_AVAILABLE:
        return ""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception:
        return ""


def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text using keyword matching."""
    text_lower = text.lower()
    found_skills = []
    for skill in KNOWN_SKILLS:
        # Whole word matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Capitalize properly
            found_skills.append(skill.title() if skill.islower() else skill)
    return list(set(found_skills))


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract email and phone from resume."""
    contact = {}

    # Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        contact["email"] = email_match.group()

    # Phone
    phone_match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3,5}[-\s\.]?[0-9]{4,6}', text)
    if phone_match:
        contact["phone"] = phone_match.group()

    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-]+)', text)
    if linkedin_match:
        contact["linkedin"] = "https://linkedin.com/in/" + linkedin_match.group(1)

    # GitHub
    github_match = re.search(r'github\.com/([a-zA-Z0-9\-]+)', text)
    if github_match:
        contact["github"] = "https://github.com/" + github_match.group(1)

    return contact


def extract_education(text: str) -> List[Dict]:
    """Extract education information."""
    education = []
    text_lower = text.lower()

    for pattern in DEGREE_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for m in matches:
            # Look for year nearby
            year_match = re.search(r'20[0-2]\d', text[max(0, m.start()-100):m.end()+100])
            year = int(year_match.group()) if year_match else None
            education.append({
                "degree": m.group().strip().title(),
                "year": year
            })

    return education[:3]  # Limit to 3 entries


def extract_certifications(text: str) -> List[Dict]:
    """Extract certifications from resume."""
    certs = []
    for pattern in CERTIFICATION_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            cert_text = m.group().strip()
            year_match = re.search(r'20[0-2]\d', text[m.start():m.end()+100])
            certs.append({
                "name": cert_text[:100],
                "date": year_match.group() if year_match else "Unknown"
            })
    return certs[:10]


def extract_years_experience(text: str) -> float:
    """Estimate years of experience from date ranges in text."""
    # Look for date ranges like "2019 - 2022" or "Jan 2020 - Present"
    year_pattern = r'20([1-2]\d)'
    years = re.findall(year_pattern, text)
    years = [2000 + int(y) for y in years]

    if not years:
        return 0

    current_year = datetime.now().year
    oldest_year = min(years)
    yoe = current_year - oldest_year

    return max(round(yoe, 1), 0)


def extract_github_username(text: str) -> Optional[str]:
    """Extract GitHub username from resume."""
    match = re.search(r'github\.com/([a-zA-Z0-9\-]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parse_resume(file_bytes: bytes, file_type: str = "pdf") -> Dict[str, Any]:
    """
    Main resume parsing function.
    Returns a structured candidate profile.
    """
    # Extract text
    if file_type.lower() == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif file_type.lower() in ("docx", "doc"):
        text = extract_text_from_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    if not text.strip():
        return {"error": "Could not extract text from resume"}

    # Extract all components
    contact = extract_contact_info(text)
    skills = extract_skills(text)
    education = extract_education(text)
    certifications = extract_certifications(text)
    yoe = extract_years_experience(text)
    github = extract_github_username(text)

    # Extract name (first line usually)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name_candidate = lines[0] if lines else "Unknown"
    # Name typically doesn't contain numbers
    if any(char.isdigit() for char in name_candidate):
        name_candidate = "Unknown"

    return {
        "name": name_candidate,
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "linkedin": contact.get("linkedin", ""),
        "github_url": contact.get("github", ""),
        "github_username": github,
        "years_of_experience": yoe,
        "education": education,
        "skills": {
            "current": skills,
            "learning": [],
            "history": []
        },
        "certifications": certifications,
        "raw_text_preview": text[:500] + "..." if len(text) > 500 else text,
        "parsed_at": datetime.now().isoformat()
    }


def build_career_timeline(candidate: Dict) -> List[Dict]:
    """Builds a chronological career timeline from candidate data."""
    timeline = []

    for cert in candidate.get("certifications", []):
        timeline.append({
            "type": "certification",
            "date": cert.get("date", ""),
            "title": cert.get("name", ""),
            "icon": "🏆"
        })

    for skill_item in candidate.get("skills", {}).get("history", []):
        timeline.append({
            "type": "skill",
            "date": skill_item.get("acquired", ""),
            "title": f"Learned {skill_item.get('skill', '')}",
            "icon": "📚"
        })

    for exp in candidate.get("experience", []):
        timeline.append({
            "type": "experience",
            "date": exp.get("start", ""),
            "title": f"{exp.get('title', '')} @ {exp.get('company', '')}",
            "icon": "💼"
        })

    # Sort by date
    def parse_date_key(item):
        try:
            d = item.get("date", "")
            if "-" in str(d):
                return datetime.strptime(str(d)[:7], "%Y-%m")
            elif str(d).isdigit():
                return datetime(int(d), 1, 1)
            return datetime(2000, 1, 1)
        except Exception:
            return datetime(2000, 1, 1)

    timeline.sort(key=parse_date_key)
    return timeline
