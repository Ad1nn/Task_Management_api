---
name: spec-to-tests
description: |
  Generate pytest test functions from structured specifications. Converts requirements and acceptance
  criteria into runnable test code with assertions. Framework-agnostic, reusable across projects.
  Use when: (1) Converting specs to tests, (2) Generating test scaffolds, (3) Creating test cases
  from requirements, (4) Building test suites from acceptance criteria.
  Triggers: "generate tests", "spec to tests", "create tests from spec", "test generation"
---

# Specification to Tests Generator

Convert structured specifications into runnable pytest test code.

## Quick Start

```python
from test_generator import TestGenerator

spec = {
    "name": "user-auth",
    "requirements": [{
        "id": "FR-001",
        "description": "Users can log in",
        "acceptance_criteria": [
            "Returns 200 OK on valid credentials",
            "Returns 401 on invalid credentials"
        ]
    }]
}

generator = TestGenerator(spec)
print(generator.generate())
```

## CLI Usage

```bash
# Generate tests from specification file
python scripts/test_generator.py --input spec.json --output tests/test_spec.py

# Function-style tests (instead of class-based)
python scripts/test_generator.py --input spec.json --style function

# Without docstrings or markers
python scripts/test_generator.py --input spec.json --no-docstrings --no-markers
```

## Input Format

The generator accepts specifications in this structure:

```json
{
  "name": "feature-name",
  "summary": "Feature description",
  "requirements": [
    {
      "id": "FR-001",
      "description": "What the feature does",
      "type": "functional",
      "priority": "high",
      "acceptance_criteria": [
        "Criterion 1 (becomes assertion)",
        "Criterion 2 (becomes assertion)"
      ]
    }
  ]
}
```

Compatible with **structured-spec** skill output.

## Assertion Generation

Acceptance criteria are automatically converted to assertions:

| Criterion | Generated Assertion |
|-----------|---------------------|
| "Returns 200 OK" | `assert response.status_code == 200` |
| "Must be unique" | `assert is_unique(result)` |
| "At least 5 items" | `assert len(result) >= 5` |
| "Within 500ms" | `assert response_time_ms <= 500` |
| "Raises ValueError" | `pytest.raises(ValueError)` |

See [references/patterns.md](references/patterns.md) for complete patterns.

## Output Styles

### Class-Based (Default)

```python
class TestUserAuth:
    def test_login_returns_200_ok_on_valid_credentials(self):
        ...
```

### Function-Based

```python
def test_login_returns_200_ok_on_valid_credentials():
    ...
```

## Programmatic API

```python
from test_generator import TestGenerator, TestSuiteBuilder, TestStyle

# Single spec
generator = TestGenerator(spec, style=TestStyle.CLASS)
code = generator.generate()

# Multiple specs
suite = (TestSuiteBuilder()
    .add_spec(auth_spec)
    .add_spec(user_spec)
    .with_style(TestStyle.FUNCTION)
    .build())

for filename, code in suite.items():
    Path(filename).write_text(code)
```

## Workflow

1. Create specification (manually or with structured-spec skill)
2. Run generator: `python test_generator.py -i spec.json -o tests/test_spec.py`
3. Implement TODOs in generated tests
4. Run tests: `pytest tests/test_spec.py`
