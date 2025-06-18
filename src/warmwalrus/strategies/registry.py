import typing

import warmwalrus.strategies.base
import warmwalrus.strategies.claude_url
import warmwalrus.strategies.file_renamer
import warmwalrus.strategies.newline_padding


class StrategyRegistry:
    """Registry for managing file processing strategies."""

    def __init__(self) -> None:
        self._strategies: typing.Dict[
            str, warmwalrus.strategies.base.FileProcessingStrategy
        ] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default strategies."""
        self.register_strategy(
            "newline_padding",
            warmwalrus.strategies.newline_padding.NewlinePaddingStrategy(),
        )
        self.register_strategy(
            "claude_url",
            warmwalrus.strategies.claude_url.ClaudeUrlStrategy(),
        )
        self.register_strategy(
            "file_renamer",
            warmwalrus.strategies.file_renamer.FileRenamerStrategy(),
        )

    def get_default_strategies(
        self,
    ) -> typing.List[warmwalrus.strategies.base.FileProcessingStrategy]:
        """Get the default strategies that should be applied if none are specified."""
        return [self.get_strategy("file_renamer"), self.get_strategy("claude_url")]

    def register_strategy(
        self, name: str, strategy: warmwalrus.strategies.base.FileProcessingStrategy
    ) -> None:
        """
        Register a strategy with a name.

        Args:
            name: Name to register the strategy under
            strategy: The strategy instance to register
        """
        self._strategies[name] = strategy

    def get_strategy(
        self, name: str
    ) -> typing.Optional[warmwalrus.strategies.base.FileProcessingStrategy]:
        """
        Get a strategy by name.

        Args:
            name: Name of the strategy to retrieve

        Returns:
            The strategy instance or None if not found
        """
        return self._strategies.get(name)

    def list_strategies(self) -> typing.List[str]:
        """Get a list of all registered strategy names."""
        return list(self._strategies.keys())

    def get_strategies_by_names(
        self, names: typing.List[str]
    ) -> typing.List[warmwalrus.strategies.base.FileProcessingStrategy]:
        """
        Get multiple strategies by their names.

        Args:
            names: List of strategy names

        Returns:
            List of strategy instances (skips any not found)
        """
        strategies = []
        for name in names:
            strategy = self.get_strategy(name)
            if strategy:
                strategies.append(strategy)
        return strategies
