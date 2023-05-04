# Build a Document Controller that will pull word documents from ./docs/in,
# parse the lines, pull out the requirements based on regex, and place information into a database.
from io import StringIO, BytesIO
from pathlib import Path
from typing import Union

from nice_test.backend.models.postgres import Postgres
from nice_test.backend.models.base import Steps, Docs, Requirements
from docx import Document
from sqlmodel import select


class DocController:
    def __init__(self, doc_path: Path, file_suffix: str) -> None:
        self.path = doc_path or Path("../docs")
        self.suffix = file_suffix
        self.db = Postgres()

    def set_dirs(self):
        self.in_dir = Path(self.path, "in")
        self.saved_dir = Path(self.path, "saved")
        self.error_dir = Path(self.path, "error")

    def get_docs(self) -> list[Path]:
        return [doc for doc in self.in_dir.iterdir() if doc.suffix == self.suffix]

    def parse_docs(self):
        raise NotImplementedError


class WordDocController(DocController):
    def __init__(self, doc_path: Path, file_suffix: str = '.docx') -> None:
        super().__init__(doc_path, file_suffix)

    async def parse_docs(self, docs: list[Union[str, Path]] = None) -> Docs:
        # Parse docs line by line, regex for requirements, create Step objects
        from .common import bracket_pattern

        if docs is None:
            docs = self.get_docs()
        steps = []
        print(docs)

        for doc in docs:
            if isinstance(doc, str):
                doc = Path(doc)
            if doc.suffix != self.suffix:
                continue

            with open(doc, 'rb') as f:
                source_stream = BytesIO(f.read())
            document = Document(source_stream)
            source_stream.close()
            for line in document.paragraphs:
                text = line.text
                # Regex for requirements, example: [E-SYS-1101]
                reqs = bracket_pattern.findall(text)

                req_models = await self.select_requirements(reqs)
                print(f"Req Models -> {req_models}")
                if reqs:
                    step = Steps(text=text, requirements=req_models)
                else:
                    step = Steps(text=line)
                steps.append(step)
                print(f"Steps -> {steps}")

            doc_model = Docs(title=doc.stem, system='Test System', version='1.0', steps=steps)

            await self.store_doc(doc_model)
            return doc_model

    async def select_requirements(self, reqs: list[str]) -> list[Requirements]:
        """
        Search for requirements in the database based on step parsing (i.e reqs)
        If none found, create a new requirement
        :param reqs: list of requirements
        """

        # Search for requirements in the database
        async with self.db.get_session() as session:
            sql = select(Requirements).where(Requirements.value.in_(reqs))

            results = await session.execute(sql)
            results = results.fetchall()

            found_reqs = [result.value for result in results]
            print(f"Found reqs -> {reqs}")
            if len(found_reqs) == len(reqs):
                return results

            # If none found, create a new requirement
            for req in reqs:
                if req not in found_reqs:
                    new_req = Requirements(value=req)
                    print(f"New Requirement -> {new_req}")
                    await session.add(new_req)
                    results.append(new_req)
            else:
                await session.commit()

            return results

    async def store_doc(self, doc: Docs):
        """
        Store the document in the database
        Relationship in SQLModel automatically creates the steps and requirements
        """
        async with self.db.get_session() as session:
            session.add(doc)
            session.commit()
