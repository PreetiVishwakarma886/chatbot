# ===============================
# IMPORTS
# ===============================
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ABC\Documents\tesseract.exe"
from PIL import Image
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import sqlite3
from flask import Flask, render_template, request, redirect, session, send_file
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import re
import pyttsx3
from courses import courses

# Panic state
PANIC_COMMAND = "secure me"

# ===============================
# APP START
# ===============================
app = Flask(__name__)
app.secret_key = "finance_secret_key"

print("Finance Advisor Running")

# ===============================
# HOME → LOGIN FIRST
# ===============================
@app.route("/")
def home():
    return redirect("/login")

# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    message = None

    # ⭐ Speak only once after login
    if session.pop('speak_voice', None):

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        expenses = cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id=?",
            (session['user_id'],)
        ).fetchone()[0]

        conn.close()

        if expenses is None:
            expenses = 0

        message = f"Welcome back. Your total expenses are rupees {int(expenses)}. Manage your finances wisely."

        speak(message)

    return render_template("dashboard.html", message=message)

# ===============================
# VOICE SPEAK FUNCTION
# ===============================
def speak(text):

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# SMART ADVICE

@app.route('/smart_advice')
def smart_advice():

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    user_id = session['user_id']

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY category
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()

    advice = []

    for category, total in data:

        if category == "Food" and total > 5000:
            advice.append("🍔 Your food spending is high. Try home meals.")

        elif category == "Entertainment" and total > 3000:
            advice.append("🎬 Reduce entertainment expenses.")

        elif category == "Shopping" and total > 4000:
            advice.append("🛍 Avoid unnecessary shopping.")

    if not advice:
        advice.append("✅ Your spending habits look balanced!")

    return render_template("smart_advice.html", advice=advice)

# ===============================
# CHATBOT
# ===============================
@app.route("/chatbot")
def chatbot():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    message = request.form["msg"].lower()

    if "hello" in message:
        return "Hello! I am your Finance Advisor."
    elif "save" in message:
        return "Try saving at least 20% of income."
    elif "investment" in message:
        return "Consider SIP or Mutual Funds."
    elif "expense" in message:
        return "Track expenses daily."

    return "Ask finance related questions."

    user_message = request.form.get("message").lower()

# Panic command detection
    if PANIC_COMMAND in user_message:
        return redirect("/secure_me")

# ===============================
# EXPENSE TRACKER
# ===============================
@app.route("/expense_tracker", methods=["GET","POST"])
def expense_tracker():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # =============================
    # ADD EXPENSE + AUTO SAVING
    # =============================
    if request.method == "POST":

        category = request.form.get("category")
        amount = request.form.get("amount")

        if category and amount:

            amount = float(amount)

            # Save expense
            cursor.execute(
                "INSERT INTO expenses(user_id, category, amount) VALUES(?,?,?)",
                (session['user_id'], category, amount)
            )

            # ===== AUTO ROUND-UP SAVING =====
            rounded_amount = ((int(amount / 100) + 1) * 100)
            saving = rounded_amount - amount

            if saving > 0:
                cursor.execute(
                    "INSERT INTO savings(user_id, saved_amount) VALUES(?,?)",
                    (session['user_id'], saving)
                )

            conn.commit()

    # =============================
    # FETCH USER EXPENSES
    # =============================
    expenses = cursor.execute(
        "SELECT category, amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    return render_template("expense.html", expenses=expenses)

# ===============================
# EXPENSE ANALYSIS
# ===============================
@app.route("/expense_analysis")
def expense_analysis():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    data = cursor.execute(
        "SELECT category, amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    if not data:
        return render_template("analytics.html", total=0, categories={})

    categories = {}

    for cat, amount in data:
        categories[cat] = categories.get(cat, 0) + amount

    total_amount = sum(categories.values())

    labels = list(categories.keys())
    values = list(categories.values())

    plt.figure(figsize=(5,5))
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.savefig("static/pie.png")
    plt.close()

    plt.figure(figsize=(6,4))
    plt.bar(labels, values)
    plt.savefig("static/bar.png")
    plt.close()

    return render_template(
        "analytics.html",
        total=total_amount,
        categories=categories
    )

# ===============================
# QUIZ
# ===============================
@app.route("/quiz", methods=["GET","POST"])
def quiz():

    if 'user_id' not in session:
        return redirect('/login')

    score = None

    if request.method == "POST":
        score = 0
        if request.form.get("q1") == "b":
            score += 1
        if request.form.get("q2") == "a":
            score += 1

    return render_template("quiz.html", score=score)

# ===============================
# INVESTMENT
# ===============================
@app.route("/investment", methods=["GET","POST"])
def investment():

    if 'user_id' not in session:
        return redirect('/login')

    advice = None

    if request.method == "POST":
        risk = request.form.get("risk")

        if risk == "low":
            advice = "Invest in FD and PPF."
        elif risk == "medium":
            advice = "Consider Mutual Funds & SIP."
        else:
            advice = "Stocks recommended."

    return render_template("investment.html", advice=advice)

# ===============================
# VOICE
# ===============================
@app.route("/voice")
def voice():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    expenses = cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()[0]

    conn.close()

    if expenses is None:
        expenses = 0

    message = f"Good morning. Your total expenses are rupees {int(expenses)}. Try saving more this week."

    # speak voice
    speak(message)

    return render_template("voice.html", message=message)
# ===============================
# FINANCIAL HEALTH
# ===============================
@app.route("/health", methods=["GET","POST"])
def health():

    if 'user_id' not in session:
        return redirect('/login')

    score = None

    if request.method == "POST":
        income = int(request.form["income"])
        expense = int(request.form["expense"])

        saving = income - expense

        if saving >= income*0.30:
            score = "✅ Excellent Financial Health"
        elif saving >= income*0.10:
            score = "👍 Good Financial Health"
        else:
            score = "⚠ Improve Savings"

    return render_template("health.html", score=score)

# ===============================
# AI REPORT (DATABASE VERSION)
# ===============================
@app.route("/ai_report")
def ai_report():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    data = cursor.execute(
        "SELECT amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    total_expense = sum([x[0] for x in data])

    if total_expense == 0:
        advice = "Start tracking expenses."
    elif total_expense < 5000:
        advice = "Excellent financial control!"
    elif total_expense < 15000:
        advice = "Spending is moderate."
    else:
        advice = "High expenses detected!"

    return render_template("ai_report.html",
                           total=total_expense,
                           advice=advice)


# ===============================
# DOWNLOAD AI REPORT PDF
# ===============================
@app.route("/download_report")
def download_report():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    data = cursor.execute(
        "SELECT category, amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    total_expense = sum(amount for _, amount in data)

    # AI Advice Logic
    if total_expense == 0:
        advice = "Start tracking expenses."
    elif total_expense < 5000:
        advice = "Excellent financial control."
    elif total_expense < 15000:
        advice = "Spending is moderate."
    else:
        advice = "High expenses detected. Reduce unnecessary costs."

    # ===== CREATE PDF =====
    filename = "AI_Finance_Report.pdf"   # ✅ FIXED PATH

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Finance Advisor AI Report", styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(
        Paragraph(f"Total Expense: ₹{total_expense}", styles['Normal'])
    )

    elements.append(Spacer(1,15))

    elements.append(Paragraph("AI Financial Advice:", styles['Heading2']))
    elements.append(Paragraph(advice, styles['Normal']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph("Expense Details:", styles['Heading2']))

    for cat, amt in data:
        elements.append(
            Paragraph(f"{cat} : ₹{amt}", styles['Normal'])
        )

    doc.build(elements)

    # ✅ DIRECT DOWNLOAD (NO 404 ERROR)
    return send_file(filename, as_attachment=True)

# ===============================
# AI EXPENSE PREDICTION
# ===============================
@app.route('/expense_prediction', methods=['GET','POST'])
def expense_prediction():

    prediction = None

    if request.method == 'POST':
        expense = float(request.form['expense'])
        prediction = expense * 1.10

    return render_template('expense_prediction.html',
                           prediction=prediction)
# ===============================
# REGISTER
# ===============================
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (request.form['username'], request.form['password'])
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# ===============================
# LOGIN
# ===============================
# ===============================
# LOGIN
# ===============================
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form['username'], request.form['password'])
        ).fetchone()

        conn.close()

        if user:
            session['user_id'] = user[0]

            # ⭐ PRO LEVEL IMPROVEMENT
            session['speak_voice'] = True   # trigger voice once

            return redirect('/dashboard')

        return "Invalid Login"

    return render_template("login.html")
# ===============================
# LOGOUT
# ===============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

#BUDGET PLANNER

@app.route("/budget_planner", methods=["GET","POST"])
def budget_planner():

    if 'user_id' not in session:
        return redirect('/login')

    budget = None

    if request.method == "POST":

        income = int(request.form["income"])

        needs = income * 0.50
        wants = income * 0.30
        savings = income * 0.20

        budget = {
            "income": income,
            "needs": needs,
            "wants": wants,
            "savings": savings
        }

    return render_template("budget.html", budget=budget)

# HIDDEN EXPENSES

@app.route("/hidden_expense")
def hidden_expense():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    data = cursor.execute(
        "SELECT category, amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    if not data:
        return render_template("hidden.html", warnings=[])

    # calculate category totals
    categories = {}

    for cat, amt in data:
        categories[cat] = categories.get(cat, 0) + amt

    total = sum(categories.values())

    warnings = []

    for cat, amt in categories.items():

        percent = (amt / total) * 100

        if percent > 40:
            warnings.append(
                f"⚠ High spending detected in {cat} ({percent:.1f}%)."
            )

        elif percent > 25:
            warnings.append(
                f"⚡ Moderate overspending in {cat}."
            )

    if not warnings:
        warnings.append("✅ Your spending habits look balanced!")

    return render_template("hidden.html", warnings=warnings)

# DAILY NOTIFICATION

@app.route("/daily_notification")
def daily_notification():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    expenses = cursor.execute(
        "SELECT amount FROM expenses WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    conn.close()

    total = sum(e[0] for e in expenses) if expenses else 0

    # AI Notification Logic
    if total == 0:
        message = "🔔 Start tracking expenses today!"
    elif total < 5000:
        message = "✅ Great control! Your spending is low."
    elif total < 15000:
        message = "⚡ Moderate spending. Try saving 20%."
    else:
        message = "⚠ High expenses detected today. Reduce unnecessary spending."

    return message

# AUTO SAVING

@app.route("/auto_savings")
def auto_savings():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    total = cursor.execute(
        "SELECT SUM(saved_amount) FROM savings WHERE user_id=?",
        (session['user_id'],)
    ).fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template("auto_savings.html", total=total)

# ===============================
# SCAN BILL MODULE
# ===============================

# Correct Tesseract path

# Ensure upload folder exists
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/scan_bill", methods=["GET","POST"])
def scan_bill():

    if 'user_id' not in session:
        return redirect('/login')

    extracted_text = ""
    detected_amount = None
    message = None

    if request.method == "POST":

        if "bill" not in request.files:
            message = "No file part in the request"
            return render_template("scan_bill.html", text=extracted_text, amount=detected_amount, message=message)

        file = request.files["bill"]

        if file.filename == "":
            message = "No file selected"
            return render_template("scan_bill.html", text=extracted_text, amount=detected_amount, message=message)

        try:
            # Save file safely
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Open image and extract text
            img = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(img)

            # Extract numbers (detect last number as amount)
            amounts = re.findall(r'\d+\.\d+|\d+', extracted_text)
            if amounts:
                detected_amount = float(amounts[-1])

                # Save to DB
                conn = sqlite3.connect("finance.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses(user_id,category,amount) VALUES(?,?,?)",
                    (session['user_id'], "Scanned Bill", detected_amount)
                )
                conn.commit()
                conn.close()
                message = f"Bill scanned successfully! Detected Amount: ₹{detected_amount}"
            else:
                message = "No amount detected in the bill."

        except Exception as e:
            message = f"Error processing the file: {str(e)}"

    return render_template(
        "scan_bill.html",
        text=extracted_text,
        amount=detected_amount,
        message=message
    )


# ===============================
# LEARNING COURSES + REWARD POINTS
# ===============================

@app.route("/learn")
def learn():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER,
        completed INTEGER,
        points INTEGER
    )
    """)

    # get total points
    cursor.execute("""
        SELECT SUM(points)
        FROM user_courses
        WHERE user_id=?
    """, (session['user_id'],))

    total_points = cursor.fetchone()[0]
    conn.close()

    return render_template(
        "learn.html",
        courses=courses,
        points=total_points or 0
    )


# COMPLETE COURSE
@app.route('/complete_course/<int:course_id>', methods=['POST'])
def complete_course(course_id):

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # prevent duplicate points
    cursor.execute("""
        SELECT * FROM user_courses
        WHERE user_id=? AND course_id=?
    """, (user_id, course_id))

    already_done = cursor.fetchone()

    if not already_done:
        cursor.execute("""
            INSERT INTO user_courses(user_id, course_id, completed, points)
            VALUES(?,?,1,10)
        """, (user_id, course_id))

    conn.commit()
    conn.close()

    return redirect('/learn')

    # ===============================
# SECURE ME PANIC MODE
# ===============================
@app.route("/secure_me")
def secure_me():
    session.clear()
    return render_template("secure_mode.html")


# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)