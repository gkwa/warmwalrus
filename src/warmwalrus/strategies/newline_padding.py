import pathlib

import warmwalrus.strategies.base


class NewlinePaddingStrategy(warmwalrus.strategies.base.FileProcessingStrategy):
    """Strategy to ensure file starts with a specified number of newlines."""

    def __init__(self, newline_count: int = 20) -> None:
        """
        Initialize the strategy.

        Args:
            newline_count: Number of newlines to ensure at the beginning of file
        """
        self.newline_count = newline_count

    def process(self, content: str, file_path: pathlib.Path) -> str:
        """
        Process content to ensure it starts with the specified number of newlines.

        Args:
            content: The file content to process
            file_path: Path to the file being processed

        Returns:
            Content with proper newline padding at the beginning
        """
        if not content:
            return "\n" * self.newline_count

        # Count existing leading newlines
        leading_newlines = 0
        for char in content:
            if char == "\n":
                leading_newlines += 1
            else:
                break

        if leading_newlines >= self.newline_count:
            return content

        # Add the needed newlines
        needed_newlines = self.newline_count - leading_newlines
        return "\n" * needed_newlines + content

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return f"newline_padding_{self.newline_count}"
