from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "genz_secret_key"

DB_PATH = "database/patients.db"

# ---------- DATABASE ----------
def init_db():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        gender TEXT,
        disease TEXT,
        contact TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- AUTH PAGE ----------
@app.route("/", methods=["GET","POST"])
def auth():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/dashboard")

    return render_template("auth.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html", total=total)

# ---------- ADD ----------
@app.route("/add", methods=["GET","POST"])
def add_patient():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        data = (
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["disease"],
            request.form["contact"]
        )

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO patients(name,age,gender,disease,contact) VALUES (?,?,?,?,?)",
            data
        )

        conn.commit()
        conn.close()

        return redirect("/view")

    return render_template("add_patient.html")

# ---------- VIEW + SEARCH ----------
@app.route("/view")
def view_patients():

    if "user" not in session:
        return redirect("/")

    search = request.args.get("search","")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE name LIKE ?",
        ('%'+search+'%',)
    )

    patients = cursor.fetchall()
    conn.close()

    return render_template("view_patients.html", patients=patients)

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete_patient(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/view")

# ---------- EDIT ----------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_patient(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
        UPDATE patients
        SET name=?, age=?, gender=?, disease=?, contact=?
        WHERE id=?
        """,(
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["disease"],
            request.form["contact"],
            id
        ))

        conn.commit()
        conn.close()
        return redirect("/view")

    cursor.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cursor.fetchone()
    conn.close()

    return render_template("edit_patient.html", patient=patient)


if __name__ == "__main__":
    app.run(debug=True)