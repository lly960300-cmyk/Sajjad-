import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# --- إعداد قاعدة البيانات ---
DB_FILE = "chat_pro_v1.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # أضفنا عمود reply_to للردود و avatar للصور
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, color TEXT, reply_to TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_user_color(username):
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def save_message(user, content, reply_to=None, avatar="👤"):
    timestamp = datetime.now().strftime("%I:%M %p")
    color = get_user_color(user)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user, content, timestamp, color, reply_to, avatar) VALUES (?, ?, ?, ?, ?, ?)", 
              (user, content, reply_to, avatar))
    conn.commit()
    conn.close()

def get_messages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, color, reply_to, avatar FROM messages ORDER BY rowid ASC")
    data = c.fetchall()
    conn.close()
    return data

# --- تصميم الواجهة والخلفية ---
st.set_page_config(page_title="قروب الشلة VIP", page_icon="🔥")

# إضافة خلفية بسيطة (تغيير لون الخلفية)
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-color: #e5ddd5; /* لون يشبه خلفية واتساب القديمة */
    background-image: url("https://www.transparenttextures.com/patterns/cubes.png");
}
.reply-box {
    background-color: rgba(0,0,0,0.05);
    border-left: 5px solid #25D366;
    padding: 5px;
    margin-bottom: 5px;
    border-radius: 5px;
    font-size: 0.8em;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

PASSWORD = "123" 

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 بوابة القروب")
    pwd = st.text_input("كلمة السر:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
else:
    # إعدادات البروفايل
    if "username" not in st.session_state:
        st.title("⚙️ إعداداتك")
        st.session_state["username"] = st.text_input("اسمك:")
        st.session_state["avatar"] = st.selectbox("اختر صورتك (إيموجي):", ["👤", "😎", "🐱", "🦁", "🤖", "👻", "⭐"])
        if st.button("حفظ ودخول"):
            if st.session_state["username"]: st.rerun()
        st.stop()

    st.title("🔥 قروب الشلة VIP")
    
    # القائمة الجانبية
    st.sidebar.title(f"{st.session_state['avatar']} {st.session_state['username']}")
    if st.sidebar.button("🗑️ مسح المحادثة"):
        conn = get_connection()
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        st.rerun()

    # عرض الرسائل
    all_messages = get_messages()
    for msg_user, msg_content, msg_time, msg_color, msg_reply, msg_avatar in all_messages:
        with st.chat_message("user", avatar=msg_avatar):
            # إذا كان هناك رد
            if msg_reply:
                st.markdown(f"<div class='reply-box'>↩️ رداً على: {msg_reply}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<span style='color:{msg_color}; font-weight:bold;'>{msg_user}</span> <small style='color:gray;'>{msg_time}</small>", unsafe_allow_html=True)
            st.write(msg_content)
            
            # زر للرد على هذه الرسالة
            if st.button(f"رد", key=f"btn_{msg_time}_{msg_user}"):
                st.session_state["reply_info"] = f"{msg_user}: {msg_content[:20]}..."

    # منطقة الكتابة
    if "reply_info" in st.session_state:
        st.info(f"جاري الرد على: {st.session_state['reply_info']}")
        if st.button("إلغاء الرد"):
            del st.session_state["reply_info"]
            st.rerun()

    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        reply_to = st.session_state.get("reply_info")
        save_message(st.session_state["username"], prompt, reply_to, st.session_state["avatar"])
        if "reply_info" in st.session_state: del st.session_state["reply_info"]
        st.rerun()
