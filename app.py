import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import time

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="مجلس الشلة VIP", page_icon="🔥")

# --- 2. قاعدة البيانات (اسم جديد لضمان الاستقرار) ---
DB_FILE = "chat_stable_v20.db"

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
            img.thumbnail((80, 80))
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
    st.stop()

if "user_name" not in st.session_state:
    st.title("👤 إعداد ملفك")
    n = st.text_input("اسمك:")
    av = st.file_uploader("صورتك:", type=['png', 'jpg', 'jpeg'])
    if st.button("بدء"):
        if n:
            st.session_state.user_name = n
            st.session_state.my_avatar = img_to_bytes(av)
            st.session_state.text_color = "#000000"
            st.rerun()
    st.stop()

# --- 4. التصميم (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #e5ddd5; background-size: cover; background-attachment: fixed; }
    .msg-box { display: flex; flex-direction: column; margin-bottom: 10px; }
    .bubble { padding: 10px 15px; border-radius: 15px; max-width: 80%; position: relative; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .my-msg { align-self: flex-end; background-color: #dcf8c6; }
    .other-msg { align-self: flex-start; background-color: #ffffff; }
    .reply-header { background: rgba(0,0,0,0.05); border-right: 3px solid #25D366; padding: 3px 8px; margin-bottom: 5px; border-radius: 5px; font-size: 0.8em; color: #666; }
    .av-img { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.session_state.text_color = st.color_picker("🎨 لون خطك:", st.session_state.text_color)
    with st.expander("📝 تعديل ملفي"):
        st.session_state.user_name = st.text_input("تعديل الاسم:", value=st.session_state.user_name)
        new_av = st.file_uploader("تحديث الصورة:", type=['png', 'jpg', 'jpeg'])
        if st.button("تحديث"):
            if new_av: st.session_state.my_avatar = img_to_bytes(new_av)
            st.rerun()
    
    bg_f = st.file_uploader("🖼️ خلفية الدردشة", type=['png', 'jpg', 'jpeg'])
    if bg_f:
        b64_bg = base64.b64encode(bg_f.read()).decode()
        st.markdown(f'<style>.stApp {{ background-image: url("data:image/png;base64,{b64_bg}"); }}</style>', unsafe_allow_html=True)

    if st.button("🗑️ مسح الكل"):
        conn = sqlite3.connect(DB_FILE); conn.cursor().execute("DELETE FROM messages"); conn.commit(); st.rerun()

# --- 6. عرض المحادثة ---
st.title("🔥 مجلس الشلة")

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("SELECT user, content, timestamp, avatar, text_color, reply_to, msg_id FROM messages")
rows = c.fetchall()

for u, con, ts, av, tc, rt, mid in rows:
    is_me = u == st.session_state.user_name
    side = "my-msg" if is_me else "other-msg"
    av_tag = f'<img src="data:image/png;base64,{av}" class="av-img">' if av else '👤'
    
    st.markdown(f'<div class="msg-box">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bubble {side}">', unsafe_allow_html=True)
        if rt: st.markdown(f'<div class="reply-header">↩️ {rt}</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="display:flex; align-items:center; margin-bottom:5px;">
                {av_tag} <b style="font-size:0.8em; color:#075e54;">{u}</b>
            </div>
            <div style="color:{tc};">{con}</div>
            <div style="text-align:left; font-size:0.6em; color:gray;">{ts}</div>
        """, unsafe_allow_html=True)
        
        # زر الرد (تم إصلاحه ليكون خفيفاً ولا يعطل الصفحة)
        if st.button(f"🗨️", key=f"re_{mid}"):
            st.session_state.reply_info = f"{u}: {con[:20]}"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
conn.close()

# --- 7. الإرسال (خانة الكتابة) ---
if "reply_info" in st.session_state:
    st.info(f"الرد على: {st.session_state.reply_info}")
    if st.button("إلغاء"):
        del st.session_state.reply_info
        st.rerun()

# هذه الخانة هي الأهم، تم وضعها في النهاية لضمان عملها
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    now = datetime.now().strftime("%I:%M %p")
    m_id = str(int(time.time() * 1000)) # معرف فريد جداً
    rep = st.session_state.get("reply_info", "")
    
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (st.session_state.user_name, prompt, now, st.session_state.my_avatar, st.session_state.text_color, rep, m_id))
    conn.commit()
    conn.close()
    
    if "reply_info" in st.session_state: del st.session_state.reply_info
    st.rerun()
