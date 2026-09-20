"""Define custom exceptions for the personal finance tracker."""


class InvalidTransactionError(ValueError):
    """Represent invalid transaction data."""


class CsvImportError(Exception):
    """Represent an error found in one CSV input line."""

    def __init__(
        self,
        line_number: int,
        reason: str,
    ) -> None:
        """Initialize the error with a line number and reason."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return a readable description of the import error."""
        raise NotImplementedError


class BudgetNotFoundError(LookupError):
    """Represent a requested budget that could not be found."""