import argparse
import importlib.metadata
import logging
import pathlib
import sys
import typing

import warmwalrus.age_parser
import warmwalrus.file_finder
import warmwalrus.file_processor
import warmwalrus.logger
import warmwalrus.strategies.registry


class CLIHandler:
    """Handles command line interface operations."""

    def setup_cleanmarkers_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup the cleanmarkers subcommand parser."""
        parser.add_argument(
            "paths", nargs="+", help="One or more directory or file paths to process"
        )

        parser.add_argument(
            "--ext", default="md", help="File extension to process (default: md)"
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

        parser.add_argument(
            "--exclude",
            action="append",
            default=[],
            help="Exclude directories containing this substring (can be used multiple times)",
        )

        parser.add_argument(
            "--age",
            help="Only process files modified within this time (e.g., 10m, 1d, 2.3w)",
        )

        parser.add_argument(
            "--strategies",
            action="append",
            default=[],
            help="Apply additional processing strategies (can be used multiple times). Available: newline_padding, claude_url, file_renamer",
        )

        parser.add_argument(
            "--no-claude-url",
            action="store_true",
            help="Disable the default claude_url strategy",
        )

        parser.add_argument(
            "--allow-overwrite",
            action="store_true",
            default=True,
            help="Allow overwriting existing files when renaming (default: True)",
        )

        parser.add_argument(
            "--no-overwrite",
            action="store_true",
            help="Prevent overwriting existing files when renaming",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Increase subcommand verbosity (can be used multiple times)",
        )

    def handle_version(self, args: argparse.Namespace) -> None:
        """Handle the version command."""
        version: str = importlib.metadata.version("warmwalrus")
        print(f"warmwalrus {version}")

        logging.info("Version command executed")

    def handle_cleanmarkers(self, args: argparse.Namespace) -> None:
        """Handle the cleanmarkers command."""
        logging.info("Starting cleanmarkers command")
        logging.debug(
            f"Arguments: paths={args.paths}, ext={args.ext}, dry_run={args.dry_run}, excludes={args.exclude}, age={args.age}, strategies={args.strategies}, no_claude_url={args.no_claude_url}, allow_overwrite={args.allow_overwrite}, no_overwrite={args.no_overwrite}, verbose={args.verbose}"
        )

        # Handle overwrite logic
        allow_overwrite = args.allow_overwrite and not args.no_overwrite
        logging.debug(f"Allow overwrite: {allow_overwrite}")

        # Setup subcommand logging based on verbosity
        logger_setup = warmwalrus.logger.LoggerSetup()
        logger_setup.setup_subcommand_logging(args.verbose)

        # Set default excludes if none provided
        excludes: typing.List[str] = args.exclude if args.exclude else [".git"]
        logging.debug(f"Using excludes: {excludes}")

        # Parse age filter if provided
        age_filter: typing.Optional[float] = None
        if args.age:
            age_parser: warmwalrus.age_parser.AgeParser = (
                warmwalrus.age_parser.AgeParser()
            )
            age_filter = age_parser.parse_age(args.age)
            logging.info(f"Age filter: {args.age} ({age_filter} seconds)")

        # Setup strategies
        strategy_registry = warmwalrus.strategies.registry.StrategyRegistry()

        # Start with default strategies if no explicit strategies provided
        if not args.strategies:
            if not args.no_claude_url:
                strategies = strategy_registry.get_default_strategies()
                logging.info("Using default strategies: file_renamer, claude_url")
            else:
                # Only file_renamer when claude_url is disabled
                strategies = [strategy_registry.get_strategy("file_renamer")]
                logging.info(
                    "Using default strategies: file_renamer (claude_url disabled)"
                )
        else:
            # User provided explicit strategies
            strategies = strategy_registry.get_strategies_by_names(args.strategies)

            # Add default claude_url unless explicitly disabled
            if not args.no_claude_url and "claude_url" not in args.strategies:
                claude_url_strategy = strategy_registry.get_strategy("claude_url")
                if claude_url_strategy:
                    strategies.insert(0, claude_url_strategy)  # Add at beginning
                    logging.info("Adding default claude_url strategy")

        # Configure file_renamer strategy with overwrite setting
        for strategy in strategies:
            if hasattr(strategy, "set_allow_overwrite"):
                strategy.set_allow_overwrite(allow_overwrite)

        if args.strategies:
            logging.info(f"Using strategies: {[s.get_name() for s in strategies]}")
            if len(strategy_registry.get_strategies_by_names(args.strategies)) != len(
                args.strategies
            ):
                strategy_registry.get_strategies_by_names(args.strategies)
                missing = [
                    name
                    for name in args.strategies
                    if name not in strategy_registry.list_strategies()
                ]
                logging.warning(f"Unknown strategies ignored: {missing}")

        # Find files to process
        file_finder: warmwalrus.file_finder.FileFinder = (
            warmwalrus.file_finder.FileFinder(
                extension=args.ext, excludes=excludes, age_filter=age_filter
            )
        )

        logging.info(f"Searching for .{args.ext} files in: {args.paths}")
        files_to_process: typing.List[pathlib.Path] = file_finder.find_files(args.paths)

        if not files_to_process:
            logging.info("No files found to process")
            return

        logging.info(f"Found {len(files_to_process)} files to process")

        # Process files
        processor: warmwalrus.file_processor.FileProcessor = (
            warmwalrus.file_processor.FileProcessor(
                strategies=strategies, age_filter=age_filter
            )
        )

        processed_count: int = 0
        for file_path in files_to_process:
            try:
                if args.dry_run:
                    if processor.needs_processing(file_path):
                        logging.info(f"Would process: {file_path}")
                        processed_count += 1
                    else:
                        logging.debug(f"Would skip (no markers): {file_path}")
                else:
                    if processor.process_file(file_path):
                        logging.info(f"Processed: {file_path}")
                        processed_count += 1
                    else:
                        logging.debug(f"Skipped (no changes): {file_path}")
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
                sys.exit(1)

        if args.dry_run:
            logging.info(
                f"Dry run complete: {processed_count} files would be processed"
            )
        else:
            logging.info(f"Processing complete: {processed_count} files processed")
