
import pandas as pd
from sqlalchemy import text

from config import get_database_engine


def load_data():

    print("\nStarting PostgreSQL loading process...")

    # STEP 1: Read processed CSV
    df = pd.read_csv(
        "data/processed/complaints_clean.csv"
    )

    if df.empty:
        print("No records available for loading.")
        return

    print(f"Records received: {len(df)}")

    # STEP 2: Define database columns
    columns = [
        "complaint_id",
        "product",
        "sub_product",
        "issue",
        "sub_issue",
        "company",
        "state",
        "zip_code",
        "date_received",
        "date_sent_to_company",
        "timely",
        "company_response",
        "company_public_response",
        "submitted_via",
        "tags"
    ]

    # Add missing optional columns
    for col in columns:
        if col not in df.columns:
            df[col] = None

    df = df[columns]
    df["complaint_id"] = df["complaint_id"].astype("string")

    # STEP 3: Convert dates
    date_columns = [
        "date_received",
        "date_sent_to_company"
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce",
            utc=True
        )

    # STEP 4: Clean missing values
    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    records = df.to_dict(orient="records")

    # STEP 5: PostgreSQL connection
    engine = get_database_engine()

    # STEP 6: Create table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS consumer_complaints (

        complaint_id VARCHAR(50) PRIMARY KEY,

        product TEXT,
        sub_product TEXT,
        issue TEXT,
        sub_issue TEXT,
        company TEXT,

        state VARCHAR(2),
        zip_code VARCHAR(10),

        date_received TIMESTAMPTZ,
        date_sent_to_company TIMESTAMPTZ,

        timely VARCHAR(10),
        company_response TEXT,
        company_public_response TEXT,
        submitted_via TEXT,
        tags TEXT

    );
    """

    # STEP 7: UPSERT query
    insert_query = text("""
        INSERT INTO consumer_complaints (
            complaint_id,
            product,
            sub_product,
            issue,
            sub_issue,
            company,
            state,
            zip_code,
            date_received,
            date_sent_to_company,
            timely,
            company_response,
            company_public_response,
            submitted_via,
            tags
        )
        VALUES (
            :complaint_id,
            :product,
            :sub_product,
            :issue,
            :sub_issue,
            :company,
            :state,
            :zip_code,
            :date_received,
            :date_sent_to_company,
            :timely,
            :company_response,
            :company_public_response,
            :submitted_via,
            :tags
        )

        ON CONFLICT (complaint_id)
        DO UPDATE SET

            product = EXCLUDED.product,
            sub_product = EXCLUDED.sub_product,
            issue = EXCLUDED.issue,
            sub_issue = EXCLUDED.sub_issue,
            company = EXCLUDED.company,
            state = EXCLUDED.state,
            zip_code = EXCLUDED.zip_code,
            date_received = EXCLUDED.date_received,
            date_sent_to_company = EXCLUDED.date_sent_to_company,
            timely = EXCLUDED.timely,
            company_response = EXCLUDED.company_response,
            company_public_response = EXCLUDED.company_public_response,
            submitted_via = EXCLUDED.submitted_via,
            tags = EXCLUDED.tags

        WHERE ROW(
            consumer_complaints.product,
            consumer_complaints.sub_product,
            consumer_complaints.issue,
            consumer_complaints.sub_issue,
            consumer_complaints.company,
            consumer_complaints.state,
            consumer_complaints.zip_code,
            consumer_complaints.date_received,
            consumer_complaints.date_sent_to_company,
            consumer_complaints.timely,
            consumer_complaints.company_response,
            consumer_complaints.company_public_response,
            consumer_complaints.submitted_via,
            consumer_complaints.tags
        ) IS DISTINCT FROM ROW(
            EXCLUDED.product,
            EXCLUDED.sub_product,
            EXCLUDED.issue,
            EXCLUDED.sub_issue,
            EXCLUDED.company,
            EXCLUDED.state,
            EXCLUDED.zip_code,
            EXCLUDED.date_received,
            EXCLUDED.date_sent_to_company,
            EXCLUDED.timely,
            EXCLUDED.company_response,
            EXCLUDED.company_public_response,
            EXCLUDED.submitted_via,
            EXCLUDED.tags
        );
    """)

    try:

        with engine.begin() as connection:

            connection.execute(
                text(create_table_query)
            )

            total_affected = 0

            # STEP 8: Batch loading
            batch_size = 500

            for start in range(0, len(records), batch_size):

                batch = records[
                    start:start + batch_size
                ]

                result = connection.execute(
                    insert_query,
                    batch
                )

                total_affected += result.rowcount

                print(
                    f"Processed batch: "
                    f"{min(start + batch_size, len(records))}"
                    f"/{len(records)}"
                )

            # STEP 9: Database validation
            db_count = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM consumer_complaints
                """)
            ).scalar()

        print("\n========== LOAD REPORT ==========")

        print("Input records:", len(records))

        print("Inserted or updated records:", total_affected)

        print(
            "Unchanged existing records:",
            len(records) - total_affected
        )

        print("Total records in database:", db_count)

        print("\nPostgreSQL loading completed successfully!")

    except Exception as error:

        print(f"\nDatabase loading failed: {error}")
        raise

    finally:

        engine.dispose()


if __name__ == "__main__":

    load_data()
