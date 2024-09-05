import hashlib


def hash(string: str) -> str:
    hash = hashlib.sha384()
    hash.update(
        bytes(
            string,
            "utf-8"
        )
    )
    return hash.hexdigest()

