
import requests
import json
import os

API_URL = (
    "https://www.consumerfinance.gov/"
    "data-research/consumer-complaints/search/api/v1/"
)


def extract_data():

    print("Starting CFPB API extraction...")

    params = {
        "size": 200,
        "no_aggs": "true",
        "no_highlight": "true"
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        # Extract complaint records from API response
        records = data.get("hits", {}).get("hits", [])

        complaints = [
            record.get("_source", {})
            for record in records
        ]

        print(f"Extracted records: {len(complaints)}")

        # Save original API response
        os.makedirs("data/raw", exist_ok=True)

        with open(
            "data/raw/complaints.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(data, file, indent=4)

        print("Raw API response saved successfully!")

        return complaints

    except requests.exceptions.RequestException as error:

        print(f"API request failed: {error}")
        return None

    except (ValueError, KeyError) as error:

        print(f"Data processing error: {error}")
        return None


if __name__ == "__main__":
    extract_data()






