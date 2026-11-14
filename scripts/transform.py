
# import json
# import pandas as pd
# import os


# def transform_data():

#     print("Starting data transformation...")

#     # STEP 1: Read raw JSON
#     with open(
#         "data/raw/complaints.json",
#         "r",
#         encoding="utf-8"
#     ) as file:

#         raw_data = json.load(file)

#     # STEP 2: Extract complaint records
#     records = raw_data.get("hits", {}).get("hits", [])

#     complaints = [
#         record.get("_source", {})
#         for record in records
#     ]

#     df = pd.DataFrame(complaints)

#     initial_count = len(df)

#     print(f"Initial records: {initial_count}")

#     # STEP 3: Validate required columns
#     required_columns = [
#         "complaint_id",
#         "date_received",
#         "product",
#         "company",
#         "state"
#     ]

#     missing_columns = [
#         col for col in required_columns
#         if col not in df.columns
#     ]

#     if missing_columns:
#         raise ValueError(
#             f"Missing required columns: {missing_columns}"
#         )

#     # STEP 4: Remove exact duplicate records
#     df = df.drop_duplicates()

#     # STEP 5: Remove duplicate complaint IDs
#     df = df.drop_duplicates(
#         subset=["complaint_id"],
#         keep="first"
#     )

#     # STEP 6: Standardize text columns
#     text_columns = df.select_dtypes(
#         include=["object", "str"]
#     ).columns

#     for col in text_columns:

#         df[col] = df[col].apply(
#             lambda x: x.strip() if isinstance(x, str) else x
#         )

#     # STEP 7: Convert date columns
#     date_columns = [
#         "date_received",
#         "date_sent_to_company"
#     ]

#     for col in date_columns:

#         df[col] = pd.to_datetime(
#             df[col],
#             errors="coerce",
#             utc=True
#         )

#     # STEP 8: Standardize state codes
#     df["state"] = df["state"].str.upper()

#     # STEP 9: Remove invalid essential records
#     df = df.dropna(
#         subset=[
#             "complaint_id",
#             "date_received",
#             "product",
#             "company",
#             "state"
#         ]
#     )

#     # STEP 10: Create data quality report
#     print("\n========== TRANSFORMATION REPORT ==========")

#     print("Initial records:", initial_count)

#     print("Final records:", len(df))

#     print("Duplicates removed:", initial_count - len(df))

#     print("\nMissing values after transformation:")
#     print(df.isnull().sum())

#     print("\nData types after transformation:")
#     print(df.dtypes)

#     # STEP 11: Save processed data
#     os.makedirs("data/processed", exist_ok=True)

#     df.to_csv(
#         "data/processed/complaints_clean.csv",
#         index=False
#     )

#     print("\nClean data saved successfully!")

#     return df


# if __name__ == "__main__":

#     transform_data()






import json
import pandas as pd
import os


def transform_data(
    input_file="data/raw/complaints.json",
    output_file="data/processed/complaints_clean.csv"
):

    print("\nStarting data transformation...")

    # STEP 1: Read raw JSON
    with open(input_file, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    # STEP 2: Extract records
    if isinstance(raw_data, list):
        complaints = raw_data

    elif isinstance(raw_data, dict):
        records = raw_data.get("hits", {}).get("hits", [])

        complaints = [
            record.get("_source", {})
            for record in records
        ]

    else:
        raise ValueError("Unsupported JSON format!")

    df = pd.DataFrame(complaints)

    initial_count = len(df)

    print(f"Initial records: {initial_count}")

    if df.empty:
        raise ValueError("No records found!")

    # STEP 3: Validate required columns
    required_columns = [
        "complaint_id",
        "date_received",
        "product",
        "company",
        "state"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # STEP 4: Standardize text columns
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for col in text_columns:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # STEP 5: Standardize complaint IDs
    df["complaint_id"] = (
        df["complaint_id"]
        .astype("string")
        .str.strip()
    )

    # STEP 6: Debug before cleaning
    print("\n========== DATA QUALITY CHECK ==========")

    print("Total raw records:", len(df))

    print(
        "Missing complaint IDs:",
        df["complaint_id"].isna().sum()
    )

    print(
        "Empty complaint IDs:",
        df["complaint_id"].eq("").sum()
    )

    print(
        "Duplicate complaint IDs:",
        df["complaint_id"].duplicated().sum()
    )

    print(
        "Unique complaint IDs:",
        df["complaint_id"].nunique()
    )

    print(
        "Missing dates before conversion:",
        df["date_received"].isna().sum()
    )

    # STEP 7: Convert dates
    date_columns = [
        "date_received",
        "date_sent_to_company"
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
                utc=True
            )

    print(
        "\nInvalid received dates:",
        df["date_received"].isna().sum()
    )

    # STEP 8: Standardize state
    df["state"] = df["state"].str.upper()

    # STEP 9: Remove exact duplicates
    before_exact = len(df)

    df = df.drop_duplicates()

    exact_removed = before_exact - len(df)

    # STEP 10: Remove duplicate complaint IDs
    before_id = len(df)

    df = df.drop_duplicates(
        subset=["complaint_id"],
        keep="first"
    )

    id_duplicates_removed = before_id - len(df)

    # STEP 11: Remove invalid essential records
    before_validation = len(df)

    df = df.dropna(
        subset=["complaint_id", "date_received"]
    )

    df = df[df["complaint_id"] != ""]

    invalid_removed = before_validation - len(df)

    # STEP 12: Final quality report
    final_count = len(df)

    print("\n========== FINAL TRANSFORMATION REPORT ==========")

    print(f"Initial records: {initial_count:,}")

    print(f"Exact duplicates removed: {exact_removed:,}")

    print(f"Duplicate IDs removed: {id_duplicates_removed:,}")

    print(f"Invalid records removed: {invalid_removed:,}")

    print(f"Final records: {final_count:,}")

    print(f"Total records removed: {initial_count - final_count:,}")

    print("\nMissing values after transformation:")

    print(df.isnull().sum())

    print("\nFinal data types:")

    print(df.dtypes)

    # STEP 13: Save processed CSV
    os.makedirs(
        os.path.dirname(output_file),
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nClean data saved successfully!")

    print(f"Output file: {output_file}")

    print("\n========== PROCESS COMPLETED ==========")

    return df


if __name__ == "__main__":

    transform_data()
