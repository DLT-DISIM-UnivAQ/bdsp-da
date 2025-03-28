from nicegui import ui, app

@ui.page("/logout")
def logout():
    app.storage.user.clear()
    ui.navigate.to('/')
