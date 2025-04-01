from nicegui import ui

def connect_wallet(address: str):
    ui.run_javascript(f"localStorage.setItem('wallet', '{address}')")

def get_wallet():
    return ui.run_javascript("localStorage.getItem('wallet')")
