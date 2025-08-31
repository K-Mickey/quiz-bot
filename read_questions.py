import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Iterable

import aiofiles

import settings
from state_manager import RedisStateManager

log = logging.getLogger(__name__)


class ParagraphParser:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.regex = re.compile(rf'^({pattern})[\d:\s]*(.*)', flags=re.IGNORECASE | re.DOTALL)

    def check(self, text: str) -> bool:
        text = text.strip()
        return bool(self.regex.search(text))

    def parse(self, text: str) -> str:
        text = text.strip()
        match = self.regex.match(text)
        parse_text = match.group(2).strip() if match else text.strip()
        return parse_text.replace("\n", " ")


async def main() -> None:
    start_time = time.perf_counter()

    state_manager = RedisStateManager(settings.REDIS_URL, prefix="")
    await state_manager.questions.clear()

    question_files = read_question_files()
    tasks = [process_file(file, state_manager) for file in question_files]
    await asyncio.gather(*tasks)

    await state_manager.disconnect()

    log.info(f"Read questions from {len(tasks)} files")
    log.info(f"Processing time: {time.perf_counter() - start_time:.2f}")


def read_question_files() -> Iterable[Path]:
    questions_path = settings.QUESTION_DIR
    if not all((questions_path.exists(), questions_path.is_dir())):
        raise FileNotFoundError(f"Questions path {questions_path} does not exist")

    log.debug(f"Starting to read files from {questions_path}")
    return tuple(file for file in questions_path.iterdir() if file.is_file() and file.suffix == ".txt")


async def process_file(file_path: Path, state_manager: RedisStateManager):
    async with aiofiles.open(file_path, "r", encoding="KOI8-R") as open_file:
        file = await open_file.read()

    questions = parse_file(file)
    log.debug(f"Found {len(questions)} questions in file {file_path}")
    await state_manager.questions.save(questions)


def parse_file(text: str) -> list[dict]:
    parsers = {
        'question': ParagraphParser('вопрос'),
        'answer': ParagraphParser('ответ'),
    }

    questions = []
    question_body = {}
    for paragraph in text.split("\n\n"):
        for title, parser in parsers.items():
            if parser.check(paragraph):
                question_body[title] = parser.parse(paragraph)
                break

        if len(question_body) == len(parsers):
            questions.append(question_body)
            question_body = {}

    return questions


if __name__ == "__main__":
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
    asyncio.run(main())
