import logging
import pathlib
import time
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
        age_filter: typing.Optional[float] = None,
    ) -> None:
        """
        Initialize the file processor.

        Args:
            strategies: List of processing strategies to apply after marker cleanup
            age_filter: Age filter in seconds (same as used by FileFinder)
        """
        self.strategies = strategies or []
        self.age_filter = age_filter

    def needs_processing(self, file_path: pathlib.Path) -> bool:
        """Check if file needs processing (has markers or strategies would modify it)."""
        try:
            # First check if file meets age criteria (same logic as FileFinder)
            if not self._meets_age_criteria(file_path):
                return False

            content: str = file_path.read_text(encoding="utf-8")

            # Check if file has markers
            if self._has_markers(content):
                return True

            # Check if any strategy would modify the content or rename the file
            if self.strategies:
                for strategy in self.strategies:
                    if strategy.is_renaming_strategy():
                        # For renaming strategies, check if rename would happen
                        new_path = strategy.rename_file(file_path)
                        if new_path and new_path != file_path:
                            return True
                    else:
                        # For content strategies, check if content would change
                        processed_content = strategy.process(content, file_path)
                        if processed_content != content:
                            return True

            return False
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            return False

    def process_file(self, file_path: pathlib.Path) -> bool:
        """Process a single file, returning True if changes were made."""
        try:
            original_content: str = file_path.read_text(encoding="utf-8")
            changes_made = False

            # First, apply renaming strategies
            current_path = file_path
            for strategy in self.strategies:
                if strategy.is_renaming_strategy():
                    new_path = strategy.rename_file(current_path)
                    if new_path and new_path != current_path:
                        current_path = new_path
                        changes_made = True

            # Then, process markers
            processed_content: str = self._process_content(original_content)

            # Then apply content strategies
            for strategy in self.strategies:
                if not strategy.is_renaming_strategy():
                    processed_content = strategy.process(
                        processed_content, current_path
                    )

            if processed_content != original_content:
                current_path.write_text(processed_content, encoding="utf-8")
                changes_made = True

            return changes_made
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

    def _meets_age_criteria(self, file_path: pathlib.Path) -> bool:
        """Check if file meets age criteria (same logic as FileFinder)."""
        if self.age_filter is None:
            return True

        try:
            file_mtime: float = file_path.stat().st_mtime
            current_time: float = time.time()
            age_seconds: float = current_time - file_mtime

            # If file is OLDER than the age limit, skip it
            return age_seconds <= self.age_filter
        except OSError:
            logging.warning(f"Could not check modification time for: {file_path}")
            return False
