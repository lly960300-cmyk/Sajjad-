import streamlit as st
from datetime import datetime
import hashlib

# --- إعداد الصفحة ---
st.set_page_config(page_title="مجلسنا الملون", page_icon="🎨")

# --- دالة لتوليد الألوان ---
def get_user_color(username):
    hash_object = hashlib.md5(username.encode())
    return f"#{hash_object.hexdigest()[:6]}"

# --- إدارة الرسائل (باستخدام ذاكرة الموقع) ---
if "messages_list" not in st.session_state:
    st.session_state.messages_list = []

# كلمة المرور
PASSWORD = "123"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- شاشة الدخول ---
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
    # --- شاشة اختيار الاسم ---
    if "username" not in st.session_state:
        st.title("💬 اختر اسمك")
        user_input = st.text_input("الاسم المستعار:")
        if st.button("بدء"):
            if user_input:
                st.session_state["username"] = user_input
                st.rerun()
        st.stop()

    # --- واجهة الدردشة ---
    st.title("💬 غرفة المحادثة")
    st.sidebar.markdown(f"👤 المستخدم: **{st.session_state['username']}**")

    # عرض الرسائل
    for msg in st.session_state.messages_list:
        with st.chat_message("user" if msg["user"] == st.session_state["username"] else "assistant"):
            st.markdown(
                f"<span style='color:{msg['color']}; font-weight:bold;'>{msg['user']}</span> "
                f"<small style='color:gray; margin-left:10px;'>{msg['time']}</small>", 
                unsafe_allow_html=True
            )
            st.write(msg["content"])

    # إرسال رسالة جديدة
    if prompt := st.chat_input("اكتب رسالتك..."):
        new_msg = {
            "user": st.session_state["username"],
            "content": prompt,
            "time": datetime.now().strftime("%I:%M %p"),
            "color": get_user_color(st.session_state["username"])
        }
        st.session_state.messages_list.append(new_msg)
        st.rerun()

    # زر المسح
    if st.sidebar.button("🗑️ تصفية الشاشة"):
        st.session_state.messages_list = []
        st.rerun()
