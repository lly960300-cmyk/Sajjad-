import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Telegram VIP", page_icon="✈️")

# --- قاعدة البيانات ---
DB_FILE = "tg_final_v5.db"
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

init_db()

# دالة لتحويل الصورة إلى نص (عشان تنحفظ بقاعدة البيانات)
def img_to_bytes(img_file):
    if img_file:
        img = Image.open(img_file).convert("RGB")
        img.thumbnail((150, 150))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# --- واجهة المستخدم ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("✈️ Telegram Login")
    if st.text_input("كلمة السر", type="password") == "123":
        if st.button("دخول"):
            st.session_state.auth = True
            st.rerun()
else:
    # إعدادات الملف الشخصي والخلفية في الجانب
    st.sidebar.title("⚙️ الإعدادات")
    if "user_name" not in st.session_state:
        st.session_state.user_name = st.sidebar.text_input("اسمك المستعار", "مستخدم")
        
    uploaded_avatar = st.sidebar.file_uploader("ارفع صورتك الشخصية 🖼️", type=['png', 'jpg', 'jpeg'])
    if uploaded_avatar:
        st.session_state.my_avatar = img_to_bytes(uploaded_avatar)
    else:
        st.session_state.my_avatar = ""

    bg_file = st.sidebar.file_uploader("غير خلفية المحادثة 🌆", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; }}</style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>.stApp { background-color: #e5ddd5; }</style>""", unsafe_allow_html=True)

    # تنسيق الفقاعات (CSS)
    st.markdown("""
    <style>
    .msg-container { display: flex; flex-direction: column; }
    .bubble { padding: 10px; border-radius: 15px; margin: 5px; max-width: 70%; position: relative; font-family: sans-serif; }
    .my-msg { align-self: flex-end; background-color: #efffde; border-bottom-right-radius: 2px; }
    .other-msg { align-self: flex-start; background-color: #ffffff; border-bottom-left-radius: 2px; }
    .avatar-img { width: 35px; height: 35px; border-radius: 50%; margin: 5px; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

    st.title("💬 Telegram VIP")

    # عرض الرسائل
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, avatar FROM messages")
    for u, con, ts, av in c.fetchall():
        is_me = u == st.session_state.user_name
        align = "my-msg" if is_me else "other-msg"
        
        # عرض الصورة الشخصية إذا وجدت
        av_html = f'<img src="data:image/png;base64,{av}" class="avatar-img">' if av else '👤'
        
        st.markdown(f"""
        <div class="msg-container">
            <div class="bubble {align}">
                {av_html} <b>{u}</b> <br> {con} <br>
                <small style="color:gray; font-size:10px;">{ts}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    conn.close()

    # الإرسال
    if prompt := st.chat_input("اكتب رسالة..."):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        now = datetime.now().strftime("%I:%M %p")
        my_av = st.session_state.get("my_avatar", "")
        c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (st.session_state.user_name, prompt, now, my_av))
        conn.commit()
        conn.close()
        st.rerun()

    if st.sidebar.button("مسح السجل"):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        st.rerun()
