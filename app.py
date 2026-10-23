
import streamlit as st
import pandas as pd
import requests

from database import get_connection
from ai_agent import ask_ai, QUESTIONS
from operations import get_operations_alerts
from support_agent import generate_support_recommendation


# ---------------------------------------
# PAGE SETUP
# ---------------------------------------

st.set_page_config(
    page_title="AI Operations Copilot",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------
# SIMPLE CUSTOM STYLING
# ---------------------------------------

st.markdown("""
<style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #203453;
        font-weight: 700;
    }

    h2, h3 {
        color: #293D57;
    }

    [data-testid="stSidebar"] {
        background-color: #F0F4F9;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 16px;
        border: 1px solid #E3E8EF;
        border-radius: 10px;
    }

    div.stButton > button[kind="primary"] {
        background-color: #285CA6;
        border-radius: 7px;
        border: none;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #1C477F;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------
# DATABASE FUNCTION
# ---------------------------------------

@st.cache_data(ttl=300)
def run_query(query):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query)
            return pd.DataFrame(cursor.fetchall())
        finally:
            cursor.close()

    finally:
        connection.close()


@st.cache_data(ttl=300)
def load_alerts():
    return get_operations_alerts()


# ---------------------------------------
# NAVIGATION
# ---------------------------------------

with st.sidebar:
    st.title("AI Operations Copilot")
    st.caption("Subscription Analytics Project")

    st.divider()

    page = st.radio(
        "Pages",
        [
            "Overview",
            "AI Analyst",
            "Operations Alerts",
            "Support Assistant"
        ]
    )

    st.divider()
    st.write("**Tools used**")
    st.caption("Python · MySQL · Streamlit · Ollama")

    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Synthetic portfolio dataset")


# ---------------------------------------
# OVERVIEW
# ---------------------------------------

if page == "Overview":

    st.title("Subscription Overview")

    st.write(
        "A summary of subscription activity, "
        "payments, and service provider performance."
    )

    st.divider()

    try:
        revenue = run_query("""
            SELECT
                COUNT(*) AS payments,
                COALESCE(SUM(AmountPaid), 0) AS revenue,
                COALESCE(AVG(AmountPaid), 0) AS avg_payment
            FROM payment
        """)

        subscription_data = run_query("""
            SELECT
                COUNT(*) AS subscriptions,
                COUNT(CancellationDate) AS cancellations
            FROM subscription
        """)

        total_revenue = float(revenue.iloc[0]["revenue"])
        payments = int(revenue.iloc[0]["payments"])
        avg_payment = float(revenue.iloc[0]["avg_payment"])
        subscriptions = int(
            subscription_data.iloc[0]["subscriptions"]
        )
        cancellations = int(
            subscription_data.iloc[0]["cancellations"]
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Recorded Revenue", f"${total_revenue:,.2f}")
        col2.metric("Payments", f"{payments:,}")
        col3.metric("Subscriptions", f"{subscriptions:,}")
        col4.metric("Cancellations", f"{cancellations:,}")

        st.caption(
            f"Average recorded payment: ${avg_payment:,.2f}"
        )

    except Exception as error:
        st.error(f"Unable to load summary: {error}")

    st.divider()

    st.subheader("Monthly Payment Revenue")

    try:
        monthly = run_query("""
            SELECT
                DATE_FORMAT(PaymentDate, '%Y-%m') AS month,
                SUM(AmountPaid) AS revenue
            FROM payment
            WHERE PaymentDate IS NOT NULL
            GROUP BY DATE_FORMAT(PaymentDate, '%Y-%m')
            ORDER BY month
        """)

        if not monthly.empty:
            monthly["revenue"] = monthly["revenue"].astype(float)

            st.line_chart(
                monthly.set_index("month")["revenue"]
            )

            with st.expander("View monthly data"):
                st.dataframe(
                    monthly,
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.info("No payment records available.")

    except Exception as error:
        st.error(f"Unable to load payment trends: {error}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Subscription Status")

        try:
            status = run_query("""
                SELECT
                    COALESCE(st.StatusName, 'Unknown') AS status,
                    COUNT(*) AS subscriptions
                FROM subscription s
                LEFT JOIN status st
                    ON s.StatusID = st.StatusID
                GROUP BY st.StatusID, st.StatusName
                ORDER BY subscriptions DESC
            """)

            if not status.empty:
                st.bar_chart(
                    status.set_index("status")["subscriptions"]
                )
        except Exception as error:
            st.error(f"Status query failed: {error}")

    with right:
        st.subheader("Top Service Providers")

        try:
            providers = run_query("""
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
            """)

            if not providers.empty:
                st.bar_chart(
                    providers.set_index("provider")["subscriptions"]
                )
        except Exception as error:
            st.error(f"Provider query failed: {error}")


# ---------------------------------------
# AI ANALYST
# ---------------------------------------

elif page == "AI Analyst":

    st.title("AI Business Analyst")

    st.write(
        "Use predefined SQL queries to analyze "
        "subscription data and get AI-assisted insights."
    )

    st.divider()

    question = st.selectbox(
        "Select a question",
        list(QUESTIONS.keys())
    )

    if st.button("Run Analysis", type="primary"):
        with st.spinner("Analyzing data..."):
            try:
                st.session_state["analysis"] = (
                    question,
                    ask_ai(question)
                )
            except Exception as error:
                st.error(f"Analysis failed: {error}")

    saved = st.session_state.get("analysis")

    if saved is not None and saved[0] == question:
        result = saved[1]

        st.subheader("SQL Results")

        st.dataframe(
            pd.DataFrame(result["sql_results"]),
            hide_index=True,
            use_container_width=True
        )

        with st.expander("Show SQL Query"):
            st.code(QUESTIONS[question], language="sql")

        st.subheader("Business Interpretation")

        # Plain text avoids unwanted Markdown formatting
        st.text(result["ai_response"])

        st.caption(
            "SQL values are authoritative. "
            "AI-generated explanations may require review."
        )


# ---------------------------------------
# OPERATIONS ALERTS
# ---------------------------------------

elif page == "Operations Alerts":

    st.title("Operations Alerts")

    st.write(
        "Review subscriptions with pending statuses "
        "or billing dates that may need attention."
    )

    st.divider()

    try:
        alerts = load_alerts()

        if not alerts.empty:

            col1, col2 = st.columns(2)

            col1.metric("Total Alerts", f"{len(alerts):,}")
            col2.metric(
                "Alert Categories",
                alerts["AlertType"].nunique()
            )

            st.subheader("Alerts by Type")

            st.bar_chart(
                alerts["AlertType"].value_counts()
            )

            st.subheader("Alert Details")

            selected = st.selectbox(
                "Filter alerts",
                ["All"] + sorted(alerts["AlertType"].unique())
            )

            if selected == "All":
                filtered = alerts
            else:
                filtered = alerts[
                    alerts["AlertType"] == selected
                ]

            st.dataframe(
                filtered,
                hide_index=True,
                use_container_width=True
            )

            st.download_button(
                "Download CSV",
                data=filtered.to_csv(index=False),
                file_name="subscription_alerts.csv",
                mime="text/csv"
            )

            st.caption(
                "Alerts are indicators for review, "
                "not confirmed payment failures."
            )

        else:
            st.success("No alerts found.")

    except Exception as error:
        st.error(f"Unable to retrieve alerts: {error}")


# ---------------------------------------
# SUPPORT ASSISTANT
# ---------------------------------------

elif page == "Support Assistant":

    st.title("AI Support Assistant")

    st.write(
        "Generate suggested support actions and "
        "customer communication drafts using Ollama."
    )

    st.divider()

    alert_type = st.selectbox(
        "Select a support scenario",
        [
            "Pending Review",
            "Upcoming Billing",
            "Past Billing Date"
        ]
    )

    if st.button("Generate Recommendation", type="primary"):
        with st.spinner("Generating recommendation..."):
            try:
                recommendation = (
                    generate_support_recommendation(alert_type)
                )

                st.session_state["support_recommendation"] = (
                    alert_type,
                    recommendation
                )

            except requests.exceptions.RequestException:
                st.error(
                    "Could not connect to Ollama. "
                    "Check that it is running."
                )

            except Exception as error:
                st.error(f"Request failed: {error}")

    saved = st.session_state.get("support_recommendation")

    if saved is not None and saved[0] == alert_type:

        st.subheader("Support Recommendation")

        st.markdown(saved[1])

        st.info(
            "This is an AI-generated draft. "
            "No messages have been sent."
        )

        st.download_button(
            "Download Recommendation",
            data=saved[1],
            file_name="support_recommendation.txt",
            mime="text/plain"
        )


# ---------------------------------------
# FOOTER
# ---------------------------------------

st.divider()

st.caption(
    "AI Operations Copilot | Python, MySQL, "
    "Streamlit & Ollama | Synthetic Data"
)
