from fastapi import FastAPI
from nice_test.app import frontend
from .controllers.doc import WordDocController
from .controllers.testing import TestController
import sys
from pathlib import Path


class NiceTestAPI(FastAPI):
    def __init__(self):
        super().__init__()
        self.doc_controller = WordDocController(doc_path=Path(sys.prefix, 'share', 'docs'))
        self.test_controller = TestController()


def start_up() -> NiceTestAPI:
    api = NiceTestAPI()
    frontend.init(api)
    return api
