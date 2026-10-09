import streamlit as st
from datetime import datetime
import sqlite3

app = st.title(...)

DATABASE = "bmi.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

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
    conn.close()


def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m * height_m)
    return round(bmi, 2)


def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obesity"


# Replace lines 55-56 with this native Streamlit code:
import streamlit as st

st.title("BMI Health Tracker")
st.write("Welcome to the application!")


import streamlit as st

st.write("Welcome to the application!")

# Create a clean UI section for your calculator instead of a route
st.subheader("BMI Calculator")

with st.form("bmi_calculator_form"):
    weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
    height = st.number_input("Height (m)", min_value=0.5, value=1.75)
    
    # This acts like your "POST" submission button
    submit_button = st.form_submit_button(label="Calculate BMI")

if submit_button:
    # This logic runs immediately when the button is clicked
    bmi = weight / (height ** 2)
    st.success(f"Your calculated BMI is: {bmi:.2f}")


    if request.method == "POST":

        name = request.form["name"]
        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])

        if height <= 0 or weight <= 0:
            return render_template(
                "calculator.html",
                error="Height and weight must be greater than zero."
            )

        bmi = calculate_bmi(weight, height)
        category = get_category(bmi)

        conn = get_db()

        conn.execute("""
            INSERT INTO health_records
            (name, age, gender, height, weight, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            age,
            gender,
            height,
            weight,
            bmi,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        conn.commit()
        conn.close()

        result = {
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "category": category
        }

    return render_template(
        "calculator.html",
        result=result
    )


@app.route("/history")
def history():

    conn = get_db()

    records = conn.execute("""
        SELECT * FROM health_records
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )


@app.route("/delete/<int:record_id>")
def delete(record_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM health_records WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
