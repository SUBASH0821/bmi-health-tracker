import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="BMI Health Tracker",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATABASE = Path(__file__).resolve().parent / "bmi.db"

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f9ff 0%, #eefaf5 100%);
    }
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #123b50;
        margin-bottom: 0;
    }
    .subtitle {
        color: #587080;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e2ecef;
        box-shadow: 0 4px 15px rgba(20, 60, 80, 0.06);
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e0ecea;
        border-radius: 12px;
        padding: 15px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.85);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2ecef;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
def get_db():
    return sqlite3.connect(str(DATABASE), timeout=10)


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.commit()


def save_record(name, age, gender, height, weight, bmi, category, record_date):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO health_records
            (name, age, gender, height, weight, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, age, gender, height, weight,
            bmi, category, record_date
        ))
        conn.commit()


def load_records():
    with get_db() as conn:
        return pd.read_sql_query(
            "SELECT * FROM health_records ORDER BY date DESC, id DESC",
            conn
        )


def delete_record(record_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM health_records WHERE id = ?",
            (int(record_id),)
        )
        conn.commit()


init_db()

# --------------------------------------------------
# BMI LOGIC
# --------------------------------------------------
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def get_category(bmi, age):
    # Adult BMI categories are intended for ages 20 and above.
    if age < 20:
        return (
            "Requires age-specific assessment",
            "BMI for children and teenagers must be interpreted "
            "using age- and sex-specific growth charts."
        )

    if bmi < 18.5:
        return (
            "Underweight",
            "Consider discussing nutrition and healthy weight "
            "goals with a healthcare professional."
        )
    elif bmi < 25:
        return (
            "Healthy weight range",
            "Maintain balanced nutrition, regular physical activity, "
            "adequate sleep, and routine health checkups."
        )
    elif bmi < 30:
        return (
            "Overweight",
            "Consider sustainable eating habits and regular physical "
            "activity. A BMI result alone does not diagnose a condition."
        )
    else:
        return (
            "Obesity range",
            "Consider discussing your overall health and appropriate "
            "next steps with a qualified healthcare professional."
        )


# --------------------------------------------------
# HEADER
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 💚 BMI Health Tracker")
    st.caption("Your personal wellness dashboard")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📝 New Assessment",
            "📊 Health History",
            "ℹ️ About BMI",
        ],
    )

    st.divider()
    st.caption("Track your measurements and wellness trends.")
    st.caption("BMI is a screening measure, not a diagnosis.")

st.markdown(
    '<p class="main-title">💚 BMI Health Tracker</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">Understand your measurements. '
    'Track your progress. Build healthier habits.</p>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if page == "🏠 Dashboard":
    records = load_records()

    st.subheader("Welcome to your health dashboard")
    st.write(
        "Calculate your Body Mass Index (BMI), save your "
        "measurements, and monitor changes over time."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("📋 Total records", len(records))

    if not records.empty:
        latest = records.iloc[0]
        col2.metric("⚖️ Latest BMI", f"{latest['bmi']:.1f}")
        col3.metric("📅 Latest record", str(latest["date"]))
    else:
        col2.metric("⚖️ Latest BMI", "—")
        col3.metric("📅 Latest record", "—")

    st.divider()
    st.subheader("Quick start")

    left, right = st.columns(2)

    with left:
        st.markdown("### 🧮 Calculate your BMI")
        st.write("Enter your height and weight to get started.")
        if st.button("Start assessment", use_container_width=True):
            st.session_state["selected_page"] = "📝 New Assessment"
            st.rerun()

    with right:
        st.markdown("### 📈 View your progress")
        st.write("Review your saved measurements and BMI trends.")
        if st.button("View health history", use_container_width=True):
            st.session_state["selected_page"] = "📊 Health History"
            st.rerun()

    # Honor navigation from dashboard buttons.
    if "selected_page" in st.session_state:
        st.session_state.pop("selected_page")

    if not records.empty:
        st.divider()
        st.subheader("Recent assessments")
        display = records.head(5)[
            ["name", "age", "weight", "height", "bmi", "category", "date"]
        ].copy()
        display.columns = [
            "Name", "Age", "Weight (kg)", "Height (cm)",
            "BMI", "Category", "Date"
        ]
        st.dataframe(display, use_container_width=True, hide_index=True)

# --------------------------------------------------
# NEW ASSESSMENT
# --------------------------------------------------
elif page == "📝 New Assessment":
    st.subheader("📝 New BMI assessment")
    st.write("Complete the form below to calculate and save a record.")

    with st.form("bmi_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full name", max_chars=100)
            age = st.number_input(
                "Age (years)", min_value=2, max_value=120, value=25
            )
            gender = st.selectbox(
                "Gender",
                ["Prefer not to say", "Female", "Male", "Other"]
            )

        with col2:
            height = st.number_input(
                "Height (cm)",
                min_value=50.0,
                max_value=250.0,
                value=170.0,
                step=0.5,
            )
            weight = st.number_input(
                "Weight (kg)",
                min_value=10.0,
                max_value=350.0,
                value=65.0,
                step=0.5,
            )
            record_date = st.date_input("Assessment date", value=date.today())

        submitted = st.form_submit_button(
            "Calculate and save BMI",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            bmi = calculate_bmi(weight, height)
            category, guidance = get_category(bmi, int(age))

            save_record(
                name.strip(),
                int(age),
                gender,
                float(height),
                float(weight),
                round(bmi, 2),
                category,
                record_date.isoformat(),
            )

            st.session_state["last_bmi"] = round(bmi, 2)
            st.session_state["last_category"] = category
            st.session_state["last_guidance"] = guidance
            st.session_state["last_age"] = int(age)

            st.success("Your assessment has been saved successfully!")

    if "last_bmi" in st.session_state:
        bmi = st.session_state["last_bmi"]
        category = st.session_state["last_category"]
        guidance = st.session_state["last_guidance"]
        assessed_age = st.session_state["last_age"]

        st.divider()
        st.subheader("Your BMI result")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric("Body Mass Index", f"{bmi:.1f}")
            st.caption("BMI = weight (kg) ÷ height (m)²")

        with col2:
            st.markdown(f"### {category}")
            st.write(guidance)

        if assessed_age < 20:
            st.info(
                "Adult BMI categories should not be applied to people "
                "under 20. A pediatric BMI-for-age assessment is needed."
            )
        else:
            st.caption(
                "Adult screening ranges: below 18.5 (underweight), "
                "18.5–24.9 (healthy weight range), 25–29.9 (overweight), "
                "30 and above (obesity range)."
            )

        st.warning(
            "BMI is a screening tool. It does not directly measure body "
            "fat or distinguish muscle from fat. Interpret results in "
            "the context of your overall health."
        )

# --------------------------------------------------
# HEALTH HISTORY
# --------------------------------------------------
elif page == "📊 Health History":
    st.subheader("📊 Health history")

    records = load_records()

    if records.empty:
        st.info("No saved records yet. Create your first assessment.")
    else:
        names = sorted(records["name"].dropna().unique().tolist())
        selected_name = st.selectbox("Filter by person", ["All"] + names)

        filtered = records.copy()
        if selected_name != "All":
            filtered = filtered[filtered["name"] == selected_name]

        st.metric("Records shown", len(filtered))

        chart_data = filtered.copy()
        chart_data["date"] = pd.to_datetime(
            chart_data["date"], errors="coerce"
        )
        chart_data = chart_data.dropna(subset=["date"])
        chart_data = chart_data.sort_values("date")

        if not chart_data.empty:
            st.markdown("### BMI trend")
            st.line_chart(
                chart_data.set_index("date")[["bmi"]],
                y="bmi",
            )

            st.markdown("### Weight trend")
            st.line_chart(
                chart_data.set_index("date")[["weight"]],
                y="weight",
            )

        st.markdown("### Saved records")
        table = filtered[
            ["id", "name", "age", "gender", "height",
             "weight", "bmi", "category", "date"]
        ].copy()

        table.columns = [
            "ID", "Name", "Age", "Gender", "Height (cm)",
            "Weight (kg)", "BMI", "Category", "Date"
        ]

        st.dataframe(table, use_container_width=True, hide_index=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download records as CSV",
            data=csv,
            file_name="bmi_health_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()
        st.markdown("### Delete a record")

        record_ids = filtered["id"].astype(int).tolist()

        selected_id = st.selectbox(
            "Choose record ID",
            record_ids,
            format_func=lambda rid: (
                f"ID {rid} — "
                f"{filtered.loc[filtered['id'] == rid, 'name'].iloc[0]} "
                f"({filtered.loc[filtered['id'] == rid, 'date'].iloc[0]})"
            ),
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to permanently delete this record."
        )

        if st.button("Delete selected record", type="secondary"):
            if confirm_delete:
                delete_record(selected_id)
                st.success("Record deleted.")
                st.rerun()
            else:
                st.warning("Please confirm before deleting.")

# --------------------------------------------------
# ABOUT BMI
# --------------------------------------------------
elif page == "ℹ️ About BMI":
    st.subheader("ℹ️ About Body Mass Index")

    st.write(
        "Body Mass Index (BMI) is calculated using weight and height. "
        "It is commonly used as an initial screening measure for adults."
    )

    st.latex(r"\text{BMI} = \frac{\text{Weight (kg)}}"
             r"{\text{Height (m)}^2}")

    st.markdown("### Adult BMI screening categories")

    category_data = pd.DataFrame({
        "BMI range": [
            "Below 18.5",
            "18.5 to below 25",
            "25 to below 30",
            "30 and above",
        ],
        "Category": [
            "Underweight",
            "Healthy weight range",
            "Overweight",
            "Obesity range",
        ],
    })

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "These adult ranges are not intended for children and teenagers. "
        "For people under 20, BMI is interpreted using age- and sex-specific "
        "growth charts. BMI also has limitations for athletes, pregnancy, "
        "older adults, and some other groups."
    )

    st.markdown("### Healthy habits")
    st.markdown("""
    - Eat a balanced and varied diet.
    - Stay physically active according to your abilities.
    - Aim for consistent, adequate sleep.
    - Discuss health concerns and weight goals with a qualified clinician.
    """)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "BMI Health Tracker • For educational and wellness tracking purposes. "
    "Not a substitute for professional medical advice."
)
