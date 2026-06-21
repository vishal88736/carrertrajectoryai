"""
CareerTrajectory AI — Resume Parser Agent
Extracts structured information from PDF/DOCX resumes.
Thin wrapper around Agent #01 for backward compatibility with fallback parsing.
"""

import re
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

# ─── Known Skills List ────────────────────────────────────────────────────────

KNOWN_SKILLS = [
    # ML / AI
    "Python", "PyTorch", "TensorFlow", "Keras", "scikit-learn", "XGBoost",
    "LightGBM", "CatBoost", "ONNX", "CUDA", "JAX", "Hugging Face", "Transformers",
    "LangChain", "LlamaIndex", "FAISS", "Pinecone", "RAG", "RLHF", "LoRA",
    "Stable Diffusion", "GPT", "BERT", "T5", "Whisper", "spaCy", "NLTK",
    "MLflow", "Ray", "Optuna", "AutoML", "Fine-Tuning", "Computer Vision", "NLP",
    "OpenAI", "LLM", "MLOps", "Kubeflow", "DVC",
    # Data
    "pandas", "NumPy", "Polars", "Dask", "PySpark", "Spark", "Kafka",
    "Airflow", "dbt", "Prefect", "Luigi", "Great Expectations",
    "SQL", "PostgreSQL", "MySQL", "SQLite", "Oracle", "Snowflake", "BigQuery",
    "Redshift", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch",
    "Neo4j", "InfluxDB", "TimescaleDB", "RabbitMQ", "Celery", "Hadoop",
    # Backend
    "FastAPI", "Django", "Flask", "Express", "Spring Boot", "gRPC", "GraphQL",
    "REST API", "Microservices", "WebSockets",
    # Frontend
    "React", "Next.js", "Vue", "Angular", "TypeScript", "JavaScript",
    "Tailwind", "HTML", "CSS", "Svelte", "Webpack", "Vite",
    # DevOps / Cloud
    "Docker", "Kubernetes", "Terraform", "Helm", "ArgoCD", "Istio",
    "AWS", "GCP", "Azure", "Cloudflare", "Vercel", "Heroku", "Ansible",
    "GitHub Actions", "CircleCI", "Jenkins", "Prometheus", "Grafana",
    "Datadog", "OpenTelemetry", "GitLab CI",
    # Languages
    "Go", "Rust", "Java", "Scala", "C++", "C", "C#", "Ruby", "PHP",
    "Swift", "Kotlin", "R", "MATLAB", "Julia", "Bash", "Elixir", "Assembly",
    # Security / Other
    "OAuth", "JWT", "TLS", "Cryptography", "Penetration Testing",
    "Linux", "Unix", "Git", "Vim", "Jupyter", "Embedded Systems", "eBPF", "Wasm", "LLVM"
]

_SKILLS_LOWER = {s.lower(): s for s in KNOWN_SKILLS}


# ─── Public Entry Points ───────────────────────────────────────────────────────

def parse_resume(file_bytes: bytes, file_type: str = "pdf") -> Dict[str, Any]:
    """
    Parse resume bytes. Uses Agent #01 when available, falls back to full
    structured regex extraction. Returns a candidate dict.
    """
    if not file_bytes:
        return {"error": "Empty file received. Please upload a valid resume."}

    try:
        # Try importing Agent #01
        from backend.agents.agent_01_resume import ResumeIntelligenceAgent
        agent = ResumeIntelligenceAgent()
        
        # Safe async runner for event loop environments (Streamlit)
        result = _run_async(agent.parse, file_bytes, file_type)

        skill_list = result.get("skills", [])
        timeline = result.get("learning_timeline", [])
        result["skills"] = {
            "current": skill_list,
            "learning": [t.get("skill", "") for t in timeline[-3:] if isinstance(t, dict)],
            "history": timeline,
        }
        result.setdefault("location", "Uploaded")
        result.setdefault("hidden_gem", False)
        result.setdefault("scores", _empty_scores())
        return result

    except Exception as e:
        logger.warning(f"Agent #01 failed: {e}. Using structured fallback parser.")
        return _fallback_parse(file_bytes, file_type)


def build_career_timeline(candidate: Dict) -> List[Dict]:
    """Builds a chronological career timeline from candidate data."""
    timeline = []

    for cert in candidate.get("certifications", []):
        timeline.append({
            "type": "certification",
            "date": cert.get("date", "") or cert.get("year", ""),
            "title": cert.get("name", ""),
            "icon": "🏆"
        })

    skills_history = candidate.get("skills", {})
    if isinstance(skills_history, dict):
        skills_history = skills_history.get("history", [])
    else:
        skills_history = candidate.get("learning_timeline", [])
        
    for skill_item in skills_history:
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
            if not d:
                return datetime(2000, 1, 1)
            if "-" in str(d):
                return datetime.strptime(str(d)[:7], "%Y-%m")
            elif str(d).isdigit():
                return datetime(int(d), 1, 1)
            return datetime(2000, 1, 1)
        except Exception:
            return datetime(2000, 1, 1)

    timeline.sort(key=parse_date_key)
    return timeline


# ─── Thread-Safe Async Helper ──────────────────────────────────────────────────

def _run_async(async_func, *args, **kwargs) -> Any:
    """Runs an async function synchronously in a separate thread if a loop is running."""
    import asyncio
    import concurrent.futures
    
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
            
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(runner)
            return future.result()
    else:
        return runner()


# ─── Fallback Parser ──────────────────────────────────────────────────────────

def _fallback_parse(file_bytes: bytes, file_type: str) -> Dict[str, Any]:
    """Full structured fallback parser — section-aware, no agent required."""
    text = ""
    try:
        if file_type == "pdf":
            text = _extract_pdf_text(file_bytes)
        elif file_type in ("docx", "doc"):
            text = _extract_docx_text(file_bytes)
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as exc:
        logger.warning(f"Text extraction failed: {exc}")

    if not text.strip():
        logger.warning("Empty text extracted from resume — returning minimal skeleton.")

    sections = _split_sections(text)

    skills       = _extract_skills(text)
    email        = _extract_email(text)
    phone        = _extract_phone(text)
    name         = _extract_name(text)
    yoe          = _extract_yoe(text)
    location     = _extract_location(text)
    linkedin     = _extract_linkedin(text)
    github       = _extract_github(text)
    education    = _extract_education(sections.get("education", ""), text)
    experience   = _extract_experience(sections.get("experience", ""))
    projects     = _extract_projects(sections.get("projects", ""))
    certs        = _extract_certifications(sections.get("certifications", ""), text)
    summary      = _extract_summary(sections.get("summary", ""), text)
    achievements = _extract_achievements(sections.get("achievements", ""), text)

    skill_history = [
        {"skill": s, "acquired": "2023-01", "proficiency": "intermediate"}
        for s in skills
    ]

    return {
        "id": f"c_parsed_{abs(hash(file_bytes)) % 10000:04d}",
        "name": name or "Uploaded Candidate",
        "email": email or "",
        "phone": phone or "",
        "location": location or "Uploaded",
        "linkedin": linkedin or "",
        "github_url": github or "",
        "github_username": _github_url_to_username(github),
        "summary": summary or "",
        "years_of_experience": yoe,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certs,
        "achievements": achievements,
        "behavioral_signals": {
            "github_active": bool(github),
            "has_projects": bool(projects),
            "has_certifications": bool(certs),
            "certifications_count": len(certs)
        },
        "skills": {
            "current": skills,
            "learning": [],
            "history": skill_history,
        },
        "hidden_gem": False,
        "scores": _empty_scores(),
        "learning_timeline": skill_history,
        "raw_text_preview": text[:500] + "..." if len(text) > 500 else text,
        "parsed_at": datetime.now().isoformat()
    }


# ─── PDF & Word Text Extraction ───────────────────────────────────────────────

def _extract_pdf_text(file_bytes: bytes) -> str:
    """
    Three-tier extraction:
      1. pdfplumber  — best layout fidelity, handles columns & tables
      2. pymupdf     — fast, good for most PDFs
      3. PyPDF2      — last resort fallback
    """

    # ── Tier 1: pdfplumber ──
    try:
        import pdfplumber
        pages_text: List[str] = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""

                for table in page.extract_tables() or []:
                    for row in table:
                        if row:
                            pages_text.append("\t".join(
                                (cell or "").strip() for cell in row
                            ))

                if page_text.strip():
                    pages_text.append(page_text)

        result = "\n".join(pages_text).strip()
        if result:
            logger.debug(f"pdfplumber extracted {len(result)} chars")
            return result
    except Exception as e:
        logger.debug(f"pdfplumber failed: {e}")

    # ── Tier 2: pymupdf (fitz) ──
    try:
        import fitz  # pymupdf
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            blocks = page.get_text("blocks")
            blocks_sorted = sorted(blocks, key=lambda b: (round(b[1] / 10), b[0]))
            page_text = "\n".join(b[4].strip() for b in blocks_sorted if b[4].strip())
            if page_text:
                pages_text.append(page_text)
        result = "\n".join(pages_text).strip()
        if result:
            logger.debug(f"pymupdf extracted {len(result)} chars")
            return result
    except Exception as e:
        logger.debug(f"pymupdf failed: {e}")

    # ── Tier 3: PyPDF2 ──
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                pages_text.append(t)
        result = "\n".join(pages_text).strip()
        if result:
            logger.debug(f"PyPDF2 extracted {len(result)} chars")
            return result
    except Exception as e:
        logger.debug(f"PyPDF2 failed: {e}")

    logger.error("All PDF extraction methods failed — returning empty string.")
    return ""


def _extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.debug(f"python-docx failed: {e}")
        return ""


# ─── Section Splitter ─────────────────────────────────────────────────────────

_SECTION_HEADINGS: Dict[str, List[str]] = {
    "summary":        ["summary", "profile", "about me", "objective", "professional summary",
                       "career objective", "overview"],
    "experience":     ["experience", "work experience", "professional experience",
                       "employment", "employment history", "work history", "career history",
                       "positions held", "relevant experience"],
    "education":      ["education", "academic background", "qualifications",
                       "academic qualifications", "educational background"],
    "skills":         ["skills", "technical skills", "core competencies", "key skills",
                       "competencies", "technologies", "tech stack", "tools & technologies",
                       "programming languages", "frameworks"],
    "projects":       ["projects", "personal projects", "key projects", "notable projects",
                       "side projects", "open source", "portfolio"],
    "certifications": ["certifications", "certificates", "certification", "licenses",
                       "professional certifications", "courses", "training"],
    "achievements":   ["achievements", "accomplishments", "awards", "honors",
                       "recognition", "publications", "patents"],
    "languages":      ["languages", "spoken languages"],
    "interests":      ["interests", "hobbies", "activities", "volunteering"],
}

_ALL_HEADINGS = [h for variants in _SECTION_HEADINGS.values() for h in variants]
_HEADING_PATTERN = re.compile(
    r"(?im)^[ \t]*(" +
    "|".join(re.escape(h) for h in sorted(_ALL_HEADINGS, key=len, reverse=True)) +
    r")[ \t]*[:\-–—]?[ \t]*$"
)


def _split_sections(text: str) -> Dict[str, str]:
    """Splits resume text into named sections based on heading detection."""
    if not text.strip():
        return {}

    matches = list(_HEADING_PATTERN.finditer(text))
    if not matches:
        return {"experience": text}

    heading_to_key: Dict[str, str] = {}
    for key, variants in _SECTION_HEADINGS.items():
        for v in variants:
            heading_to_key[v.lower()] = key

    sections: Dict[str, str] = {}
    for i, match in enumerate(matches):
        heading_text = match.group(1).strip().lower()
        canonical = heading_to_key.get(heading_text, heading_text)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        
        if canonical in sections:
            sections[canonical] += "\n" + content
        else:
            sections[canonical] = content

    return sections


# ─── Field Extractors ─────────────────────────────────────────────────────────

def _extract_email(text: str) -> str:
    m = re.search(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    m = re.search(
        r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}", text
    )
    return m.group(0).strip() if m else ""


def _extract_linkedin(text: str) -> str:
    m = re.search(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE)
    return f"https://{m.group(0)}" if m else ""


def _extract_github(text: str) -> str:
    m = re.search(r"github\.com/[\w\-]+", text, re.IGNORECASE)
    return f"https://{m.group(0)}" if m else ""


def _github_url_to_username(url: str) -> Optional[str]:
    if not url:
        return None
    m = re.search(r"github\.com/([a-zA-Z0-9\-]+)", url, re.IGNORECASE)
    return m.group(1) if m else None


def _extract_location(text: str) -> str:
    """Extracts city/state/country from the top portion of the resume."""
    header = "\n".join(text.splitlines()[:15])
    patterns = [
        r"\b([A-Z][a-zA-Z\s]+),\s*([A-Z]{2,})\b",
        r"\b([A-Z][a-zA-Z\s]+),\s*([A-Z][a-zA-Z\s]+)\b",
    ]
    for pat in patterns:
        m = re.search(pat, header)
        if m:
            candidate = m.group(0).strip()
            if len(candidate) < 50 and not any(w in candidate.lower() for w in
                                                ["engineer", "developer", "manager", "analyst"]):
                return candidate
    return ""


def _extract_name(text: str) -> str:
    """Extracts candidate name from the first non-empty lines."""
    skip_patterns = re.compile(
        r"[@\d|•]|linkedin|github|http|resume|curriculum|vitae|"
        r"engineer|developer|analyst|manager|director|scientist|"
        r"intern|consultant|architect|designer|lead|senior|junior",
        re.IGNORECASE,
    )
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:8]:
        words = line.split()
        if 2 <= len(words) <= 4 and not skip_patterns.search(line):
            if all(w[0].isupper() for w in words if w):
                return line
    return ""


def _extract_yoe(text: str) -> float:
    """Extracts explicit years-of-experience claims, with date-range fallback."""
    explicit_patterns = [
        r"(\d+)\+?\s+years?\s+(?:of\s+)?(?:professional\s+)?experience",
        r"(\d+)\+?\s+yrs?\s+(?:of\s+)?(?:exp(?:erience)?)",
        r"experience[:\s]+(\d+)\+?\s+years?",
        r"over\s+(\d+)\s+years?\s+(?:of\s+)?experience",
    ]
    for pat in explicit_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 0 < val < 50:
                return val

    # Fallback: date ranges
    years = re.findall(r"\b(20\d{2}|19[89]\d)\b", text)
    if len(years) >= 2:
        year_ints = sorted(set(int(y) for y in years))
        span = year_ints[-1] - year_ints[0]
        if 0 < span < 50:
            return float(span)

    return 2.0


def _extract_summary(summary_section: str, full_text: str) -> str:
    """Returns the professional summary / objective."""
    if summary_section.strip():
        sentences = re.split(r"(?<=[.!?])\s+", summary_section.strip())
        return " ".join(sentences[:5]).strip()
    return ""


# ─── Structured Block Extractors ─────────────────────────────────────────────

def _parse_start_end_dates(date_str: str) -> tuple:
    """Parses date range string (e.g. 'Jan 2020 - Present') to YYYY-MM and present."""
    if not date_str:
        return "", ""
    parts = re.split(r'[-–—]', date_str)
    start = parts[0].strip()
    end = parts[1].strip() if len(parts) > 1 else ""
    
    def clean_part(p: str, default_end: bool = False) -> str:
        p_lower = p.lower()
        if "present" in p_lower or "current" in p_lower or "now" in p_lower:
            return "present"
        yr_match = re.search(r'\b(20\d{2}|19[89]\d)\b', p)
        if not yr_match:
            return p
        yr = yr_match.group(1)
        months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        for idx, m in enumerate(months):
            if m in p_lower:
                return f"{yr}-{idx+1:02d}"
        return f"{yr}-01" if not default_end else f"{yr}-12"

    return clean_part(start), clean_part(end, default_end=True)


def _extract_experience(section_text: str) -> List[Dict]:
    """
    Parses experience section into structured job entries.
    Robust to Title -> Company -> Date format and bullets.
    """
    if not section_text.strip():
        return []

    DATE_RE = re.compile(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*(\d{4})"
        r"|(\d{4})\s*[-–—]\s*(\d{4}|present|current|now)",
        re.IGNORECASE,
    )
    
    TITLE_RE = re.compile(
        r"\b(engineer|developer|analyst|manager|director|lead|scientist|"
        r"designer|architect|consultant|intern|specialist|officer|head)\b",
        re.IGNORECASE,
    )

    entries: List[Dict] = []
    blocks = re.split(r"\n{2,}", section_text.strip())

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        title, company, duration = "", "", ""
        description_lines = []
        
        date_line_idx = -1
        for idx, line in enumerate(lines):
            if DATE_RE.search(line):
                duration = line
                date_line_idx = idx
                break
        
        non_date_lines = [l for i, l in enumerate(lines) if i != date_line_idx]
        if not non_date_lines:
            continue
            
        first_line = non_date_lines[0]
        second_line = non_date_lines[1] if len(non_date_lines) > 1 else ""
        
        if TITLE_RE.search(first_line):
            title = first_line
            if second_line and not second_line.startswith(('-', '•', '▸', '*')):
                company = second_line
        else:
            if second_line and TITLE_RE.search(second_line):
                title = second_line
                company = first_line
            else:
                title = first_line
                
        for line in lines:
            if line != title and line != company and line != duration:
                description_lines.append(line)
                
        if title or company:
            start, end = _parse_start_end_dates(duration)
            entries.append({
                "title": title,
                "company": company,
                "start": start,
                "end": end,
                "duration": duration,
                "description": " ".join(description_lines),
                "bullets": description_lines,
            })
            
    return entries


def _extract_education(section_text: str, full_text: str) -> List[Dict]:
    """Parses education entries, falling back to full text if section is empty."""
    text_to_parse = section_text if section_text.strip() else full_text
    if not text_to_parse.strip():
        return []

    DEGREE_RE = re.compile(
        r"\b(B\.?S\.?|B\.?E\.?|B\.?Tech|B\.?Sc|B\.?A\.?|M\.?S\.?|M\.?E\.?|"
        r"M\.?Tech|M\.?Sc|M\.?A\.?|Ph\.?D\.?|MBA|BCA|MCA|Bachelor|Master|Doctor)"
        r"[\s\w,\.]*",
        re.IGNORECASE,
    )
    YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
    GPA_RE  = re.compile(r"(?:GPA|CGPA|Grade)[:\s]*(\d+\.?\d*)\s*/?\s*(\d+\.?\d*)?", re.IGNORECASE)

    entries: List[Dict] = []
    blocks = re.split(r"\n{2,}", text_to_parse.strip())

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        degree, institution, year, gpa = "", "", "", ""
        for line in lines:
            dm = DEGREE_RE.search(line)
            if dm and not degree:
                degree = line
            ym = YEAR_RE.search(line)
            if ym and not year:
                year = ym.group(0)
            gm = GPA_RE.search(line)
            if gm and not gpa:
                gpa = gm.group(0)
            if not degree and not institution:
                institution = line
            elif degree and not institution and line != degree:
                institution = line

        if degree or institution:
            entries.append({
                "degree": degree,
                "institution": institution,
                "year": year,
                "gpa": gpa,
            })

    return entries if entries else []


def _extract_projects(section_text: str) -> List[Dict]:
    """Parses project entries: name, description, tech stack."""
    if not section_text.strip():
        return []

    TECH_RE = re.compile(
        r"\b(Python|PyTorch|TensorFlow|FastAPI|React|Node\.js|Docker|Kubernetes|"
        r"AWS|GCP|Azure|PostgreSQL|MongoDB|Redis|Kafka|Spark|LangChain|"
        r"TypeScript|Go|Rust|Java|Scala|C\+\+|SQL|GraphQL|FAISS|RAG)\b",
        re.IGNORECASE,
    )
    URL_RE = re.compile(r"https?://\S+|github\.com/\S+", re.IGNORECASE)

    entries: List[Dict] = []
    blocks = re.split(r"\n{2,}", section_text.strip())

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        name = lines[0].lstrip("•▸-–— ").strip()
        desc_lines = lines[1:]
        description = " ".join(desc_lines)
        tech = list(set(TECH_RE.findall(description + " " + name)))
        
        normalized_tech = []
        for t in tech:
            if t.lower() in _SKILLS_LOWER:
                normalized_tech.append(_SKILLS_LOWER[t.lower()])
            else:
                normalized_tech.append(t)
                
        url_m = URL_RE.search(block)

        entries.append({
            "name": name,
            "description": description,
            "tech_stack": normalized_tech,
            "skills": normalized_tech,
            "url": url_m.group(0) if url_m else "",
        })

    return entries


def _extract_certifications(section_text: str, full_text: str) -> List[Dict]:
    """Extracts certifications, falling back to full text if empty."""
    text_to_parse = section_text if section_text.strip() else full_text
    if not text_to_parse.strip():
        return []

    ISSUERS = re.compile(
        r"(AWS|Google|Microsoft|Meta|Coursera|Udemy|edX|LinkedIn|IBM|Cisco|"
        r"Oracle|CompTIA|PMI|Salesforce|HashiCorp|NVIDIA|DeepLearning\.AI)",
        re.IGNORECASE,
    )
    YEAR_RE = re.compile(r"\b(20\d{2})\b")

    entries: List[Dict] = []
    lines = [l.strip().lstrip("•▸-–— ") for l in text_to_parse.splitlines() if l.strip()]

    for line in lines:
        if len(line) < 5:
            continue
        issuer_m = ISSUERS.search(line)
        year_m   = YEAR_RE.search(line)
        
        # Keep year and date for schema compatibility
        year_val = year_m.group(0) if year_m else ""
        entries.append({
            "name": line,
            "issuer": issuer_m.group(0) if issuer_m else "Unknown",
            "year": year_val,
            "date": year_val or "Unknown",
        })

    return entries


def _extract_achievements(section_text: str, full_text: str) -> List[str]:
    """Extracts achievements from section, falling back to full text if empty."""
    text_to_parse = section_text if section_text.strip() else full_text
    if not text_to_parse.strip():
        return []
    lines = [
        l.strip().lstrip("•▸-–— ").strip()
        for l in text_to_parse.splitlines()
        if l.strip()
    ]
    return [l for l in lines if len(l) > 10]


# ─── Skills Extractor ─────────────────────────────────────────────────────────

def _extract_skills(text: str) -> List[str]:
    """Case-insensitive skill detection over the full resume text."""
    found_lower = set()
    found = []
    text_lower = text.lower()
    for lower, canonical in _SKILLS_LOWER.items():
        pattern = r"(?<![a-z])" + re.escape(lower) + r"(?![a-z])"
        if re.search(pattern, text_lower):
            if lower not in found_lower:
                found.append(canonical)
                found_lower.add(lower)
    return sorted(found)


# ─── Backwards Compatible Wrapper Functions ───────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    return _extract_pdf_text(file_bytes)


def extract_text_from_docx(file_bytes: bytes) -> str:
    return _extract_docx_text(file_bytes)


def extract_skills(text: str) -> List[str]:
    return _extract_skills(text)


def extract_contact_info(text: str) -> Dict[str, str]:
    return {
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "linkedin": _extract_linkedin(text),
        "github": _extract_github(text)
    }


def extract_education(text: str) -> List[Dict]:
    return _extract_education("", text)


def extract_certifications(text: str) -> List[Dict]:
    return _extract_certifications("", text)


def extract_years_experience(text: str) -> float:
    return _extract_yoe(text)


def extract_github_username(text: str) -> Optional[str]:
    github_url = _extract_github(text)
    if github_url:
        return _github_url_to_username(github_url)
    return None


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _empty_scores() -> Dict[str, float]:
    return {
        "fps": 0.0, "semantic_fit": 0.0, "career_trajectory": 0.0,
        "behavioral_evidence": 0.0, "project_quality": 0.0,
        "future_growth": 0.0, "organization_fit": 0.0,
        "career_momentum": 0.0, "contextual_intelligence": 0.0,
    }
