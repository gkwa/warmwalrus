import abc
import pathlib


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
