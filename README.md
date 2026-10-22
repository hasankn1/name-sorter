# Name sorter

A small Python command-line application that sorts names by surname, then by all given names in order. Requires Python 3.10 or newer; no third-party dependencies or installation required.

## Run

From this repository directory on macOS/Linux:

```sh
./name-sorter ./unsorted-names-list.txt
```

Portable alternative (including Windows):

```sh
python3 name-sorter ./unsorted-names-list.txt
```

On Windows, use `py -3` instead of `python3` if needed. You can also run `python3 -m name_sorter ./unsorted-names-list.txt` from the repository root. To use the exact command `name-sorter` without `./`, add the repository directory to your PATH.

Sorted names are printed to stdout and written to `sorted-names-list.txt` **in the current working directory**, overwriting any existing contents. Relative input paths are resolved from that same directory. The provided sample preserves `Vaugh Lewis`; the assessment's expected output spells it `Vaughn Lewis`, which appears to be a typo.

## Verify

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q name_sorter
```

Tests cover surname ordering, ties across all given names, duplicate preservation, empty input, whitespace, Unicode, the supplied example, 1,000 names, output location and overwrite behavior, arguments, invalid names, encoding errors, and filesystem failures. Integration tests run the real command in isolated temporary directories.

GitHub Actions validates compilation and runs the tests on Python 3.10 and 3.14, on Linux and Windows. The workflow is provided; hosted execution occurs after pushing to GitHub.

## Decisions and boundaries

- The final whitespace-separated token is the surname; preceding tokens are one to three given names. Compound surnames require a different input format and are outside this assessment's model.
- Ordering uses Python's deterministic, case-sensitive Unicode string comparison, without locale-specific collation. Given names are compared as a sequence; a shorter matching prefix sorts first.
- Blank lines are ignored. Whitespace between name parts is normalized to one space. Spelling, case, punctuation, accents, and duplicates are preserved.
- Input is UTF-8, with an optional BOM; Windows and Unix input line endings are accepted. Output is UTF-8 with LF line endings and a final newline when nonempty.
- Invalid input is rejected with a physical line number before output is overwritten. Empty input produces an empty output file.
- Usage errors exit with code 2; input, validation, and I/O errors exit with code 1 and a message on stderr; success exits with code 0.
- The output is written before success is printed. Writes are ordinary filesystem overwrites, not transactional writes; interruption during a write may leave partial output.

## Design

`name_sorter/domain.py` owns the immutable `Name` value object, validation, and pure sorting function. `name_sorter/cli.py` owns argument handling, input parsing with line context, and file/console orchestration. `name-sorter` is a thin executable entry point.

These responsibilities can change independently: the ordering function has no filesystem or console dependency, and another adapter can reuse it directly. Standard `Iterable` and `Sequence` contracts keep boundaries small. No inheritance, factories, or custom sorting algorithm are necessary for this scope; adding them would make the code harder to navigate without a concrete benefit. This applies SOLID proportionately, particularly single responsibility and keeping domain logic independent of I/O.

Sorting takes O(n log n) comparisons and O(n) memory for bounded-length names. This is appropriate for the assessment's thousand-name input. There is no artificial limit on input count.
