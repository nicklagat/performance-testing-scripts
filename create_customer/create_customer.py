import csv
import json
import os
import random

from dotenv import load_dotenv
from faker import Faker
from locust import HttpUser, TaskSet, task, between

load_dotenv()

fake = Faker()
uri = ""
existing_store_names = []

auth_url = 'endpoints'
cust_url = 'endpoints'


# created by  Nickson Lagat


def write_to_csv(response):
    with open("response.csv", "a") as f:
        writer = csv.DictWriter(f,
                                fieldnames=["store_name", "manager_last_name", "manager_first_name", "phone_number",
                                            "self_password"])
        writer.writerow(response)


def generate_random_4_digit_pin():
    return str(random.randint(1000, 999999999))


def generate_random_phone_number():
    # Kenyan phone numbers start with +254
    prefix = "+254"
    suffix = "".join([str(random.randint(0, 9)) for i in range(8)])
    return prefix + suffix


def generate_unique_store_name():
    store_name = "SALES-ORDER-CREATE-QA " + str(random.randint(100, 999))
    while store_name in existing_store_names:
        store_name = "SALES-ORDER-CREATE-QA " + str(random.randint(100, 999))
    existing_store_names.append(store_name)
    return store_name


class CreateCustomers(TaskSet):

    # The auth_call is subject to be refined
    def auth_call(self):
        email_id = os.getenv("EMAILID")
        password = os.getenv("PASSWORD")
        auth_payload = {"emailId": email_id, "applicationId": "f20ee0e8-85ca-4b14-8c23-81f09a653f96",
                        "password": password, "emailLogin": True}
        response = self.client.post(auth_url, json.dumps(auth_payload), headers={"Content-Type": "application/json"},
                                    name="Generate Tokens")
        print(json.dumps(response.text))

        access_auth_token = response.json()["data"]["token_details"]["access_token"]
        print(access_auth_token)
        return access_auth_token

    @task
    def create_customer(self):
        access_token = self.auth_call()
        phone_number = generate_random_phone_number()
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}
        payload = {
            "appVersion": "8.2.6",
            "status": True,
            "exists": False,
            "fr_code": "",
            "gender": "Male",
            "is_mobile": True,
            "land_mark": fake.address(),
            "language": {
                "code": "en_US",
                "id": "0a70d45c-a4cc-4dff-9aee-1d101c88f797",
                "name": "English",
                "status": True
            },
            "latitude": random.uniform(-3, 0),
            "longitude": random.uniform(0, 40),
            "organization_location_id": "eb4a652e-4e1f-456b-8999-87dc2aad39f5",
            "location_name": "Kasarani/Thika Road",
            "phone_number": phone_number,
            "phoneVerified": True,
            "manager_first_name": fake.first_name(),
            "manager_last_name": fake.last_name(),
            "store_name": generate_unique_store_name(),
            "sign_up_mode": "mobile",
            "self_password": generate_random_4_digit_pin()
        }

        response = self.client.post(cust_url, json.dumps(payload), headers=headers, name="Create Customers")
        print(json.dumps(response.text))

        extracted_id = response.json()["id"]

        with open("customer_ids.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([extracted_id])

        write_to_csv(
            {"manager_first_name": payload["manager_first_name"], "manager_last_name": payload["manager_last_name"],
             "store_name": payload["store_name"], "self_password": payload["self_password"],
             "phone_number": payload["phone_number"]})


class CreateCustomer(HttpUser):
    count = 0
    host = "host url"
    wait_time = between(1, 2)
    tasks = [CreateCustomers]
