import re
from dataclasses import dataclass
from pathlib import Path
import logging
import random
from typing import Generator

log = logging.getLogger(__name__)


@dataclass(slots=True)
class Question:
    question: str = ""
    answer: str = ""
    comment: str = ""
    source: str = ""
    author: str = ""


def get_random_question():
    for file in read_files():
        return random.choice(parse_file(file))


def read_files() -> Generator[str, None, None]:
    base_path = Path(__file__).parent.parent
    questions_path = base_path / "questions"

    if not all((questions_path.exists(), questions_path.is_dir())):
        log.error(f"Questions path {questions_path} does not exist")
        exit(1)

    log.debug(f"Starting to read files from {questions_path}")

    counter = 0
    for file in questions_path.iterdir():
        if not file.is_file():
            log.debug(f"File {file} is not a file")
            continue

        counter += 1
        with open(file, "r", encoding="KOI8-R") as open_file:
            yield open_file.read()

    log.debug(f"Finished reading files from {questions_path}")
    log.info(f"Read {counter} files")


def parse_file(text: str) -> list[Question]:
    key_words = {
        "вопрос": "question",
        "ответ": "answer",
        "комментарий": "comment",
        "источник": "source",
        "автор": "author",
    }

    paragraphs = text.split("\n\n")
    questions = []
    question = Question()
    for paragraph in paragraphs:
        head_and_body = paragraph.split("\n", 1)
        if len(head_and_body) != 2:
            continue

        head, body = head_and_body
        header = re.search(r"\w+", head.lower()).group()
        if header not in key_words:
            continue

        if header == "вопрос" and question.question:
            questions.append(question)
            question = Question()

        body = body.replace("\n", " ")
        setattr(question, key_words[header], body)

    if question.question:
        questions.append(question)

    log.debug(f"Found {len(questions)} questions")
    return questions
