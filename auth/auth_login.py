from locust import HttpUser, TaskSet, task, between
import json

auth_url = 'endpoints'


# The auth_call is subject to be refined/deleted
class AuthLogin(TaskSet):
    @task
    def auth_call(self):
        auth_payload = {"emailId": "email", "applicationId": "f20ee0e8-85ca-4b14-8c23-81f09a653f96",
                        "password": "password", "emailLogin": True}
        response = self.client.post(auth_url, json.dumps(auth_payload), headers={"Content-Type": "application/json"},
                                    name="Generate Tokens")
        print(json.dumps(response.text))

        access_token = response.json()["data"]["token_details"]["access_token"]
        print(access_token)


class AuthenLogin(HttpUser):
    host = 'host url'
    wait_time = between(1, 2)
    tasks = [AuthLogin]
