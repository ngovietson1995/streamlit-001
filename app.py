from __future__ import annotations

import hashlib
import html
import random
import re
import unicodedata
from difflib import SequenceMatcher
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


APP_TITLE = "Kiểm tra thông tư"
APP_VERSION = "2026.07.26-v3"
DEFAULT_DATA_FILE = Path(__file__).with_name("kho_cau_hoi.xlsx")


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
:root {
    --app-blue: #2f80c9;
    --app-blue-dark: #2467a4;
    --border: #d5dbe3;
    --text: #111827;
    --muted: #6b7280;
    --surface: #ffffff;
    --soft: #f6f8fb;
}

.stApp {
    background: linear-gradient(135deg, #f9fcff 0%, #eef5fa 100%);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.app-title {
    text-align: center;
    color: #111827;
    font-size: 2rem;
    font-weight: 650;
    margin: 0.2rem 0 1.3rem 0;
}

.question-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.09);
    margin-bottom: 0.85rem;
    font-size: 1.18rem;
    line-height: 1.55;
    color: #111111;
}

.question-label {
    color: #4b5563;
    margin-right: 0.35rem;
}

.question-text {
    color: #000000;
    font-weight: 650;
}

.panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: 0 2px 7px rgba(15, 23, 42, 0.06);
    overflow: hidden;
}

.panel-title {
    background: #f1f4f8;
    border-bottom: 1px solid var(--border);
    padding: 0.7rem 0.95rem;
    color: #111111;
    font-weight: 700;
}

.answer-body {
    min-height: 360px;
    max-height: 520px;
    overflow-y: auto;
    padding: 0.9rem 1rem;
    color: #000000;
    background: #ffffff;
    font-size: 1rem;
    line-height: 1.75;
    white-space: pre-wrap;
}

.answer-hidden {
    min-height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    color: var(--muted);
    background: repeating-linear-gradient(
        45deg,
        #fafbfc,
        #fafbfc 10px,
        #f5f7fa 10px,
        #f5f7fa 20px
    );
    text-align: center;
}

.answer-hidden .lock {
    font-size: 2rem;
}

.input-title {
    background: #f1f4f8;
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    padding: 0.7rem 0.95rem;
    color: #111111;
    font-weight: 700;
}

.middle-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 275px;
    color: #607082;
    font-size: 1.75rem;
    user-select: none;
}

.hint-card {
    margin-top: 0.9rem;
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 0.95rem;
    box-shadow: 0 2px 7px rgba(15, 23, 42, 0.05);
}

.hint-title {
    color: #111111;
    font-weight: 700;
    margin-bottom: 0.55rem;
}

.hint-flow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.42rem;
}

.hint-chip {
    display: inline-block;
    background: #f1f3f6;
    border: 1px solid #d7dce3;
    border-radius: 7px;
    padding: 0.35rem 0.62rem;
    color: #111111;
    line-height: 1.25;
}

.hint-arrow {
    color: #7c8794;
    font-weight: 700;
}

.progress-text {
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
    margin: 0.15rem 0 0.75rem 0;
}

div[data-testid="stTextArea"] textarea {
    min-height: 360px !important;
    color: #000000 !important;
    background: #ffffff !important;
    border: 1px solid #7ab0d9 !important;
    border-radius: 0 0 10px 10px !important;
    box-shadow: 0 0 0 2px rgba(47, 128, 201, 0.09);
    line-height: 1.65;
    font-size: 1rem;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--app-blue) !important;
    box-shadow: 0 0 0 3px rgba(47, 128, 201, 0.16) !important;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 650;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(15, 23, 42, 0.12);
}

.stButton > button[kind="primary"] {
    background: var(--app-blue);
    border-color: var(--app-blue);
}

.stButton > button[kind="primary"]:hover {
    background: var(--app-blue-dark);
    border-color: var(--app-blue-dark);
}

[data-testid="stAlert"] {
    border-radius: 9px;
}

@media (max-width: 760px) {
    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
        padding-top: 1rem;
    }

    .app-title {
        font-size: 1.55rem;
    }

    .question-card {
        font-size: 1.03rem;
    }

    .middle-arrow {
        min-height: auto;
        padding: 0.25rem 0;
        transform: rotate(90deg);
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def simplify_column_name(value: object) -> str:
    text = unicodedata.normalize("NFD", str(value).strip().lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", text)


def normalize_answer(value: object) -> str:
    text = unicodedata.normalize("NFC", str(value or "")).lower()
    text = re.sub(r"(^|\n)\s*\d+[\.\)\-:]\s*", r"\1", text)
    text = re.sub(r"[^0-9a-zA-ZÀ-ỹđĐ\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def automatic_hints(answer: str) -> list[str]:
    lines = [
        re.sub(r"^\s*\d+[\.\)\-:]\s*", "", line).strip()
        for line in str(answer).splitlines()
        if line.strip()
    ]

    hints: list[str] = []
    for line in lines[:6]:
        words = line.split()
        if not words:
            continue
        visible = " ".join(words[: min(3, len(words))])
        if len(words) > 3:
            visible += " …"
        hints.append(visible)

    if hints:
        return hints

    words = str(answer).split()
    return [" ".join(words[:3]) + (" …" if len(words) > 3 else "")] if words else []


@st.cache_data(show_spinner=False)
def load_question_bank(file_bytes: bytes) -> pd.DataFrame:
    """Đọc kho câu hỏi từ mọi sheet và tự tìm dòng tiêu đề.

    Hàm chấp nhận các trường hợp thường gặp:
    - Có vài dòng tiêu đề/ghi chú trống phía trên bảng dữ liệu.
    - Bảng câu hỏi nằm ở sheet không phải sheet đầu tiên.
    - Tên cột có khác biệt nhẹ như: Câu hỏi, Nội dung câu hỏi,
      Đáp án, Đáp án mẫu, Câu trả lời, Gợi ý, Từ khóa...
    """

    column_aliases = {
        "question": {
            "cauhoi",
            "noidungcauhoi",
            "cauhoituluan",
            "debaicauhoi",
            "question",
            "questions",
        },
        "answer": {
            "dapan",
            "dapanmau",
            "noidungdapan",
            "dapandung",
            "cautraloi",
            "noidungtraloi",
            "traloi",
            "answer",
            "answers",
        },
        "hint": {
            "goiy",
            "tukhoa",
            "tukhoagoiy",
            "goiydapan",
            "hint",
            "hints",
            "keyword",
            "keywords",
        },
    }

    def find_matching_column(
        simplified_headers: list[str],
        aliases: set[str],
    ) -> int | None:
        # Ưu tiên khớp chính xác.
        for index, header in enumerate(simplified_headers):
            if header in aliases:
                return index

        # Sau đó cho phép tên cột dài hơn, ví dụ "Nội dung đáp án mẫu".
        for index, header in enumerate(simplified_headers):
            if not header:
                continue
            if any(alias in header or header in alias for alias in aliases):
                return index
        return None

    try:
        excel_file = pd.ExcelFile(BytesIO(file_bytes))
    except Exception as error:
        raise ValueError(
            "Tệp không phải file Excel .xlsx hợp lệ hoặc file đang bị hỏng."
        ) from error

    inspected_sheets: list[str] = []
    diagnostic_headers: list[str] = []

    for sheet_name in excel_file.sheet_names:
        try:
            raw = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None,
                dtype=str,
            )
        except Exception:
            continue

        raw = raw.dropna(axis=0, how="all").dropna(axis=1, how="all")
        if raw.empty:
            continue

        inspected_sheets.append(str(sheet_name))
        scan_limit = min(100, len(raw))

        # Ghi lại một số dòng đầu để thông báo lỗi dễ chẩn đoán hơn.
        for diagnostic_position in range(min(8, len(raw))):
            diagnostic_values = [
                "" if pd.isna(value) else str(value).strip()
                for value in raw.iloc[diagnostic_position].tolist()
            ]
            non_empty = [value for value in diagnostic_values if value]
            if non_empty:
                diagnostic_headers.append(
                    f"Sheet '{sheet_name}', dòng {diagnostic_position + 1}: "
                    + " | ".join(non_empty[:10])
                )

        for row_position in range(scan_limit):
            header_values = [
                "" if pd.isna(value) else str(value).strip()
                for value in raw.iloc[row_position].tolist()
            ]
            simplified_headers = [
                simplify_column_name(value) for value in header_values
            ]

            question_index = find_matching_column(
                simplified_headers,
                column_aliases["question"],
            )
            answer_index = find_matching_column(
                simplified_headers,
                column_aliases["answer"],
            )

            if question_index is None or answer_index is None:
                continue

            hint_index = find_matching_column(
                simplified_headers,
                column_aliases["hint"],
            )

            data_rows = raw.iloc[row_position + 1 :].copy()

            result = pd.DataFrame(
                {
                    "question": data_rows.iloc[:, question_index],
                    "answer": data_rows.iloc[:, answer_index],
                    "hint": (
                        data_rows.iloc[:, hint_index]
                        if hint_index is not None
                        else ""
                    ),
                }
            )

            result = result.fillna("")
            result["question"] = result["question"].astype(str).str.strip()
            result["answer"] = result["answer"].astype(str).str.strip()
            result["hint"] = result["hint"].astype(str).str.strip()
            result = result[
                (result["question"] != "") & (result["answer"] != "")
            ]
            result = result.reset_index(drop=True)

            if not result.empty:
                return result

    sheets_text = ", ".join(inspected_sheets) if inspected_sheets else "không xác định"
    diagnostic_text = " || ".join(diagnostic_headers[:12])
    if not diagnostic_text:
        diagnostic_text = "Không đọc được dòng dữ liệu nào trong các sheet."
    raise ValueError(
        "Không tìm thấy bảng dữ liệu hợp lệ. Ứng dụng đã kiểm tra các sheet: "
        f"{sheets_text}. Cần có một dòng tiêu đề chứa cột 'Câu hỏi' và "
        "'Đáp án' hoặc 'Đáp án mẫu'. Các dòng đầu đã đọc được: "
        f"{diagnostic_text}"
    )


def reset_learning_session(question_count: int, signature: str) -> None:
    order = list(range(question_count))
    random.shuffle(order)

    st.session_state.bank_signature = signature
    st.session_state.question_count = question_count
    st.session_state.question_order = order
    st.session_state.question_position = 0
    st.session_state.cycle_number = 1
    st.session_state.show_answer = False
    st.session_state.user_answer = ""
    st.session_state.feedback = None


def next_question() -> None:
    count = st.session_state.question_count
    position = st.session_state.question_position + 1

    if position >= count:
        new_order = list(range(count))
        random.shuffle(new_order)
        st.session_state.question_order = new_order
        st.session_state.question_position = 0
        st.session_state.cycle_number += 1
    else:
        st.session_state.question_position = position

    st.session_state.show_answer = False
    st.session_state.user_answer = ""
    st.session_state.feedback = None


def toggle_answer() -> None:
    st.session_state.show_answer = not st.session_state.show_answer


def clear_user_answer() -> None:
    st.session_state.user_answer = ""
    st.session_state.feedback = None


def check_user_answer(sample_answer: str, user_answer: str) -> dict[str, object]:
    normalized_sample = normalize_answer(sample_answer)
    normalized_user = normalize_answer(user_answer)

    if not normalized_user:
        return {
            "level": "empty",
            "score": 0,
            "message": "Bạn chưa nhập câu trả lời.",
        }

    score = round(SequenceMatcher(None, normalized_sample, normalized_user).ratio() * 100)

    if normalized_user == normalized_sample:
        level = "perfect"
        message = "Chính xác hoàn toàn. Bạn đã nhớ đúng nội dung đáp án."
    elif score >= 90:
        level = "good"
        message = "Rất tốt. Câu trả lời gần như trùng khớp với đáp án mẫu."
    elif score >= 75:
        level = "close"
        message = "Khá tốt. Bạn nên mở đáp án mẫu để kiểm tra các ý còn thiếu hoặc khác thứ tự."
    else:
        level = "review"
        message = "Câu trả lời còn khác khá nhiều. Hãy xem gợi ý hoặc mở đáp án mẫu rồi thử lại."

    return {"level": level, "score": score, "message": message}


with st.sidebar:
    st.header("Kho dữ liệu")
    uploaded_file = st.file_uploader(
        "Tải file Excel khác",
        type=["xlsx"],
        help="File cần có cột Câu hỏi, Đáp án và có thể thêm cột Gợi ý.",
    )
    st.caption("Không tải file mới thì ứng dụng dùng kho_cau_hoi.xlsx đi kèm.")
    st.caption(f"Phiên bản ứng dụng: **{APP_VERSION}**")

try:
    if uploaded_file is not None:
        source_bytes = uploaded_file.getvalue()
        source_name = uploaded_file.name
    else:
        if not DEFAULT_DATA_FILE.exists():
            st.error("Không tìm thấy file kho_cau_hoi.xlsx trong thư mục ứng dụng.")
            st.stop()
        source_bytes = DEFAULT_DATA_FILE.read_bytes()
        source_name = DEFAULT_DATA_FILE.name

    questions = load_question_bank(source_bytes)
except Exception as error:
    st.error(f"Không thể đọc kho câu hỏi: {error}")
    st.stop()

signature = hashlib.sha256(source_bytes).hexdigest()
if st.session_state.get("bank_signature") != signature:
    reset_learning_session(len(questions), signature)

current_position = st.session_state.question_position
current_index = st.session_state.question_order[current_position]
current_row = questions.iloc[current_index]
current_question = str(current_row["question"])
current_answer = str(current_row["answer"])
raw_hint = str(current_row["hint"])

hints = [item.strip() for item in re.split(r"[|;]", raw_hint) if item.strip()]
if not hints:
    hints = automatic_hints(current_answer)

st.markdown(f'<div class="app-title">📖 {html.escape(APP_TITLE)}</div>', unsafe_allow_html=True)
st.markdown(
    (
        '<div class="progress-text">'
        f'Câu {current_position + 1}/{len(questions)} · Vòng {st.session_state.cycle_number} · '
        f'Nguồn: {html.escape(source_name)} · Phiên bản: {APP_VERSION}'
        '</div>'
    ),
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="question-card">'
        '<span class="question-label">Câu hỏi:</span>'
        f'<span class="question-text">{html.escape(current_question)}</span>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

left_column, arrow_column, right_column = st.columns([1, 0.075, 1], gap="small")

with left_column:
    st.markdown('<div class="panel-title" style="border:1px solid #d5dbe3;border-radius:10px 10px 0 0;">Đáp án mẫu</div>', unsafe_allow_html=True)

    if st.session_state.show_answer:
        escaped_answer = html.escape(current_answer).replace("\n", "<br>")
        st.markdown(
            f'<div class="answer-body" style="border:1px solid #d5dbe3;border-top:none;border-radius:0 0 10px 10px;">{escaped_answer}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            (
                '<div class="answer-hidden" style="border:1px solid #d5dbe3;border-top:none;border-radius:0 0 10px 10px;">'
                '<div class="lock">🔒</div>'
                '<div>Đáp án đang được ẩn.<br>Hãy tự trả lời trước khi mở đáp án.</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    toggle_label = "🙈 Ẩn đáp án" if st.session_state.show_answer else "👁 Hiện đáp án"
    st.button(
        toggle_label,
        on_click=toggle_answer,
        use_container_width=True,
        key="toggle_answer_button",
    )

with arrow_column:
    st.markdown('<div class="middle-arrow">⇄</div>', unsafe_allow_html=True)

with right_column:
    st.markdown('<div class="input-title">Gõ đáp án</div>', unsafe_allow_html=True)
    st.text_area(
        "Gõ đáp án",
        key="user_answer",
        height=360,
        placeholder="Nhập lại toàn bộ đáp án theo trí nhớ của bạn…",
        label_visibility="collapsed",
    )

hint_html_parts: list[str] = []
for index, hint in enumerate(hints):
    if index > 0:
        hint_html_parts.append('<span class="hint-arrow">→</span>')
    hint_html_parts.append(f'<span class="hint-chip">{html.escape(hint)}</span>')

st.markdown(
    (
        '<div class="hint-card">'
        '<div class="hint-title">Gợi ý</div>'
        f'<div class="hint-flow">{"".join(hint_html_parts)}</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

button_spacer, check_column, clear_column, next_column = st.columns([1.2, 1, 1, 1.15])

with check_column:
    if st.button("Kiểm tra", type="primary", use_container_width=True):
        st.session_state.feedback = check_user_answer(
            current_answer,
            st.session_state.user_answer,
        )

with clear_column:
    st.button(
        "Xóa bài làm",
        on_click=clear_user_answer,
        use_container_width=True,
    )

with next_column:
    st.button(
        "Câu tiếp theo →",
        on_click=next_question,
        use_container_width=True,
    )

feedback = st.session_state.feedback
if feedback:
    level = feedback["level"]
    message = str(feedback["message"])
    score = int(feedback["score"])

    if level == "empty":
        st.warning(message)
    elif level in {"perfect", "good"}:
        st.success(f"{message} Mức tương đồng: {score}%.")
    elif level == "close":
        st.warning(f"{message} Mức tương đồng: {score}%.")
    else:
        st.error(f"{message} Mức tương đồng: {score}%.")

st.caption(
    "Điểm tương đồng chỉ dùng để hỗ trợ tự học; hãy đối chiếu đáp án mẫu để kiểm tra chính xác từng ý."
)