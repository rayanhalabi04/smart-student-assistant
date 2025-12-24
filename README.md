🧠 Smart Assistant for Students

A personalized AI study assistant that helps students understand their lecture slides faster.

Upload your slides → ask questions → get summaries → generate quizzes → build study plans.

Learning shouldn’t be painful… so I built the tool I always wished I had during university 🎓.

🚀 Live Demo
🔗 Try the app here:

https://smart-student-assistant-9fwarfjgszgq3hhu8mntqo.streamlit.app
(Requires a free Gemini API Key — instructions below)

📌 Why I built this

During my degree, I struggled with long PDF lectures, confusing explanations, and last-minute exams.

AI tools were helpful… but they hallucinated or answered with information not inside my slides.

So I built a personalized RAG-based study assistant that:

✔️ Reads only your PDF

✔️ Extracts the correct content

✔️ Never hallucinates

✔️ Generates helpful summaries, quizzes, and study plans
✔️ Works like a personal “smart notebook”

✨ Features
1. 🧩 RAG-Powered Q&A
Ask questions about your PDF and get answers strictly based on your slides (no outside assumptions).
2. 📝 Auto-Summaries
Generate a short, medium, or long summary of your lecture.
3. 🧠 Auto-Generated Quiz
Create MCQs to test yourself on any lecture.
4. 📅 Personalized Study Plan
Choose your exam date, hours per day, and difficulty → get a custom plan.
5. 📄 Upload Multiple PDF Slides
Upload large lecture files (200MB limit per file).

🏗️ Tech Stack
Component	Used For
Python	Backend logic, PDF parsing, RAG pipeline
Streamlit	UI + Web app
FAISS / Chroma-like search	Vector similarity search
Google Gemini API	Embeddings + generation
PyPDF / pypdf	PDF text extraction
RAG (Retrieval Augmented Generation)	Ensures answers come only from user PDFs

🔑 How Users Can Use the App (Live Version)

Open the deployed app ( https://smart-student-assistant-9fwarfjgszgq3hhu8mntqo.streamlit.app ).

Paste your Gemini API Key into the sidebar.

Get a free key here: https://ai.google.dev

Upload your lecture PDF.

Click Process Slides.

Use:

❓ Q&A

📝 Summary

🧠 Quiz

📅 Study Plan

💬 Contact


LinkedIn: www.linkedin.com/in/rayan-halabi-aa0765251

GitHub: https://github.com/rayanhalabi04
