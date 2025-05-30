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
            f"Arguments: paths={args.paths}, ext={args.ext}, dry_run={args.dry_run}, excludes={args.exclude}, age={args.age}, verbose={args.verbose}"
        )

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

        # Find files to process
        file_finder: warmwalrus.file_finder.FileFinder = (
            warmwalrus.file_finder.FileFinder(
                extension=args.ext, excludes=excludes, age_filter=age_filter
            )
        )

        logging.info(f"Searching for .{args.ext} files in: {args.paths}")
        files_to_process: typing.List[pathlib.Path] = file_finder.find_files(args.paths)

        if not files_to_process:
            if args.verbose > 0:
                print("No files found to process", file=sys.stderr)
            logging.info("No files found to process")
            return

        logging.info(f"Found {len(files_to_process)} files to process")

        # Process files
        processor: warmwalrus.file_processor.FileProcessor = (
            warmwalrus.file_processor.FileProcessor()
        )
        processed_count: int = 0

        for file_path in files_to_process:
            try:
                if args.dry_run:
                    if processor.needs_processing(file_path):
                        print(f"Would process: {file_path}")
                        processed_count += 1
                    elif args.verbose > 0:
                        print(f"Would skip (no markers): {file_path}")
                else:
                    if processor.process_file(file_path):
                        if args.verbose > 0:
                            print(f"Processed: {file_path}")
                        processed_count += 1
                    elif args.verbose > 0:
                        print(f"Skipped (no changes): {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
                logging.error(f"Error processing {file_path}: {e}")
                sys.exit(1)

        if args.dry_run:
            logging.info(
                f"Dry run complete: {processed_count} files would be processed"
            )
        else:
            logging.info(f"Processing complete: {processed_count} files processed")
