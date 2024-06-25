from .parser import parse_new


def parse_str(text: str):
    return parse_new(text)


def parse_file(filename: str):
    with open(filename, "r") as f:
        return parse_new(f.read())


__all__ = ["parse_str", "parse_file"]
