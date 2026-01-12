# Test Patterns Reference

## Table of Contents
- [Assertion Patterns](#assertion-patterns)
- [Fixture Patterns](#fixture-patterns)
- [Parametrization](#parametrization)
- [Markers](#markers)

---

## Assertion Patterns

### Status Code Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "Returns 200 OK" | `assert response.status_code == 200` |
| "Status code 404" | `assert response.status_code == 404` |
| "Returns 401 Unauthorized" | `assert response.status_code == 401` |

### Boolean Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "Should be true" | `assert result is True` |
| "Should be false" | `assert result is False` |
| "Must be valid" | `assert is_valid(result)` |
| "Must be unique" | `assert is_unique(result)` |

### Existence Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "Must exist" | `assert result is not None` |
| "Should not exist" | `assert result is None` |
| "Must contain X" | `assert expected in result` |
| "Should include Y" | `assert expected in result` |

### Comparison Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "At least 5" | `assert len(result) >= 5` |
| "At most 10" | `assert len(result) <= 10` |
| "Exactly 3" | `assert len(result) == 3` |
| "Greater than 0" | `assert result > 0` |
| "Less than 100" | `assert result < 100` |

### Time-Based Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "Within 500ms" | `assert response_time_ms <= 500` |
| "Within 2 seconds" | `assert response_time_s <= 2` |
| "Expires in 24 hours" | `assert expiry_delta <= timedelta(hours=24)` |

### Exception Assertions

| Criterion Pattern | Generated Assertion |
|-------------------|---------------------|
| "Raises ValueError" | `pytest.raises(ValueError)` |
| "Throws InvalidException" | `pytest.raises(InvalidException)` |

---

## Fixture Patterns

### Basic Fixture

```python
@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"id": 1, "name": "Test"}
```

### Fixture with Teardown

```python
@pytest.fixture
def db_session():
    """Provide database session with cleanup."""
    session = create_session()
    yield session
    session.rollback()
    session.close()
```

### Scoped Fixture

```python
@pytest.fixture(scope="module")
def expensive_resource():
    """Shared resource across module."""
    resource = create_expensive_resource()
    yield resource
    resource.cleanup()
```

### Factory Fixture

```python
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    created = []

    def _create_user(**kwargs):
        user = User(**kwargs)
        created.append(user)
        return user

    yield _create_user

    for user in created:
        user.delete()
```

---

## Parametrization

### Basic Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_email_validation(email, valid):
    assert validate_email(email) == valid
```

### IDs for Clarity

```python
@pytest.mark.parametrize("status,expected", [
    pytest.param(200, True, id="success"),
    pytest.param(404, False, id="not_found"),
    pytest.param(500, False, id="server_error"),
])
def test_is_success(status, expected):
    assert is_success(status) == expected
```

---

## Markers

### Built-in Markers

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature(): ...

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_syntax(): ...

@pytest.mark.xfail(reason="Known bug")
def test_known_issue(): ...
```

### Custom Markers

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "critical: mark test as critical")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark as integration test")

# test file
@pytest.mark.critical
def test_critical_path(): ...

@pytest.mark.slow
def test_large_dataset(): ...

@pytest.mark.integration
def test_external_api(): ...
```

### Running by Marker

```bash
# Run only critical tests
pytest -m critical

# Skip slow tests
pytest -m "not slow"

# Run critical but not slow
pytest -m "critical and not slow"
```

---

## Test Organization

### Class-Based (Recommended for grouping)

```python
class TestUserAuthentication:
    """Tests for user authentication feature."""

    def test_login_success(self):
        """Valid credentials return token."""
        ...

    def test_login_invalid_password(self):
        """Invalid password returns 401."""
        ...

    def test_login_missing_user(self):
        """Unknown user returns 404."""
        ...
```

### Function-Based (Simpler, flat)

```python
def test_user_login_success():
    """Valid credentials return token."""
    ...

def test_user_login_invalid_password():
    """Invalid password returns 401."""
    ...
```

### AAA Pattern (Arrange-Act-Assert)

```python
def test_create_order():
    # Arrange
    user = create_test_user()
    product = create_test_product(price=10.00)

    # Act
    order = create_order(user, [product])

    # Assert
    assert order.total == 10.00
    assert order.status == "pending"
    assert len(order.items) == 1
```
