# SQLModel Relationships Reference

## Table of Contents
- [One-to-Many Relationships](#one-to-many-relationships)
- [Many-to-Many Relationships](#many-to-many-relationships)
- [Self-Referential Relationships](#self-referential-relationships)
- [Cascade Operations](#cascade-operations)
- [Lazy Loading vs Eager Loading](#lazy-loading-vs-eager-loading)

---

## One-to-Many Relationships

### Basic One-to-Many

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str

    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

### Key Points

- **Foreign Key**: `Field(foreign_key="table.column")` on the "many" side
- **Relationship**: `Relationship(back_populates="...")` on both sides
- **back_populates**: Links both sides for bidirectional navigation
- **Optional**: Use `| None` when relationship is optional

### Creating Related Data

```python
# Method 1: Create with foreign key
team = Team(name="Avengers", headquarters="NYC")
session.add(team)
session.commit()

hero = Hero(name="Spider-Man", secret_name="Peter", team_id=team.id)
session.add(hero)
session.commit()

# Method 2: Create via relationship
team = Team(name="X-Men", headquarters="Westchester")
hero = Hero(name="Wolverine", secret_name="Logan", team=team)
session.add(hero)  # team is added automatically
session.commit()

# Method 3: Add to list
team = Team(name="Fantastic Four", headquarters="Baxter Building")
team.heroes.append(Hero(name="Mr. Fantastic", secret_name="Reed Richards"))
session.add(team)
session.commit()
```

### Querying Relationships

```python
# Get hero's team
hero = session.get(Hero, 1)
if hero.team:
    print(hero.team.name)

# Get team's heroes
team = session.get(Team, 1)
for hero in team.heroes:
    print(hero.name)
```

---

## Many-to-Many Relationships

### Link Table Model

```python
class HeroTeamLink(SQLModel, table=True):
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
```

### Full Many-to-Many Setup

```python
class HeroTeamLink(SQLModel, table=True):
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    heroes: list["Hero"] = Relationship(
        back_populates="teams",
        link_model=HeroTeamLink
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    teams: list[Team] = Relationship(
        back_populates="heroes",
        link_model=HeroTeamLink
    )
```

### Link Table with Extra Fields

```python
class HeroTeamLink(SQLModel, table=True):
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    role: str = "member"
    is_leader: bool = False
```

### Creating Many-to-Many Data

```python
# Create entities
team_avengers = Team(name="Avengers")
team_xmen = Team(name="X-Men")
hero_wolverine = Hero(name="Wolverine")

# Link via relationship
hero_wolverine.teams.append(team_avengers)
hero_wolverine.teams.append(team_xmen)

session.add(hero_wolverine)
session.commit()

# Or via link table directly
link = HeroTeamLink(hero_id=hero.id, team_id=team.id, role="leader")
session.add(link)
session.commit()
```

---

## Self-Referential Relationships

### Parent-Child (Tree Structure)

```python
class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_id: int | None = Field(default=None, foreign_key="category.id")

    parent: "Category | None" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: list["Category"] = Relationship(back_populates="parent")
```

### Employee-Manager

```python
class Employee(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    manager_id: int | None = Field(default=None, foreign_key="employee.id")

    manager: "Employee | None" = Relationship(
        back_populates="reports",
        sa_relationship_kwargs={"remote_side": "Employee.id"}
    )
    reports: list["Employee"] = Relationship(back_populates="manager")
```

---

## Cascade Operations

### Cascade Delete

```python
class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    heroes: list["Hero"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

When team is deleted, all associated heroes are also deleted.

### Cascade Options

| Option | Effect |
|--------|--------|
| `save-update` | Cascade add operations |
| `merge` | Cascade merge operations |
| `delete` | Delete children when parent deleted |
| `delete-orphan` | Delete children when removed from parent |
| `all` | All of the above |

---

## Lazy Loading vs Eager Loading

### Lazy Loading (Default)

```python
hero = session.get(Hero, 1)
# team not loaded yet
print(hero.team.name)  # Separate query executed here
```

### Eager Loading with selectinload

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

statement = select(Hero).options(selectinload(Hero.team))
heroes = session.exec(statement).all()
# Teams already loaded, no additional queries
for hero in heroes:
    print(hero.team.name if hero.team else "No team")
```

### Eager Loading with joinedload

```python
from sqlalchemy.orm import joinedload

statement = select(Hero).options(joinedload(Hero.team))
heroes = session.exec(statement).unique().all()
```

### When to Use Each

| Strategy | Use When |
|----------|----------|
| Lazy | Only need related data sometimes |
| selectinload | Loading many related objects |
| joinedload | Loading single related object |
