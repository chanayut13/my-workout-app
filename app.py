import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="My Fitness Tracker", page_icon="💪", layout="wide")

# 1. เริ่มต้นระบบเก็บข้อมูล (State Management) เพื่อให้แอปจำค่าที่ปรับเปลี่ยนได้
if 'workout_program' not in st.session_state:
    st.session_state.workout_program = {
        "Push Day": [
            {"name": "Dumbbell Floor Press", "sets": 4, "reps": 12},
            {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": 12},
            {"name": "Lateral Raise", "sets": 4, "reps": 15},
            {"name": "Dumbbell Tricep Kickback", "sets": 3, "reps": 12}
        ],
        "Pull Day": [
            {"name": "Dumbbell Row", "sets": 4, "reps": 12},
            {"name": "Dumbbell Bicep Curl", "sets": 3, "reps": 12},
            {"name": "Hammer Curl", "sets": 3, "reps": 12},
            {"name": "Plank / Bird-Dog", "sets": 3, "reps": 45} # วินาที
        ],
        "Legs & Core": [
            {"name": "Goblet Squat", "sets": 4, "reps": 12},
            {"name": "Dumbbell Romanian Deadlift", "sets": 4, "reps": 12},
            {"name": "Lying Leg Raise", "sets": 3, "reps": 15},
            {"name": "Bicycle Crunch", "sets": 3, "reps": 20}
        ],
        "Rest Day": [
            {"name": "Active Recovery (Stretching เบาๆ)", "sets": 1, "reps": 10},
            {"name": "Vestibular Exercise (ฝึกบาลานซ์/หูชั้นใน)", "sets": 1, "reps": 5}
        ]
    }

if 'history' not in st.session_state:
    st.session_state.history = []

# ส่วนหัวของแอป
st.title("💪 Personal Workout & Nutrition Tracker")
st.subheader(f"ประจำวันที่: {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# แบ่งหน้าจอเป็น 2 ฝั่ง (ฝั่งซ้าย: บันทึกประจำวัน / ฝั่งขวา: ปรับแต่งท่าและเป้าหมาย)
tab1, tab2 = st.tabs(["🏋️ บันทึกการออกกำลังกาย & โปรตีน", "⚙️ ปรับแต่งท่าออกกำลังกาย"])

# ==========================================
# TAB 1: บันทึกการออกกำลังกาย & โปรตีน
# ==========================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("วันนี้คุณจะเล่นส่วนไหน?")
        day_type = st.selectbox("เลือกโปรแกรมของวันนี้:", list(st.session_state.workout_program.keys()))
        
        # เตือนความปลอดภัยก่อนเริ่ม
        st.warning("⚠️ **ก่อนเริ่มเล่น:** อย่าลืมวอร์มอัพด้วยท่า **Cat-Cow Stretch (2-3 นาที)** เพื่อคลายกระดูกสันหลังและเซฟหลังส่วนล่างนะครับ")
        
        st.subheader(f"📋 รายการท่าสำหรับ {day_type}")
        st.caption("ติ๊กถูกเมื่อเล่นครบตามเซ็ตที่กำหนด")
        
        # แสดงรายการท่าตามที่ตั้งค่าไว้
        all_completed = True
        for idx, exercise in enumerate(st.session_state.workout_program[day_type]):
            label = f"**{exercise['name']}** — {exercise['sets']} เซ็ต x {exercise['reps']} ครั้ง"
            checked = st.checkbox(label, key=f"ex_{day_type}_{idx}")
            if not checked:
                all_completed = False
                
        st.markdown("---")
        
        # ปุ่มบันทึกกิจกรรมลงประวัติ
        if st.button("💾 บันทึกกิจกรรมวันนี้ลง Log", type="primary"):
            status_text = "เสร็จสมบูรณ์ทั้งหมด" if all_completed else "เล่นบางส่วน"
            log_entry = {
                "วันที่": datetime.now().strftime('%Y-%m-%d'),
                "โปรแกรม": day_type,
                "สถานะ": status_text
            }
            st.session_state.history.append(log_entry)
            st.success(f"บันทึกข้อมูล {day_type} เรียบร้อยแล้ว!")

    with col2:
        st.header("🥩 แทร็กโปรตีนวันนี้")
        st.caption("เป้าหมายของคุณ: **80 - 110 กรัม / วัน**")
        
        protein_input = st.number_input("เติมปริมาณโปรตีนที่ทานเพิ่ม (กรัม):", min_value=0, max_value=300, value=0, step=5)
        
        if 'today_protein' not in st.session_state:
            st.session_state.today_protein = 0
            
        if st.button("➕ เพิ่มโปรตีน"):
            st.session_state.today_protein += protein_input
            st.experimental_rerun()
            
        if st.button("🔄 รีเซ็ตโปรตีนวันนี้"):
            st.session_state.today_protein = 0
            st.experimental_rerun()
            
        # แสดงผลความคืบหน้าของโปรตีน
        current_p = st.session_state.today_protein
        st.metric(label="โปรตีนที่ได้รับวันนี้", value=f"{current_p} กรัม")
        
        if current_p >= 80 and current_p <= 110:
            st.success("🎉 ยอดเยี่ยม! โปรตีนอยู่ในเกณฑ์เป้าหมายแล้ว")
        elif current_p < 80:
            st.info(f"ขาดอีก {80 - current_p} กรัม จะถึงเกณฑ์ขั้นต่ำ")
        else:
            st.warning("ทานโปรตีนเกินเป้าหมายสูงสุดเล็กน้อย ร่างกายอาจนำไปใช้ไม่หมด")

    # ส่วนแสดงประวัติย้อนหลังล่างสุดของ Tab 1
    st.markdown("---")
    st.subheader("📜 ประวัติการออกกำลังกายย้อนหลัง")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการบันทึกในเซสชั่นนี้")

# ==========================================
# TAB 2: ปรับแต่งท่าออกกำลังกาย (Dynamic Setup)
# ==========================================
with tab2:
    st.header("🛠️ ปรับแต่งตารางและจำนวนครั้งได้ตามใจชอบ")
    st.write("คุณสามารถเปลี่ยนชื่อท่า ปรับเซ็ต/ครั้ง หรือเพิ่มท่าใหม่ในแต่ละวันได้จากส่วนนี้เลยครับ")
    
    edit_day = st.selectbox("เลือกวันมัดกล้ามเนื้อที่ต้องการแก้ไขข้อมูล:", list(st.session_state.workout_program.keys()))
    
    # วนลูปแสดงข้อมูลเดิมเพื่อให้แก้ไขได้
    updated_exercises = []
    
    st.subheader(f"แก้ไขรายการท่าของ {edit_day}")
    for idx, exercise in enumerate(st.session_state.workout_program[edit_day]):
        st.markdown(f"**ท่าที่ {idx + 1}**")
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            new_name = st.text_input("ชื่อท่าออกกำลังกาย", value=exercise['name'], key=f"name_{edit_day}_{idx}")
        with c2:
            new_sets = st.number_input("จำนวนเซ็ต", min_value=1, max_value=10, value=int(exercise['sets']), key=f"sets_{edit_day}_{idx}")
        with c3:
            new_reps = st.number_input("จำนวนครั้ง/วินาที", min_value=1, max_value=100, value=int(exercise['reps']), key=f"reps_{edit_day}_{idx}")
            
        updated_exercises.append({"name": new_name, "sets": new_sets, "reps": new_reps})
        
    # ฟังก์ชันเพิ่มท่าใหม่เข้าไปในลิสต์
    st.markdown("---")
    st.markdown("**➕ เพิ่มท่าใหม่เข้าไปในวันนี้**")
    add_col1, add_col2, add_col3 = st.columns([3, 1, 1])
    with add_col1:
        add_name = st.text_input("ชื่อท่าใหม่ที่ต้องการเพิ่ม:", value="", key=f"add_name_{edit_day}")
    with add_col2:
        add_sets = st.number_input("จำนวนเซ็ตสำหรับท่าใหม่:", min_value=1, max_value=10, value=3, key=f"add_sets_{edit_day}")
    with add_col3:
        add_reps = st.number_input("จำนวนครั้งสำหรับท่าใหม่:", min_value=1, max_value=100, value=12, key=f"add_reps_{edit_day}")
        
    if st.button("➕ เพิ่มท่านี้เข้าไปในตาราง"):
        if add_name:
            updated_exercises.append({"name": add_name, "sets": add_sets, "reps": add_reps})
            st.session_state.workout_program[edit_day] = updated_exercises
            st.success(f"เพิ่มท่า {add_name} สำเร็จ!")
            st.experimental_rerun()
        else:
            st.error("กรุณากรอกชื่อท่าก่อนกดเพิ่มครับ")

    # ปุ่มบันทึกการเปลี่ยนแปลงทั้งหมด
    if st.button("💾 บันทึกการแก้ไขท่าทั้งหมดของวันนี้", type="primary"):
        st.session_state.workout_program[edit_day] = updated_exercises
        st.success(f"อัปเดตระบบตารางท่าของ {edit_day} เรียบร้อยแล้ว! ลองกลับไปดูหน้าแรกได้เลย")