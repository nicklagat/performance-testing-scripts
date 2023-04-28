import json
import os
import random

from dotenv import load_dotenv
from locust import HttpUser, TaskSet, task

load_dotenv()

uri = "endpoints"
cancel_url = 'endpoints'
auth_url = 'endpoints'

# create customers using the script, get the generated  customer ids and add it for use in creating sales orders
customer_ids = ["15457549-28c1-4230-a868-695392c6baab",
                "5c2bcb74-83fe-44a5-b507-777edc647051",
                "27d30375-2602-4e8b-ad8b-66fec546ecf2",
                "26267311-454d-41b2-b928-1d8d4c3e8488",
                "80f7b42b-77ca-4c9a-a133-1fad60e6815c",
                "f45d7663-11ac-4695-9290-3b91611d4f90",
                "0c1868fd-df41-4f2e-bc5a-fc7b2fb7732f",
                "c1718985-ee44-4765-9bbe-7fdd0a8ea8a9",
                "2cad2a9a-5f90-480f-a2d8-dbcca1d5128f",
                "93ea5d93-c9cc-4695-a0ed-dee74517c3d1",
                "a4c7c2df-266c-4926-8228-e911772ecb8e",
                "93ea5d93-c9cc-4695-a0ed-dee74517c3d1",
                "53b0c866-bf1f-4f57-b189-6a4f96eadd5c",
                "00e6aec6-7fe5-49b3-a36d-ba12701297d3",
                "f094c5d6-86d6-412d-b324-44100f0987c1",
                "f1ebf4bf-acee-4f18-ba2b-58457e958447",
                "08d2c02d-3c81-4c4b-bb50-8877d15244b3",
                "5daa6231-4938-48bb-bf43-f0c3eae853e4",
                "b9c4c2d4-e111-402a-87f1-e4bd056dae1a",
                "02451730-c78f-4ace-96ec-2d1aa60103c7",
                "e303031b-dc3a-4ac0-9ae3-ea2e68743887",
                "6170a363-20d3-40c6-950d-4b5ecc66eaf1",
                "74f4c658-5aa0-429e-863c-020e93881455",
                "432631e5-3da0-4489-84f9-c09fd170834d"]


def get_random_id():
    return random.choice(customer_ids)


class SalesOrderCreation(TaskSet):

    @task
    def auth_call(self):
        email_id = os.getenv("EMAILID")
        password = os.getenv("PASSWORD")

        auth_payload = {"emailId": email_id, "applicationId": "b5318e50-2192-4647-9c90-1e569f49fe69",
                        "password": password, "emailLogin": True}
        response = self.client.post(auth_url, json.dumps(auth_payload), headers={"Content-Type": "application/json"},
                                    name="Generate Tokens")
        print(json.dumps(response.text))

        access_auth_token = response.json()["data"]["token_details"]["access_token"]
        print(access_auth_token)
        return access_auth_token

    @task
    def create_sales_order(self):
        c_id = get_random_id()
        access_token = self.auth_call()

        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + access_token}

        payload = {
            "appVersion": "8.2.6",
            "booked_by": c_id,
            "booked_through": "customer",
            "credit_fee": 0,
            "paid_credit_fee": False,
            "customer_id": c_id,
            "delivery_fee": 0.0,
            "edit_order": False,
            "expected_delivery_time": "2023-02-08T09:54:31Z",
            "gross_amount": 11200.2,
            "id": None,
            "lat": 37.4220936,
            "lon": -122.083922,
            "netAmount": 11200.2,
            "sales_order_items_attributes": [
                {
                    "category": None,
                    "department_name": "Dry Food",
                    "product_package_id": "1115caa8-f8b5-417a-842f-a649e7729bd7",
                    "product_code": "0000071",
                    "product_id": "bbdd92ee-6fa1-4bf9-8cf7-ba3a747b449e",
                    "productName": "Soko Wheat Flour 2kg",
                    "product_package": {
                        "case_count": 1,
                        "default_pack": False,
                        "default_sellable": False,
                        "id": "1115caa8-f8b5-417a-842f-a649e7729bd7",
                        "inner_count": 12,
                        "outer_count": 1,
                        "product_pack_description": {
                            "description": "old_pkg_Bale",
                            "name": None
                        },
                        "sellable": True
                    },
                    "promo_code": "",
                    "pack_quantity": 5,
                    "quantityMap": {},
                    "soh": 2000000,
                    "sub_class": {
                        "category": "commodity",
                        "description": "Wheat Flour",
                        "id": "9a556766-3767-48cb-94d0-0f5572388fe9"
                    },
                    "supplier_name": None,
                    "total_discount": 0.0,
                    "pack_price": 2240.04
                }],
            "promo_code": None,
            "sale_order_id": None,
            "scheduled_delivery_time": "2023-02-08T09:54:31Z",
            "status": True,
            "total_discount": 0.0,
            "wallet_pay": False,
            "wallet_pay_amount": 0.0,
            "wants_credit": False

        }

        response = self.client.post(uri, json.dumps(payload), headers=headers, name="Sales Order Creation")

        if response.status_code == 400:
            pass

        response_dict = response.json()
        print(response_dict)

        sales_order_id = response_dict['data']['id']
        print(sales_order_id)

        cancel_payload = {"appVersion": "8.2.6", "ids": [sales_order_id], "cancellation_reason": "Wrong order"}

        cancel_response = self.client.patch(cancel_url, json.dumps(cancel_payload), headers=headers,
                                            name="Sales Order Cancellation")

        cancel_response_data = json.dumps(cancel_response.text)
        print(cancel_response_data)

        cancel_dict = cancel_response.json
        print(cancel_dict)


class SalesOrder(HttpUser):
    count = 0
    host = "host url"
    # wait_time = between(1, 2)
    tasks = [SalesOrderCreation]
