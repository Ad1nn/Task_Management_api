# SQLModel CRUD Operations Reference

## Table of Contents
- [Database Setup](#database-setup)
- [Session Management](#session-management)
- [Create (INSERT)](#create-insert)
- [Read (SELECT)](#read-select)
- [Update](#update)
- [Delete](#delete)
- [Transactions](#transactions)

---

## Database Setup

### Create Engine

```python
from sqlmodel import create_engine, SQLModel

# SQLite
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# PostgreSQL
postgres_url = "postgresql://user:password@localhost:5432/dbname"
engine = create_engine(postgres_url)

# PostgreSQL with async
postgres_async_url = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# MySQL
mysql_url = "mysql+pymysql://user:password@localhost:3306/dbname"
engine = create_engine(mysql_url)
```

### Create Tables

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Call after all models are imported
if __name__ == "__main__":
    create_db_and_tables()
```

---

## Session Management

### Basic Session

```python
from sqlmodel import Session

with Session(engine) as session:
    # Operations here
    session.commit()
```

### Session Dependency (FastAPI)

```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/heroes/")
def read_heroes(session: SessionDep):
    return session.exec(select(Hero)).all()
```

---

## Create (INSERT)

### Single Insert

```python
with Session(engine) as session:
    hero = Hero(name="Spider-Man", secret_name="Peter Parker")
    session.add(hero)
    session.commit()
    session.refresh(hero)  # Get auto-generated ID
    print(hero.id)
```

### Bulk Insert

```python
with Session(engine) as session:
    heroes = [
        Hero(name="Spider-Man", secret_name="Peter Parker"),
        Hero(name="Iron Man", secret_name="Tony Stark"),
        Hero(name="Thor", secret_name="Thor Odinson"),
    ]
    session.add_all(heroes)
    session.commit()
```

### Insert with Relationship

```python
with Session(engine) as session:
    team = Team(name="Avengers", headquarters="NYC")
    hero = Hero(name="Captain America", secret_name="Steve Rogers", team=team)
    session.add(hero)  # team added automatically
    session.commit()
```

---

## Read (SELECT)

### Get by ID

```python
hero = session.get(Hero, 1)  # Returns Hero or None
```

### Get All

```python
from sqlmodel import select

statement = select(Hero)
heroes = session.exec(statement).all()
```

### Filter with WHERE

```python
# Single condition
statement = select(Hero).where(Hero.name == "Spider-Man")
hero = session.exec(statement).first()

# Multiple conditions (AND)
statement = select(Hero).where(Hero.age > 18, Hero.team_id == 1)
heroes = session.exec(statement).all()

# OR condition
from sqlmodel import or_
statement = select(Hero).where(or_(Hero.name == "Spider-Man", Hero.name == "Iron Man"))
```

### Comparison Operators

```python
# Equals
select(Hero).where(Hero.name == "Spider-Man")

# Not equals
select(Hero).where(Hero.name != "Spider-Man")

# Greater than
select(Hero).where(Hero.age > 30)

# Less than or equal
select(Hero).where(Hero.age <= 25)

# IN list
select(Hero).where(Hero.name.in_(["Spider-Man", "Iron Man"]))

# LIKE pattern
select(Hero).where(Hero.name.like("%Man%"))

# IS NULL
select(Hero).where(Hero.team_id == None)

# IS NOT NULL
select(Hero).where(Hero.team_id != None)
```

### Pagination

```python
# LIMIT and OFFSET
statement = select(Hero).offset(10).limit(20)
heroes = session.exec(statement).all()

# Pagination helper
def paginate(session, model, page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    statement = select(model).offset(offset).limit(per_page)
    return session.exec(statement).all()
```

### Ordering

```python
# Ascending
statement = select(Hero).order_by(Hero.name)

# Descending
statement = select(Hero).order_by(Hero.age.desc())

# Multiple columns
statement = select(Hero).order_by(Hero.team_id, Hero.name)
```

### Counting

```python
from sqlmodel import func

statement = select(func.count()).select_from(Hero)
count = session.exec(statement).one()

# With filter
statement = select(func.count()).select_from(Hero).where(Hero.age > 30)
count = session.exec(statement).one()
```

### Selecting Specific Columns

```python
statement = select(Hero.name, Hero.age)
results = session.exec(statement).all()
for name, age in results:
    print(f"{name}: {age}")
```

### Joins

```python
# Implicit join via relationship
statement = select(Hero, Team).where(Hero.team_id == Team.id)

# Using join()
statement = select(Hero).join(Team).where(Team.name == "Avengers")
heroes = session.exec(statement).all()

# Left outer join
statement = select(Hero).outerjoin(Team)
```

---

## Update

### Update Single Record

```python
with Session(engine) as session:
    hero = session.get(Hero, 1)
    if hero:
        hero.name = "Spider-Boy"
        hero.age = 17
        session.add(hero)
        session.commit()
        session.refresh(hero)
```

### Partial Update (PATCH)

```python
def update_hero(session: Session, hero_id: int, hero_update: HeroUpdate):
    hero = session.get(Hero, hero_id)
    if not hero:
        return None

    # Only update provided fields
    hero_data = hero_update.model_dump(exclude_unset=True)
    hero.sqlmodel_update(hero_data)

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```

### Bulk Update

```python
from sqlmodel import update

statement = (
    update(Hero)
    .where(Hero.team_id == 1)
    .values(age=Hero.age + 1)
)
session.exec(statement)
session.commit()
```

---

## Delete

### Delete Single Record

```python
with Session(engine) as session:
    hero = session.get(Hero, 1)
    if hero:
        session.delete(hero)
        session.commit()
```

### Delete with Filter

```python
from sqlmodel import delete

statement = delete(Hero).where(Hero.age < 18)
session.exec(statement)
session.commit()
```

### Delete All

```python
statement = delete(Hero)
session.exec(statement)
session.commit()
```

---

## Transactions

### Basic Transaction

```python
with Session(engine) as session:
    try:
        hero1 = Hero(name="Hero 1", secret_name="Secret 1")
        hero2 = Hero(name="Hero 2", secret_name="Secret 2")
        session.add(hero1)
        session.add(hero2)
        session.commit()  # Both saved or neither
    except Exception:
        session.rollback()
        raise
```

### Nested Transactions (Savepoints)

```python
with Session(engine) as session:
    hero = Hero(name="Outer", secret_name="Outer Secret")
    session.add(hero)

    try:
        with session.begin_nested():
            # Savepoint created
            risky_hero = Hero(name="Risky", secret_name="Risky Secret")
            session.add(risky_hero)
            raise ValueError("Something went wrong")
    except ValueError:
        # Only risky_hero is rolled back
        pass

    session.commit()  # hero is still saved
```

### Explicit Transaction Control

```python
session = Session(engine)
try:
    hero = Hero(name="Test", secret_name="Test Secret")
    session.add(hero)
    session.commit()
except Exception:
    session.rollback()
finally:
    session.close()
```
