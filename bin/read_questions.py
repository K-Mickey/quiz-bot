import re
from pathlib import Path
import logging
from typing import Iterable

from bin.redis import RedisStateManager
from bin.tg import settings

log = logging.getLogger(__name__)


def main() -> None:
    database = RedisStateManager(settings.REDIS_URL)
    file_number = question_number = 0

    for file in read_question_files():
        with open(file, "r", encoding="KOI8-R") as open_file:
            file = open_file.read()
        file_number += 1

        for question in parse_file(file):
            question_number += 1
            # TODO: add append to database

    log.info(f"Read {question_number} questions from {file_number} files")


def read_question_files() -> Iterable:
    base_path = Path(__file__).parent.parent
    questions_path = base_path / "questions"

    if not all((questions_path.exists(), questions_path.is_dir())):
        raise FileNotFoundError(f"Questions path {questions_path} does not exist")

    log.debug(f"Starting to read files from {questions_path}")

    for file in questions_path.iterdir():
        if file.is_file() and file.suffix == ".txt":
            yield file


def parse_file(text: str) -> list[dict]:
    titles = {
        "вопрос": "question",
        "ответ": "answer",
    }

    paragraphs = text.split("\n\n")

    questions = []
    question_body = {}
    for paragraph in paragraphs:
        head_and_body = paragraph.strip().split("\n", 1)

        try:
            head, body = head_and_body
        except ValueError:
            log.debug(f"Can't parse head and body from {paragraph}")
            continue

        try:
            title = re.search(r"\w+", head.lower()).group()
        except AttributeError:
            log.warning(f"Can't parse title from {head}")
            continue

        body = body.replace("\n", " ")
        question_body[titles[title]] = body

        if len(question_body) == len(titles):
            questions.append(question_body)
            question_body = {}

    log.debug(f"Found {len(questions)} questions in file")
    return questions


if __name__ == "__main__":
    main()
