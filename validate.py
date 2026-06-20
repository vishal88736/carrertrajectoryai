"""Quick validation script for CareerTrajectory AI"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing data layer...")
from data.sample_data import get_candidates, get_jobs
candidates = get_candidates()
jobs = get_jobs()
print(f"  Candidates loaded: {len(candidates)}")
print(f"  Jobs loaded: {len(jobs)}")

print("\nTesting scoring engine...")
from backend.scoring_engine import (
    rank_candidates, detect_hidden_gems,
    simulate_skill_gap, generate_shap_values,
    predict_future_role
)

ranked = rank_candidates(candidates, jobs[0])
top = ranked[0]
print(f"  Top ranked: {top['name']} — FPS={top['scores']['fps']}")
print(f"  All ranked: {[c['name'] for c in ranked]}")

gems = detect_hidden_gems(candidates)
print(f"  Hidden gems: {len(gems)} — {[g['name'] for g in gems]}")

shap_data = generate_shap_values(top)
print(f"  SHAP explanation: {len(shap_data['explanation'])} chars")
print(f"  Counterfactuals: {len(shap_data['counterfactuals'])}")

sim = simulate_skill_gap(ranked[-1], jobs[0], ['Docker', 'Kubernetes'])
print(f"  Skill gap sim: {sim['current_fps']:.3f} -> {sim['predicted_fps']:.3f} (+{sim['improvement']:.4f})")

traj = predict_future_role(top)
print(f"  Future trajectory: {traj['trajectory']}")

print("\nTesting resume parser...")
from backend.resume_parser import extract_skills, extract_years_experience
sample_text = """
John Doe - Python Developer
Experience: 3 years at Google (2021-2024)
Skills: Python, Docker, Kubernetes, AWS, Terraform, PostgreSQL
Education: B.Tech Computer Science, IIT 2021
"""
skills = extract_skills(sample_text)
yoe = extract_years_experience(sample_text)
print(f"  Skills extracted: {skills}")
print(f"  YoE extracted: {yoe}")

print("\nTesting UI components...")
# Just test that imports work (no Streamlit context needed for these)
import plotly.graph_objects as go
import pandas as pd
import numpy as np
fig = go.Figure(go.Bar(x=[1,2,3], y=[0.8, 0.7, 0.9]))
print(f"  Plotly figure created: {type(fig)}")

print("\n" + "="*50)
print("ALL SYSTEMS OPERATIONAL [OK]")
print("="*50)
print(f"\nFPS Range: {min(c['scores']['fps'] for c in ranked):.3f} - {max(c['scores']['fps'] for c in ranked):.3f}")
print(f"Avg Momentum: {sum(c['scores']['career_momentum'] for c in ranked)/len(ranked):.3f}")
print(f"\nRanking Order:")
for c in ranked:
    gem = " [HIDDEN GEM]" if c.get('hidden_gem') else ""
    print(f"  #{c['rank']} {c['name']:20s} FPS={c['scores']['fps']:.3f}  Momentum={c['scores']['career_momentum']:.3f}{gem}")
