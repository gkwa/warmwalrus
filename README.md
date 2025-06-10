# warmwalrus

A Python CLI tool for cleaning marker delimiters from files.

## Usage

Clean markers from markdown files in current directory:
```bash
warmwalrus cleanmarkers .
```

Clean markers from Python files with dry run:
```bash
warmwalrus cleanmarkers --ext=py --dry-run /path/to/files
```

Clean markers from files modified in last 2 hours, excluding git directories:
```bash
warmwalrus cleanmarkers --age=2h --exclude=.git --exclude=node_modules /path/to/project
```

## Features

- Removes content between `.......... START ..........` and `.......... END ..........` markers
- Supports multiple file extensions via `--ext` parameter
- Dry run mode with `--dry-run`
- Age-based filtering with `--age` parameter
- Directory exclusion with `--exclude` parameter
- Verbose logging with `-v` or `--verbose`
