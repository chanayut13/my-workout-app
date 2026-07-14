import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้าจอแอป
st.set_page_config(page_title="Personalized Fitness App V3.1", page_icon="🏋️‍♂️", layout="wide")

# กำหนดชื่อไฟล์ฐานข้อมูลจำลอง
USER_DB = "users_db.csv"
WORKOUT_DB = "workout_db.csv"
PROTEIN_DB = "protein_db.csv"

# ฟังก์ชันจัดการไฟล์ CSV ให้บันทึกและอ่านได้ทันที
def load_db(file_name, columns):
    if os.path.exists(file_name):
        try:
            return pd.read_csv(file_name)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_db(df, file_name):
    df.to_csv(file_name, index=False)

# ระบบจำสถานะการ Login ในเซสชันปัจจุบัน
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_info = {}

# ==========================================
# หน้าจอการยืนยันตัวตน (LOGIN / SIGN UP)
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 เข้าสู่ระบบแอปฟิตเนสส่วนบุคคล")
    auth_tab1, auth_tab2 = st.tabs(["🔒 ล็อกอินเข้าใช้งาน", "📝 สมัครสมาชิกใหม่ (คำนวณเป้าหมายส่วนตัว)"])
    
    with auth_tab1:
        # โหลดฐานข้อมูลใหม่ทุกครั้งที่เปิดหน้านี้ เพื่อให้เจอ User ที่พึ่งสมัคร
        df_users_login = load_db(USER_DB, ["username", "password", "weight", "height", "bmi", "protein_target"])
        
        login_user = st.text_input("ชื่อผู้ใช้งาน (Username):", key="login_u").strip()
        login_pass = st.text_input("รหัสผ่าน (Password):", type="password", key="login_p").strip()
        
        if st.button("เข้าสู่ระบบ", type="primary"):
            # แปลงค่าให้เป็น String ก่อนเทียบ เพื่อป้องกันปัญหาประเภทข้อมูล
            df_users_login["username"] = df_users_login["username"].astype(str)
            df_users_login["password"] = df_users_login["password"].astype(str)
            
            user_check = df_users_login[(df_users_login["username"] == login_user) & (df_users_login["password"] == login_pass)]
            
            if not user_check.empty:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.session_state.user_info = user_check.to_dict('records')[0]
                st.success("เข้าสู่ระบบสำเร็จ!")
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง หรือโปรดลองสมัครสมาชิกใหม่อีกครั้ง")
                
    with auth_tab2:
        st.subheader("สร้างบัญชีผู้ใช้พร้อมคำนวณสุขภาพ")
        new_user = st.text_input("ตั้งชื่อผู้ใช้งาน (ภาษาอังกฤษ):", key="new_u").strip()
        new_pass = st.text_input("ตั้งรหัสผ่าน:", type="password", key="new_p").strip()
        
        col_w, col_h = st.columns(2)
        with col_w:
            weight = st.number_input("น้ำหนักตัว (กิโลกรัม):", min_value=10.0, max_value=200.0, value=65.0, step=0.1)
        with col_h:
            height = st.number_input("ส่วนสูง (เซนติเมตร):", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
            
        if st.button("สมัครสมาชิกและคำนวณผล"):
            df_users_sync = load_db(USER_DB, ["username", "password", "weight", "height", "bmi", "protein_target"])
            
            if new_user in df_users_sync["username"].astype(str).values:
                st.error("❌ ชื่อผู้ใช้งานนี้มีคนใช้แล้ว กรุณาเปลี่ยนชื่อใหม่ครับ")
            elif new_user == "" or new_pass == "":
                st.error("❌ กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน")
            else:
                # 1. คำนวณ BMI
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 2)
                
                # 2. คำนวณโปรตีนที่เหมาะสม (น้ำหนักตัว x 1.6 กรัม)
                protein_target = int(weight * 1.6)
                
                # บันทึกลงระบบทันที
                new_row = pd.DataFrame([{
                    "username": str(new_user), "password": str(new_pass),
                    "weight": weight, "height": height, "bmi": bmi, "protein_target": protein_target
                }])
                df_users_sync = pd.concat([df_users_sync, new_row], ignore_index=True)
                save_db(df_users_sync, USER_DB)
                
                st.balloons() # แสดงเอฟเฟกต์ฉลองการสมัคร
                st.success(f"🎉 สมัครสมาชิกสำเร็จ! ชื่อผู้ใช้ของคุณคือ '{new_user}' (เป้าหมายโปรตีน: {protein_target} กรัม) กรุณาสลับไปที่แท็บ 'ล็อกอินเข้าใช้งาน' ได้เลยครับ")

# ==========================================
# หน้าจอหลักของแอปหลังจาก LOGIN สำเร็จ
# ==========================================
else:
    u_info = st.session_state.user_info
    username = st.session_state.username
    
    # โหดลข้อมูลกิจกรรมล่าสุดของ User
    df_workout = load_db(WORKOUT_DB, ["username", "date", "program", "status"])
    df_protein = load_db(PROTEIN_DB, ["username", "date", "amount"])
    
    bmi_val = u_info["bmi"]
    if bmi_val < 18.5: bmi_status = "น้ำหนักต่ำกว่าเกณฑ์ 🦴"
    elif bmi_val < 23.0: bmi_status = "สมส่วน สุขภาพดี 🟢"
    elif bmi_val < 25.0: bmi_status = "น้ำหนักเกิน 🟡"
    else: bmi_status = "เริ่มอ้วน / อ้วน 🔴"
    
    st.title(f"💪 ยินดีต้อนรับคุณ {username} เข้าสู่ระบบ")
    
    c_bmi, c_prot, c_logout = st.columns([2, 2, 1])
    with c_bmi:
        st.info(f"📊 **ค่า BMI ของคุณ:** {bmi_val} ({bmi_status})")
    with c_prot:
        st.success(f"🥩 **เป้าหมายโปรตีนเฉพาะคุณ:** {u_info['protein_target']} กรัม / วัน")
    with c_logout:
        if st.button("🔒 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏋️ บันทึกกิจกรรมวันนี้", "📊 ดูสรุปประวัติวันต่อวัน"])
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    workout_program = {
        "Push Day": ["Cat-Cow Warmup", "Dumbbell Floor Press", "Dumbbell Shoulder Press", "Lateral Raise", "Tricep Kickback"],
        "Pull Day": ["Cat-Cow Warmup", "Dumbbell Row", "Dumbbell Bicep Curl", "Hammer Curl", "Plank / Bird-Dog"],
        "Legs & Core": ["Cat-Cow Warmup", "Goblet Squat", "Dumbbell Romanian Deadlift", "Lying Leg Raise", "Bicycle Crunch"],
        "Rest Day": ["Stretching เบาๆ", "Vestibular Exercise (ฝึกบาลานซ์หูชั้นใน)"]
    }
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.header("บันทึกการฝึก")
            day_type = st.selectbox("เลือกโปรแกรมวันนี้:", list(workout_program.keys()))
            
            all_done = True
            for idx, ex in enumerate(workout_program[day_type]):
                c = st.checkbox(ex, key=f"ex_{idx}")
                if not c: all_done = False
                
            if st.button("💾 บันทึกกิจกรรม", type="primary"):
                df_workout = df_workout[(df_workout["username"] != username) | (df_workout["date"] != today_str)]
                new_w = pd.DataFrame([{"username": username, "date": today_str, "program": day_type, "status": "เสร็จสมบูรณ์" if all_done else "บางส่วน"}])
                df_workout = pd.concat([df_workout, new_w], ignore_index=True)
                save_db(df_workout, WORKOUT_DB)
                st.success("บันทึกตารางฝึกสำเร็จ!")
                
        with col2:
            st.header("แทร็กสารอาหาร")
            user_p_today = df_protein[(df_protein["username"] == username) & (df_protein["date"] == today_str)]
            current_p = int(user_p_today["amount"].sum()) if not user_p_today.empty else 0
            
            st.metric(label="โปรตีนที่กินแล้ววันนี้", value=f"{current_p} / {u_info['protein_target']} กรัม")
            
            p_add = st.number_input("เพิ่มโปรตีน (กรัม):", min_value=0, max_value=200, step=5)
            if st.button("➕ บันทึกมื้ออาหาร"):
                df_protein = df_protein[(df_protein["username"] != username) | (df_protein["date"] != today_str)]
                new_p = pd.DataFrame([{"username": username, "date": today_str, "amount": current_p + p_add}])
                df_protein = pd.concat([df_protein, new_p], ignore_index=True)
                save_db(df_protein, PROTEIN_DB)
                st.success("อัปเดตปริมาณโปรตีนสำเร็จ!")
                st.rerun()

    with tab2:
        st.header("📊 ประวัติการคำนวณและบันทึกย้อนหลังของคุณ")
        u_workout = df_workout[df_workout["username"] == username]
        u_protein = df_protein[df_protein["username"] == username]
        
        if not u_workout.empty or not u_protein.empty:
            all_dates = pd.concat([u_workout["date"], u_protein["date"]]).unique()
            summary = []
            
            for d in sorted(all_dates, reverse=True):
                w_row = u_workout[u_workout["date"] == d]
                p_row = u_protein[u_protein["date"] == d]
                
                prog = w_row["program"].values[0] if not w_row.empty else "ไม่ได้บันทึก"
                stat = w_row["status"].values[0] if not w_row.empty else "-"
                prot = p_row["amount"].values[0] if not p_row.empty else 0
                
                target = u_info['protein_target']
                if prot >= target:
                    p_eval = f"🟢 ครบเกณฑ์เป้าหมาย ({target}g)"
                else:
                    p_eval = f"🔴 ขาดอีก {target - prot}g"
                    
                summary.append({
                    "วันที่": d, "ตารางที่เล่น": prog, "สถานะเวท": stat, "โปรตีนที่ได้รับ (กรัม)": prot, "สรุปผลโปรตีน": p_eval
                })
            st.dataframe(pd.DataFrame(summary), use_container_width=True)
        else:
            st.info("ยังไม่มีประวัติการบันทึกของคุณในระบบ")
