import re


def parse_answer(answer: str) -> str:
    real_answer = answer.lower()
    root_answer = re.search(r"[\w\s,]+", real_answer)
    return root_answer.group() if root_answer else real_answer
