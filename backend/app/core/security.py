from uuid import uuid4


def request_id() -> str:
    return str(uuid4())

