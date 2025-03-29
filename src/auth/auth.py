from fastapi import Request
from nicegui import app

MOCK_USERS = [
    {'email': 'engineer@gmail.com', 'password': '1234', 'role': 'engineer'},
    {'email': 'installer@gmail.com', 'password': '1234', 'role': 'installer'},
    {'email': 'director@gmail.com', 'password': '1234', 'role': 'director'},
]

@app.post("/api/handle_login")
async def handle_login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        wallet = data.get("wallet")
        role = data.get("role")

        for user in MOCK_USERS:
            if user["email"] == email and user["password"] == password and user["role"] == role and wallet:
                app.storage.user.update({
                    "email": email,
                    "role": role,
                    "wallet": wallet,
                })
                print('[DEBUG:login] Stored user:', app.storage.user)
                return {'success': True, 'email': email, 'role': role, 'wallet': wallet}

        return {'success': False}
    except Exception as e:
        print('Login API error:', e)
        return {'success': False, 'error': str(e)}
