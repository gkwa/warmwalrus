import logging
import sys


class LoggerSetup:
    """Handles logging configuration for the application."""

    def setup_main_logging(self, verbose_count: int) -> None:
        """Configure main app logging based on verbosity level."""
        log_levels = {
            0: logging.WARNING,  # Only warnings and errors
            1: logging.INFO,  # Command execution info
            2: logging.DEBUG,  # Detailed debugging
        }

        level = log_levels.get(verbose_count, logging.DEBUG)

        # Configure main logger
        main_logger = logging.getLogger()
        if not main_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("MAIN %(levelname)s: %(message)s"))
            main_logger.addHandler(handler)
        main_logger.setLevel(level)

    def setup_subcommand_logging(self, verbose_count: int) -> None:
        """Configure subcommand logging based on verbosity level."""
        # Subcommand verbosity controls different output than main app verbosity
        # This is for internal subcommand logging only
        sub_log_levels = {
            0: logging.ERROR,  # Only errors
            1: logging.WARNING,  # Warnings and errors
            2: logging.INFO,  # Info, warnings, errors
            3: logging.DEBUG,  # Everything
        }

        level = sub_log_levels.get(verbose_count, logging.DEBUG)

        # Create subcommand logger
        sub_logger = logging.getLogger("subcommand")
        if not sub_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("SUB %(levelname)s: %(message)s"))
            sub_logger.addHandler(handler)
        sub_logger.setLevel(level)

    def setup_logging(self, verbose_count: int) -> None:
        """Legacy method for backward compatibility."""
        self.setup_main_logging(verbose_count)
