"""
Backend Controller For Nice Test
TODO:
1. Have a way to upload/reuse previous test documents 
    - Should this pull directly from the document or in a database
2. Figure out how I want to store test results (Postgres DB?)
3. Movement of new files uploaded
"""
from abc import ABC, abstractmethod
from nice_test.backend.models.postgres import Postgres


class AbstractTestController(ABC):
    def __init__(self, test_id: str) -> None:
        self._id = test_id

    @abstractmethod
    def get_test(self):
        raise NotImplementedError

    @abstractmethod
    def save_test(self):
        raise NotImplementedError

    @abstractmethod
    def delete_test(self):
        raise NotImplementedError

    @abstractmethod
    def update_test(self):
        raise NotImplementedError
