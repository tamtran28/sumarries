import streamlit as st
import os
import fitz  # PyMuPDF
import docx  # python-docx
from gensim.summarization import summarize # Ví dụ dùng gensim cho extractive summarization

# --- HÀM XỬ LÝ ---
def extract_text_from_file(file_path):
    """Tự động trích xuất văn bản từ file PDF hoặc DOCX."""
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        try:
            doc = fitz.open(file_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
            return text
        except Exception as e:
            return f"Lỗi khi đọc file PDF: {e}"
    elif file_extension == ".docx":
        try:
            doc = docx.Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs)
            return text
        except Exception as e:
            return f"Lỗi khi đọc file DOCX: {e}"
    else:
        return "Định dạng file không được hỗ trợ."

def summarize_text_extractive(text):
    """Tóm tắt văn bản bằng phương pháp trích xuất (Gensim)."""
    # Xử lý trường hợp text quá ngắn để tóm tắt
    if len(text.split()) < 100: # Cần ít nhất 100 từ để tóm tắt có nghĩa
        return "Nội dung quá ngắn để tóm tắt. Vui lòng cung cấp văn bản dài hơn."
    try:
        # Tóm tắt với độ dài bằng 20% bản gốc
        return summarize(text, ratio=0.2)
    except Exception as e:
        return "Không thể tạo bản tóm tắt. Văn bản có thể không đủ cấu trúc câu rõ ràng."

# --- GIAO DIỆN ỨNG DỤNG ---
st.set_page_config(page_title="Trợ lý Tóm tắt Văn bản", layout="wide")

st.title("Trợ lý Tóm tắt Văn bản 🤖")
st.write("Tải lên văn bản pháp luật, quyết định... dưới dạng PDF hoặc Word để nhận bản tóm tắt nhanh chóng.")

# Cho phép tải lên cả file pdf và docx
uploaded_file = st.file_uploader("Chọn một file PDF hoặc Word", type=["pdf", "docx"])

if uploaded_file is not None:
    # Tạo một thư mục tạm để lưu file
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    file_path = os.path.join("temp", uploaded_file.name)

    # Lưu file từ bộ nhớ đệm vào đĩa
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Đã tải lên thành công file: **{uploaded_file.name}**")

    if st.button("Tạo bản tóm tắt"):
        with st.spinner("Đang phân tích và tóm tắt văn bản..."):
            # Bước 1: Trích xuất văn bản
            raw_text = extract_text_from_file(file_path)

            if "Lỗi" in raw_text or "không được hỗ trợ" in raw_text:
                st.error(raw_text)
            else:
                # Bước 2: Tóm tắt văn bản
                summary = summarize_text_extractive(raw_text)
                
                # Hiển thị kết quả
                st.subheader("Bản tóm tắt:")
                st.write(summary)

                with st.expander("Xem nội dung gốc đã trích xuất"):
                    st.text_area("Nội dung gốc", raw_text, height=300)

    # Dọn dẹp file tạm sau khi xử lý
    if os.path.exists(file_path):
        os.remove(file_path)
