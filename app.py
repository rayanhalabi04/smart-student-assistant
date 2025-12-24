import os
import tempfile
from datetime import date

import streamlit as st
from dotenv import load_dotenv

from rag_utils import (
    build_store_from_pdf,
    answer_question,
    summarize_lecture,
    generate_quiz,
    generate_study_plan,
    set_gemini_api_key,
)

# ------------ Setup ------------

load_dotenv()
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="Smart Assistant for Students",
    page_icon="🎓",
    layout="wide",
)


def configure_gemini() -> None:
    api_key = st.session_state.get("gemini_key", DEFAULT_API_KEY)
    if not api_key:
        st.error("❌ Please enter your Gemini API key in the sidebar.")
        st.stop()
    try:
        set_gemini_api_key(api_key)
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        st.stop()


# ------------ Sidebar ------------

with st.sidebar:
    st.title("⚙️ Settings")

    api_key_input = st.text_input(
        "Gemini API key",
        type="password",
        value=st.session_state.get("gemini_key", DEFAULT_API_KEY),
        help="You can get a key for free from Google AI Studio.",
    )

    if st.button("Save key to session"):
        st.session_state["gemini_key"] = api_key_input
        st.success("Gemini key saved for this session ✅")

    uploaded_file = st.file_uploader(
        "Upload lecture slides (PDF only)",
        type=["pdf"],
        help="One lecture (or a set of slides) at a time.",
    )

    process_btn = st.button("📚 Process Slides")

# ------------ Main layout ------------

st.title("🎓 Smart Assistant for Students")
st.caption("Upload your lecture slides → ask questions, get summaries, quizzes, and a study plan.")

# Make sure Gemini is configured before doing anything
configure_gemini()

# Build vector store when user clicks
if process_btn:
    if not uploaded_file:
        st.warning("Please upload a PDF first.")
    else:
        with st.spinner("Processing PDF and building knowledge base..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            store = build_store_from_pdf(temp_path)
            st.session_state["vector_store"] = store
        st.success("Slides processed successfully! You can now use the tools below. ✅")

store = st.session_state.get("vector_store", None)

if not store:
    st.info("⬆️ Upload a PDF and click **Process Slides** to start.")
    st.stop()

# ------------ Tabs ------------

tab_qa, tab_summary, tab_quiz, tab_plan = st.tabs(
    ["❓ Q&A", "📝 Summary", "🧠 Quiz", "📅 Study Plan"]
)

# --- Q&A tab ---
with tab_qa:
    st.subheader("Ask anything about this lecture")
    question = st.text_area("Your question:", height=80)
    if st.button("Get answer", key="qa_btn"):
        if not question.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Thinking..."):
                answer = answer_question(question, store)
            st.markdown("### Answer")
            st.write(answer)

# --- Summary tab ---
with tab_summary:
    st.subheader("Generate a lecture summary")
    level = st.radio(
        "Summary detail level:",
        ["short", "medium", "long"],
        index=1,
        horizontal=True,
    )
    if st.button("Generate summary", key="summary_btn"):
        with st.spinner("Summarizing..."):
            summary = summarize_lecture(store, detail=level)
        st.markdown("### Summary")
        st.write(summary)

# --- Quiz tab ---
with tab_quiz:
    st.subheader("Generate a practice quiz")
    num_questions = st.slider("Number of questions", min_value=3, max_value=20, value=8)
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)

    if st.button("Generate quiz", key="quiz_btn"):
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(store, num_questions=num_questions, difficulty=difficulty)
        st.markdown("### Quiz")
        st.write(quiz)

# --- Study plan tab ---
with tab_plan:
    st.subheader("Create a personalized study plan")
    exam_date = st.date_input("Exam date", value=date.today())
    hours_per_day = st.slider("Hours available per day", 1, 8, 2)
    level = st.selectbox("Your level with this course", ["beginner", "intermediate", "advanced"], index=1)
    weak_topics = st.text_area(
        "Topics you feel weak in (optional)",
        placeholder="e.g., paging, virtual memory, deadlocks...",
    )

    if st.button("Generate study plan", key="plan_btn"):
        with st.spinner("Designing your plan..."):
            plan = generate_study_plan(
                store=store,
                exam_date=str(exam_date),
                hours_per_day=hours_per_day,
                level=level,
                weak_topics=weak_topics,
            )
        st.markdown("### Study Plan")
        st.write(plan)
