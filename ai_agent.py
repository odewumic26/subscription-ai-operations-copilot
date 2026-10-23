
import json
import re
import requests

from database import get_connection


# --------------------------------
# LOCAL AI CONFIGURATION
# --------------------------------

MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"


# --------------------------------
# APPROVED SQL BUSINESS QUESTIONS
# --------------------------------

QUESTIONS = {

    "How much revenue did we record?": """
        SELECT
            COUNT(*) AS total_payments,
            COALESCE(ROUND(SUM(AmountPaid), 2), 0)
                AS total_revenue,
            COALESCE(ROUND(AVG(AmountPaid), 2), 0)
                AS average_payment
        FROM payment
    """,

    "Which providers have the most subscriptions?": """
        SELECT
            sp.ServiceProviderName AS provider,
            COUNT(*) AS subscriptions
        FROM subscription s
        JOIN serviceprovider sp
            ON s.ServiceProviderID = sp.ServiceProviderID
        GROUP BY
            sp.ServiceProviderID,
            sp.ServiceProviderName
        ORDER BY subscriptions DESC
        LIMIT 10
    """,

    "What are our subscription statuses?": """
        SELECT
            COALESCE(st.StatusName, 'Unknown')
                AS status,
            COUNT(*) AS subscriptions
        FROM subscription s
        LEFT JOIN status st
            ON s.StatusID = st.StatusID
        GROUP BY
            st.StatusID,
            st.StatusName
        ORDER BY subscriptions DESC
    """,

    "How many subscriptions have cancellation dates?": """
        SELECT
            COUNT(*) AS total_subscriptions,
            COUNT(CancellationDate)
                AS dated_cancellations
        FROM subscription
    """
}


# --------------------------------
# RETRIEVE VERIFIED MYSQL RESULTS
# --------------------------------

def get_sql_results(question):

    if question not in QUESTIONS:
        raise ValueError("Unsupported business question.")

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(QUESTIONS[question])
            results = cursor.fetchall()

        finally:
            cursor.close()

    finally:
        connection.close()

    return results


# --------------------------------
# GENERATE LOCAL AI EXPLANATION
# --------------------------------

def generate_ai_explanation(question, results):

    prompt = f"""
You are an AI business operations analyst.

You are analyzing fictional subscription business data.

BUSINESS QUESTION:
{question}

VERIFIED MYSQL RESULTS:
{json.dumps(results, default=str)}

INSTRUCTIONS:

1. Explain the operational meaning of the results.
2. Do not repeat exact numerical values.
3. Do not invent statistics, amounts, or percentages.
4. Do not invent business trends or causes.
5. Give practical, relevant business insights.
6. Keep the explanation concise.
7. All information relates to synthetic data.
8. The application displays the verified metrics separately.

Write a brief business interpretation.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0
                }
            },
            timeout=180
        )

        response.raise_for_status()

        ai_text = response.json().get("response", "").strip()

        if not ai_text:
            return (
                "The AI did not return an explanation. "
                "Please review the verified SQL results."
            )

        # Prevent unverified numerical claims.
        if re.search(r"\d", ai_text):
            return (
                "The verified SQL results provide the relevant "
                "business metrics. These records can support "
                "subscription monitoring, operational reporting, "
                "and further business analysis. "
                "Refer to the SQL table for exact figures."
            )

        return ai_text

    except requests.exceptions.RequestException as error:
        return (
            "The local AI service could not generate an explanation. "
            f"Check that Ollama is running. Details: {error}"
        )

    except (ValueError, KeyError):
        return (
            "The AI service returned an unexpected response. "
            "The verified SQL results remain available."
        )


# --------------------------------
# MAIN AI ASSISTANT FUNCTION
# --------------------------------

def ask_ai(question):

    results = get_sql_results(question)

    # Revenue figures are explained directly from SQL
    # so the language model cannot alter them.
    if question == "How much revenue did we record?":

        row = results[0]

        ai_text = (
            "The database contains "
            f"{int(row['total_payments']):,} recorded payments, "
            "totaling "
            f"${float(row['total_revenue']):,.2f}, "
            "with an average payment of "
            f"${float(row['average_payment']):,.2f}. "
            "These synthetic records support financial "
            "monitoring and operational analytics."
        )

    else:
        ai_text = generate_ai_explanation(
            question,
            results
        )

    return {
        "sql_results": results,
        "ai_response": ai_text
    }
