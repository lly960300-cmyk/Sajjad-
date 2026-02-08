import streamlit as st
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# --- إعدادات الصفحة ---
st.set_page_config(page_title="تطبيقي الخاص", page_icon="💬")

# --- قاعدة البيانات ---
DB_FILE = "chat_v9_pro.db"
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user TEXT, content TEXT, timestamp TEXT, avatar TEXT)''')
    conn.commit()
    conn.close()

init_db()

# دالة تحويل الصورة
def img_to_bytes(img_file):
    if img_file:
        img = Image.open(img_file).convert("RGB")
        img.thumbnail((120, 120))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    return None

# --- نظام الدخول ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 تسجيل الدخول")
    if st.text_input("كلمة السر:", type="password") == "123":
        if st.button("دخول"):
            st.session_state.auth = True
            st.rerun()
else:
    # إعدادات المستخدم الأولية
    if "user_name" not in st.session_state:
        st.title("👤 إعداد ملفك الشخصي لأول مرة")
        name = st.text_input("اكتب اسمك الشخصي:")
        avatar_file = st.file_uploader("اختر صورتك الشخصية 🖼️", type=['png', 'jpg', 'jpeg'])
        if st.button("حفظ والدخول للدردشة"):
            if name:
                st.session_state.user_name = name
                st.session_state.my_avatar = img_to_bytes(avatar_file) if avatar_file else ""
                st.rerun()
        st.stop()

    # --- القائمة الجانبية (تعديل الملف الشخصي + الخلفية) ---
    st.sidebar.title("⚙️ الإعدادات والملف الشخصي")
    
    # قسم تعديل الملف الشخصي
    with st.sidebar.expander("📝 تعديل اسمك وصورتك"):
        new_name = st.text_input("تغيير الاسم:", value=st.session_state.user_name)
        new_avatar_file = st.file_uploader("تغيير الصورة الشخصية:", type=['png', 'jpg', 'jpeg'], key="navatar")
        if st.button("تحديث الملف الشخصي"):
            st.session_state.user_name = new_name
            if new_avatar_file:
                st.session_state.my_avatar = img_to_bytes(new_avatar_file)
            st.success("تم التحديث!")
            st.rerun()

    # قسم تغيير الخلفية
    bg_file = st.sidebar.file_uploader("🖼️ تغيير خلفية الدردشة", type=['png', 'jpg', 'jpeg'], key="nbg")
    if bg_file:
        bg_bytes = base64.b64encode(bg_file.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: url("data:image/png;base64,{bg_bytes}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>.stApp { background-color: #e5ddd5; }</style>""", unsafe_allow_html=True)

    # --- واجهة الدردشة ---
    st.title("🔥 مجلسنا الخاص") 

    # تنسيق الفقاعات (CSS)        
