import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# --- إعداد قاعدة البيانات باسم جديد لتجنب الأخطاء ---
DB_FILE = "chat_final_v2.db" 

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # التأكد من وجود كل الأعمدة المطلوبة
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
              (user, content, timestamp, color, reply_to, avatar))
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

# ستايل الخلفية والردود
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

PASSWORD = "555" 

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("كلمة سر المنظمه")
    pwd = st.text_input("كلمة السر:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("كلمة السر خطأ!")
else:
    # إعدادات الاسم والأفاتار
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

    st.title(" قروب المنظمه السريه")
    
    # القائمة الجانبية
    st.sidebar.markdown(f"### مرحباً {st.session_state['avatar']}\n## {st.session_state['username']}")
    if st.sidebar.button("🗑️ مسح المحادثة بالكامل"):
        conn = get_connection()
        conn.cursor().execute("DELETE FROM messages")
        conn.commit()
        st.rerun()

    # عرض الرسائل
    messages = get_messages()
    for m_user, m_content, m_time, m_color, m_reply, m_avatar in messages:
        # تحديد جهة الرسالة (يمين إذا كانت لي، يسار إذا لغيري)
        is_me = m_user == st.session_state["username"]
        with st.chat_message("user" if is_me else "assistant", avatar=m_avatar):
            if m_reply:
                st.markdown(f"<div class='reply-box'><b>↩️ رد على:</b><br>{m_reply}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<span style='color:{m_color}; font-weight:bold;'>{m_user}</span> <small style='color:gray;'>{m_time}</small>", unsafe_allow_html=True)
            st.write(m_content)
            
            # زر الرد
            if st.button("رد", key=f"r_{m_time}_{m_user}"):
                st.session_state["reply_to"] = f"{m_user}: {m_content[:30]}..."
                st.rerun()

    # شريط الرد النشط
    if "reply_to" in st.session_state:
        st.warning(f"تكتب رداً على: {st.session_state['reply_to']}")
        if st.button("إلغاء الرد"):
            del st.session_state["reply_to"]
            st.rerun()

    # إدخال الرسالة
    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        reply = st.session_state.get("reply_to")
        save_message(st.session_state["username"], prompt, reply, st.session_state["avatar"])
        if "reply_to" in st.session_state: del st.session_state["reply_to"]
        st.rerun()
