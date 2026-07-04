from datetime import datetime
from io import BytesIO
import html
import os

from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Blood AI Analyst",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --app-bg: #f7f9fc;
    --panel: #ffffff;
    --ink: #111827;
    --muted: #64748b;
    --line: #e6edf5;
    --blue: #2563eb;
    --green: #16a34a;
    --red: #ef4444;
    --amber: #f59e0b;
}

.stApp {
    background: var(--app-bg);
    color: var(--ink);
}

.block-container {
    max-width: 1180px;
    padding: 1.4rem 1.7rem 2rem;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #334155;
}

[data-testid="stSidebar"] .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 4px 18px;
    font-weight: 800;
    color: #111827;
}

.brand-mark {
    width: 24px;
    height: 24px;
    display: inline-grid;
    place-items: center;
    border-radius: 50%;
    background: #fee2e2;
    color: #dc2626;
    font-size: 14px;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 4px;
}

[data-testid="stSidebar"] [role="radio"] {
    border-radius: 8px;
    padding: 10px 12px;
    color: #334155;
}

[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: #eef4ff;
    color: #1d4ed8;
    font-weight: 800;
}

[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none;
}

.page-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
    margin-bottom: 18px;
    padding-top: 2px;
    animation: fadeUp 0.42s ease both;
}

.eyebrow {
    color: #334155;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0;
}

.page-title {
    font-size: 26px;
    font-weight: 850;
    color: #0f172a;
    margin-top: 4px;
}

.status-pill {
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 8px 12px;
    background: #ffffff;
    color: #334155;
    font-size: 13px;
    white-space: nowrap;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 16px;
    animation: fadeUp 0.46s ease both;
}

.metric-card,
.panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
}

.metric-card {
    min-height: 92px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.metric-card:hover,
.panel:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
}

.metric-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-weight: 800;
}

.metric-icon.green { background: #dcfce7; color: #16a34a; }
.metric-icon.blue { background: #dbeafe; color: #2563eb; }
.metric-icon.red { background: #fee2e2; color: #ef4444; }
.metric-icon.slate { background: #f1f5f9; color: #475569; }

.metric-label {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
}

.metric-value {
    color: #111827;
    font-size: 22px;
    font-weight: 850;
    margin-top: 2px;
}

.metric-sub {
    color: #64748b;
    font-size: 12px;
    margin-top: 2px;
}

.panel {
    padding: 16px;
    margin-bottom: 16px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    animation: fadeUp 0.48s ease both;
}

.panel-title {
    color: #0f172a;
    font-weight: 800;
    font-size: 15px;
    margin-bottom: 12px;
}

.scroll-box {
    min-height: 145px;
    max-height: 280px;
    overflow-y: auto;
    padding: 13px;
    border-radius: 8px;
    background: #fbfdff;
    border: 1px solid #edf2f7;
    color: #334155;
    line-height: 1.62;
    font-size: 14px;
    white-space: pre-wrap;
}

.upload-note {
    color: #64748b;
    font-size: 13px;
    line-height: 1.55;
    padding-top: 4px;
}

.disclaimer {
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
    color: #92400e;
    padding: 12px 14px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.55;
}

.mini-list {
    display: grid;
    gap: 9px;
}

.mini-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eef2f7;
    color: #334155;
    font-size: 13px;
}

.mini-row:last-child {
    border-bottom: 0;
    padding-bottom: 0;
}

.tag {
    font-weight: 800;
}

.tag.green { color: #16a34a; }
.tag.blue { color: #2563eb; }
.tag.red { color: #ef4444; }

.center-message {
    min-height: 380px;
    display: grid;
    place-items: center;
}

.center-message .panel {
    max-width: 520px;
    text-align: center;
}

.analysis-overlay {
    position: fixed;
    inset: 0;
    z-index: 999999;
    display: grid;
    place-items: center;
    background: rgba(247, 249, 252, 0.68);
    backdrop-filter: blur(9px);
    -webkit-backdrop-filter: blur(9px);
}

.analysis-loader {
    min-width: 360px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(219, 229, 239, 0.95);
    box-shadow: 0 24px 70px rgba(15, 23, 42, 0.18);
    padding: 28px 32px;
    text-align: center;
    color: #0f172a;
    animation: loaderEnter 0.32s ease both;
}

.loader-pulse {
    width: 54px;
    height: 54px;
    margin: 0 auto 16px;
    border-radius: 50%;
    background: #fee2e2;
    position: relative;
    display: grid;
    place-items: center;
    color: #dc2626;
    font-weight: 900;
}

.loader-pulse::before,
.loader-pulse::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2px solid rgba(220, 38, 38, 0.34);
    animation: ripple 1.4s ease-out infinite;
}

.loader-pulse::after {
    animation-delay: 0.45s;
}

.loader-title {
    font-size: 18px;
    font-weight: 850;
    margin-bottom: 6px;
}

.loader-text {
    color: #475569;
    font-size: 14px;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes loaderEnter {
    from { opacity: 0; transform: translateY(12px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes ripple {
    from { opacity: 0.65; transform: scale(1); }
    to { opacity: 0; transform: scale(1.9); }
}

.stTextArea textarea,
[data-testid="stFileUploader"] section {
    background-color: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #dbe5ef !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] [data-testid="stWidgetLabel"],
[data-testid="stFileUploader"] [data-testid="stWidgetLabel"] *,
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] *,
.stTextArea label {
    color: #334155 !important;
}

[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"],
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] * {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

.stButton button,
.stDownloadButton button {
    min-height: 46px;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 800;
    background: #2563eb !important;
    border: 1px solid #2563eb !important;
    color: white !important;
}

.stDownloadButton button {
    background: #16a34a !important;
    border-color: #16a34a !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.18);
    transform: translateY(-1px);
}

@media (max-width: 900px) {
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .page-top {
        align-items: flex-start;
        flex-direction: column;
    }

    .analysis-loader {
        min-width: auto;
        width: calc(100vw - 36px);
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def extract_uploaded_text(uploaded_file):
    if not uploaded_file:
        return "", ""

    file_name = uploaded_file.name
    suffix = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    data = uploaded_file.getvalue()

    if suffix == "pdf":
        if PdfReader is None:
            return "", "PDF upload needs the pypdf package. Please install pypdf or paste the report text."
        try:
            reader = PdfReader(BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(page.strip() for page in pages if page.strip()), ""
        except Exception as exc:
            return "", f"Could not read the PDF text: {exc}"

    if suffix in {"txt", "csv"}:
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return data.decode(encoding), ""
            except UnicodeDecodeError:
                continue
        return "", "Could not decode the uploaded text file."

    return "", "This upload type cannot be read as text yet. Please upload PDF/TXT/CSV or paste the report content."


def extract_section(text, start, end=None):
    if start not in text:
        return ""
    part = text.split(start, 1)[1]
    if end and end in part:
        part = part.split(end, 1)[0]
    return part.strip()


def render_panel(title, content, min_height=145):
    safe_content = html.escape(content or "No data available.")
    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">{title}</div>
            <div class="scroll-box" style="min-height: {min_height}px;">{safe_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title, message):
    st.markdown(
        f"""
        <div class="center-message">
            <div class="panel">
                <div class="panel-title">{html.escape(title)}</div>
                <div class="upload-note">{html.escape(message)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_overlay():
    st.markdown(
        """
        <div class="analysis-overlay">
            <div class="analysis-loader">
                <div class="loader-pulse">+</div>
                <div class="loader-title">Analyzing your blood work report...</div>
                <div class="loader-text">Reviewing values and preparing your summary. This will stop automatically if the AI service does not respond.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_download_text(analysis):
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
    return f"""Blood AI Analyst - Analysis Summary
Generated: {timestamp}

HEALTH SUMMARY
{analysis.get("health_summary", "").strip()}

ABNORMAL PARAMETERS
{analysis.get("abnormal_values", "").strip()}

INDIAN DIET PLAN
{analysis.get("diet_plan", "").strip()}

LIFESTYLE AND FOLLOW-UP
{analysis.get("lifestyle", "").strip()}

Note: This AI-generated summary is for informational purposes only. Please consult a qualified doctor before making medical decisions.
"""


def analyze_report(llm, report_text):
    prompt = f"""
You are a responsible medical report assistant.

Analyze the following blood report and provide output in exactly these sections:

SECTION 1 - HEALTH SUMMARY
Give a simple 4-5 line summary in non-technical language.

SECTION 2 - ABNORMAL PARAMETERS
List abnormal values only.
Format:
- Test Name: Value | Status: HIGH/LOW | Reference Range | Simple Meaning

If no abnormal values are found, write:
No major abnormal values detected based on the provided reference ranges.

SECTION 3 - INDIAN DIET PLAN
Give practical Indian food suggestions.
Include:
Foods to eat more:
Foods to avoid/reduce:

Use common Indian foods like dal, roti, sabzi, rice, curd, fruits, nuts, sprouts, vegetables, etc.

SECTION 4 - LIFESTYLE AND FOLLOW-UP
Give concise lifestyle advice.
Also mention when to consult a doctor.

Important:
- Do not diagnose disease.
- Do not prescribe medicine.
- Keep language simple.
- Always recommend consulting a qualified doctor.

Blood Report:
{report_text}
"""
    response = llm.invoke(prompt)
    full_response = response.content

    health_summary = extract_section(
        full_response,
        "SECTION 1 - HEALTH SUMMARY",
        "SECTION 2 - ABNORMAL PARAMETERS",
    )
    abnormal_values = extract_section(
        full_response,
        "SECTION 2 - ABNORMAL PARAMETERS",
        "SECTION 3 - INDIAN DIET PLAN",
    )
    diet_plan = extract_section(
        full_response,
        "SECTION 3 - INDIAN DIET PLAN",
        "SECTION 4 - LIFESTYLE AND FOLLOW-UP",
    )
    lifestyle = extract_section(full_response, "SECTION 4 - LIFESTYLE AND FOLLOW-UP")

    if not any([health_summary, abnormal_values, diet_plan, lifestyle]):
        health_summary = full_response

    return {
        "health_summary": health_summary,
        "abnormal_values": abnormal_values,
        "diet_plan": diet_plan,
        "lifestyle": lifestyle,
        "raw": full_response,
    }


def render_page_header(active_page, has_analysis):
    page_titles = {
        "Dashboard": ("Health Overview", "Blood report analysis dashboard"),
        "Blood Report": ("Report Upload", "Upload or paste blood report"),
        "Analysis": ("Analysis", "Generated blood report insights"),
        "Health Summary": ("Health Summary", "Simple patient-friendly overview"),
        "Diet Plan": ("Diet Plan", "Indian diet and lifestyle guidance"),
        "Download Report": ("Download", "Export your analysis summary"),
    }
    eyebrow, title = page_titles.get(active_page, page_titles["Dashboard"])
    pill = "Summary generated" if has_analysis else "Upload, analyze, and download your summary"
    st.markdown(
        f"""
        <div class="page-top">
            <div>
                <div class="eyebrow">{eyebrow}</div>
                <div class="page-title">{title}</div>
            </div>
            <div class="status-pill">{pill}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(analysis, source_loaded):
    has_analysis = analysis is not None
    abnormal_text = analysis.get("abnormal_values", "") if has_analysis else ""
    high_count = abnormal_text.upper().count("HIGH") if has_analysis else 0
    low_count = abnormal_text.upper().count("LOW") if has_analysis else 0
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-icon green">✓</div>
                <div>
                    <div class="metric-label">Overall Status</div>
                    <div class="metric-value">{'Ready' if has_analysis else 'Pending'}</div>
                    <div class="metric-sub">{'Summary generated' if has_analysis else 'Awaiting analysis'}</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon blue">#</div>
                <div>
                    <div class="metric-label">Report Source</div>
                    <div class="metric-value">{'Loaded' if source_loaded else 'Paste'}</div>
                    <div class="metric-sub">PDF, TXT, CSV or manual text</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon red">↑</div>
                <div>
                    <div class="metric-label">High Values</div>
                    <div class="metric-value">{high_count}</div>
                    <div class="metric-sub">Detected by AI summary</div>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-icon slate">↓</div>
                <div>
                    <div class="metric-label">Low Values</div>
                    <div class="metric-value">{low_count}</div>
                    <div class="metric-sub">Detected by AI summary</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_report_input():
    st.markdown('<div class="panel"><div class="panel-title">Blood Report Input</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload blood report",
        type=["pdf", "txt", "csv"],
        help="Upload a text-based PDF, TXT, or CSV blood report.",
    )

    if uploaded_file:
        uploaded_text, upload_warning = extract_uploaded_text(uploaded_file)
        st.session_state.uploaded_text = uploaded_text
        if upload_warning:
            st.warning(upload_warning)
        elif uploaded_text:
            st.success(f"Loaded text from {uploaded_file.name}")

    pasted_report = st.text_area(
        "Paste blood report text",
        value=st.session_state.uploaded_text,
        height=270,
        placeholder="Paste your blood work report here if you do not upload a file...",
    )

    st.markdown(
        """
        <div class="upload-note">
            Uploaded report text is placed in the editor so you can review or adjust it before analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    analyze_clicked = st.button("Analyze Blood Report", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="disclaimer">
            This AI report is for informational purposes only. Please consult a qualified doctor before taking any medical decision.
        </div>
        """,
        unsafe_allow_html=True,
    )
    return analyze_clicked, pasted_report


def render_preview_cards():
    top_right_a, top_right_b = st.columns([1, 1], gap="medium")
    with top_right_a:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Key Parameters</div>
                <div class="mini-list">
                    <div class="mini-row"><span>Hemoglobin</span><span class="tag green">Review</span></div>
                    <div class="mini-row"><span>WBC Count</span><span class="tag green">Review</span></div>
                    <div class="mini-row"><span>Platelets</span><span class="tag blue">Review</span></div>
                    <div class="mini-row"><span>Cholesterol</span><span class="tag red">Review</span></div>
                    <div class="mini-row"><span>Vitamin D</span><span class="tag blue">Review</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right_b:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title">Diet Preview</div>
                <div class="mini-list">
                    <div class="mini-row"><span>Include</span><span class="tag green">Dal, curd, fruits</span></div>
                    <div class="mini-row"><span>Avoid</span><span class="tag red">Fried, sugary foods</span></div>
                    <div class="mini-row"><span>Focus</span><span class="tag blue">Hydration, fiber</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_analysis_panels(analysis):
    has_analysis = analysis is not None
    render_panel("Health Summary", analysis.get("health_summary") if has_analysis else "Your health summary will appear here.")
    render_panel("Abnormal Parameters", analysis.get("abnormal_values") if has_analysis else "High and low values will appear here.")
    render_panel("Suggested Indian Diet Plan", analysis.get("diet_plan") if has_analysis else "Diet suggestions will appear here.")
    render_panel("Lifestyle and Follow-up Advice", analysis.get("lifestyle") if has_analysis else "Lifestyle recommendations will appear here.")


def render_download(analysis):
    if not analysis:
        render_empty_state("No report generated yet", "Analyze a blood report first, then this page will show the download option.")
        return

    download_text = build_download_text(analysis)
    st.download_button(
        "Download Analysis Summary",
        data=download_text,
        file_name=f"blood_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
    )
    render_panel("Download Preview", download_text, min_height=260)


if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = st.session_state.active_page
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = ""
if "pending_nav" in st.session_state:
    st.session_state.active_page = st.session_state.pending_nav
    st.session_state.nav_choice = st.session_state.pending_nav
    del st.session_state.pending_nav

nav_options = ["Dashboard", "Blood Report", "Analysis", "Health Summary", "Diet Plan", "Download Report"]
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span class="brand-mark">+</span>
            <span>Blood AI Analyst</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    active_page = st.radio(
        "Navigation",
        nav_options,
        key="nav_choice",
        label_visibility="collapsed",
    )
    st.session_state.active_page = active_page

if not api_key:
    st.error("GOOGLE_API_KEY or GEMINI_API_KEY not found in .env file.")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0,
    request_timeout=45,
    retries=1,
)

analysis = st.session_state.analysis
has_analysis = analysis is not None

if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error)

render_page_header(active_page, has_analysis)
render_metrics(analysis, bool(st.session_state.uploaded_text))

analyze_clicked = False
pasted_report = ""

if active_page == "Dashboard":
    left_col, right_col = st.columns([0.95, 1.35], gap="large")
    with left_col:
        analyze_clicked, pasted_report = render_report_input()
    with right_col:
        render_preview_cards()
        render_analysis_panels(analysis)
elif active_page == "Blood Report":
    input_col, helper_col = st.columns([1.05, 0.95], gap="large")
    with input_col:
        analyze_clicked, pasted_report = render_report_input()
    with helper_col:
        render_preview_cards()
elif active_page == "Analysis":
    if has_analysis:
        render_analysis_panels(analysis)
    else:
        render_empty_state("Analysis is waiting", "Upload or paste a blood report, then click Analyze Blood Report.")
elif active_page == "Health Summary":
    if has_analysis:
        render_panel("Health Summary", analysis.get("health_summary"), min_height=260)
        render_panel("Abnormal Parameters", analysis.get("abnormal_values"), min_height=220)
    else:
        render_empty_state("No health summary yet", "Generate an analysis first, then this menu will show the summary.")
elif active_page == "Diet Plan":
    if has_analysis:
        render_panel("Suggested Indian Diet Plan", analysis.get("diet_plan"), min_height=260)
        render_panel("Lifestyle and Follow-up Advice", analysis.get("lifestyle"), min_height=220)
    else:
        render_empty_state("No diet plan yet", "Generate an analysis first, then this menu will show diet and lifestyle guidance.")
elif active_page == "Download Report":
    render_download(analysis)

if analyze_clicked:
    report_text = pasted_report.strip()
    if not report_text:
        st.warning("Please upload a readable report or paste blood work text before analyzing.")
    else:
        render_analysis_overlay()
        st.session_state.analysis_error = ""
        try:
            st.session_state.analysis = analyze_report(llm, report_text)
            st.session_state.pending_nav = "Analysis"
        except Exception as exc:
            st.session_state.analysis_error = (
                "Analysis could not finish. Please check your internet/API key and try again. "
                f"Details: {exc}"
            )
        st.rerun()
