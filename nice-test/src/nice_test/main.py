from pathlib import Path
from nice_test.backend.api import NiceTestAPI
from nice_test.app.frontend import init
import sys
import ntlog

from nice_test import __app_name__, __version__

debug = False  # TODO: Change to based on configuration

# ntlog.load(app_name=__app_name__, app_version=__version__, debug=debug)

app = NiceTestAPI()

init(app)
