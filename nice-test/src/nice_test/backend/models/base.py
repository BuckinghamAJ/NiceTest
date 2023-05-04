"""
SQLModel
TODO:
1. Figure out the modal structures of TestDoc

"""
from typing import Optional, Sequence, List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class StepsReqLink(SQLModel, table=True):
    step_id: Optional[int] = Field(default=None, foreign_key="steps.id", primary_key=True)
    req_id: Optional[int] = Field(default=None, foreign_key="requirements.id", primary_key=True)


class StepsTestLink(SQLModel, table=True):
    step_id: Optional[int] = Field(default=None, foreign_key="steps.id", primary_key=True)
    test_id: Optional[int] = Field(default=None, foreign_key="tests.id", primary_key=True)


class ReqTestLink(SQLModel, table=True):
    req_id: Optional[int] = Field(default=None, foreign_key="requirements.id", primary_key=True)
    test_id: Optional[int] = Field(default=None, foreign_key="tests.id", primary_key=True)


class StepDocLink(SQLModel, table=True):
    step_id: Optional[int] = Field(default=None, foreign_key="steps.id", primary_key=True)
    doc_id: Optional[int] = Field(default=None, foreign_key="docs.id", primary_key=True)


class TestDocLink(SQLModel, table=True):
    doc_id: Optional[int] = Field(default=None, foreign_key="docs.id", primary_key=True)
    test_id: Optional[int] = Field(default=None, foreign_key="tests.id", primary_key=True)


class Docs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    system: str
    version: str = Field(default="1.0")
    steps: List["Steps"] = Relationship(back_populates="doc", link_model=StepDocLink)
    tests: List["Tests"] = Relationship(back_populates="doc", link_model=TestDocLink)
    created_at: datetime = Field(default=datetime.now(timezone.utc))


class Steps(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirements: List["Requirements"] = Relationship(back_populates="steps", link_model=StepsReqLink)
    text: str

    doc: Optional[Docs] = Relationship(back_populates="steps", link_model=StepDocLink)
    failed_in_test: List["Tests"] = Relationship(back_populates="failed_steps", link_model=StepsTestLink)
    passed_in_test: List["Tests"] = Relationship(back_populates="passed_steps", link_model=StepsTestLink)


class Requirements(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: str  # Requirement value, example: E-SYS-1101
    description: str  # Requirement criteria, example: "The system shall..."
    steps: List[Steps] = Relationship(back_populates="requirements", link_model=StepsReqLink)
    failed_in_test: List["Tests"] = Relationship(back_populates="failed_reqs", link_model=ReqTestLink)
    passed_in_test: List["Tests"] = Relationship(back_populates="pass_reqs", link_model=ReqTestLink)


class Tests(SQLModel, table=True):
    """Model for storing test results from nicegui"""

    id: Optional[int] = Field(default=None, primary_key=True)
    doc: Optional[Docs] = Relationship(back_populates="tests", link_model=TestDocLink)
    failed_reqs: List[Requirements] = Relationship(back_populates="failed_in_test", link_model=ReqTestLink)
    pass_reqs: List[Requirements] = Relationship(back_populates="passed_in_test", link_model=ReqTestLink)

    failed_steps: List[Steps] = Relationship(back_populates="failed_in_test", link_model=StepsTestLink)
    passed_steps: List[Steps] = Relationship(back_populates="passed_in_test", link_model=StepsTestLink)
    start_time: datetime = Field(default=datetime.now(timezone.utc))
    end_time: Optional[datetime] = Field(default=None)
