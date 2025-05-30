import argparse
import importlib.metadata
import sys

import warmwalrus.cli
import warmwalrus.logger


def main() -> None:
    """Main entry point for the warmwalrus CLI application."""
    parser = argparse.ArgumentParser(
        description="Clean marker delimiters from files", prog="warmwalrus"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('warmwalrus')}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase main app verbosity (can be used multiple times)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add version subcommand
    subparsers.add_parser("version", help="Show version information")

    # Add cleanmarkers subcommand
    cleanmarkers_parser = subparsers.add_parser(
        "cleanmarkers", help="Clean marker delimiters from files"
    )

    cli_handler = warmwalrus.cli.CLIHandler()
    cli_handler.setup_cleanmarkers_parser(cleanmarkers_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup main app logging based on verbosity
    logger_setup = warmwalrus.logger.LoggerSetup()
    logger_setup.setup_main_logging(args.verbose)

    if args.command == "version":
        cli_handler.handle_version(args)
    elif args.command == "cleanmarkers":
        cli_handler.handle_cleanmarkers(args)
