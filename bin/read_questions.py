import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import logging
import random
from typing import Self

log = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True, eq=True)
class Question:
    question: str = ""
    answer: str = ""
    comment: str = ""
    source: str = ""
    author: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        titles = {
            "вопрос": "question",
            "ответ": "answer",
            "комментарий": "comment",
            "источник": "source",
            "автор": "author",
        }
        return cls(**{titles[title]: value for title, value in data.items() if title in titles})


def get_random_question() -> Question:
    questions = get_questions()
    return random.choice(questions)

@lru_cache(maxsize=None)
def get_questions() -> tuple[Question, ...]:
    path = find_path()
    files = read_txt_files(path)

    questions = []
    for file in files:
        with open(file, "r", encoding="KOI8-R") as open_file:
            file = open_file.read()
        questions += parse_file(file)

    log.info(f"Read {len(questions)} questions from {len(files)} files")
    return tuple(questions)


def find_path() -> Path:
    base_path = Path(__file__).parent.parent
    questions_path = base_path / "questions"

    if not all((questions_path.exists(), questions_path.is_dir())):
        raise FileNotFoundError(f"Questions path {questions_path} does not exist")

    log.debug(f"Starting to read files from {questions_path}")
    return questions_path


def read_txt_files(questions_path: Path) -> tuple[str, ...]:
    all_files = tuple(file for file in questions_path.iterdir() if file.is_file() and file.suffix == ".txt")
    count_files = len(all_files)
    log.debug(f"Read {count_files} files")
    return all_files


def parse_file(text: str) -> list[Question]:

    paragraphs = text.split("\n\n")
    primary_title = 'вопрос'

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

        if title == primary_title and primary_title in question_body:
            questions.append(Question.from_dict(question_body))
            question_body = {}

        body = body.replace("\n", " ")
        question_body[title] = body

    if primary_title in question_body:
        questions.append(Question.from_dict(question_body))

    log.debug(f"Found {len(questions)} questions in file")
    return questions
