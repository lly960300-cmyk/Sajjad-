import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import time

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥")

# --- 2. قاعدة البيانات مع ميزة التحديث التلقائي ---
DB_FILE = "chat_v12_pro.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    # إنشاء الجدول إذا لم يكن موجوداً
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT, text_color TEXT, reply_to TEXT, msg_id TEXT)''')
    
    # --- حيلة برمجية: إضافة الأعمدة الناقصة إذا كانت القاعدة قديمة لتجنب الخطأ ---
    try:
        c.execute("ALTER TABLE messages ADD COLUMN text_color TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE messages ADD COLUMN reply_to TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE messages ADD COLUMN msg_id TEXT")
    except: pass
    
    conn.commit()
    conn.close()

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
    pwd = st.text_input("كلمة السر:", type="password")
    if st.button("دخول"):
        if pwd == "123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("كلمة السر غلط")
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

# --- 4. الإعدادات الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    st.session_state.text_color = st.color_picker("🎨 لون خطك:", st.session_state.get("text_color", "#000000"))
    
    with st.expander("📝 تعديل ملفي"):
        st.session_state.user_name = st.text_input("الاسم:", value=st.session_state.user_name)
        new_av = st.file_uploader("تغيير الصورة:", type=['png', 'jpg', 'jpeg'], key="sidebar_av")
        if st.button("تحديث"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.rerun()
    
    bg_file = st.file_uploader("🖼️ تغيير الخلفية:", type=['png', 'jpg', 'jpeg'], key="sidebar_bg")
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; background-attachment: fixed; }}</style>', unsafe_allow_html=True)
    else:
        st.markdown('<style>.stApp { background-color: #e5ddd5; }</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح الكل"):
        conn = sqlite3.connect(DB_FILE); conn.cursor().execute("DELETE FROM messages"); conn.commit(); conn.close()
        st.rerun()

# --- 5. واجهة الدردشة وتنسيق CSS ---
st.markdown("""
<style>
    .msg-container { display: flex; flex-direction: column; margin-bottom: 12px; }
    .bubble { padding: 12px; border-radius: 15px; max-width: 80%; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); position: relative; }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; border-bottom-right-radius: 2px; }
    .other-msg { align-self: flex-start; background-color: #ffffff; border-bottom-left-radius: 2px; }
    .reply-quote { background: rgba(0,0,0,0.07); border-right: 4px solid #25D366; padding: 5px 10px; margin-bottom: 8px; border-radius: 5px; font-size: 0.85em; color: #444; font-style: italic; }
    .avatar-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

st.title("💬 مجلسنا VIP")

# عرض الرسائل من قاعدة البيانات
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("SELECT user, content, timestamp, avatar, text_color, reply_to, msg_id FROM messages")
rows = c.fetchall()
for u, con, ts, av, t_color, r_to, m_id in rows:
    is_me = u == st.session_state.user_name
    align = "my-msg" if is_me else "other-msg"
    av_html = f'<img src="data:image/png;base64,{av}" class="avatar-img">' if av else '👤'
    
    st.markdown(f'<div class="msg-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="bubble {align}">', unsafe_allow_html=True)
    
    if r_to:
        st.markdown(f'<div class="reply-quote">↩️ {r_to}</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
            {av_html} <b style="font-size: 0.85em; color: #075e54;">{u}</b>
        </div>
        <div style="color: {t_color if t_color else '#000000'}; font-size: 1.05em;">{con}</div>
        <div style="text-align:left; font-size: 0.65em; color: gray; margin-top:5px;">{ts}</div>
    """, unsafe_allow_html=True)    
