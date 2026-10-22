"""Name validation and ordering, independent of the command line and filesystem."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Name:
    given_names: tuple[str, ...]
    surname: str

    def __post_init__(self) -> None:
        parts = (*self.given_names, self.surname)
        if not 1 <= len(self.given_names) <= 3:
            raise ValueError('expected one to three given names followed by a surname')
        if any(not part or any(c.isspace() for c in part) for part in parts):
            raise ValueError('each name part must be a nonempty word')

    @classmethod
    def parse(cls, text: str) -> 'Name':
        parts = text.split()
        if not 2 <= len(parts) <= 4:
            raise ValueError('expected one to three given names followed by a surname')
        return cls(tuple(parts[:-1]), parts[-1])

    def __str__(self) -> str:
        return ' '.join((*self.given_names, self.surname))


def sort_names(names: Iterable[Name]) -> list[Name]:
    """Return a new list ordered by surname, then given names in sequence."""
    return sorted(names, key=lambda name: (name.surname, name.given_names))
