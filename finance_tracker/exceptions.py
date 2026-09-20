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
        self.line_number = line_number
        self.reason = reason

        super().__init__(
            f"CSV import error on line {line_number}: {reason}"
        )

    def __str__(self) -> str:
        """Return a readable description of the import error."""
        return (
            f"CSV import error on line {self.line_number}: "
            f"{self.reason}"
        )


class BudgetNotFoundError(LookupError):
    """Represent a requested budget that could not be found."""