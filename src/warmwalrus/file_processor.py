import logging
import pathlib
import typing


class FileProcessor:
    """Processes files by removing content between markers."""

    START_MARKER: str = ".......... START .........."
    END_MARKER: str = ".......... END .........."

    def needs_processing(self, file_path: pathlib.Path) -> bool:
        """Check if file needs processing (has markers)."""
        try:
            content: str = file_path.read_text(encoding="utf-8")
            return self._has_markers(content)
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return False

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file, returning True if changes were made."""
        try:
            original_content: str = file_path.read_text(encoding="utf-8")
            processed_content: str = self._process_content(original_content)

            if processed_content != original_content:
                file_path.write_text(processed_content, encoding="utf-8")
                return True

            return False
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            raise

    def _has_markers(self, content: str) -> bool:
        """Check if content has start or end markers at line beginnings."""
        lines: typing.List[str] = content.splitlines()

        for line in lines:
            if line.strip() == self.START_MARKER or line.strip() == self.END_MARKER:
                return True

        return False

    def _process_content(self, content: str) -> str:
        """Process content by keeping only what's between markers."""
        lines: typing.List[str] = content.splitlines(keepends=True)
        result_lines: typing.List[str] = []
        keep_mode: bool = False
        found_start: bool = False

        for line in lines:
            stripped_line: str = line.strip()

            if stripped_line == self.START_MARKER:
                keep_mode = True
                found_start = True
                continue
            elif stripped_line == self.END_MARKER:
                keep_mode = False
                continue

            if keep_mode:
                result_lines.append(line)

        # If no START marker was found, return original content
        if not found_start:
            return content

        return "".join(result_lines)
