"""Enumerations for financial categories and transaction types."""

from enum import Enum


class Category(Enum):
    """Represent the supported financial transaction categories."""

    HOUSING = "housing"
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    EDUCATION = "education"
    CLOTHING = "clothing"
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    OTHER = "other"


class TransactionType(Enum):
    """Represent whether a transaction is income or an expense."""

    INCOME = "income"
    EXPENSE = "expense"