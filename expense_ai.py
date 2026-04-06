def analyze_expense(food, travel, shopping, income):

    total = food + travel + shopping

    savings = income - total

    advice = []

    if shopping > income * 0.3:
        advice.append("⚠️ You are overspending on Shopping.")

    if food > income * 0.25:
        advice.append("⚠️ Food expenses are high.")

    if savings < income * 0.2:
        advice.append("❌ Savings are too low. Try saving at least 20%.")

    if not advice:
        advice.append("✅ Excellent financial management!")

    return {
        "total_expense": total,
        "savings": savings,
        "advice": advice
    }