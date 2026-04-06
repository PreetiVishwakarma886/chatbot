def calculate_finance_score(income, expense, savings):

    score = 0

    savings_ratio = savings / income
    expense_ratio = expense / income

    # Savings scoring
    if savings_ratio >= 0.3:
        score += 40
    elif savings_ratio >= 0.2:
        score += 30
    else:
        score += 10

    # Expense scoring
    if expense_ratio <= 0.5:
        score += 40
    elif expense_ratio <= 0.7:
        score += 25
    else:
        score += 10

    # Stability bonus
    if savings > 0:
        score += 20

    # Status
    if score >= 80:
        status = "Excellent Financial Health ✅"
    elif score >= 60:
        status = "Good Financial Condition 👍"
    else:
        status = "Needs Improvement ⚠️"

    return {
        "score": score,
        "status": status
    }