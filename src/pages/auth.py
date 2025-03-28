from fastapi import Request
from nicegui import app

@app.post("/api/handle_login")
async def handle_login(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        wallet = data.get("wallet")

        if email == 'engineer@gmail.com' and password == '1234' and wallet:
            app.storage.user['email'] = email
            app.storage.user['wallet'] = wallet
            return {'success': True}
        return {'success': False}
    except Exception as e:
        print('Login API error:', e)
        return {'success': False, 'error': str(e)}
