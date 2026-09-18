# Personal Finance Tracker

The Personal Finance Tracker manages income and expense transactions.

## Phase 1 features

- Transaction and category enums
- Dictionary-based transaction data
- Dictionary-based account data
- Input validation
- Balance calculation
- Income and expense totals
- Filtering by category
- Filtering by transaction type
- Automated tests with pytest

## Run the tests

```bash
uv sync
uv run pytest -v

## Phase 1 UML diagram

The following diagram shows the dictionary-based domain model and the
relationships between categories, transactions, and accounts.

![Phase 1 UML diagram](docs/phase_1_uml.png)

The editable draw.io source file is available in
[`docs/phase_1_uml.drawio`](docs/phase_1_uml.drawio).

## Phase 1 UML diagram

The following UML diagram shows the dictionary-based structure of Phase 1.

```mermaid
classDiagram
    direction TB

    class Category {
        <<enumeration>>
        HOUSING
        FOOD
        TRANSPORT
        ENTERTAINMENT
        HEALTH
        EDUCATION
        CLOTHING
        SALARY
        FREELANCE
        INVESTMENT
        OTHER
    }

    class TransactionType {
        <<enumeration>>
        INCOME
        EXPENSE
    }

    class TransactionData {
        <<dictionary>>
        +str description
        +float amount
        +TransactionType transaction_type
        +Category category
        +str date
        +set~str~ tags
    }

    class AccountData {
        <<dictionary>>
        +str name
        +list~TransactionData~ transactions
    }

    class TransactionFunctions {
        +create_transaction() dict
        +is_expense() bool
        +is_income() bool
        +signed_amount() float
        +format_transaction() str
    }

    class AccountFunctions {
        +create_account() dict
        +add_transaction() None
        +calculate_balance() float
        +calculate_income_total() float
        +calculate_expense_total() float
        +filter_by_category() list
        +filter_by_type() list
    }

    TransactionData --> Category : uses
    TransactionData --> TransactionType : uses
    AccountData "1" o-- "0..*" TransactionData : contains
    TransactionFunctions ..> TransactionData : creates and processes
    AccountFunctions ..> AccountData : manages
    AccountFunctions ..> TransactionData : filters
```