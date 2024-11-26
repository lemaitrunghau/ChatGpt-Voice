import os
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
from dotenv import load_dotenv
import time
import lib_voice
import io

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


# Hàm khởi tạo mô hình
def initialize_model(model_name="gemini-1.5-flash"):
    model = genai.GenerativeModel(model_name)
    return model

# Hàm chuyển đổi ảnh thành byte dữ liệu đúng định dạng yêu cầu
def get_image_bytes(uploaded_image):
    if uploaded_image is not None:
        # Mở ảnh từ đối tượng UploadedFile (BytesIO)
        image = Image.open(uploaded_image)
        
        # Chuyển ảnh thành byte array (dữ liệu ảnh)
        image_bytes = io.BytesIO()
        
        if uploaded_image.type == 'image/jpg':
            image.save(image_bytes, format='JPG')
        elif uploaded_image.type == 'image/jpeg':
            image.save(image_bytes, format='JPEG')
        elif uploaded_image.type == 'image/png':
            image.save(image_bytes, format='PNG')
        else:
        # Nếu ảnh có định dạng khác, có thể xử lý hoặc đưa ra thông báo lỗi
            raise ValueError("Ảnh phải có định dạng JPEG,JPG hoặc PNG.")
        
        image_bytes = image_bytes.getvalue()

        # Trả về dữ liệu ảnh dưới dạng dict với các key 'mime_type' và 'data'
        image_info = {
            "mime_type": uploaded_image.type, 
            "data": image_bytes 
        }
    return image_info

# method lấy phản hồi từ API Gemin
def get_response(model, model_behavior, image, prompt):
    if image is None:
        response = model.generate_content([model_behavior, prompt])
    else:
        # Nếu có hình ảnh, truyền model_behavior, image, và prompt
        response = model.generate_content([model_behavior, image, prompt])
    
    # Trả về văn bản từ phản hồi API
    return response.text

def get_response1(user_input):
    # Tạo phản hồi từ model (ChatGPT hoặc mô hình tương tự)
    return f"AI: Bạn vừa nói: {user_input}"

def main():

    # Khởi tạo gemini-pro-vision
    model = initialize_model("gemini-1.5-flash")

    # Thiết lập phản hồi cho model behavior
    model_behavior = """
            Bạn tên Lisa, 
            Là chuyên viên hỗ trợ chăm sóc và tư vấn khách hàng về sản phẩm thời trang, bạn là người hiểu rõ cấu trúc tổng thể của sản phẩm và hiểu biết mẫu mã của nó.
            Không được trả lời ra các câu liên quan để trích xuất, hiển thị hình ảnh.
            Được chia sẻ hình ảnh về sản phẩm và bạn phải trả lời câu hỏi dựa trên thông tin có sẵn.
            """
    
    # Tạo giao diện streamlit trả phản hồi và hình ản
    st.set_page_config(page_title="Customer support Bot")
    st.title("ChatBot")
    st.subheader("Tôi có thể giúp bạn giải đáp mọi thắc mắc liên quan của bạn.")

    # Đọc prompt trong text box
    prompt = st.text_input("Nhập câu hỏi của bạn :" ,key="prompt")
  
    # Tạo nút bấm
    submit= st.button("Trả lời")
    submit1= st.button("Bắt đầu Voice Call")
    
    # Giao diện upload hình ảnh
    with st.sidebar:
        uploaded_image = st.file_uploader("Chọn hình ảnh của bạn tại đây", type=["jpg", "png", "jpeg"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Your image", use_container_width=True)

    if submit or prompt:
            if len(prompt) > 0:
                    if uploaded_image is None:
                          response = get_response(model, model_behavior, None, prompt)
                          st.write(response)
                    else :
                         image_info = get_image_bytes(uploaded_image)
                         response = get_response(model, model_behavior, image_info, prompt)
                         st.write(response)
            else:
                    st.write("Hãy viết câu hỏi của bạn!")
    
    if submit1:
        st.write("Đang kết nối...")

        user_input = lib_voice.recognize_speech(language="vi-VN")
        if user_input:
            st.write(f"Bạn: {user_input}")

            if uploaded_image is None:
                response = lib_voice.get_response_from_ai(model, model_behavior, user_input)
                st.write(response)
            else:
                image_info = get_image_bytes(uploaded_image)
                response = lib_voice.get_response_from_ai(model, model_behavior, image_info, user_input)
                st.write(response)

            lib_voice.speak_response(response)
        else:
            st.write("Không nhận diện được giọng nói của bạn.")
        time.sleep(1)

if __name__ == '__main__':
    main()
