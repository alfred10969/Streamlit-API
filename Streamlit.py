import streamlit as st
import pandas as pd
import datetime
import time
import hashlib

if 'profile' not in st.session_state:
    st.session_state.profile = {
        'name': '',
        'age': 25,
        'weight': None,
        'height': None,
        'goal': 'Select Goal',
        'target_cal': 0, 
        'target_p': 0, 
        'target_c': 0, 
        'target_f': 0
    }

if 'consumed' not in st.session_state:
    st.session_state.consumed = {
        'cal': 0, 
        'p': 0, 
        'c': 0, 
        'f': 0
    }

if 'food_log' not in st.session_state:
    st.session_state.food_log = []

st.set_page_config(page_title="TrackCross", page_icon="🏋️", layout="wide")

def dashboard_page():
    display_name = st.session_state.profile['name'] if st.session_state.profile['name'] else 'User'
    st.title(f"Hello, {display_name}!")
    st.header("Today's Macro Dashboard")
    
    cal_pct = min(st.session_state.consumed['cal'] / st.session_state.profile['target_cal'], 1.0) if st.session_state.profile['target_cal'] > 0 else 0.0
    p_pct = min(st.session_state.consumed['p'] / st.session_state.profile['target_p'], 1.0) if st.session_state.profile['target_p'] > 0 else 0.0
    c_pct = min(st.session_state.consumed['c'] / st.session_state.profile['target_c'], 1.0) if st.session_state.profile['target_c'] > 0 else 0.0
    f_pct = min(st.session_state.consumed['f'] / st.session_state.profile['target_f'], 1.0) if st.session_state.profile['target_f'] > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Calories", f"{int(st.session_state.consumed['cal'])} / {st.session_state.profile['target_cal']} kcal")
        st.progress(cal_pct)
    with col2:
        st.metric("Protein", f"{int(st.session_state.consumed['p'])} / {st.session_state.profile['target_p']} g")
        st.progress(p_pct)
    with col3:
        st.metric("Carbs", f"{int(st.session_state.consumed['c'])} / {st.session_state.profile['target_c']} g")
        st.progress(c_pct)
    with col4:
        st.metric("Fats", f"{int(st.session_state.consumed['f'])} / {st.session_state.profile['target_f']} g")
        st.progress(f_pct)

    st.divider()
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Quick Add Macros")
        with st.popover("➕ Add Custom Meal"):
            meal_name = st.text_input("Meal Name")
            add_cal = st.number_input("Calories", min_value=0, step=50, value=None)
            add_p = st.number_input("Protein (g)", min_value=0, step=5, value=None)
            add_c = st.number_input("Carbs (g)", min_value=0, step=5, value=None)
            add_f = st.number_input("Fats (g)", min_value=0, step=5, value=None)
            
            if st.button("Log Custom Meal"):
                c_cal = add_cal or 0
                c_p = add_p or 0
                c_c = add_c or 0
                c_f = add_f or 0

                st.session_state.consumed['cal'] += c_cal
                st.session_state.consumed['p'] += c_p
                st.session_state.consumed['c'] += c_c
                st.session_state.consumed['f'] += c_f
                st.session_state.food_log.append({
                    "Time": datetime.datetime.now().strftime("%H:%M"), 
                    "Food": meal_name, 
                    "Cals": c_cal,
                    "Protein (g)": c_p,
                    "Carbs (g)": c_c,
                    "Fats (g)": c_f
                })
                st.toast(f"Logged {meal_name} successfully!", icon="✅")
                st.rerun()
                
    with col_b:
        with st.expander("View Today's Food Log"):
            if not st.session_state.food_log:
                st.write("No food logged yet today.")
            else:
                df_log = pd.DataFrame(st.session_state.food_log)
                df_log.index = df_log.index + 1
                st.dataframe(df_log, use_container_width=True)

def mock_macro_analysis(food_name, grams):
    db = {
        "protein powder": {"cal": 375, "p": 75.0, "c": 10.0, "f": 3.0},
        "chicken": {"cal": 165, "p": 31.0, "c": 0.0, "f": 3.6},
        "rice": {"cal": 130, "p": 2.7, "c": 28.0, "f": 0.3},
        "egg": {"cal": 155, "p": 13.0, "c": 1.1, "f": 11.0},
        "beef": {"cal": 250, "p": 26.0, "c": 0.0, "f": 15.0},
        "apple": {"cal": 52, "p": 0.3, "c": 14.0, "f": 0.2},
        "banana": {"cal": 89, "p": 1.1, "c": 23.0, "f": 0.3},
        "oats": {"cal": 389, "p": 16.9, "c": 66.0, "f": 6.9}
    }
    
    query = food_name.lower().strip()
    matched_base = None
    
    for key, val in db.items():
        if key in query:
            matched_base = val
            break
            
    if not matched_base:
        h = int(hashlib.md5(query.encode()).hexdigest(), 16)
        matched_base = {
            'cal': (h % 300) + 50,
            'p': (h % 25) + 1,
            'c': ((h // 25) % 40) + 1,
            'f': ((h // 1000) % 15) + 1
        }
        
    multiplier = grams / 100.0
    return {
        'cal': int(matched_base['cal'] * multiplier),
        'p': round(matched_base['p'] * multiplier, 1),
        'c': round(matched_base['c'] * multiplier, 1),
        'f': round(matched_base['f'] * multiplier, 1)
    }

def food_log_page():
    st.title("Auto-Macro Food Logger")
    st.write("Search our food database or upload a picture of your meal to automatically calculate macros! (Simulated)")
    
    tab1, tab2 = st.tabs(["🔍 Search Database", "📸 Upload/Take Photo"])
    
    with tab1:
        st.subheader("Search Food")
        search_query = st.text_input("What did you eat?", placeholder="e.g. protein powder")
        grams_input = st.number_input("How many grams did you consume?", min_value=1, value=100, step=10)
        
        if st.button("Search & Log", type="primary"):
            if search_query:
                with st.spinner("Analyzing nutritional database..."):
                    time.sleep(1.5) 
                    macros = mock_macro_analysis(search_query, grams_input)
                    
                    st.session_state.consumed['cal'] += macros['cal']
                    st.session_state.consumed['p'] += macros['p']
                    st.session_state.consumed['c'] += macros['c']
                    st.session_state.consumed['f'] += macros['f']
                    st.session_state.food_log.append({
                        "Time": datetime.datetime.now().strftime("%H:%M"), 
                        "Food": f"{search_query} ({grams_input}g)", 
                        "Cals": macros['cal'],
                        "Protein (g)": macros['p'],
                        "Carbs (g)": macros['c'],
                        "Fats (g)": macros['f']
                    })
                    
                    st.success(f"Found it! Added {grams_input}g of {search_query} to your daily log.")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Calories", f"+{macros['cal']} kcal")
                    c2.metric("Protein", f"+{macros['p']} g")
                    c3.metric("Carbs", f"+{macros['c']} g")
                    c4.metric("Fats", f"+{macros['f']} g")
            else:
                st.error("Please enter a food item to search.")

    with tab2:
        st.subheader("AI Macro Scanner")
        upload_col, camera_col = st.columns(2)
        
        with upload_col:
            uploaded_file = st.file_uploader("Upload an image of your food", type=["jpg", "png", "jpeg"])
        with camera_col:
            camera_image = st.camera_input("Or take a picture of your meal")
            
        if st.button("Analyze Image"):
            if uploaded_file is not None or camera_image is not None:
                with st.spinner("Processing image with AI Scanner..."):
                    time.sleep(2) 
                    detected_food = random.choice(["Oatmeal with Berries", "Cheeseburger", "Salmon and Rice", "Avocado Toast"])
                    macros = mock_macro_analysis(detected_food, 150) 
                    
                    st.session_state.consumed['cal'] += macros['cal']
                    st.session_state.consumed['p'] += macros['p']
                    st.session_state.consumed['c'] += macros['c']
                    st.session_state.consumed['f'] += macros['f']
                    st.session_state.food_log.append({
                        "Time": datetime.datetime.now().strftime("%H:%M"), 
                        "Food": detected_food + " (Scanned)", 
                        "Cals": macros['cal'],
                        "Protein (g)": macros['p'],
                        "Carbs (g)": macros['c'],
                        "Fats (g)": macros['f']
                    })
                    
                    st.success(f"AI Detected: **{detected_food}**! Macros automatically added to your dashboard.")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Calories", f"+{macros['cal']} kcal")
                    c2.metric("Protein", f"+{macros['p']} g")
                    c3.metric("Carbs", f"+{macros['c']} g")
                    c4.metric("Fats", f"+{macros['f']} g")
                    st.balloons()
            else:
                st.warning("Please upload an image or take a picture first.")

def profile_page():
    st.title("Profile & Fitness Plan")
    
    with st.form("profile_form"):
        st.subheader("Personal Credentials")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.profile['name'], placeholder="Enter your name")
            age = st.slider("Age", 16, 100, st.session_state.profile['age'])
            height = st.number_input("Height (cm)", min_value=0.0, value=st.session_state.profile['height'], step=1.0, placeholder="e.g. 175")
        with col2:
            weight = st.number_input("Current Weight (kg)", min_value=0.0, value=st.session_state.profile['weight'], step=0.5, placeholder="e.g. 70.5")
            goal_options = ["Select Goal", "Lose Weight", "Maintain", "Build Muscle"]
            current_goal_idx = goal_options.index(st.session_state.profile['goal']) if st.session_state.profile['goal'] in goal_options else 0
            goal = st.selectbox("Primary Goal", goal_options, index=current_goal_idx)
            
        submitted = st.form_submit_button("Calculate & Save Profile")
        
        if submitted:
            if not name or weight is None or height is None or goal == "Select Goal":
                st.error("Please fill in all fields (Name, Height, Weight, and Goal) to calculate your macros.")
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
                tdee = bmr * 1.55
                
                if goal == "Lose Weight":
                    t_cal = int(tdee - 500)
                elif goal == "Build Muscle":
                    t_cal = int(tdee + 300)
                else:
                    t_cal = int(tdee)
                    
                t_p = int(weight * 2.2)
                t_f = int(weight * 1.0)
                t_c = int((t_cal - (t_p * 4) - (t_f * 9)) / 4)
                
                st.session_state.profile.update({
                    'name': name, 'age': age, 'weight': weight, 'height': height, 'goal': goal,
                    'target_cal': t_cal, 'target_p': t_p, 'target_c': t_c, 'target_f': t_f
                })
                st.success("Profile updated! Your new macro targets have been calculated.")

    st.divider()
    st.subheader("Your Daily Macro Targets")
    
    if st.session_state.profile['target_cal'] > 0:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{st.session_state.profile['target_cal']} kcal")
        c2.metric("Protein", f"{st.session_state.profile['target_p']} g")
        c3.metric("Carbs", f"{st.session_state.profile['target_c']} g")
        c4.metric("Fats", f"{st.session_state.profile['target_f']} g")
    else:
        st.info("👆 Please complete and submit your profile form above to reveal your personalized macro targets.")

def about_page():
    st.title("About TrackCross")
    st.divider()
    
    with st.container(border=True):
        st.subheader("1. What the app does (Use-case)")
        st.markdown("""
        TrackCross is a smart health and nutrition application. It allows users to dynamically track their daily 
        macronutrient intake (calories, protein, carbs, fats) against personalized targets calculated from their biometrics. 
        It features an innovative "Auto-Macro" logger that simulates AI vision and database searches to automatically 
        extract nutritional value from user text input or uploaded food photos.
        """)
        
    with st.container(border=True):
        st.subheader("2. Who the target user is")
        st.markdown("""
        The target users are fitness enthusiasts, health-conscious individuals, and anyone wanting to simplify 
        their diet tracking. By eliminating the need to manually weigh and calculate every ingredient, it serves users 
        who want rapid, on-the-go nutritional insights to meet their weight loss or muscle-building goals.
        """)
        
    with st.container(border=True):
        st.subheader("3. Inputs and Outputs")
        st.markdown("""
        * **Inputs:** The app collects biometric profiling data (Name, Age, Weight, Height, Goals). For daily tracking, it accepts text-based food searches, manual macro entries via a popover, and image uploads (file or camera) for AI scanning.
        * **Outputs:** It auto-calculates BMR/TDEE to output optimal daily macro goals. It generates real-time visual progress bars showing macro compliance, interactive success/toast notifications upon logging food, and a persistent daily food log table. The simulated AI scanner outputs dynamically generated nutritional estimates based on the input.
        """)

pg_dashboard = st.Page(dashboard_page, title="Dashboard & Macros")
pg_food = st.Page(food_log_page, title="Log Food (Auto-Macro)")
pg_profile = st.Page(profile_page, title="Profile Setup", default=True)
pg_about = st.Page(about_page, title="About")

pg = st.navigation({"Navigainztion": [pg_dashboard, pg_food, pg_profile, pg_about]})
pg.run()
