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
- Test-driven development

## Run the tests

```bash
uv sync
uv run pytest -v
```

Expected result:

```text
33 passed
```

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
    TransactionFunctions ..> TransactionData : processes
    AccountFunctions ..> AccountData : manages
    AccountFunctions ..> TransactionData : filters
```

### UML diagram explanation

The diagram represents the dictionary-based domain model used in Phase 1.

#### Multiplicity

- `1` means exactly one element.
- `0..*` means zero, one, or any number of elements.
- Therefore, one account can contain zero or many transactions.

A newly created account initially contains no transactions. After transactions
are added, the same account can contain multiple transaction dictionaries.

#### UML symbols

| Symbol | Meaning |
|---|---|
| `+` | Public field or function |
| `1` | Exactly one element |
| `0..*` | Zero to any number of elements |
| `o--` | Aggregation: an account contains transactions |
| `-->` | Association: one element uses another element |
| `..>` | Dependency: a function creates, reads, or processes data |
| `<<enumeration>>` | A fixed collection of allowed values |
| `<<dictionary>>` | Data is represented by a Python dictionary |
| `: uses` | A transaction uses an enum value |
| `: contains` | An account contains transaction dictionaries |
| `: manages` | Functions manage account data |
| `: filters` | Functions select matching transactions |
| `: processes` | Functions create or process transaction data |

#### Relationships

- `TransactionData --> Category`: Each transaction uses one category, such as `FOOD` or `HOUSING`.
- `TransactionData --> TransactionType`: Each transaction is either `INCOME` or `EXPENSE`.
- `AccountData "1" o-- "0..*" TransactionData`: One account contains zero or many transactions.
- `TransactionFunctions ..> TransactionData`: The functions create, validate, format, and evaluate transaction dictionaries.
- `AccountFunctions ..> AccountData`: The functions create and manage account dictionaries.
- `AccountFunctions ..> TransactionData`: The functions calculate totals and filter transaction dictionaries.

## Test-Driven Development

Phase 1 was developed using the TDD cycle:

1. **RED:** The tests were written before the implementation and initially failed.
2. **GREEN:** The required functions were implemented until all tests passed.
3. **REFACTOR:** The code was reviewed and improved while keeping all tests green.

### RED – failing tests before implementation

![TDD RED phase](docs/tdd_red.png)

### GREEN – all tests passing after implementation

![TDD GREEN phase](docs/tdd_green.png)

## Phase 2 features

Phase 2 adds filtering, search, analysis, and dictionary-based budget
management.

### Filtering and search

- Inclusive date-range filtering
- Filtering by month
- Filtering by transaction tags
- Case-insensitive regular-expression search

### Financial analysis

- Monthly income, expense, and net summaries
- Expense totals grouped by category
- Ranking of the largest expenses
- Daily expense totals grouped by date

### Budget management

- Dictionary-based budgets
- Dictionary-based budget tracker
- Remaining budget calculations
- Budget usage percentages
- Detection of exceeded budgets
- Replacement of existing budgets for the same category and month

### Testing

Phase 2 was developed with Test-Driven Development:

1. Tests were written before the implementation.
2. The new tests initially failed with `NotImplementedError`.
3. The required functions were implemented.
4. All existing and new tests passed.

```text
64 passed


````markdown
## Phase 2 UML diagram

Phase 2 extends the core model with filtering, search, financial analysis,
budgets, and budget tracking.

The Phase 1 structures remain unchanged. The following diagram focuses on the
new components and their relationships with the existing account and
transaction dictionaries.

```mermaid
classDiagram
    direction TB

    class AccountData {
        <<dictionary>>
        +str name
        +list transactions
    }

    class TransactionData {
        <<dictionary>>
        +str description
        +float amount
        +TransactionType transaction_type
        +Category category
        +str date
        +set tags
    }

    class AnalysisFunctions {
        +filter_by_date_range(account, start, end)
        +filter_by_month(account, month)
        +search_transactions(account, query)
        +filter_by_tags(account, tags)
        +monthly_summary(account)
        +category_breakdown(account)
        +top_expenses(account, n)
        +daily_spending(account, month)
    }

    class BudgetData {
        <<dictionary>>
        +Category category
        +float monthly_limit
        +str month
    }

    class BudgetTrackerData {
        <<dictionary>>
        +list budgets
    }

    class BudgetFunctions {
        +create_budget(category, limit, month)
        +calculate_spent_amount(budget, account)
        +remaining(budget, account)
        +is_exceeded(budget, account)
        +usage_percentage(budget, account)
        +create_budget_tracker()
        +set_budget(tracker, category, limit, month)
        +check_budgets(tracker, account)
        +exceeded_budgets(tracker, account)
    }

    AccountData "1" o-- "0..*" TransactionData : contains
    BudgetTrackerData "1" o-- "0..*" BudgetData : contains

    AnalysisFunctions ..> AccountData : analyzes
    AnalysisFunctions ..> TransactionData : processes

    BudgetData ..> AccountData : checks spending
    BudgetFunctions ..> BudgetData : creates
    BudgetFunctions ..> BudgetTrackerData : manages
    BudgetFunctions ..> AccountData : evaluates

### Phase 2 UML explanation

Phase 2 extends the dictionary-based data model created in Phase 1. It does not replace the existing account and transaction structures. Instead, it adds filtering, search, financial analysis, and budget management functions that process the existing data.

#### New Phase 2 components

* `AnalysisFunctions` represents the filtering, search, and aggregation functions implemented in `analysis.py`.
* `BudgetData` represents one dictionary containing the information for a monthly category budget.
* `BudgetTrackerData` represents a dictionary that stores and manages multiple budget dictionaries.
* `BudgetFunctions` represents the budget creation, calculation, and management functions implemented in `budget.py`.

#### Relationships

* `AccountData "1" o-- "0..*" TransactionData`

  One account contains zero or many transaction dictionaries. A newly created account can initially have an empty transaction list. More transactions can be added later.

* `BudgetTrackerData "1" o-- "0..*" BudgetData`

  One budget tracker contains zero or many budget dictionaries. A newly created budget tracker is initially empty and can later manage multiple budgets.

* `AnalysisFunctions ..> AccountData`

  The analysis functions receive an account dictionary and read its transaction list.

* `AnalysisFunctions ..> TransactionData`

  The analysis functions filter, search, sort, group, and summarize the transaction dictionaries stored in an account.

* `BudgetData ..> AccountData`

  A budget is compared with the actual expenses stored in an account. Only expenses from the matching category and month are included in the calculation.

* `BudgetFunctions ..> BudgetData`

  The budget functions create budget dictionaries and calculate their remaining amount, usage percentage, and exceeded status.

* `BudgetFunctions ..> BudgetTrackerData`

  The budget functions add new budgets, replace existing budgets, calculate usage percentages, and select exceeded budgets.

* `BudgetFunctions ..> AccountData`

  The budget functions read account transactions to compare actual spending with the defined monthly limits.

#### Multiplicities

* `1` means exactly one element.
* `0..*` means zero to any number of elements.
* One account dictionary can contain zero, one, or many transaction dictionaries.
* One budget tracker dictionary can contain zero, one, or many budget dictionaries.
* Both collections may be empty when they are created and can grow as new data is added.

#### UML symbols

| Symbol           | Meaning                                                   |
| ---------------- | --------------------------------------------------------- |
| `+`              | Public field or function                                  |
| `1`              | Exactly one element                                       |
| `0..*`           | Zero to any number of elements                            |
| `o--`            | Aggregation: one structure contains other structures      |
| `..>`            | Dependency: a function reads, creates, or processes data  |
| `<<dictionary>>` | The data is represented by a Python dictionary            |
| `: contains`     | One data structure contains other data structures         |
| `: analyzes`     | Functions analyze account data                            |
| `: processes`    | Functions filter, search, sort, or aggregate transactions |
| `: creates`      | Functions create budget dictionaries                      |
| `: manages`      | Functions add, replace, and check tracked budgets         |
| `: evaluates`    | Functions compare actual expenses with budget limits      |

#### Summary

The Phase 2 UML diagram shows a clear separation between data and functionality. Account, transaction, budget, and budget tracker information is stored in dictionaries. The analysis and budget functions process these dictionaries without depending on a graphical user interface. This separation makes the business logic easier to test and allows it to be reused later by a Qt-based user interface.
