import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import time

# --- إعداد قاعدة البيانات ---
DB_FILE = "chat_pro_final.db" 

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, color TEXT, reply_to TEXT, avatar TEXT, msg_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_user_color(username):
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def save_message(user, content, reply_to=None, avatar="👤"):
    timestamp = datetime.now().strftime("%I:%M %p")
    msg_id = str(time.time()) # معرف فريد لكل رسالة لمنع تكرار المفاتيح
    color = get_user_color(user)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user, content, timestamp, color, reply_to, avatar, msg_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (user, content, timestamp, color, reply_to, avatar, msg_id))
    conn.commit()
    conn.close()

def get_messages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, color, reply_to, avatar, msg_id FROM messages ORDER BY rowid ASC")
    data = c.fetchall()
    conn.close()
    return data

# --- تصميم الواجهة ---
st.set_page_config(page_title="ديوانية الشلة VIP", page_icon="🔥")

st.markdown('''
<style>
[data-testid="stAppViewContainer"] {
    background-color: #dfd7d0;
    background-image: url("https://www.transparenttextures.com/patterns/gray-floral.png");
}
.reply-box {
    background-color: rgba(0,0,0,0.1);
    border-right: 5px solid #25D366;
    padding: 8px;
    margin-bottom: 5px;
    border-radius: 5px;
    font-size: 0.85em;
    direction: rtl;
}
</style>
''', unsafe_allow_html=True)

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
            st.error("كلمة السر خطأ!")
else:
    if "username" not in st.session_state:
        st.title("⚙️ إعداداتك")
        u = st.text_input("اسمك المستعار:")
        a = st.selectbox("اختر صورتك الشخصية:", ["👤", "😎", "🥷", "🦁", "🤖", "👻", "🦄", "👑"])
        if st.button("حفظ ودخول"):
            if u:
                st.session_state["username"] = u
                st.session_state["avatar"] = a
                st.rerun()
        st.stop()

    st.title("المنظمه")
    
    # القائمة الجانبية
    st.sidebar.markdown(f"### مرحباً {st.session_state['avatar']}\n## {st.session_state['username']}")
    if st.sidebar.button("🗑️ مسح المحادثة بالكامل"):
        conn = get_connection()
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        st.rerun()

    # عرض الرسائل
    messages = get_messages()
    for m_user, m_content, m_time, m_color, m_reply, m_avatar, m_id in messages:
        is_me = m_user == st.session_state["username"]
        with st.chat_message("user" if is_me else "assistant", avatar=m_avatar):
            if m_reply:
                st.markdown(f"<div class='reply-box'><b>↩️ رد على:</b><br>{m_reply}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<span style='color:{m_color}; font-weight:bold;'>{m_user}</span> <small style='color:gray;'>{m_time}</small>", unsafe_allow_html=True)
            st.write(m_content)
            
            # تم إضافة m_id هنا لضمان عدم تكرار المفتاح
            if st.button("رد", key=f"reply_{m_id}"):
                st.session_state["reply_to_info"] = f"{m_user}: {m_content[:30]}..."
                st.rerun()

    if "reply_to_info" in st.session_state:
        st.warning(f"تكتب رداً على: {st.session_state['reply_to_info']}")
        if st.button("إلغاء الرد"):
            del st.session_state["reply_to_info"]
            st.rerun()

    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        reply = st.session_state.get("reply_to_info")
        save_message(st.session_state["username"], prompt, reply, st.session_state["avatar"])
        if "reply_to_info" in st.session_state: del st.session_state["reply_to_info"]
        st.rerun()
