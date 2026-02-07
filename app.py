            import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# --- إعداد قاعدة البيانات ---
# قمنا بتغيير اسم الجدول لتجنب تضارب البيانات القديمة
conn = sqlite3.connect('chat_db.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS messages_v3
             (user TEXT, content TEXT, timestamp TEXT, color TEXT)''')
conn.commit()

# وظيفة لتوليد لون ثابت لكل اسم مستخدم بناءً على الحروف
def get_user_color(username):
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

def save_message(user, content):
    timestamp = datetime.now().strftime("%I:%M %p")
    color = get_user_color(user)
    c.execute("INSERT INTO messages_v3 (user, content, timestamp, color) VALUES (?, ?, ?, ?)", 
              (user, content, timestamp, color))
    conn.commit()

def get_messages():
    c.execute("SELECT user, content, timestamp, color FROM messages_v3 ORDER BY rowid ASC")
    return c.fetchall()

# --- واجهة التطبيق ---
st.set_page_config(page_title="مجلسنا الملون", page_icon="🎨")

# كلمة المرور الخاصة بك
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
    st.title(" المنظمه السريه 🕵 ")
    
    # اختيار اسم المستخدم
    if "username" not in st.session_state:
        st.subheader("أهلاً بك! اختر اسماً مستعاراً للدخول")
        user_input = st.text_input("الاسم:", placeholder="مثلاً: صقر")
        if st.button("بدء الدردشة"):
            if user_input:
                st.session_state["username"] = user_input
                st.rerun()
            else:
                st.warning("رجاءً اكتب اسماً أولاً")
        st.stop()
    
    st.sidebar.markdown(f"### 👤 المستخدم الحالي:\n**{st.session_state['username']}**")
    
    # عرض الرسائل بتنسيق جميل
    all_messages = get_messages()
    for msg_user, msg_content, msg_time, msg_color in all_messages:
        with st.chat_message("user" if msg_user == st.session_state["username"] else "assistant"):
            # عرض الاسم باللون الخاص به والوقت بخط صغير
            st.markdown(f"<span style
