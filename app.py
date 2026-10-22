import streamlit as st
import random
import time

st.set_page_config(page_title="Game Sút Penalty", page_icon="⚽", layout="centered")

st.title("⚽ Game Sút Penalty - Streamlit")
st.write("Hãy chọn góc sút để đánh bại thủ môn!")

# Khởi tạo trạng thái game (Session State)
if "score" not in st.session_state:
    st.session_state.score = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "history" not in st.session_state:
    st.session_state.history = []

# Bảng điểm
col1, col2 = st.columns(2)
with col1:
    st.metric("Số bàn thắng", st.session_state.score)
with col2:
    st.metric("Số lượt sút", st.session_state.attempts)

st.divider()

# Các hướng sút
DIRECTIONS = {
    "Góc cao trái ↖️": "top_left",
    "Chính giữa cao ⬆️": "top_center",
    "Góc cao phải ↗️": "top_right",
    "Góc thấp trái ↙️": "bottom_left",
    "Chính giữa thấp ⬇️": "bottom_center",
    "Góc thấp phải ↘️": "bottom_right"
}

st.subheader("🎯 Chọn hướng sút của bạn:")

# Tạo giao diện các nút sút (2 hàng, mỗi hàng 3 nút)
cols = st.columns(3)
choices = list(DIRECTIONS.keys())

shot = None
for i in range(3):
    if cols[i].button(choices[i], use_container_width=True):
        shot = choices[i]

cols_bottom = st.columns(3)
for i in range(3, 6):
    if cols_bottom[i-3].button(choices[i], use_container_width=True):
        shot = choices[i]

# Xử lý khi người chơi thực hiện cú sút
if shot:
    st.session_state.attempts += 1
    gk_choice = random.choice(choices)
    
    with st.spinner("Cầu thủ đang chạy đà... 🏃💨"):
        time.sleep(1)

    st.write(f"👉 Bạn sút vào: **{shot}**")
    st.write(f"🧤 Thủ môn bay người về: **{gk_choice}**")

    if shot == gk_choice:
        st.error("❌ **CẢN PHÁ TUYỆT VỜI!** Thủ môn đã đoán đúng hướng!")
        st.session_state.history.append("X")
    else:
        st.success("⚽ **VÀOOOOOO!** Cú sút quá hiểm hóc!")
        st.session_state.score += 1
        st.session_state.history.append("O")

# Hiển thị chuỗi lượt sút
if st.session_state.history:
    st.write("**Lịch sử các lượt sút:** " + " ".join([f"[{x}]" for x in st.session_state.history]))

st.divider()

# Nút chơi lại
if st.button("🔄 Chơi lại từ đầu"):
    st.session_state.score = 0
    st.session_state.attempts = 0
    st.session_state.history = []
    st.rerun()
