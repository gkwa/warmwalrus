import logging
import pathlib
import re

import warmwalrus.strategies.base


class ClaudeUrlStrategy(warmwalrus.strategies.base.FileProcessingStrategy):
    """Strategy to extract Claude discussion URLs and prepend them to processed content."""

    def __init__(self) -> None:
        """Initialize the strategy."""
        # Pattern to match Claude discussion URLs in reference text
        # More flexible pattern to catch variations
        self.claude_url_pattern = re.compile(
            r"Claude discussion:\s*(https://claude\.ai/chat/[a-f0-9-]+)", re.IGNORECASE
        )
        self.logger = logging.getLogger(__name__)

    def process(self, content: str, file_path: pathlib.Path) -> str:
        """
        Extract Claude URL from the full document and prepend it to the processed content.

        Note: This strategy should be applied AFTER marker processing, so the content
        passed here is already the extracted content between START/END markers.
        To access the full document, we need to read the original file.

        Args:
            content: The already processed content (between markers)
            file_path: Path to the file being processed

        Returns:
            Content with Claude URL prepended if found
        """
        self.logger.debug(f"Processing file {file_path} with claude_url strategy")

        try:
            # Read the full original file to search for the Claude URL
            full_content = file_path.read_text(encoding="utf-8")
            self.logger.debug(f"Read {len(full_content)} characters from {file_path}")

            # Search for Claude discussion URL in the full document
            match = self.claude_url_pattern.search(full_content)

            if match:
                claude_url = match.group(1).strip()
                self.logger.info(f"Found Claude URL in {file_path}: {claude_url}")

                # Prepend the URL to the processed content with proper spacing
                if content.strip():
                    self.logger.debug(
                        f"Prepending Claude URL to existing content ({len(content)} chars)"
                    )
                    # Add the URL with spacing before the existing content
                    return f"\n\n\n\n\n{claude_url}\n\n\n\n\n{content}"
                else:
                    self.logger.debug(
                        "No existing content, returning just the Claude URL"
                    )
                    # If no content, just return the URL
                    return claude_url
            else:
                self.logger.debug(f"No Claude URL found in {file_path}")

            # No Claude URL found, return content unchanged
            return content

        except Exception as e:
            self.logger.error(
                f"Error processing {file_path} with claude_url strategy: {e}"
            )
            # If there's any error reading the file, return content unchanged
            return content

    def get_name(self) -> str:
        """Get the name of this strategy."""
        return "claude_url"
