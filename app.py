 import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import time

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥")

# --- 2. قاعدة البيانات (مع التحديث التلقائي) ---
DB_FILE = "chat_v15_final.db" # تغيير الاسم لضمان بداية نظيفة وسريعة

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT, text_color TEXT, reply_to TEXT, msg_id TEXT)''')
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

# --- 3. نظام الدخول والتعريف ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 دخول")
    pwd = st.text_input("كلمة السر:", type="password")
    if st.button("دخول"):
        if pwd == "123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

if "user_name" not in st.session_state:
    st.title("👤 من أنت؟")
    name_init = st.text_input("اكتب اسمك:")
    avatar_init = st.file_uploader("صورتك الشخصية:", type=['png', 'jpg', 'jpeg'])
    if st.button("دخول للدردشة"):
        if name_init:
            st.session_state.user_name = name_init
            st.session_state.my_avatar = img_to_bytes(avatar_init)
            st.session_state.text_color = "#000000"
            st.rerun()
    st.stop()

# --- 4. القائمة الجانبية (الاعدادات) ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    st.session_state.text_color = st.color_picker("🎨 لون خطك:", st.session_state.get("text_color", "#000000"))
    
    with st.expander("📝 تعديل ملفي"):
        st.session_state.user_name = st.text_input("تعديل الاسم:", value=st.session_state.user_name)
        new_av = st.file_uploader("تحديث صورتك:", type=['png', 'jpg', 'jpeg'])
        if st.button("تحديث الملف"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.rerun()
            
    bg_file = st.file_uploader("🖼️ تغيير خلفية الدردشة", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; background-attachment: fixed; }}</style>', unsafe_allow_html=True)
    else:
        st.markdown('<style>.stApp { background-color: #e5ddd5; }</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح الكل"):
        conn = sqlite3.connect(DB_FILE); conn.cursor().execute("DELETE FROM messages"); conn.commit(); conn.close()
        st.rerun()

# --- 5. واجهة الدردشة ---
st.markdown("""
<style>
    .msg-container { display: flex; flex-direction: column; margin-bottom: 10px; }
    .bubble { padding: 10px 15px; border-radius: 15px; max-width: 80%; position: relative; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; }
    .other-msg { align-self: flex-start; background-color: #ffffff; }
    .reply-text { background: rgba(0,0,0,0.05); border-right: 3px solid #25D366; padding: 3px 8px; margin-bottom: 5px; border-radius: 5px; font-size: 0.8em; color: #666; }
    .avatar-img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
</style>
""", unsafe_allow_html=True)

st.title("💬 مجلسنا VIP")

# عرض الرسائل
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("SELECT user, content, timestamp, avatar, text_color, reply_to, msg_id FROM messages")
rows = c.fetchall()
for u, con, ts, av, t_color, r_to, m_id in rows:
    is_me = u == st.session_state.user_name
    align = "my-msg" if is_me else "other-msg"
    av_html = f'<img src="data:image/png;base64,{av}" class="avatar-img">' if av else '👤'
    
    st.markdown(f'<div class="msg-container">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bubble {align}">', unsafe_allow_html=True)
        if r_to:
            st.markdown(f'<div class="reply-text">↩️ {r_to}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:3px;">
                {av_html} <b style="font-size: 0.8em; color: #075e54;">{u}</b>
            </div>
            <div style="color: {t_color if t_color else '#000000'};">{con}</div>
            <div style="text-align:left; font-size: 0.6em; color: gray; margin-top:3px;">{ts}</div>
        """, unsafe_allow_html=True)
        
        # زر الرد صغير وبسيط لتجنب تعليق الصفحة
        if st.button("💬 رد", key=f"re_{m_id}"):
            st.session_state.reply_info = f"{u}: {con[:20]}..."
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
conn.close()

# شريط الرد
if "reply_info" in st.session_state:
    st.warning(f"جاري الرد على: {st.session_state.reply_info}")
    if st.button("إلغاء الرد"):
        del st.session_state.reply_info
        st.rerun()

# --- خانة الكتابة (خارج أي loop لضمان ظهورها) ---
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    now = datetime.now().strftime("%I:%M %p")
    m_id = str(time.time()).replace(".", "")
    r_text = st.session_state.get("reply_info", "")
    c.execute("INSERT INTO messages (user, content, timestamp, avatar, text_color, reply_to, msg_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (st.session_state.user_name, prompt, now, st.session_state.get("my_avatar", ""), st.session_state.text_color, r_text, m_id))
    conn.commit(); conn.close()
    if "reply_info" in st.session_state: del st.session_state.reply_info
    st.rerun()   
