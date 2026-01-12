#!/usr/bin/env python3
"""
Specification to Pytest Test Generator

Converts structured specifications into runnable pytest test code.
Framework-agnostic, generates clean and maintainable test functions.

Usage:
    python test_generator.py --input spec.json --output tests/test_spec.py

    Or as a module:
        from test_generator import TestGenerator
        generator = TestGenerator(spec)
        code = generator.generate()
"""

import argparse
import json
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable


class TestStyle(Enum):
    """Test organization styles."""
    FUNCTION = "function"      # test_<name>() functions
    CLASS = "class"            # class Test<Name> with methods
    PARAMETRIZED = "parametrized"  # @pytest.mark.parametrize


@dataclass
class TestCase:
    """A single test case derived from a requirement."""
    name: str
    description: str
    requirement_id: str
    assertions: list[str] = field(default_factory=list)
    setup: list[str] = field(default_factory=list)
    teardown: list[str] = field(default_factory=list)
    markers: list[str] = field(default_factory=list)
    parametrize: list[dict] | None = None


@dataclass
class TestModule:
    """A complete test module with imports and test cases."""
    name: str
    description: str
    imports: list[str] = field(default_factory=list)
    fixtures: list[str] = field(default_factory=list)
    test_cases: list[TestCase] = field(default_factory=list)


class TestGenerator:
    """
    Generate pytest tests from structured specifications.

    Example:
        spec = {
            "name": "user-auth",
            "requirements": [
                {
                    "id": "FR-001",
                    "description": "Users can log in with email/password",
                    "acceptance_criteria": [
                        "Returns 200 OK with token on valid credentials",
                        "Returns 401 on invalid credentials"
                    ]
                }
            ]
        }
        generator = TestGenerator(spec)
        code = generator.generate()
    """

    def __init__(
        self,
        spec: dict,
        style: TestStyle = TestStyle.CLASS,
        include_docstrings: bool = True,
        include_markers: bool = True,
    ):
        self.spec = spec
        self.style = style
        self.include_docstrings = include_docstrings
        self.include_markers = include_markers
        self._test_module = None

    def generate(self) -> str:
        """Generate complete pytest test module code."""
        self._test_module = self._build_test_module()

        parts = [
            self._generate_header(),
            self._generate_imports(),
            self._generate_fixtures(),
        ]

        if self.style == TestStyle.CLASS:
            parts.append(self._generate_class_tests())
        else:
            parts.append(self._generate_function_tests())

        return "\n\n".join(filter(None, parts)) + "\n"

    def _build_test_module(self) -> TestModule:
        """Build test module structure from specification."""
        module = TestModule(
            name=self._to_module_name(self.spec.get("name", "spec")),
            description=self.spec.get("summary", ""),
            imports=self._determine_imports(),
        )

        for req in self.spec.get("requirements", []):
            test_cases = self._requirement_to_tests(req)
            module.test_cases.extend(test_cases)

        return module

    def _requirement_to_tests(self, req: dict) -> list[TestCase]:
        """Convert a requirement to one or more test cases."""
        test_cases = []
        req_id = req.get("id", "REQ")
        description = req.get("description", "")
        req_type = req.get("type", "functional")
        priority = req.get("priority", "medium")
        criteria = req.get("acceptance_criteria", [])

        if not criteria:
            # Single test for requirement without specific criteria
            test_cases.append(TestCase(
                name=self._to_test_name(description),
                description=description,
                requirement_id=req_id,
                assertions=[self._criterion_to_assertion(description)],
                markers=self._get_markers(req_type, priority),
            ))
        else:
            # One test per acceptance criterion
            for i, criterion in enumerate(criteria, 1):
                test_name = self._to_test_name(criterion)
                if len(criteria) > 1:
                    test_name = f"{self._to_test_name(description)}_{i}"

                test_cases.append(TestCase(
                    name=test_name,
                    description=f"{description}: {criterion}",
                    requirement_id=req_id,
                    assertions=[self._criterion_to_assertion(criterion)],
                    markers=self._get_markers(req_type, priority),
                ))

        return test_cases

    def _criterion_to_assertion(self, criterion: str) -> str:
        """Convert acceptance criterion to pytest assertion."""
        criterion_lower = criterion.lower()

        # Pattern matching for common assertion types
        patterns: list[tuple[str, Callable[[str], str]]] = [
            # Status codes
            (r"returns?\s+(\d{3})", lambda m: f"assert response.status_code == {m.group(1)}"),
            (r"status\s+code\s+(\d{3})", lambda m: f"assert response.status_code == {m.group(1)}"),

            # Boolean checks
            (r"should\s+be\s+true", lambda m: "assert result is True"),
            (r"should\s+be\s+false", lambda m: "assert result is False"),
            (r"must\s+be\s+valid", lambda m: "assert is_valid(result)"),
            (r"must\s+be\s+unique", lambda m: "assert is_unique(result)"),

            # Existence checks
            (r"must\s+exist", lambda m: "assert result is not None"),
            (r"should\s+not\s+exist", lambda m: "assert result is None"),
            (r"must\s+contain", lambda m: "assert expected in result"),
            (r"should\s+include", lambda m: "assert expected in result"),

            # Comparison checks
            (r"at\s+least\s+(\d+)", lambda m: f"assert len(result) >= {m.group(1)}"),
            (r"at\s+most\s+(\d+)", lambda m: f"assert len(result) <= {m.group(1)}"),
            (r"exactly\s+(\d+)", lambda m: f"assert len(result) == {m.group(1)}"),
            (r"greater\s+than\s+(\d+)", lambda m: f"assert result > {m.group(1)}"),
            (r"less\s+than\s+(\d+)", lambda m: f"assert result < {m.group(1)}"),

            # Time-based checks
            (r"within\s+(\d+)\s*(ms|milliseconds?)",
             lambda m: f"assert response_time_ms <= {m.group(1)}"),
            (r"within\s+(\d+)\s*(s|seconds?)",
             lambda m: f"assert response_time_s <= {m.group(1)}"),
            (r"expires?\s+in\s+(\d+)\s*(hours?|minutes?|days?)",
             lambda m: f"assert expiry_delta <= timedelta({m.group(2)}={m.group(1)})"),

            # Error handling
            (r"raises?\s+(\w+error)", lambda m: f"pytest.raises({m.group(1).title()})"),
            (r"throws?\s+(\w+exception)", lambda m: f"pytest.raises({m.group(1).title()})"),
        ]

        for pattern, formatter in patterns:
            match = re.search(pattern, criterion_lower)
            if match:
                return formatter(match)

        # Default: create a descriptive assertion placeholder
        safe_desc = self._sanitize_string(criterion[:50])
        return f"assert result, \"{safe_desc}\""

    def _get_markers(self, req_type: str, priority: str) -> list[str]:
        """Generate pytest markers based on requirement metadata."""
        if not self.include_markers:
            return []

        markers = []

        # Type-based markers
        type_markers = {
            "functional": None,  # Default, no marker
            "non_functional": "performance",
            "constraint": "constraint",
        }
        if marker := type_markers.get(req_type):
            markers.append(marker)

        # Priority-based markers
        if priority == "critical":
            markers.append("critical")
        elif priority == "low":
            markers.append("slow")  # Often low priority = less urgent = can be slow

        return markers

    def _determine_imports(self) -> list[str]:
        """Determine required imports based on spec content."""
        imports = ["import pytest"]

        # Check if we need datetime
        spec_str = json.dumps(self.spec).lower()
        if any(x in spec_str for x in ["expire", "timeout", "duration", "timedelta"]):
            imports.append("from datetime import datetime, timedelta")

        return imports

    def _generate_header(self) -> str:
        """Generate module header with docstring."""
        name = self.spec.get("name", "specification")
        summary = self.spec.get("summary", "")
        timestamp = datetime.now().strftime("%Y-%m-%d")

        header = f'''"""
Tests for: {name}
{summary}

Generated from structured specification on {timestamp}.
"""'''
        return header

    def _generate_imports(self) -> str:
        """Generate import statements."""
        return "\n".join(self._test_module.imports)

    def _generate_fixtures(self) -> str:
        """Generate pytest fixtures."""
        # Generate common fixtures based on spec
        fixtures = []

        # Add a sample fixture for the entity being tested
        name = self._to_snake_case(self.spec.get("name", "subject"))
        fixtures.append(f'''
@pytest.fixture
def {name}_fixture():
    """Set up test {name}."""
    # TODO: Implement fixture setup
    yield None
    # TODO: Implement fixture teardown
''')

        return "\n".join(fixtures)

    def _generate_class_tests(self) -> str:
        """Generate class-based test structure."""
        class_name = self._to_class_name(self.spec.get("name", "Spec"))

        lines = [f"class Test{class_name}:"]

        if self.include_docstrings:
            summary = self.spec.get("summary", "Test cases")
            lines.append(f'    """{summary}"""')

        # Group tests by requirement
        req_groups: dict[str, list[TestCase]] = {}
        for tc in self._test_module.test_cases:
            req_groups.setdefault(tc.requirement_id, []).append(tc)

        for req_id, test_cases in req_groups.items():
            lines.append(f"\n    # {req_id}")
            for tc in test_cases:
                lines.append(self._generate_test_method(tc))

        return "\n".join(lines)

    def _generate_function_tests(self) -> str:
        """Generate function-based test structure."""
        tests = []

        for tc in self._test_module.test_cases:
            tests.append(self._generate_test_function(tc))

        return "\n\n".join(tests)

    def _generate_test_method(self, tc: TestCase) -> str:
        """Generate a single test method."""
        lines = []

        # Markers
        for marker in tc.markers:
            lines.append(f"    @pytest.mark.{marker}")

        # Method signature
        lines.append(f"    def test_{tc.name}(self):")

        # Docstring
        if self.include_docstrings:
            lines.append(f'        """{tc.description}"""')

        # Arrange
        lines.append("        # Arrange")
        if tc.setup:
            for setup in tc.setup:
                lines.append(f"        {setup}")
        else:
            lines.append("        # TODO: Set up test data")

        # Act
        lines.append("")
        lines.append("        # Act")
        lines.append("        result = None  # TODO: Call function under test")

        # Assert
        lines.append("")
        lines.append("        # Assert")
        for assertion in tc.assertions:
            lines.append(f"        {assertion}")

        return "\n".join(lines)

    def _generate_test_function(self, tc: TestCase) -> str:
        """Generate a standalone test function."""
        lines = []

        # Markers
        for marker in tc.markers:
            lines.append(f"@pytest.mark.{marker}")

        # Function signature
        lines.append(f"def test_{tc.name}():")

        # Docstring
        if self.include_docstrings:
            lines.append(f'    """{tc.description}')
            lines.append(f'    Requirement: {tc.requirement_id}')
            lines.append('    """')

        # Arrange
        lines.append("    # Arrange")
        if tc.setup:
            for setup in tc.setup:
                lines.append(f"    {setup}")
        else:
            lines.append("    # TODO: Set up test data")

        # Act
        lines.append("")
        lines.append("    # Act")
        lines.append("    result = None  # TODO: Call function under test")

        # Assert
        lines.append("")
        lines.append("    # Assert")
        for assertion in tc.assertions:
            lines.append(f"    {assertion}")

        return "\n".join(lines)

    # Utility methods

    def _to_test_name(self, text: str) -> str:
        """Convert text to valid test function name."""
        # Remove special chars, convert to snake_case
        name = re.sub(r'[^\w\s]', '', text.lower())
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        # Truncate and ensure valid Python identifier
        name = name[:50]
        if name and name[0].isdigit():
            name = f"test_{name}"
        return name or "unnamed"

    def _to_module_name(self, text: str) -> str:
        """Convert text to valid module name."""
        return self._to_snake_case(text)

    def _to_class_name(self, text: str) -> str:
        """Convert text to PascalCase class name."""
        words = re.sub(r'[^\w\s]', '', text).split()
        return ''.join(word.capitalize() for word in words)

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        name = re.sub(r'[^\w\s]', '', text.lower())
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'_+', '_', name)
        return name.strip('_')

    def _sanitize_string(self, text: str) -> str:
        """Sanitize string for use in code."""
        return text.replace('"', '\\"').replace('\n', ' ')


class TestSuiteBuilder:
    """
    Builder for creating test suites from multiple specifications.

    Example:
        suite = (TestSuiteBuilder()
            .add_spec(auth_spec)
            .add_spec(user_spec)
            .with_style(TestStyle.CLASS)
            .with_markers(True)
            .build())
    """

    def __init__(self):
        self._specs: list[dict] = []
        self._style = TestStyle.CLASS
        self._include_docstrings = True
        self._include_markers = True

    def add_spec(self, spec: dict) -> "TestSuiteBuilder":
        """Add a specification to the test suite."""
        self._specs.append(spec)
        return self

    def with_style(self, style: TestStyle) -> "TestSuiteBuilder":
        """Set test organization style."""
        self._style = style
        return self

    def with_docstrings(self, include: bool) -> "TestSuiteBuilder":
        """Include/exclude docstrings."""
        self._include_docstrings = include
        return self

    def with_markers(self, include: bool) -> "TestSuiteBuilder":
        """Include/exclude pytest markers."""
        self._include_markers = include
        return self

    def build(self) -> dict[str, str]:
        """Build test modules for all specs."""
        modules = {}
        for spec in self._specs:
            generator = TestGenerator(
                spec,
                style=self._style,
                include_docstrings=self._include_docstrings,
                include_markers=self._include_markers,
            )
            name = spec.get("name", "spec").replace("-", "_")
            modules[f"test_{name}.py"] = generator.generate()
        return modules


def main():
    parser = argparse.ArgumentParser(
        description="Generate pytest tests from structured specifications"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input specification file (JSON)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output test file (default: stdout)"
    )
    parser.add_argument(
        "--style", "-s",
        choices=["function", "class"],
        default="class",
        help="Test organization style (default: class)"
    )
    parser.add_argument(
        "--no-docstrings",
        action="store_true",
        help="Exclude docstrings from generated tests"
    )
    parser.add_argument(
        "--no-markers",
        action="store_true",
        help="Exclude pytest markers"
    )

    args = parser.parse_args()

    # Load specification
    spec = json.loads(Path(args.input).read_text())

    # Generate tests
    style = TestStyle.CLASS if args.style == "class" else TestStyle.FUNCTION
    generator = TestGenerator(
        spec,
        style=style,
        include_docstrings=not args.no_docstrings,
        include_markers=not args.no_markers,
    )
    code = generator.generate()

    # Output
    if args.output:
        Path(args.output).write_text(code)
        print(f"Generated tests written to: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
