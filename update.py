import os

files = [
    'pages/01_Dashboard.py',
    'pages/02_Ranking.py',
    'pages/03_Profile.py',
    'pages/04_HiddenGems.py',
    'pages/05_SkillGap.py',
    'pages/06_Analytics.py',
    'pages/07_Copilot.py',
    'pages/08_Jobs.py'
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        'if "custom_candidates" not in st.session_state:\n    from data.database import load_custom_candidates\n    st.session_state.custom_candidates = load_custom_candidates()',
        'if "custom_candidates" not in st.session_state:\n    st.session_state.custom_candidates = []'
    )
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Done!')
