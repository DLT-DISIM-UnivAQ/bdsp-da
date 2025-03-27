from nicegui import ui
from src.pages.login import login_page
from src.pages.dashboard import dashboard_page
from src.pages.upload import upload_page
from src.pages.nfts import nfts_page
from src.pages.documents import documents_page

def main():
    ui.page("/")(login_page)
    ui.page("/dashboard")(dashboard_page)
    ui.page("/upload")(upload_page)
    ui.page("/nfts")(nfts_page)
    ui.page("/documents")(documents_page)
    
    ui.run(title='NICGUI Document Manager', port=8081)

if __name__ in {"__main__", "__mp_main__"}:
    main()
