---
name: sqlmodel-db
description: |
  Build database models and perform CRUD operations using SQLModel (SQLAlchemy + Pydantic).
  Use when: (1) Creating database models with SQLModel, (2) Defining table schemas and fields,
  (3) Setting up relationships (one-to-many, many-to-many, self-referential), (4) Performing
  CRUD operations (create, read, update, delete), (5) Managing database sessions and transactions,
  (6) Integrating SQLModel with FastAPI, (7) Any SQLModel or database modeling task.
  Triggers: "sqlmodel", "database model", "orm", "crud operations", "db schema", "table relationships"
---

# SQLModel Database Skill

Build type-safe database models and perform CRUD operations using SQLModel.

## Quick Reference

### Basic Model

```python
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None
```

### Session Usage

```python
from sqlmodel import Session, create_engine, select

engine = create_engine("sqlite:///database.db")

with Session(engine) as session:
    hero = Hero(name="Spider-Man", secret_name="Peter Parker")
    session.add(hero)
    session.commit()
```

### FastAPI Integration

```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

## Workflow

1. Define models with appropriate fields and constraints
2. Set up relationships between models
3. Create engine and database tables
4. Use sessions for all CRUD operations
5. Handle transactions appropriately

## Reference Files

- **Model patterns**: See [references/models.md](references/models.md) for field configuration, data types, indexes, and inheritance patterns
- **Relationships**: See [references/relationships.md](references/relationships.md) for one-to-many, many-to-many, self-referential relationships, and cascade operations
- **CRUD operations**: See [references/crud.md](references/crud.md) for database setup, session management, queries, and transactions

## Common Patterns

### Model Inheritance (API Models)

```python
class HeroBase(SQLModel):
    name: str
    secret_name: str
    age: int | None = None

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

### One-to-Many Relationship

```python
class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

### Partial Update

```python
def update_hero(session: Session, hero_id: int, hero_update: HeroUpdate):
    hero = session.get(Hero, hero_id)
    if not hero:
        return None
    hero_data = hero_update.model_dump(exclude_unset=True)
    hero.sqlmodel_update(hero_data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```

## Key Points

- Use `table=True` for database tables, omit for data-only models
- Primary keys: `id: int | None = Field(default=None, primary_key=True)`
- Foreign keys: `Field(foreign_key="table.column")`
- Always use `session.commit()` after modifications
- Use `session.refresh(obj)` to get auto-generated values
- Prefer `select()` over raw SQL for type safety
