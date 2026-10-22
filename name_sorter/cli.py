"""Command-line adapter for the name-sorting domain."""

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .domain import Name, sort_names

OUTPUT_FILENAME = 'sorted-names-list.txt'


def read_names(path: Path) -> list[Name]:
    """Read UTF-8 names, ignoring blank lines and reporting invalid line numbers."""
    names = []
    with path.open(encoding='utf-8-sig') as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                names.append(Name.parse(line))
            except ValueError as error:
                raise ValueError(f'{path}: line {line_number}: {error}') from error
    return names


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='name-sorter', description='Sort names by surname and given names.')
    parser.add_argument('input_file', type=Path, help='UTF-8 file with one name per line')
    args = parser.parse_args(arguments)

    try:
        names = sort_names(read_names(args.input_file))
        content = ''.join(f'{name}\n' for name in names)
        Path(OUTPUT_FILENAME).write_text(content, encoding='utf-8', newline='\n')
        sys.stdout.write(content)
    except (OSError, ValueError) as error:
        print(f'name-sorter: error: {error}', file=sys.stderr)
        return 1
    return 0
