from nicegui import ui
from fastapi.responses import RedirectResponse


def navbar() -> None:
    with ui.tabs():
        ui.button('Home', on_click=lambda: ui.open('/')).props('icon=home')
        ui.button('Testing', on_click=lambda: ui.open('/test')).props('icon=info')
