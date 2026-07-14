import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าจอแอป
st.set_page_config(page_title="Personalized Fitness App V4 (Google Sheets)", page_icon="🏋️‍♂️", layout="wide")

# 🔌 เชื่อมต่อกับฐานข้อมูล Google Sheets
# หมายเหตุ: แอปจะดึงลิงก์ตารางจากไฟล์ความลับหลังบ้าน (.streamlit/secrets.toml) อัตโนมัติ
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันโหลดข้อมูลจากแท็บต่างๆ ใน Google Sheets
def load_sheet_data(worksheet_name, columns):
    try:
        return conn.read(worksheet=worksheet_name, ttl="0")
    except:
        return pd.DataFrame(columns=columns)

# ระบบจำสถานะการ Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_info = {}

# ตั้งค่าตารางท่าเริ่มต้นในระบบ
if 'workout_program' not in st.session_state:
    st.session_state.workout_program = {
        "Push Day": [
            {"name": "Cat-Cow Warmup", "sets": 1, "reps": 10},
            {"name": "Dumbbell Floor Press", "sets": 4, "reps": 12},
            {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": 12},
            {"name": "Lateral Raise", "sets": 4, "reps": 15},
            {"name": "Tricep Kickback", "sets": 3, "reps": 12}
        ],
        "Pull Day": [
            {"name": "Cat-Cow Warmup", "sets": 1, "reps": 10},
            {"name": "Dumbbell Row", "sets": 4, "reps": 12},
            {"name": "Dumbbell Bicep Curl", "sets": 3, "reps": 12},
            {"name": "Hammer Curl", "sets": 3, "reps": 12},
            {"name": "Plank / Bird-Dog", "sets": 3, "reps": 45}
        ],
        "Legs & Core": [
            {"name": "Cat-Cow Warmup", "sets": 1, "reps": 10},
            {"name": "Goblet Squat", "sets": 4, "reps": 12},
            {"name": "Dumbbell Romanian Deadlift", "sets": 4, "reps": 12},
            {"name": "Lying Leg Raise", "sets": 3, "reps": 15},
            {"name": "Bicycle Crunch", "sets": 3, "reps": 20}
        ],
        "Rest Day": [
            {"name": "Stretching เบาๆ", "sets": 1, "reps": 10},
            {"name": "Vestibular Exercise (ฝึกบาลานซ์หูชั้นใน)", "sets": 1, "reps": 5}
        ]
    }

# ==========================================
# หน้าจอการยืนยันตัวตน (LOGIN / SIGN UP)
# ==========================================
if not st.session_state.logged_in:
    st.title("🔐 เข้าสู่ระบบแอปฟิตเนส (ฐานข้อมูล Google Sheets)")
    auth_tab1, auth_tab2 = st.tabs(["🔒 ล็อกอินเข้าใช้งาน", "📝 สมัครสมาชิกใหม่"])
    
    # โดโหลดข้อมูล User ปัจจุบันจาก Google Sheets
    df_users = load_sheet_data("users", ["username", "password", "weight", "height", "bmi", "protein_target"])
    
    with auth_tab1:
        login_user = st.text_input("ชื่อผู้ใช้งาน (Username):", key="login_u").strip()
        login_pass = st.text_input("รหัสผ่าน (Password):", type="password", key="login_p").strip()
        
        if st.button("เข้าสู่ระบบ", type="primary"):
            if not df_users.empty:
                df_users["username"] = df_users["username"].astype(str)
                df_users["password"] = df_users["password"].astype(str)
                user_check = df_users[(df_users["username"] == login_user) & (df_users["password"] == login_pass)]
                
                if not user_check.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.user_info = user_check.to_dict('records')[0]
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
            else:
                st.error("❌ ยังไม่มีข้อมูลผู้ใช้งานในระบบ กรุณาสมัครสมาชิกก่อนครับ")
                
    with auth_tab2:
        st.subheader("สร้างบัญชีผู้ใช้พร้อมคำนวณสุขภาพ")
        new_user = st.text_input("ตั้งชื่อผู้ใช้งาน (ภาษาอังกฤษ):", key="new_u").strip()
        new_pass = st.text_input("ตั้งรหัสผ่าน:", type="password", key="new_p").strip()
        
        col_w, col_h = st.columns(2)
        with col_w: weight = st.number_input("น้ำหนัก (กก.):", min_value=10.0, value=65.0)
        with col_h: height = st.number_input("ส่วนสูง (ซม.):", min_value=100.0, value=170.0)
            
        if st.button("สมัครสมาชิกและคำนวณผล"):
            if not df_users.empty and new_user in df_users["username"].astype(str).values:
                st.error("❌ ชื่อผู้ใช้งานนี้มีคนใช้แล้ว")
            elif new_user == "" or new_pass == "":
                st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 2)
                protein_target = int(weight * 1.6)
                
                new_row = pd.DataFrame([{
                    "username": str(new_user), "password": str(new_pass),
                    "weight": weight, "height": height, "bmi": bmi, "protein_target": protein_target
                }])
                
                df_users = pd.concat([df_users, new_row], ignore_index=True)
                # อัปเดตกลับไปยัง Google Sheets
                conn.update(worksheet="users", data=df_users)
                st.balloons()
                st.success(f"🎉 สมัครสำเร็จ! เชิญไปที่แท็บ ล็อกอิน ได้เลยครับ")

# ==========================================
# หน้าจอหลักของแอปหลังจาก LOGIN สำเร็จ
# ==========================================
else:
    u_info = st.session_state.user_info
    username = st.session_state.username
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # โหลดประวัติกิจกรรมจาก Google Sheets
    df_workout = load_sheet_data("workout_logs", ["username", "date", "program", "status"])
    df_protein = load_sheet_data("protein_logs", ["username", "date", "amount"])
    
    bmi_val = u_info["bmi"]
    if bmi_val < 18.5: bmi_status = "น้ำหนักต่ำกว่าเกณฑ์ 🦴"
    elif bmi_val < 23.0: bmi_status = "สมส่วน สุขภาพดี 🟢"
    elif bmi_val < 25.0: bmi_status = "น้ำหนักเกิน 🟡"
    else: bmi_status = "เริ่มอ้วน / อ้วน 🔴"
    
    st.title(f"💪 ระบบฟิตเนสออนไลน์ ของคุณ {username}")
    
    c_bmi, c_prot, c_logout = st.columns([2, 2, 1])
    with c_bmi: st.info(f"📊 **BMI:** {bmi_val} ({bmi_status})")
    with c_prot: st.success(f"🥩 **เป้าหมายโปรตีน:** {u_info['protein_target']} กรัม / วัน")
    with c_logout:
        if st.button("🔒 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["🏋️ บันทึกกิจกรรมวันนี้", "📊 ดูสรุปประวัติวันต่อวัน", "⚙️ ปรับแต่งตารางท่า"])
    
    # TAB 1: บันทึกประจำวัน
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.header("บันทึกการฝึก")
            day_type = st.selectbox("เลือกโปรแกรมวันนี้:", list(st.session_state.workout_program.keys()))
            
            all_done = True
            for idx, ex in enumerate(st.session_state.workout_program[day_type]):
                label = f"**{ex['name']}** — {ex['sets']} เซ็ต x {ex['reps']} ครั้ง"
                c = st.checkbox(label, key=f"ex_{day_type}_{idx}")
                if not c: all_done = False
                
            if st.button("💾 บันทึกกิจกรรมลง Google Sheets", type="primary"):
                if not df_workout.empty:
                    df_workout = df_workout[(df_workout["username"] != username) | (df_workout["date"] != today_str)]
                new_w = pd.DataFrame([{"username": username, "date": today_str, "program": day_type, "status": "เสร็จสมบูรณ์" if all_done else "บางส่วน"}])
                df_workout = pd.concat([df_workout, new_w], ignore_index=True)
                
                conn.update(worksheet="workout_logs", data=df_workout)
                st.success("ส่งข้อมูลตารางฝึกเข้า Google Sheets สำเร็จ!")
                
        with col2:
            st.header("แทร็กสารอาหาร")
            current_p = 0
            if not df_protein.empty:
                user_p_today = df_protein[(df_protein["username"] == username) & (df_protein["date"] == today_str)]
                current_p = int(user_p_today["amount"].sum()) if not user_p_today.empty else 0
            
            st.metric(label="โปรตีนสะสมวันนี้", value=f"{current_p} / {u_info['protein_target']} กรัม")
            p_add = st.number_input("เพิ่มโปรตีน (กรัม):", min_value=0, max_value=200, step=5)
            
            if st.button("➕ บันทึกมื้ออาหาร"):
                if not df_protein.empty:
                    df_protein = df_protein[(df_protein["username"] != username) | (df_protein["date"] != today_str)]
                new_p = pd.DataFrame([{"username": username, "date": today_str, "amount": current_p + p_add}])
                df_protein = pd.concat([df_protein, new_p], ignore_index=True)
                
                conn.update(worksheet="protein_logs", data=df_protein)
                st.success("อัปเดตปริมาณโปรตีนสำเร็จ!")
                st.rerun()

    # TAB 2: สรุปผลรายวัน
    with tab2:
        st.header("📊 ประวัติจากฐานข้อมูลกลาง")
        u_workout = df_workout[df_workout["username"] == username] if not df_workout.empty else pd.DataFrame()
        u_protein = df_protein[df_protein["username"] == username] if not df_protein.empty else pd.DataFrame()
        
        if not u_workout.empty or not u_protein.empty:
            all_dates = pd.concat([u_workout["date"] if not u_workout.empty else pd.Series(), 
                                   u_protein["date"] if not u_protein.empty else pd.Series()]).unique()
            summary = []
            for d in sorted(all_dates, reverse=True):
                w_row = u_workout[u_workout["date"] == d] if not u_workout.empty else pd.DataFrame()
                p_row = u_protein[u_protein["date"] == d] if not u_protein.empty else pd.DataFrame()
                
                prog = w_row["program"].values[0] if not w_row.empty else "ไม่ได้บันทึก"
                stat = w_row["status"].values[0] if not w_row.empty else "-"
                prot = p_row["amount"].values[0] if not p_row.empty else 0
                
                target = u_info['protein_target']
                p_eval = f"🟢 ครบเกณฑ์ ({target}g)" if prot >= target else f"🔴 ขาดอีก {target - prot}g"
                summary.append({"วันที่": d, "ตารางที่เล่น": prog, "สถานะเวท": stat, "โปรตีนที่ได้รับ (กรัม)": prot, "สรุปผลโปรตีน": p_eval})
            st.dataframe(pd.DataFrame(summary), use_container_width=True)
        else:
            st.info("ยังไม่มีประวัติการบันทึกของคุณในระบบ")

    # TAB 3: ปรับแต่งตารางท่า
    with tab3:
        st.header("🛠️ ปรับแต่งตารางท่าออกกำลังกาย")
        edit_day = st.selectbox("เลือกวันมัดกล้ามเนื้อ:", list(st.session_state.workout_program.keys()))
        updated_exercises = []
        for idx, exercise in enumerate(st.session_state.workout_program[edit_day]):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1: new_name = st.text_input("ชื่อท่าออกกำลังกาย", value=exercise['name'], key=f"name_{edit_day}_{idx}")
            with c2: new_sets = st.number_input("จำนวนเซ็ต", min_value=1, value=int(exercise['sets']), key=f"sets_{edit_day}_{idx}")
            with c3: new_reps = st.number_input("ครั้ง/วินาที", min_value=1, value=int(exercise['reps']), key=f"reps_{edit_day}_{idx}")
            updated_exercises.append({"name": new_name, "sets": new_sets, "reps": new_reps})
        if st.button("💾 บันทึกการแก้ไขท่าทั้งหมด"):
            st.session_state.workout_program[edit_day] = updated_exercises
            st.success("อัปเดตตารางท่าสำเร็จ!")
