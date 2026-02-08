import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# --- إعدادات الصفحة ---
# هنا تغير اسم المتصفح
st.set_page_config(page_title="تطبيقي الخاص", page_icon="💬")

# --- قاعدة البيانات ---
DB_FILE = "chat_v8.db"
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

init_db()

def img_to_bytes(img_file):
    if img_file:
        img = Image.open(img_file).convert("RGB")
        img.thumbnail((100, 100)) # تصغير الصورة لسرعة التحميل
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# --- نظام الدخول والأسماء ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 تسجيل الدخول")
    pwd = st.text_input("أدخل كلمة السر (123):", type="password")
    if st.button("دخول"):
        if pwd == "123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("خطأ!")
elif "user_name" not in st.session_state:
    st.title("👤 خطوة أخيرة: من أنت؟")
    name = st.text_input("اكتب اسمك الشخصي الذي سيظهر للكل:")
    avatar_file = st.file_uploader("اختر صورتك الشخصية من الاستوديو 🖼️", type=['png', 'jpg', 'jpeg'])
    if st.button("بدء الدردشة"):
        if name:
            st.session_state.user_name = name
            st.session_state.my_avatar = img_to_bytes(avatar_file) if avatar_file else ""
            st.rerun()
        else:
            st.warning("الرجاء كتابة اسمك!")
else:
    # --- واجهة الدردشة ---
    # هنا تقدر تغير اسم البرنامج اللي يظهر فوق الرسائل
    st.title("🔥المنظمه السريه  ") 

    # إعدادات الخلفية في الجانب
    bg_file = st.sidebar.file_uploader("🖼️ تغيير خلفية الدردشة", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>.stApp { background-color: #e5ddd5; }</style>""", unsafe_allow_html=True)

    # تنسيق الفقاعات (CSS)
    st.markdown("""
    <style>
    .msg-container { display: flex; flex-direction: column; margin-bottom: 10px; }
    .bubble { padding: 12px; border-radius: 18px; max-width: 75%; position: relative; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; color: black; border-bottom-right-radius: 2px; }
    .other-msg { align-self: flex-start; background-color: #ffffff; color: black; border-bottom-left-radius: 2px; }
    .avatar-img { width: 40px; height: 40px; border-radius: 50%; margin-bottom: 5px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

    # عرض الرسائل
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, avatar FROM messages")
    for u, con, ts, av in c.fetchall():
        is_me = u == st.session_state.user_name
        align = "my-msg" if is_me else "other-msg"
        av_html = f'<img src="data:image/png;base64,{av}" class="avatar-img">' if av else '👤'
        
        st.markdown(f"""
        <div class="msg-container">
            <div class="bubble {align}">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:5px;">
                    {av_html} <b style="font-size: 0.9em;">{u}</b>
                </div>
                <div>{con}</div>
                <div style="text-align:left; font-size: 0.7em; color: gray; margin-top:5px;">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    conn.close()

    # حقل الإرسال
    if prompt := st.chat_input("اكتب رسالتك..."):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        now = datetime.now().strftime("%I:%M %p")
        c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (st.session_state.user_name, prompt, now, st.session_state.my_avatar))
        conn.commit()
        conn.close()
        st.rerun()

    if st.sidebar.button("🗑️ مسح المحادثة"):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        st.rerun()
