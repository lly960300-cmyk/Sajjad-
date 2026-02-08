 import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥", layout="centered")

# --- 2. قاعدة البيانات ---
DB_FILE = "chat_final_v10.db"
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

init_db()

# دالة تحويل الصور
def img_to_bytes(img_file):
    if img_file:
        img = Image.open(img_file).convert("RGB")
        img.thumbnail((120, 120))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    return ""

# --- 3. نظام الدخول والتعريف ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 دخول")
    if st.text_input("كلمة السر:", type="password") == "123":
        if st.button("دخول"):
            st.session_state.auth = True
            st.rerun()
    st.stop() # توقف هنا حتى يدخل الباسورد

# إذا دخل الباسورد وما عنده اسم، يطلب منه الاسم مرة واحدة
if "user_name" not in st.session_state:
    st.title("👤 من أنت؟")
    name_init = st.text_input("اكتب اسمك للشلة:")
    avatar_init = st.file_uploader("صورتك الشخصية (اختياري):", type=['png', 'jpg', 'jpeg'])
    if st.button("دخول للدردشة"):
        if name_init:
            st.session_state.user_name = name_init
            st.session_state.my_avatar = img_to_bytes(avatar_init) if avatar_init else ""
            st.rerun()
    st.stop() # توقف هنا حتى يختار اسمه

# --- 4. واجهة الدردشة (بعد الدخول واختيار الاسم) ---

# تصميم الخلفية والفقاعات
st.markdown("""
<style>
    .stApp { background-color: #e5ddd5; background-size: cover; background-attachment: fixed; }
    .msg-container { display: flex; flex-direction: column; margin-bottom: 15px; }
    .bubble { padding: 12px; border-radius: 18px; max-width: 75%; position: relative; box-shadow: 0px 1px 3px rgba(0,0,0,0.1); }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; border-bottom-right-radius: 2px; }
    .other-msg { align-self: flex-start; background-color: #ffffff; border-bottom-left-radius: 2px; }
    .avatar-img { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; }
</style>
""", unsafe_allow_html=True)

st.title("🔥 مجلس الشلة VIP")

# القائمة الجانبية للتعديلات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    # تعديل البروفايل
    with st.expander("📝 تعديل ملفي الشخصي"):
        st.session_state.user_name = st.text_input("الاسم الحالي:", value=st.session_state.user_name)
        new_av = st.file_uploader("تغيير صورتي:", type=['png', 'jpg', 'jpeg'])
        if st.button("تحديث"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.success("تم!")
            st.rerun()
    
    # تعديل الخلفية
    bg_file = st.file_uploader("🖼️ تغيير خلفية المحادثة:", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); }}</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح المحادثة للكل"):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        st.rerun()

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
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
                {av_html} <b style="font-size: 0.85em; color: #075e54;">{u}</b>
            </div>
            <div>{con}</div>
            <div style="text-align:left; font-size: 0.6em; color: gray; margin-top:5px;">{ts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
conn.close()

# خانة إرسال الرسالة (دائماً في الأسفل)
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().strftime("%I:%M %p")
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", 
              (st.session_state.user_name, prompt, now, st.session_state.my_avatar))
    conn.commit()
    conn.close()
    st.rerun()           
