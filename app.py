import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import os

# --- إعداد قاعدة البيانات في مسار مسموح به ---
DB_FILE = "chat_database.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, color TEXT)''')
    conn.commit()
    conn.close()

# تشغيل تهيئة قاعدة البيانات
init_db()

# وظيفة لتوليد لون ثابت لكل مستخدم
def get_user_color(username):
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def save_message(user, content):
    timestamp = datetime.now().strftime("%I:%M %p")
    color = get_user_color(user)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user, content, timestamp, color) VALUES (?, ?, ?, ?)", 
              (user, content, timestamp, color))
    conn.commit()
    conn.close()

def get_messages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user, content, timestamp, color FROM messages ORDER BY rowid ASC")
    data = c.fetchall()
    conn.close()
    return data

# --- واجهة التطبيق ---
st.set_page_config(page_title="ديوانية الشلة", page_icon="💬")

PASSWORD = "123" 

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔑 دخول آمن")
    pwd = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("الكلمة خطأ!")
else:
    if "username" not in st.session_state:
        st.title("👤 من أنت؟")
        user_input = st.text_input("اكتب اسمك المستعار:")
        if st.button("دخول للدردشة"):
            if user_input:
                st.session_state["username"] = user_input
                st.rerun()
        st.stop()

    st.title("💬 دردشة الشلة المستمرة")
    st.sidebar.write(f"المستخدم: **{st.session_state['username']}**")
    
    # عرض الرسائل القديمة والجديدة
    all_messages = get_messages()
    for msg_user, msg_content, msg_time, msg_color in all_messages:
        with st.chat_message("user" if msg_user == st.session_state["username"] else "assistant"):
            st.markdown(f"<span style='color:{msg_color}; font-weight:bold;'>{msg_user}</span> <small style='color:gray;'>({msg_time})</small>", unsafe_allow_html=True)
            st.write(msg_content)

    # إرسال رسالة
    if prompt := st.chat_input("اكتب شيئاً..."):
        save_message(st.session_state["username"], prompt)
        st.rerun()

    # ميزة مسح السجل (متاحة للجميع من القائمة الجانبية)
    st.sidebar.divider()
    if st.sidebar.button("🗑️ مسح السجل للكل"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        st.success("تم مسح السجل بنجاح!")
        st.rerun()    
