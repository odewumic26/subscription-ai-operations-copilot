
import pandas as pd
from database import get_connection


def get_operations_alerts():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    s.SubscriptionID,
                    s.SubscriptionName,
                    st.StatusName,
                    s.NextBillingDate,
                    CASE
                        WHEN st.StatusName = 'Pending'
                            THEN 'Pending Review'
                        WHEN st.StatusName = 'Active'
                             AND s.NextBillingDate
                                 BETWEEN CURDATE()
                                 AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                            THEN 'Upcoming Billing'
                        WHEN st.StatusName = 'Active'
                             AND s.NextBillingDate < CURDATE()
                            THEN 'Past Billing Date'
                        ELSE 'No Alert'
                    END AS AlertType
                FROM subscription s
                LEFT JOIN status st
                    ON s.StatusID = st.StatusID
            """)

            results = cursor.fetchall()

        finally:
            cursor.close()

    finally:
        connection.close()

    df = pd.DataFrame(results)

    if df.empty:
        return df

    return df[df["AlertType"] != "No Alert"].copy()
