
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Subscription AI Operations Copilot Demo",
    page_icon="📊",
    layout="wide"
)

DATA = Path(__file__).parent / "demo_data"

st.markdown("""
<style>
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    border: 1px solid #E3E8EF;
    border-radius: 10px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_csv(filename):
    return pd.read_csv(DATA / filename)


with st.sidebar:
    st.title("Operations Copilot")
    st.caption("Public Portfolio Demo")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Overview", "Operations Alerts", "AI Features"]
    )

    st.divider()
    st.caption("Python · SQL · Streamlit")
    st.caption("Synthetic data only")


st.title("Subscription AI Operations Copilot")
st.caption(
    "Business Analytics | Subscription Monitoring | AI Integration"
)

st.info(
    "This public demo uses exported synthetic business data. "
    "The full local application also includes Ollama-powered "
    "business explanations and customer support recommendations."
)


if page == "Overview":
    st.header("Business Overview")

    summary = load_csv("summary.csv").iloc[0]

    a, b, c, d = st.columns(4)

    a.metric(
        "Recorded Revenue",
        f"${summary['revenue']:,.2f}"
    )
    b.metric("Payments", f"{int(summary['payments']):,}")
    c.metric(
        "Subscriptions",
        f"{int(summary['subscriptions']):,}"
    )
    d.metric(
        "Dated Cancellations",
        f"{int(summary['cancellations']):,}"
    )

    st.divider()
    st.subheader("Monthly Payment Revenue")

    monthly = load_csv("monthly_revenue.csv")
    monthly["month"] = pd.to_datetime(
        monthly["month"] + "-01"
    )

    st.line_chart(
        monthly.set_index("month")["revenue"]
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Subscription Status")
        status = load_csv("subscription_status.csv")
        st.bar_chart(
            status.set_index("status")["subscriptions"]
        )

    with right:
        st.subheader("Top Service Providers")
        providers = load_csv("providers.csv")
        st.bar_chart(
            providers.set_index("provider")["subscriptions"]
        )

    with st.expander("View Source Data"):
        st.dataframe(monthly, hide_index=True)


elif page == "Operations Alerts":
    st.header("Operations Alert Center")

    st.write(
        "Subscriptions are grouped using predefined "
        "SQL rules for billing dates and pending statuses."
    )

    alerts = load_csv("alerts.csv")
    alerts = alerts[alerts["alert_type"] != "No Alert"]

    if not alerts.empty:
        st.metric(
            "Total Alerts",
            f"{int(alerts['total'].sum()):,}"
        )

        st.bar_chart(
            alerts.set_index("alert_type")["total"]
        )

        st.dataframe(
            alerts,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            "Download Alert Summary",
            alerts.to_csv(index=False),
            file_name="alert_summary.csv",
            mime="text/csv"
        )
    else:
        st.success("No alerts in this snapshot.")

    st.caption(
        "This is an exported data snapshot. "
        "Alert counts may change when the local "
        "MySQL queries are run again."
    )


elif page == "AI Features":
    st.header("Local AI Features")

    st.write(
        "The complete application integrates the "
        "Qwen 2.5 language model through Ollama."
    )

    st.subheader("AI Business Analyst")
    st.write(
        "Runs four approved SQL business queries, "
        "displays verified database results, and "
        "generates explanations using a local model."
    )

    st.subheader("AI Support Assistant")
    st.write(
        "Generates suggested support actions, "
        "customer message drafts, and internal "
        "follow-up recommendations for billing "
        "and subscription scenarios."
    )

    st.warning(
        "Live AI generation is not available in "
        "this hosted demo. It requires Ollama "
        "running locally."
    )

    st.markdown(
        "[View the complete source code on GitHub]"
        "(https://github.com/odewumic26/"
        "subscription-ai-operations-copilot)"
    )


st.divider()
st.caption(
    "Portfolio demonstration using synthetic data. "
    "Not a live billing or customer support system."
)
