import logging
import pathlib
import time
import typing


class FileFinder:
    """Finds files to process based on criteria."""

    def __init__(
        self,
        extension: str,
        excludes: typing.List[str],
        age_filter: typing.Optional[float] = None,
    ) -> None:
        self.extension: str = extension
        self.excludes: typing.List[str] = excludes
        self.age_filter: typing.Optional[float] = age_filter

    def find_files(self, paths: typing.List[str]) -> typing.List[pathlib.Path]:
        """Find files matching the criteria."""
        files: typing.List[pathlib.Path] = []

        for path_str in paths:
            path: pathlib.Path = pathlib.Path(path_str)

            if path.is_file():
                if self._should_process_file(path):
                    files.append(path)
            elif path.is_dir():
                files.extend(self._find_files_in_directory(path))
            else:
                logging.warning(f"Path does not exist: {path}")

        logging.info(f"Found {len(files)} files to process")
        return files

    def _find_files_in_directory(
        self, directory: pathlib.Path
    ) -> typing.List[pathlib.Path]:
        """Recursively find files in directory."""
        files: typing.List[pathlib.Path] = []

        try:
            for item in directory.iterdir():
                if item.is_file():
                    if self._should_process_file(item):
                        files.append(item)
                elif item.is_dir():
                    if not self._should_exclude_directory(item):
                        files.extend(self._find_files_in_directory(item))
        except PermissionError:
            logging.warning(f"Permission denied accessing: {directory}")

        return files

    def _should_process_file(self, file_path: pathlib.Path) -> bool:
        """Check if file should be processed."""
        # Check extension
        if not file_path.name.endswith(f".{self.extension}"):
            return False

        # Check age filter
        if self.age_filter is not None:
            try:
                file_mtime: float = file_path.stat().st_mtime
                current_time: float = time.time()
                age_seconds: float = current_time - file_mtime

                # If file is OLDER than the age limit, skip it
                if age_seconds > self.age_filter:
                    return False
            except OSError:
                logging.warning(f"Could not check modification time for: {file_path}")
                return False

        return True

    def _should_exclude_directory(self, directory: pathlib.Path) -> bool:
        """Check if directory should be excluded."""
        abs_path_str: str = str(directory.absolute())

        for exclude in self.excludes:
            if exclude in abs_path_str:
                logging.debug(f"Excluding directory: {directory}")
                return True

        return False
