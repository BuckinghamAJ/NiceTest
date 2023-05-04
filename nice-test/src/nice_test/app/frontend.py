from fastapi import FastAPI
from nicegui import ui
from nice_test.app.pages import home, test
from nice_test import ntlog
import logging

log = logging.getLogger(__name__)


# Modularization of nice gui example: https://github.com/zauberzeug/nicegui/tree/main/examples/modularization


def init(app: FastAPI):
    @app.get('/testing')
    async def testing():
        log.info('Testing')
        return {'hello': 'world'}

    # Register the pages
    home(app)
    test()

    ui.run_with(app, title='Nice Test')
