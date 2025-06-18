import logging
import pathlib
import re
import typing

import pathvalidate

import warmwalrus.strategies.base


class FileRenamerStrategy(warmwalrus.strategies.base.FileProcessingStrategy):
    """Strategy to rename files based on CLAUDE_THREAD_TITLE found in the content."""

    # Placeholder value to skip when searching for actual titles
    TITLE_PLACEHOLDER: str = "{title}"

    def __init__(self) -> None:
        """Initialize the strategy."""
        # Pattern to match CLAUDE_THREAD_TITLE line
        self.thread_title_pattern = re.compile(
            r"CLAUDE_THREAD_TITLE:\s*(.+?)(?:\s*</boilerplate_text>|\s*$)",
            re.IGNORECASE | re.MULTILINE,
        )
        self.logger = logging.getLogger(__name__)

    def is_renaming_strategy(self) -> bool:
        """Return True since this strategy renames files."""
        return True

    def rename_file(self, file_path: pathlib.Path) -> typing.Optional[pathlib.Path]:
        """
        Rename the file based on CLAUDE_THREAD_TITLE found in the content.

        Args:
            file_path: Path to the file to rename

        Returns:
            New path if renamed, None if not renamed
        """
        self.logger.debug(f"Processing file {file_path} with file_renamer strategy")

        try:
            full_content = file_path.read_text(encoding="utf-8")
            self.logger.debug(f"Read {len(full_content)} characters from {file_path}")
        except UnicodeDecodeError as e:
            self.logger.error(f"Cannot read {file_path} as UTF-8: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None

        # Find all CLAUDE_THREAD_TITLE matches in the document
        matches = list(self.thread_title_pattern.finditer(full_content))
        if not matches:
            self.logger.debug(f"No CLAUDE_THREAD_TITLE found in {file_path}")
            return None

        # Look for the first non-placeholder title
        actual_title = None
        for match in matches:
            title = match.group(1).strip()
            if title != self.TITLE_PLACEHOLDER:
                actual_title = title
                self.logger.info(
                    f"Found actual CLAUDE_THREAD_TITLE in {file_path}: {title}"
                )
                break
            else:
                self.logger.debug(
                    f"Skipping placeholder title '{self.TITLE_PLACEHOLDER}' in {file_path}"
                )

        if not actual_title:
            self.logger.debug(f"Only placeholder titles found in {file_path}")
            return None

        # Clean the title for use as filename
        clean_title = self._sanitize_filename(actual_title)
        if not clean_title:
            self.logger.warning(
                f"Title '{actual_title}' resulted in empty filename after sanitization"
            )
            return None

        # Create new filename with .md extension
        new_filename = f"{clean_title}.md"
        new_path = file_path.parent / new_filename

        # Check if rename is needed
        if new_path == file_path:
            self.logger.debug(f"File {file_path} already has the correct name")
            return file_path

        # Check if target already exists
        if new_path.exists():
            self.logger.warning(
                f"Cannot rename {file_path} to {new_path}: target file already exists"
            )
            return None

        # Perform the rename
        try:
            file_path.rename(new_path)
            self.logger.info(f"Successfully renamed {file_path} to {new_path}")
            return new_path
        except OSError as e:
            self.logger.error(f"Failed to rename {file_path} to {new_path}: {e}")
            return None

    def process(self, content: str, file_path: pathlib.Path) -> str:
        """
        This method is kept for compatibility but renaming happens via rename_file().

        Args:
            content: The file content (unused for renaming)
            file_path: Path to the file being processed (unused)

        Returns:
            Content unchanged
        """
        # For renaming strategies, the actual work is done in rename_file()
        return content

    def _sanitize_filename(self, title: str) -> str:
        """
        Sanitize the title to make it suitable for use as a filename.

        Args:
            title: The raw title string

        Returns:
            Sanitized filename string
        """
        if not title or not title.strip():
            return ""

        # Use pathvalidate to handle cross-platform filename sanitization
        # replacement_text=" " preserves spaces instead of using underscores
        sanitized = pathvalidate.sanitize_filename(title, replacement_text=" ")

        # Limit length to reasonable filename length (most filesystems support 255 chars)
        # Leave room for .md extension (3 chars)
        max_length = 200
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip()

        # Final cleanup
        sanitized = sanitized.strip()

        # Final check - ensure we still have something left
        if not sanitized:
            return ""

        return sanitized

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "file_renamer"
