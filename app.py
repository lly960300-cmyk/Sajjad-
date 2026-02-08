import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import time

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥")

# --- 2. قاعدة البيانات (نسخة محدثة لدعم الردود) ---
DB_FILE = "chat_v12_pro.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (user TEXT, content TEXT, timestamp TEXT, avatar TEXT, text_color TEXT, reply_to TEXT, msg_id TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"خطأ في قاعدة البيانات: {e}")

init_db()

def img_to_bytes(img_file):
    try:
        if img_file:
            img = Image.open(img_file).convert("RGB")
            img.thumbnail((100, 100))
            buf = BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode()
    except: return ""
    return ""

# --- 3. نظام الدخول ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 دخول")
    if st.text_input("كلمة السر:", type="password") == "123":
        if st.button("دخول"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

if "user_name" not in st.session_state:
    st.title("👤 من أنت؟")
    name_init = st.text_input("اكتب اسمك:")
    avatar_init = st.file_uploader("صورتك (اختياري):", type=['png', 'jpg', 'jpeg'])
    if st.button("بدء الدردشة"):
        if name_init:
            st.session_state.user_name = name_init
            st.session_state.my_avatar = img_to_bytes(avatar_init)
            st.session_state.text_color = "#000000"
            st.rerun()
    st.stop()

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الاعدادات")
    st.session_state.text_color = st.color_picker("🎨 لون خطك:", st.session_state.get("text_color", "#000000"))
    
    with st.expander("📝 تعديل ملفي"):
        st.session_state.user_name = st.text_input("الاسم:", value=st.session_state.user_name)
        new_av = st.file_uploader("تغيير الصورة:", type=['png', 'jpg', 'jpeg'])
        if st.button("تحديث"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.rerun()
    
    bg_file = st.file_uploader("🖼️ تغيير الخلفية:", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; background-attachment: fixed; }}</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح الكل"):
        conn = sqlite3.connect(DB_FILE); conn.cursor().execute("DELETE FROM messages"); conn.commit(); conn.close()
        st.rerun()

# --- 5. واجهة الدردشة ---
st.markdown("""
<style>
    .stApp { background-color: #e5ddd5; }
    .msg-container { display: flex; flex-direction: column; margin-bottom: 10px; }
    .bubble { padding: 12px; border-radius: 15px; max-width: 80%; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; }
    .other-msg { align-self: flex-start; background-color: #ffffff; }
    .reply-quote { background: rgba(0,0,0,0.05); border-right: 4px solid #25D366; padding: 5px; margin-bottom: 8px; border-radius: 4px; font-size: 0.8em; color: #555; }
    .avatar-img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
</style>
""", unsafe_allow_html=True)

st.title("💬 مجلسنا VIP")

# عرض الرسائل
try:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, avatar, text_color, reply_to, msg_id FROM messages")
    for u, con, ts, av, t_color, r_to, m_id in c.fetchall():
        is_me = u == st.session_state.user_name
        align = "my-msg" if is_me else "other-msg"
        av_html = f'<img src="data:image/png;base64,{av}" class="avatar-img">' if av else '👤'
        
        st.markdown(f'<div class="msg-container">', unsafe_allow_html=True)
        with st.container():
            st.markdown(f'<div class="bubble {align}">', unsafe_allow_
