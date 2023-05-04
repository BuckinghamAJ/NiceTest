"""
General Page for the different Tests
"""
from nice_test.app.theme import frame
from nicegui import ui


@ui.page('/test')
def test():
    with frame('Home'):
        ui.label('This is a Test Page')
