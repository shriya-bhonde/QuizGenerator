import streamlit as st
from PyPDF2 import PdfReader
import docx
import json
from backend import generate_mcq_questions, generate_flashcard_questions

# ================== PAGE SETUP ==================
st.set_page_config(page_title="Study Buddy - Quiz Generator", page_icon="📘", layout="wide")
st.title("📘 Study Buddy - Quiz Generator")

# ================== CSS STYLING ==================
st.markdown("""
<style>
div.stButton > button {
    background-color: #4CAF50;  /* Green */
    color: white;
    padding: 10px 25px;
    font-size: 16px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

/* Hover effect */
div.stButton > button:hover {
    background-color: #45a049;
    color: #fff;
    transform: scale(1.05);
}   

/* Bold the label text above sliders */
div[data-baseweb="slider"] > div:first-child {
    font-weight: 1000;
    font-size: 25px;
    margin-bottom: 2px;
}

/* Remove extra space above sliders with empty labels */
div[data-testid="stSlider"] > div:first-child {
    margin-top: -15px;
}
            
/* Make the slider track thicker */
div[data-baseweb="slider"] [role="slider"] {
    height: 14px !important;
}

/* Make the thumb (circle) bigger */
div[data-baseweb="slider"] [role="slider"]::before {
    width: 20px !important;
    height: 20px !important;
}         

/* Tab spacing & font */
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 22px;
    padding-left: 20px;
    padding-right: 20px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 30px;
}
.stTabs [data-baseweb="tab-list"] button {
    min-width: 500px;
    width: auto;
}

/* MCQ card styling */
.mcq-card {
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #f0f8ff;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}

/* Flip-card container */
.flip-card {
  background-color: transparent;
  width: 300px;
  height: 150px;
  perspective: 1000px;
  margin-bottom: 20px;
}
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.8s;
  transform-style: preserve-3d;
  cursor: pointer;
}
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 15px;
  font-weight: bold;
  padding: 10px;
  color: white;
}
.flip-card-front {
  background-color: #4CAF50;
}
.flip-card-back {
  background-color: #FFC107;
  color: black;
  transform: rotateY(180deg);
}
</style>
""", unsafe_allow_html=True)

# ================== FUNCTIONS ==================
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file.type == "text/plain":
        return file.read().decode("utf-8")

    else:
        st.error("Unsupported file type!")
        return ""

# ================== LAYOUT ==================
col1, col2 = st.columns([1, 2])  # 1:2 ratio

# -------- LEFT COLUMN --------
with col1:
    st.header("📂 Upload File")
    uploaded_file = st.file_uploader(
        "Upload your notes/textbook",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)  # Spacer
    st.markdown("<br>", unsafe_allow_html=True)  # Spacer

    # st.markdown("**How many MCQs do you want to generate ?**", unsafe_allow_html=True)
    st.markdown("<p style='font-size:20px; font-weight:700;'>How many MCQs do you want to generate ?</p>", unsafe_allow_html=True)
    num_mcq = st.slider("", 1, 10, 5)

    st.markdown("<p style='font-size:20px; font-weight:700;'>How many True/False questions would you like to generate ?</p>", unsafe_allow_html=True)
    num_tf = st.slider(" ", 1, 10, 5)

    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        text = extract_text(uploaded_file)
        st.session_state["uploaded_text"] = text

# -------- RIGHT COLUMN --------
with col2:
    st.header("📝 Quiz Sections")

    if "uploaded_text" not in st.session_state:
        st.info("👈 Upload a file to generate quiz questions.")
    else:
        tab1, tab2 = st.tabs(["📘 Multiple Choice Questions", "🔀 True/False"])

        with tab1:
            st.subheader("Multiple Choice Questions")

            if st.button("Generate MCQs"):
                with st.spinner("Generating questions..."):
                    quiz = generate_mcq_questions(st.session_state["uploaded_text"], num_questions=num_mcq)
                    st.session_state.quiz_mcq = quiz
                    st.session_state.responses_mcq = {}

            if "quiz_mcq" in st.session_state:
                quiz = st.session_state.quiz_mcq

                for i, q in enumerate(quiz):
                    with st.container():
                        st.markdown(f'<div class="mcq-card"><b>Q{i+1}:</b> {q["question"]}</div>', unsafe_allow_html=True)
                        choice = st.radio(
                            f"Select answer for Q{i+1}:",
                            q[f"options"],
                            index=None,
                            key=f"mcq{i}"
                        )
                        st.session_state.responses_mcq[i+1] = choice

                if st.button("Submit MCQs"):
                    score = 0
                    for i, q in enumerate(quiz):
                        selected = st.session_state.responses_mcq[i+1]

                        if selected:  # Ensure something was selected
                            # Extract just the option letter (e.g., "A" from "A. text")
                            selected_letter = selected.split(".")[0].strip()
                            correct_answer = q["answer"].strip()

                            if selected_letter == correct_answer:
                                score += 1
                                st.success(f"Q{i+1}: ✅ Correct")
                            else:
                                st.error(f"Q{i+1}: ❌ Wrong (Correct: {correct_answer})")
                        else:
                            st.warning(f"Q{i+1}: ⚠️ No answer selected")

                    st.write(f"### Final Score: {score} / {len(quiz)}")
                    high_score = (len(quiz) - 1)
                    if score >= high_score:
                        st.balloons()
                        st.success("🎉 Awesome! You scored high!")

        # ===== TAB 2 - True/False =====
        with tab2:
            st.subheader("True or False (Flashcards)")
            
            if st.button("Generate True/False Questions"):
                with st.spinner("Generating questions..."):
                    quiz = generate_flashcard_questions(st.session_state["uploaded_text"], num_questions=num_tf)
                    st.session_state.quiz_tf = quiz
                    st.session_state.responses_tf = {}

            if "quiz_tf" in st.session_state:
                quiz = st.session_state.quiz_tf

                for i, q in enumerate(quiz):
                    with st.expander(f"Q{i+1}: {q['question']}"):
                        st.info(f"Answer: {q['answer']}")
                        st.info(f"Justification: {q.get('justification', 'N/A')}")