
import csv
from pathlib import Path
from database import get_connection

OUTPUT = Path(__file__).parent / "demo_data"
OUTPUT.mkdir(exist_ok=True)

QUERIES = {
    "summary.csv": """
        SELECT
            (SELECT COUNT(*) FROM payment) AS payments,
            (SELECT COALESCE(SUM(AmountPaid), 0)
             FROM payment) AS revenue,
            (SELECT COUNT(*) FROM subscription)
                AS subscriptions,
            (SELECT COUNT(CancellationDate)
             FROM subscription) AS cancellations
    """,

    "monthly_revenue.csv": """
        SELECT
            DATE_FORMAT(PaymentDate, '%Y-%m') AS month,
            ROUND(SUM(AmountPaid), 2) AS revenue
        FROM payment
        WHERE PaymentDate IS NOT NULL
        GROUP BY DATE_FORMAT(PaymentDate, '%Y-%m')
        ORDER BY month
    """,

    "subscription_status.csv": """
        SELECT
            COALESCE(st.StatusName, 'Unknown') AS status,
            COUNT(*) AS subscriptions
        FROM subscription s
        LEFT JOIN status st ON s.StatusID = st.StatusID
        GROUP BY st.StatusID, st.StatusName
        ORDER BY subscriptions DESC
    """,

    "providers.csv": """
        SELECT
            sp.ServiceProviderName AS provider,
            COUNT(*) AS subscriptions
        FROM subscription s
        JOIN serviceprovider sp
            ON s.ServiceProviderID = sp.ServiceProviderID
        GROUP BY sp.ServiceProviderID,
                 sp.ServiceProviderName
        ORDER BY subscriptions DESC
        LIMIT 10
    """,

    "alerts.csv": """
        SELECT
            CASE
                WHEN st.StatusName = 'Pending'
                    THEN 'Pending Review'
                WHEN st.StatusName = 'Active'
                     AND s.NextBillingDate BETWEEN CURDATE()
                     AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                    THEN 'Upcoming Billing'
                WHEN st.StatusName = 'Active'
                     AND s.NextBillingDate < CURDATE()
                    THEN 'Past Billing Date'
                ELSE 'No Alert'
            END AS alert_type,
            COUNT(*) AS total
        FROM subscription s
        LEFT JOIN status st ON s.StatusID = st.StatusID
        GROUP BY alert_type
    """
}

connection = get_connection()

try:
    cursor = connection.cursor()

    try:
        for filename, sql in QUERIES.items():
            cursor.execute(sql)

            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()

            filepath = OUTPUT / filename

            with filepath.open(
                "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(columns)
                writer.writerows(rows)

            print(f"Created {filename}: {len(rows)} rows")
    finally:
        cursor.close()
finally:
    connection.close()

print("Demo data export completed.")
