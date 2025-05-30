import logging
import pathlib
import typing

import warmwalrus.strategies.base


class FileProcessor:
    """Processes files by removing content between markers and applying strategies."""

    START_MARKERS: typing.List[str] = [".......... START ..........", "<response>"]
    END_MARKERS: typing.List[str] = [".......... END ..........", "</response>"]

    def __init__(
        self,
        strategies: typing.Optional[
            typing.List[warmwalrus.strategies.base.FileProcessingStrategy]
        ] = None,
    ) -> None:
        """
        Initialize the file processor.

        Args:
            strategies: List of processing strategies to apply after marker cleanup
        """
        self.strategies = strategies or []

    def needs_processing(self, file_path: pathlib.Path) -> bool:
        """Check if file needs processing (has markers or strategies would modify it)."""
        try:
            content: str = file_path.read_text(encoding="utf-8")

            # Check if file has markers
            if self._has_markers(content):
                return True

            # Check if any strategy would modify the content
            if self.strategies:
                processed_content = self._apply_strategies(content, file_path)
                return processed_content != content

            return False
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return False

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file, returning True if changes were made."""
        try:
            original_content: str = file_path.read_text(encoding="utf-8")

            # First, process markers
            processed_content: str = self._process_content(original_content)

            # Then apply strategies
            if self.strategies:
                processed_content = self._apply_strategies(processed_content, file_path)

            if processed_content != original_content:
                file_path.write_text(processed_content, encoding="utf-8")
                return True

            return False
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            raise

    def _apply_strategies(self, content: str, file_path: pathlib.Path) -> str:
        """Apply all configured strategies to the content."""
        result = content
        for strategy in self.strategies:
            logging.debug(f"Applying strategy {strategy.get_name()} to {file_path}")
            result = strategy.process(result, file_path)
        return result

    def _has_markers(self, content: str) -> bool:
        """Check if content has start or end markers at line beginnings."""
        lines: typing.List[str] = content.splitlines()

        for line in lines:
            stripped_line: str = line.strip()
            if stripped_line in self.START_MARKERS or stripped_line in self.END_MARKERS:
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

            if stripped_line in self.START_MARKERS:
                keep_mode = True
                found_start = True
                continue
            elif stripped_line in self.END_MARKERS:
                keep_mode = False
                continue

            if keep_mode:
                result_lines.append(line)

        # If no START marker was found, return original content
        if not found_start:
            return content

        return "".join(result_lines)
