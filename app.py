import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥")

# --- 2. قاعدة البيانات ---
DB_FILE = "main_chat_db.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (user TEXT, content TEXT, timestamp TEXT, avatar TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"خطأ في قاعدة البيانات: {e}")

init_db()

# دالة تحويل الصور
def img_to_bytes(img_file):
    try:
        if img_file:
            img = Image.open(img_file).convert("RGB")
            img.thumbnail((100, 100))
            buf = BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode()
    except:
        return ""
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
            st.error("كلمة السر خطأ")
    st.stop()

# طلب الاسم لأول مرة فقط
if "user_name" not in st.session_state:
    st.title("👤 من أنت؟")
    name_init = st.text_input("اكتب اسمك:")
    avatar_init = st.file_uploader("صورتك (اختياري):", type=['png', 'jpg', 'jpeg'])
    if st.button("بدء الدردشة"):
        if name_init:
            st.session_state.user_name = name_init
            st.session_state.my_avatar = img_to_bytes(avatar_init)
            st.rerun()
    st.stop()

# --- 4. واجهة الدردشة ---

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

# القائمة الجانبية للتعديلات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    with st.expander("📝 تعديل ملفي الشخصي"):
        st.session_state.user_name = st.text_input("تعديل الاسم:", value=st.session_state.user_name)
        new_av = st.file_uploader("تحديث صورتي:", type=['png', 'jpg', 'jpeg'])
        if st.button("تحديث الآن"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.success("تم التحديث!")
            st.rerun()
    
    bg_file = st.file_uploader("🖼️ تغيير خلفية الدردشة:", type=['png', 'jpg', 'jpeg'])
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); }}</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح المحادثة للكل"):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        st.rerun()

st.title("🔥 مجلس الشلة")

# عرض الرسائل
try:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, avatar FROM messages")
    rows = c.fetchall()
    for u, con, ts, av in rows:
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
except:
    st.info("اكتب أول رسالة لبدء المحادثة!")

# خانة إرسال الرسالة
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().strftime("%I:%M %p")
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", 
              (st.session_state.user_name, prompt, now, st.session_state.get("my_avatar", "")))
    conn.commit()
    conn.close()
    st.rerun()
