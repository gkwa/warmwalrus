import abc
import pathlib
import typing


class FileProcessingStrategy(abc.ABC):
    """Abstract base class for file processing strategies."""

    @abc.abstractmethod
    def process(self, content: str, file_path: pathlib.Path) -> str:
        """
        Process file content and return modified content.

        Args:
            content: The file content to process
            file_path: Path to the file being processed

        Returns:
            The processed content
        """
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """Get the name of this strategy."""
        pass

    def is_renaming_strategy(self) -> bool:
        """Return True if this strategy renames files."""
        return False

    def rename_file(self, file_path: pathlib.Path) -> typing.Optional[pathlib.Path]:
        """
        Rename the file if this is a renaming strategy.
        Args:
            file_path: Path to the file to potentially rename
        Returns:
            New path if renamed, None if not renamed or not a renaming strategy
        """
        return None
