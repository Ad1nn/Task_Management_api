# SQLModel Models Reference

## Table of Contents
- [Basic Model Definition](#basic-model-definition)
- [Field Configuration](#field-configuration)
- [Data Types](#data-types)
- [Indexes](#indexes)
- [Model Inheritance Patterns](#model-inheritance-patterns)

---

## Basic Model Definition

### Table Model

```python
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
```

- `table=True`: Creates actual database table
- Without `table=True`: Data-only model (Pydantic model)

### Data-Only Model (No Table)

```python
class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: int | None = None
```

---

## Field Configuration

### Primary Key

```python
id: int | None = Field(default=None, primary_key=True)
```

Database auto-generates ID. Use `None` default for new instances.

### Required vs Optional Fields

```python
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str                          # Required (NOT NULL)
    secret_name: str                   # Required (NOT NULL)
    age: int | None = None             # Optional (NULL allowed)
    email: str | None = Field(default=None)  # Optional with explicit Field
```

### Field Parameters

```python
from sqlmodel import Field

Field(
    default=None,              # Default value
    primary_key=True,          # Primary key constraint
    foreign_key="table.column", # Foreign key reference
    index=True,                # Create index for faster queries
    unique=True,               # Unique constraint
    nullable=True,             # Allow NULL (inferred from type)
    sa_column_kwargs={},       # SQLAlchemy Column kwargs
)
```

### String Constraints

```python
from sqlmodel import Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    username: str = Field(unique=True, index=True)
```

### Numeric Constraints

```python
class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    price: float = Field(gt=0, description="Price must be positive")
    quantity: int = Field(ge=0, le=1000)
    rating: float = Field(ge=0, le=5)
```

---

## Data Types

### Common Types

| Python Type | SQL Type | Notes |
|-------------|----------|-------|
| `int` | INTEGER | Standard integer |
| `float` | FLOAT | Floating point |
| `str` | VARCHAR | Variable length string |
| `bool` | BOOLEAN | True/False |
| `bytes` | BLOB | Binary data |
| `datetime` | DATETIME | Date and time |
| `date` | DATE | Date only |
| `time` | TIME | Time only |
| `Decimal` | NUMERIC | Precise decimals |
| `UUID` | UUID/CHAR(32) | Unique identifiers |

### DateTime Fields

```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
```

### UUID Primary Key

```python
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
```

### Decimal for Money

```python
from decimal import Decimal
from sqlmodel import Field, SQLModel

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal = Field(decimal_places=2, max_digits=10)
```

### Enum Fields

```python
from enum import Enum
from sqlmodel import Field, SQLModel

class Status(str, Enum):
    pending = "pending"
    active = "active"
    completed = "completed"

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    status: Status = Status.pending
```

---

## Indexes

### Single Column Index

```python
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # Indexed for fast lookups
    secret_name: str
```

### Unique Index

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
```

### When to Use Indexes

**Add index when:**
- Column used frequently in WHERE clauses
- Column used in ORDER BY
- Column used in JOIN conditions
- Column has high cardinality (many unique values)

**Avoid index when:**
- Column rarely queried
- Table has few rows
- Column has low cardinality
- Table has heavy write operations

---

## Model Inheritance Patterns

### Base Model with Shared Fields

```python
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class HeroCreate(HeroBase):
    pass

class HeroPublic(HeroBase):
    id: int

class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
```

### Pattern Benefits

| Model | Purpose |
|-------|---------|
| `HeroBase` | Shared fields for validation |
| `Hero` | Database table model |
| `HeroCreate` | API input (create) |
| `HeroPublic` | API output (excludes sensitive data) |
| `HeroUpdate` | Partial update (all optional) |

### Example Usage

```python
# Create
hero_data = HeroCreate(name="Spider-Man", secret_name="Peter Parker")
hero = Hero.model_validate(hero_data)

# Read (return public model)
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id: int):
    return session.get(Hero, hero_id)

# Update (partial)
hero_update = HeroUpdate(name="Spider-Boy")
hero_data = hero_update.model_dump(exclude_unset=True)
hero.sqlmodel_update(hero_data)
```
