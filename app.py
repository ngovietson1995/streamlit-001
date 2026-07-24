import difflib
import html
import io
import random
import re
import unicodedata

import pandas as pd
import streamlit as st


# =========================================================
# CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Ứng dụng học thuộc lòng",
    page_icon="📖",
    layout="wide",
)


# =========================================================
# GIAO DIỆN CSS
# =========================================================
st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .sub-title {
            text-align: center;
            color: #666666;
            margin-bottom: 25px;
        }

        .question-box {
            padding: 20px;
            border-radius: 12px;
            background-color: #f2f6ff;
            border-left: 6px solid #3366cc;

            /* Chuyển chữ câu hỏi sang màu đen */
            color: #000000 !important;

            /* Làm chữ nổi bật hơn */
            font-weight: 600;
            font-size: 20px;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .answer-box {
            height: 260px;
            overflow-y: auto;
            padding: 16px;
            border-radius: 10px;
            background-color: #fff8dc;
            border: 1px solid #e0c96d;
            color: #000000 !important;
            font-size: 17px;
            line-height: 1.7;
            white-space: pre-wrap;
        }

        .correct-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #e8f5e9;
            border-left: 6px solid #2e7d32;
        }

        .warning-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #fff3e0;
            border-left: 6px solid #ef6c00;
        }

        .incorrect-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #ffebee;
            border-left: 6px solid #c62828;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HÀM XỬ LÝ DỮ LIỆU
# =========================================================
def normalize_column_name(value: str) -> str:
    """
    Chuẩn hóa tên cột để chấp nhận các cách viết như:
    - Câu hỏi
    - cau hoi
    - câu_hỏi
    - CAU HOI
    """
    value = str(value).strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def standardize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Tìm và chuẩn hóa hai cột Câu hỏi, Đáp án.
    """
    column_mapping = {}

    question_aliases = {
        "cauhoi",
        "question",
        "questions",
        "noidungcauhoi",
    }

    answer_aliases = {
        "dapan",
        "answer",
        "answers",
        "noidungdapan",
    }

    for column in dataframe.columns:
        normalized_column = normalize_column_name(column)

        if normalized_column in question_aliases:
            column_mapping[column] = "Câu hỏi"

        if normalized_column in answer_aliases:
            column_mapping[column] = "Đáp án"

    dataframe = dataframe.rename(columns=column_mapping)

    required_columns = {"Câu hỏi", "Đáp án"}

    if not required_columns.issubset(dataframe.columns):
        raise ValueError(
            "Không tìm thấy hai cột 'Câu hỏi' và 'Đáp án' trong dữ liệu."
        )

    dataframe = dataframe[["Câu hỏi", "Đáp án"]].copy()

    # Xóa những dòng bị trống
    dataframe = dataframe.dropna(subset=["Câu hỏi", "Đáp án"])

    # Chuyển dữ liệu về dạng chuỗi
    dataframe["Câu hỏi"] = dataframe["Câu hỏi"].astype(str).str.strip()
    dataframe["Đáp án"] = dataframe["Đáp án"].astype(str).str.strip()

    # Loại bỏ dòng có chuỗi rỗng
    dataframe = dataframe[
        (dataframe["Câu hỏi"] != "")
        & (dataframe["Đáp án"] != "")
    ]

    dataframe = dataframe.reset_index(drop=True)

    if dataframe.empty:
        raise ValueError("Kho dữ liệu không có câu hỏi hợp lệ.")

    return dataframe


@st.cache_data
def load_uploaded_file(file_content: bytes, file_name: str) -> pd.DataFrame:
    """
    Đọc dữ liệu Excel hoặc CSV được tải lên.
    """
    file_name = file_name.lower()

    if file_name.endswith(".xlsx"):
        dataframe = pd.read_excel(io.BytesIO(file_content))

    elif file_name.endswith(".csv"):
        try:
            dataframe = pd.read_csv(
                io.BytesIO(file_content),
                encoding="utf-8-sig",
            )
        except UnicodeDecodeError:
            dataframe = pd.read_csv(
                io.BytesIO(file_content),
                encoding="latin-1",
            )

    else:
        raise ValueError("Ứng dụng chỉ hỗ trợ file XLSX hoặc CSV.")

    return standardize_dataframe(dataframe)


@st.cache_data
def load_default_file() -> pd.DataFrame:
    """
    Đọc file mặc định kho_cau_hoi.xlsx nếu có trong thư mục dự án.
    """
    dataframe = pd.read_excel("kho_cau_hoi.xlsx")
    return standardize_dataframe(dataframe)


# =========================================================
# HÀM SO SÁNH ĐÁP ÁN
# =========================================================
def normalize_answer(text: str) -> str:
    """
    Chuẩn hóa nội dung trước khi so sánh.

    Ứng dụng bỏ qua:
    - Chữ hoa và chữ thường
    - Dấu câu
    - Khoảng trắng thừa

    Ứng dụng vẫn giữ nguyên dấu tiếng Việt.
    """
    text = str(text).lower().strip()
    text = unicodedata.normalize("NFC", text)

    # Thay dấu câu bằng khoảng trắng
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

    # Loại bỏ khoảng trắng thừa
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_similarity(reference_answer: str, user_answer: str) -> float:
    """
    Tính tỷ lệ giống nhau từ 0 đến 100.
    """
    reference_normalized = normalize_answer(reference_answer)
    user_normalized = normalize_answer(user_answer)

    if not user_normalized:
        return 0.0

    similarity = difflib.SequenceMatcher(
        None,
        reference_normalized,
        user_normalized,
    ).ratio()

    return round(similarity * 100, 1)


def compare_words(reference_answer: str, user_answer: str) -> tuple[list, list]:
    """
    Tìm các từ có thể bị thiếu hoặc bị nhập thêm.
    """
    reference_words = normalize_answer(reference_answer).split()
    user_words = normalize_answer(user_answer).split()

    reference_word_set = set(reference_words)
    user_word_set = set(user_words)

    missing_words = [
        word for word in reference_words
        if word not in user_word_set
    ]

    extra_words = [
        word for word in user_words
        if word not in reference_word_set
    ]

    # Loại bỏ phần tử trùng lặp nhưng giữ thứ tự
    missing_words = list(dict.fromkeys(missing_words))
    extra_words = list(dict.fromkeys(extra_words))

    return missing_words, extra_words


# =========================================================
# QUẢN LÝ TRẠNG THÁI
# =========================================================
def initialize_session_state() -> None:
    default_values = {
        "question_index": None,
        "previous_question_index": None,
        "answer_input": "",
        "last_score": None,
        "last_user_answer": "",
        "attempt_count": 0,
        "excellent_count": 0,
        "data_source_id": None,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def select_random_question(number_of_questions: int) -> None:
    """
    Chọn câu hỏi ngẫu nhiên và tránh lặp lại ngay câu vừa học.
    """
    if number_of_questions <= 0:
        return

    current_index = st.session_state.question_index

    if number_of_questions == 1:
        new_index = 0
    else:
        possible_indices = [
            index
            for index in range(number_of_questions)
            if index != current_index
        ]
        new_index = random.choice(possible_indices)

    st.session_state.previous_question_index = current_index
    st.session_state.question_index = new_index
    st.session_state.answer_input = ""
    st.session_state.last_score = None
    st.session_state.last_user_answer = ""


def reset_learning_session(number_of_questions: int) -> None:
    st.session_state.attempt_count = 0
    st.session_state.excellent_count = 0
    select_random_question(number_of_questions)


# =========================================================
# KHỞI TẠO
# =========================================================
initialize_session_state()


# =========================================================
# TIÊU ĐỀ
# =========================================================
st.markdown(
    '<div class="main-title">📖 Ứng dụng học thuộc lòng</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
        Quan sát đáp án mẫu, sau đó gõ lại nội dung để kiểm tra khả năng ghi nhớ
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# THANH BÊN
# =========================================================
with st.sidebar:
    st.header("⚙️ Kho dữ liệu")

    uploaded_file = st.file_uploader(
        "Tải kho câu hỏi",
        type=["xlsx", "csv"],
        help="File cần có hai cột: Câu hỏi và Đáp án.",
    )

    st.caption(
        "Nếu không tải file lên, ứng dụng sẽ sử dụng "
        "file kho_cau_hoi.xlsx trong thư mục dự án."
    )


# =========================================================
# ĐỌC KHO DỮ LIỆU
# =========================================================
try:
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()

        questions_dataframe = load_uploaded_file(
            file_bytes,
            uploaded_file.name,
        )

        current_data_source_id = (
            uploaded_file.name,
            len(file_bytes),
        )

        data_source_name = uploaded_file.name

    else:
        questions_dataframe = load_default_file()
        current_data_source_id = ("kho_cau_hoi.xlsx", len(questions_dataframe))
        data_source_name = "kho_cau_hoi.xlsx"

except FileNotFoundError:
    st.error(
        "Không tìm thấy file kho_cau_hoi.xlsx. "
        "Hãy đặt file này cùng thư mục với app.py "
        "hoặc tải file lên bằng thanh bên."
    )
    st.stop()

except Exception as error:
    st.error(f"Không thể đọc kho dữ liệu: {error}")
    st.stop()


# Đặt lại phiên học nếu người dùng thay kho dữ liệu
if st.session_state.data_source_id != current_data_source_id:
    st.session_state.data_source_id = current_data_source_id
    reset_learning_session(len(questions_dataframe))


# Chọn câu đầu tiên
if st.session_state.question_index is None:
    select_random_question(len(questions_dataframe))


# =========================================================
# THỐNG KÊ
# =========================================================
with st.sidebar:
    st.success(f"Đã tải {len(questions_dataframe)} câu hỏi")
    st.caption(f"Nguồn dữ liệu: {data_source_name}")

    st.divider()
    st.subheader("📊 Kết quả học")

    st.metric(
        label="Số lượt đã luyện",
        value=st.session_state.attempt_count,
    )

    st.metric(
        label="Số lượt đạt từ 90%",
        value=st.session_state.excellent_count,
    )

    if st.session_state.attempt_count > 0:
        excellent_rate = (
            st.session_state.excellent_count
            / st.session_state.attempt_count
            * 100
        )

        st.metric(
            label="Tỷ lệ ghi nhớ tốt",
            value=f"{excellent_rate:.1f}%",
        )

    st.button(
        "🔄 Bắt đầu lại",
        use_container_width=True,
        on_click=reset_learning_session,
        args=(len(questions_dataframe),),
    )


# =========================================================
# HIỂN THỊ CÂU HỎI
# =========================================================
current_index = st.session_state.question_index
current_row = questions_dataframe.iloc[current_index]

question = str(current_row["Câu hỏi"])
reference_answer = str(current_row["Đáp án"])

safe_question = html.escape(question)
safe_answer = html.escape(reference_answer)

st.markdown("### Câu hỏi")

st.markdown(
    f'<div class="question-box">{safe_question}</div>',
    unsafe_allow_html=True,
)


# =========================================================
# HAI KHUNG ĐÁP ÁN
# =========================================================
left_column, right_column = st.columns(2, gap="large")

with left_column:
    st.markdown("### 👀 Đáp án mẫu")

    st.info(
        "Đáp án đang được ẩn. "
        "Hãy thử tự nhớ và gõ lại trước khi xem đáp án."
    )

    # Đáp án mặc định được ẩn.
    # Khi người dùng bấm nút, một cửa sổ nhỏ sẽ hiện ra.
    with st.popover(
        "👁️ Xem đáp án mẫu",
        use_container_width=True,
    ):
        st.markdown(
            f'<div class="answer-box">{safe_answer}</div>',
            unsafe_allow_html=True,
        )

with right_column:
    st.markdown("### ✍️ Gõ lại đáp án")

    with st.form("answer_form"):
        st.text_area(
            "Nhập nội dung bạn ghi nhớ:",
            key="answer_input",
            height=210,
            placeholder="Gõ lại đáp án tại đây...",
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button(
            "✅ Kiểm tra kết quả",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        user_answer = st.session_state.answer_input.strip()

        if not user_answer:
            st.warning("Bạn chưa nhập nội dung đáp án.")
        else:
            score = calculate_similarity(
                reference_answer,
                user_answer,
            )

            st.session_state.last_score = score
            st.session_state.last_user_answer = user_answer
            st.session_state.attempt_count += 1

            if score >= 90:
                st.session_state.excellent_count += 1


# =========================================================
# KẾT QUẢ SO SÁNH
# =========================================================
if st.session_state.last_score is not None:
    st.divider()
    st.markdown("## Kết quả")

    score = st.session_state.last_score

    metric_column, progress_column = st.columns([1, 3])

    with metric_column:
        st.metric(
            label="Mức độ chính xác",
            value=f"{score}%",
        )

    with progress_column:
        st.write("")
        st.progress(min(score / 100, 1.0))

    if score >= 95:
        result_message = (
            "🎉 Rất tốt! Nội dung bạn nhập gần như hoàn toàn chính xác."
        )

        st.markdown(
            f'<div class="correct-box">{result_message}</div>',
            unsafe_allow_html=True,
        )

    elif score >= 80:
        result_message = (
            "👍 Khá tốt! Bạn đã ghi nhớ phần lớn nội dung, "
            "nhưng vẫn còn một vài điểm khác biệt."
        )

        st.markdown(
            f'<div class="warning-box">{result_message}</div>',
            unsafe_allow_html=True,
        )

    else:
        result_message = (
            "📚 Bạn nên quan sát lại đáp án mẫu và luyện thêm một lần nữa."
        )

        st.markdown(
            f'<div class="incorrect-box">{result_message}</div>',
            unsafe_allow_html=True,
        )

    missing_words, extra_words = compare_words(
        reference_answer,
        st.session_state.last_user_answer,
    )

    detail_column_1, detail_column_2 = st.columns(2)

    with detail_column_1:
        st.markdown("#### Từ có thể bị thiếu")

        if missing_words:
            st.write(", ".join(missing_words[:30]))
        else:
            st.success("Không phát hiện từ bị thiếu.")

    with detail_column_2:
        st.markdown("#### Từ có thể bị nhập thêm")

        if extra_words:
            st.write(", ".join(extra_words[:30]))
        else:
            st.success("Không phát hiện từ nhập thêm.")

    with st.expander("Xem lại nội dung đã nhập"):
        st.write(st.session_state.last_user_answer)


# =========================================================
# NÚT ĐIỀU KHIỂN
# =========================================================
st.divider()

button_column_1, button_column_2 = st.columns(2)

with button_column_1:
    st.button(
        "🎲 Câu hỏi ngẫu nhiên khác",
        use_container_width=True,
        on_click=select_random_question,
        args=(len(questions_dataframe),),
    )

with button_column_2:
    if st.button(
        "🧹 Xóa nội dung để luyện lại",
        use_container_width=True,
    ):
        st.session_state.answer_input = ""
        st.session_state.last_score = None
        st.session_state.last_user_answer = ""
        st.rerun()