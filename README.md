import streamlit as st
import sqlite3
from datetime import datetime

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('chat_db.db', check_same_thread=False)
c = conn.cursor()

# إنشاء الجدول إذا لم يكن موجوداً
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (user TEXT, content TEXT, timestamp TEXT)''')
conn.commit()

def save_message(user, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (user, content, timestamp) VALUES (?, ?, ?)", 
              (user, content, timestamp))
    conn.commit()

def get_messages():
    c.execute("SELECT user, content FROM messages ORDER BY timestamp ASC")
    return c.fetchall()

# --- واجهة التطبيق ---
st.set_page_config(page_title="مجلسنا الخاص", page_icon="🔒")

# كلمة مرور الدخول
PASSWORD = "123" 

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔑 دخول آمن")
    pwd = st.text_input("أدخل كلمة المرور الخاصة بالشلة:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("الكلمة غلط يا صاحبي!")
else:
    st.title("💬 غرفة محادثة الأصدقاء")
    
    # اختيار اسم المستخدم
    if "username" not in st.session_state:
        st.session_state["username"] = st.text_input("أدخل اسمك المستعار:", "مجهول")
    
    st.write(f"مرحباً بك يا **{st.session_state['username']}**")
    st.divider()

    # عرض الرسائل من قاعدة البيانات
    all_messages = get_messages()
    for msg_user, msg_content in all_messages:
        with st.chat_message("user" if msg_user == st.session_state["username"] else "assistant"):
            st.write(f"**{msg_user}**: {msg_content}")

    # إرسال رسالة جديدة
    if prompt := st.chat_input("اكتب شيئاً..."):
        save_message(st.session_state["username"], prompt)
        st.rerun() # لإظهار الرسالة فوراً

    # زر لمسح المحادثات (للمسؤول فقط مثلاً)
    if st.sidebar.button("مسح جميع الرسائل"):
        c.execute("DELETE FROM messages")
        conn.commit()
        st.rerun()
