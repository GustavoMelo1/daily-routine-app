import requests
from pipeline.validation import validate_day
from pipeline.payloads import (build_quarantine_day_payload, build_quarantine_task_payload, build_day_payload, build_task_payload)

API_BASE_URL = "http://localhost:8000"

def normalize_date(raw_date):
    if isinstance (raw_date, str):
        return raw_date.replace("/", "-")
    return raw_date

def publish_days(extracted_data):
    for day in extracted_data["dias"]:
        raw_date = day.get("data")
        normalized_date = normalize_date(raw_date)
        day["data"] = normalized_date
        validation_errors = validate_day(day)
        if validation_errors:
            quarantine_day_payload = build_quarantine_day_payload(day, validation_errors)
            quarantine_day_response = requests.post(f"{API_BASE_URL}/erros-quarentena", json=quarantine_day_payload)
            if quarantine_day_response.status_code == 400:
                continue
            quarantine_day_response.raise_for_status()
            quarantine_day_id = quarantine_day_response.json()['id']

            tasks = day.get("itens")
            if isinstance(tasks, list):
                for item in tasks:
                    quarantine_task_payload = build_quarantine_task_payload(item, quarantine_day_id)

                    quarantine_task_response = requests.post(
                        f"{API_BASE_URL}/tarefas-quarentena",
                        json=quarantine_task_payload
                    )
                    quarantine_task_response.raise_for_status()

            continue

        existing_day_response = requests.get(f"{API_BASE_URL}/dias/{normalized_date}")
        if existing_day_response.status_code == 200:
            continue

        day_payload = build_day_payload(day)
        day_response = requests.post(f"{API_BASE_URL}/dias", json=day_payload)
        day_id = day_response.json()['dia']

        for item in day["itens"]:
            task_payload = build_task_payload(item, day_id)
            requests.post(f"{API_BASE_URL}/tarefas", json=task_payload)