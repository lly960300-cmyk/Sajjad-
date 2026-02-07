import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('chat_db.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS messages
             (user TEXT, content TEXT, timestamp TEXT, color TEXT)''')
conn.commit()

# وظيفة لتوليد لون ثابت لكل اسم مستخدم
def get_user_color(username):
    # نستخدم "hash" ليكون لكل اسم لون محدد دائماً
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def save_message(user, content):
    timestamp = datetime.now().strftime("%I:%M %p") # الوقت بصيغة (12:30 PM)
    color = get_user_color(user)
    c.execute("INSERT INTO messages (user, content, timestamp, color) VALUES (?, ?, ?, ?)", 
              (user, content, timestamp, color))
    conn.commit()

def get_messages():
    c.execute("SELECT user, content, timestamp, color FROM messages ORDER BY rowid ASC")
    return c.fetchall()

# --- واجهة التطبيق ---
st.set_page_config(page_title="مجلسنا الملون", page_icon="🎨")

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
            st.error("الكلمة غلط!")
else:
    st.title(" المنظمه السريه جدن 🕵 ")
    
    if "username" not in st.session_state:
        user_input = st.text_input("أدخل اسمك المستعار لتبدأ:", "")
        if user_input:
            st.session_state["username"] = user_input
            st.rerun()
        st.stop()
    
    st.sidebar.write(f"أهلاً بك: **{st.session_state['username']}**")
    
    # عرض الرسائل
    all_messages = get_messages()
    for msg_user, msg_content, msg_time, msg_color in all_messages:
        # تنسيق الرسالة بشكل ملون
        with st.chat_message("user" if msg_user == st.session_state["username"] else "assistant"):
            st.markdown(f"<span style='color:{msg_color}; font-weight:bold;'>{msg_user}</span> <small style='color:gray;'>({msg_time})</small>", unsafe_allow_html=True)
            st.write(msg_content)

    # إرسال رسالة
    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        save_message(st.session_state["username"], prompt)
        st.rerun()

    if st.sidebar.button("مسح السجل"):
        c.execute("DELETE FROM messages")
        conn.commit()
        st.rerun()
