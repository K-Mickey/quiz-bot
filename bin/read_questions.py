import re
from dataclasses import dataclass
from pathlib import Path
import logging
import random

log = logging.getLogger(__name__)


@dataclass(slots=True)
class Question:
    question: str = ""
    answer: str = ""
    comment: str = ""
    source: str = ""
    author: str = ""


def get_random_question():
    base_path = Path(__file__).parent.parent
    questions_path = base_path / "questions"

    if not all((questions_path.exists(), questions_path.is_dir())):
        raise FileNotFoundError(f"Questions path {questions_path} does not exist")

    log.debug(f"Starting to read files from {questions_path}")
    file_path = random.choice(read_files(questions_path))

    with open(file_path, "r", encoding="KOI8-R") as open_file:
        file = open_file.read()

    return random.choice(parse_file(file))


def read_files(questions_path: Path) -> tuple[str, ...]:
    all_files = tuple(file for file in questions_path.iterdir() if file.is_file())
    count_files = len(all_files)
    log.debug(f"Read {count_files} files")
    return all_files


def parse_file(text: str) -> list[Question]:
    titles = {
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
        title = re.search(r"\w+", head.lower()).group()
        if title not in titles:
            continue

        if title == "вопрос" and question.question:
            questions.append(question)
            question = Question()

        body = body.replace("\n", " ")
        setattr(question, titles[title], body)

    if question.question:
        questions.append(question)

    log.debug(f"Found {len(questions)} questions")
    return questions
