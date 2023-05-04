from dataclasses import dataclass
from typing import Union
from sqlmodel import select
from datetime import datetime
from asyncio import run
from nice_test.backend.models.postgres import Postgres
from nice_test.backend.models.base import Tests, Steps, Requirements, Docs
from .base import AbstractTestController


@dataclass
class TestingSteps:
    model: Steps
    passed: bool
    failed: bool


@dataclass
class RunningTest:
    title: str
    steps: list[TestingSteps]
    model: Tests


class TestController(AbstractTestController):
    def __init__(self, test_id: str = None) -> None:
        super().__init__(test_id)
        self.db = Postgres()
        self._test = None

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def test(self) -> RunningTest:
        if self._test is None:
            tm = run(self.get_test())  # Type: Tests
            self._test = self.make_test(tm)
        return self._test

    async def get_test(self) -> Tests:
        """Select Test based on id, if id is None, select based on self.test_id"""
        async with self.db.get_session() as session:
            result = await session.execute(select(Tests).where(Tests.id == self.id)).first()
            return result

    async def create_test(self, doc: Docs) -> Tests:
        """Create a new test based on a document"""
        async with self.db.get_session() as session:
            test = Tests(doc=doc)
            await session.add(test)
            await session.commit()
            self.id = test.id
        return test

    async def get_documents(self, newer_than: datetime = None) -> list[Docs]:
        async with self.db.get_session() as session:
            if newer_than:
                result = await session.execute(select(Docs).where(Docs.created_at > newer_than)).all()
            else:
                result = await session.execute(select(Docs)).all()
        return result

    async def get_tests(self) -> list[Tests]:
        """Get all tests that have not been finished yet"""
        async with self.db.get_session() as session:
            result = await session.execute(select(Tests).where(Tests.end_time != None)).all()
        return result

    def make_test(self, test_model: Tests) -> RunningTest:
        test_steps = [TestingSteps(step=s, passed=False, failed=False) for s in test_model.doc.steps]

        return RunningTest(title=test_model.doc.title, steps=test_steps, model=test_model)

    async def save_test(self):
        running_test = self.test
        passed = []
        failed = []
        for step in running_test.steps:
            if step.passed:
                passed.append(step.model)
            elif step.failed:
                failed.append(step.model)

        running_test.model.passed = passed
        running_test.model.failed = failed

        async with self.db.get_session() as session:
            await session.add(running_test.model)
            await session.commit()

    async def delete_test(self):
        async with self.db.get_session() as session:
            result = await session.execute(select(Tests).where(Tests.id == self.id)).first()
            await session.delete(result)
            await session.commit()

    async def update_test(self):
        pass
