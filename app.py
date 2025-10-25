import streamlit as st
from modules import resume_parser, jd_matcher, keyword_extractor, score_calculator

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

st.markdown("""
<h1 style='text-align: center;'>🤖 AI Resume Analyzer</h1>
<p style='text-align: center;'>An ATS Checker using NLP to analyze keyword optimization in resumes</p>
<hr>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("🧭 Select Option", ["Home", "Analyze Resume"])

# ========================= HOME =========================
if menu == "Home":
    st.markdown("""
    ### Welcome to **AI Resume Analyzer**
    Optimize your resume for ATS systems and improve your chances of getting shortlisted.

    **Features:**
    - 📄 Extract text from PDF/DOCX resumes
    - 🧠 Compare resume with job description using NLP
    - 🔍 Keyword extraction & match percentage
    - 📊 ATS score with improvement suggestions
    """)

# ========================= ANALYZE =========================
elif menu == "Analyze Resume":
    st.subheader("📄 Upload Your Resume")
    resume_file = st.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])

    st.subheader("📝 Paste Job Description")
    jd_text = st.text_area("Paste job description here", height=200)

    if resume_file and jd_text:
        if st.button("Analyze"):
            with st.spinner("Analyzing resume... please wait..."):
                resume_text = resume_parser.extract_text(resume_file)
                jd_keywords = keyword_extractor.extract_keywords(jd_text)
                resume_keywords = keyword_extractor.extract_keywords(resume_text)
                similarity_score = score_calculator.calculate_similarity(resume_text, jd_text)
                matched_keywords, missing_keywords = jd_matcher.match_keywords(jd_keywords, resume_keywords)

            st.success("✅ Analysis Complete!")

            st.markdown(f"### 🧮 ATS Score: **{similarity_score:.2f}%**")
            st.progress(int(similarity_score))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✅ Matched Keywords")
                st.write(", ".join(matched_keywords))
            with col2:
                st.markdown("### ❌ Missing Keywords")
                st.write(", ".join(missing_keywords))

            st.markdown("### 💡 Suggestions")
            st.write("Add more keywords related to the job description to improve your ATS score.")
