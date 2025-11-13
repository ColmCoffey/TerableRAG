import requests
import json
import subprocess

# Get function URL from Terraform
func_name = subprocess.check_output(
    ["terraform", "output", "-raw", "function_app_name"]
).decode().strip()

url = f"https://{func_name}.azurewebsites.net/api/query"

query = "What are the cardinal motor symptoms of Parkinson's disease?"

response = requests.post(
    url,
    json={"query": query},
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"\nResults:\n{json.dumps(response.json(), indent=2)}")