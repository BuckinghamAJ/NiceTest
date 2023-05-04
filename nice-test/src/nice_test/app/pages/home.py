"""
Building the Home Page
"""
from functools import partial
from pathlib import Path
from nice_test.app.theme import frame
from nice_test.app.components import file_picker
from nicegui import ui, app
import logging

log = logging.getLogger(__name__)


async def pick_file(ctrl) -> None:
    result = await file_picker('~', multiple=False)
    if result:
        try:
            dm = await ctrl.parse_docs(result)
            ui.notify(f'File Chosen: {dm.title}')
        except Exception as e:
            log.error(f'Error: {e}')
            ui.notify(f'Error: {e}')
    else:
        ui.notify('No File Chosen')


def view(app):
    @ui.page('/')
    def home():
        with frame('Home'):
            with ui.row():
                ui.label('Welcome to the home page!')
            with ui.row():
                pick = partial(pick_file, app.doc_controller)
                ui.button('Choose file', on_click=pick).props('icon=folder')
