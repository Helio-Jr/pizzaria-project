import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzU1MTc1NTY2fQ.0uAqACn22yfzaykQ1za7NVb_E5fqeg4y-AdQuC-7fqw"
}

req = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)

print(req)
print(req.json())