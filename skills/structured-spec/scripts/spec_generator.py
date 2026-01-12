#!/usr/bin/env python3
"""
Structured Specification Generator

Converts loose requirements into normalized, machine-readable specifications.
Framework-agnostic, suitable for any project type.

Usage:
    python spec_generator.py --input "requirement text or file" [--output spec.json] [--format json|yaml]

    Or as a module:
        from spec_generator import SpecificationBuilder, Specification
        spec = SpecificationBuilder().from_text(input_text).build()
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"


@dataclass
class Requirement:
    """A single requirement with metadata."""
    id: str
    description: str
    type: RequirementType = RequirementType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    acceptance_criteria: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type.value,
            "priority": self.priority.value,
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "notes": self.notes,
        }


@dataclass
class Boundary:
    """Defines explicit scope boundaries."""
    in_scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Specification:
    """
    Complete structured specification.

    Attributes:
        name: Short identifier for the specification
        summary: One-paragraph description of purpose
        requirements: List of functional and non-functional requirements
        boundaries: Scope boundaries and assumptions
        external_dependencies: External systems, services, or data
        glossary: Domain-specific terms and definitions
        metadata: Version, author, timestamps
    """
    name: str
    summary: str
    requirements: list[Requirement] = field(default_factory=list)
    boundaries: Boundary = field(default_factory=Boundary)
    external_dependencies: list[str] = field(default_factory=list)
    glossary: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "status": "draft",
            }

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "summary": self.summary,
            "requirements": [r.to_dict() for r in self.requirements],
            "boundaries": self.boundaries.to_dict(),
            "external_dependencies": self.external_dependencies,
            "glossary": self.glossary,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_yaml(self) -> str:
        """Convert to YAML format (no external dependency)."""
        return self._dict_to_yaml(self.to_dict())

    def _dict_to_yaml(self, data: dict | list, indent: int = 0) -> str:
        """Simple YAML serializer without external dependencies."""
        lines = []
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    lines.append(f"{prefix}{key}: null")
                elif isinstance(value, (dict, list)) and value:
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._dict_to_yaml(value, indent + 1))
                elif isinstance(value, list) and not value:
                    lines.append(f"{prefix}{key}: []")
                elif isinstance(value, dict) and not value:
                    lines.append(f"{prefix}{key}: {{}}")
                elif isinstance(value, str):
                    if "\n" in value:
                        lines.append(f"{prefix}{key}: |")
                        for line in value.split("\n"):
                            lines.append(f"{prefix}  {line}")
                    else:
                        lines.append(f"{prefix}{key}: {json.dumps(value)}")
                else:
                    lines.append(f"{prefix}{key}: {json.dumps(value)}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}-")
                    lines.append(self._dict_to_yaml(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {json.dumps(item)}")

        return "\n".join(lines)

    def add_requirement(self, req: Requirement) -> "Specification":
        """Fluent method to add a requirement."""
        self.requirements.append(req)
        return self

    def validate(self) -> list[str]:
        """Validate specification completeness. Returns list of issues."""
        issues = []
        if not self.name:
            issues.append("Missing specification name")
        if not self.summary:
            issues.append("Missing summary")
        if not self.requirements:
            issues.append("No requirements defined")
        for req in self.requirements:
            if not req.acceptance_criteria:
                issues.append(f"Requirement {req.id} has no acceptance criteria")
        if self.boundaries.open_questions:
            issues.append(f"{len(self.boundaries.open_questions)} open question(s) remain")
        return issues


class SpecificationBuilder:
    """
    Builder for creating specifications from various input formats.

    Example:
        spec = (SpecificationBuilder()
            .with_name("user-auth")
            .with_summary("User authentication system")
            .add_functional("Users can log in with email/password")
            .add_constraint("Must complete auth in under 2 seconds")
            .in_scope("Login, logout, password reset")
            .out_of_scope("Social login, MFA")
            .build())
    """

    def __init__(self):
        self._name = ""
        self._summary = ""
        self._requirements: list[Requirement] = []
        self._boundaries = Boundary()
        self._external_deps: list[str] = []
        self._glossary: dict[str, str] = {}
        self._metadata: dict = {}
        self._req_counter = 0

    def _next_id(self, prefix: str = "REQ") -> str:
        self._req_counter += 1
        return f"{prefix}-{self._req_counter:03d}"

    def with_name(self, name: str) -> "SpecificationBuilder":
        self._name = name
        return self

    def with_summary(self, summary: str) -> "SpecificationBuilder":
        self._summary = summary
        return self

    def with_metadata(self, **kwargs) -> "SpecificationBuilder":
        self._metadata.update(kwargs)
        return self

    def add_requirement(
        self,
        description: str,
        req_type: RequirementType = RequirementType.FUNCTIONAL,
        priority: Priority = Priority.MEDIUM,
        acceptance_criteria: list[str] | None = None,
        dependencies: list[str] | None = None,
        notes: str | None = None,
    ) -> "SpecificationBuilder":
        prefix = {
            RequirementType.FUNCTIONAL: "FR",
            RequirementType.NON_FUNCTIONAL: "NFR",
            RequirementType.CONSTRAINT: "CON",
        }.get(req_type, "REQ")

        self._requirements.append(
            Requirement(
                id=self._next_id(prefix),
                description=description,
                type=req_type,
                priority=priority,
                acceptance_criteria=acceptance_criteria or [],
                dependencies=dependencies or [],
                notes=notes,
            )
        )
        return self

    def add_functional(
        self,
        description: str,
        priority: Priority = Priority.MEDIUM,
        acceptance_criteria: list[str] | None = None,
    ) -> "SpecificationBuilder":
        return self.add_requirement(
            description,
            RequirementType.FUNCTIONAL,
            priority,
            acceptance_criteria,
        )

    def add_non_functional(
        self,
        description: str,
        priority: Priority = Priority.MEDIUM,
        acceptance_criteria: list[str] | None = None,
    ) -> "SpecificationBuilder":
        return self.add_requirement(
            description,
            RequirementType.NON_FUNCTIONAL,
            priority,
            acceptance_criteria,
        )

    def add_constraint(
        self,
        description: str,
        priority: Priority = Priority.HIGH,
    ) -> "SpecificationBuilder":
        return self.add_requirement(
            description,
            RequirementType.CONSTRAINT,
            priority,
        )

    def in_scope(self, *items: str) -> "SpecificationBuilder":
        self._boundaries.in_scope.extend(items)
        return self

    def out_of_scope(self, *items: str) -> "SpecificationBuilder":
        self._boundaries.out_of_scope.extend(items)
        return self

    def assume(self, *assumptions: str) -> "SpecificationBuilder":
        self._boundaries.assumptions.extend(assumptions)
        return self

    def open_question(self, *questions: str) -> "SpecificationBuilder":
        self._boundaries.open_questions.extend(questions)
        return self

    def depends_on(self, *dependencies: str) -> "SpecificationBuilder":
        self._external_deps.extend(dependencies)
        return self

    def define_term(self, term: str, definition: str) -> "SpecificationBuilder":
        self._glossary[term] = definition
        return self

    def from_dict(self, data: dict) -> "SpecificationBuilder":
        """Load specification from a dictionary."""
        self._name = data.get("name", "")
        self._summary = data.get("summary", "")
        self._metadata = data.get("metadata", {})
        self._external_deps = data.get("external_dependencies", [])
        self._glossary = data.get("glossary", {})

        if "boundaries" in data:
            b = data["boundaries"]
            self._boundaries = Boundary(
                in_scope=b.get("in_scope", []),
                out_of_scope=b.get("out_of_scope", []),
                assumptions=b.get("assumptions", []),
                open_questions=b.get("open_questions", []),
            )

        for req in data.get("requirements", []):
            self._requirements.append(
                Requirement(
                    id=req.get("id", self._next_id()),
                    description=req.get("description", ""),
                    type=RequirementType(req.get("type", "functional")),
                    priority=Priority(req.get("priority", "medium")),
                    acceptance_criteria=req.get("acceptance_criteria", []),
                    dependencies=req.get("dependencies", []),
                    notes=req.get("notes"),
                )
            )
        return self

    def from_json(self, json_str: str) -> "SpecificationBuilder":
        """Load specification from JSON string."""
        return self.from_dict(json.loads(json_str))

    def from_file(self, path: str | Path) -> "SpecificationBuilder":
        """Load specification from a JSON file."""
        with open(path) as f:
            return self.from_json(f.read())

    def build(self) -> Specification:
        """Build and return the specification."""
        return Specification(
            name=self._name,
            summary=self._summary,
            requirements=self._requirements,
            boundaries=self._boundaries,
            external_dependencies=self._external_deps,
            glossary=self._glossary,
            metadata=self._metadata or None,
        )


def create_template() -> Specification:
    """Create an empty template specification."""
    return (
        SpecificationBuilder()
        .with_name("specification-name")
        .with_summary("Brief description of what this specification covers")
        .add_functional(
            "Example functional requirement",
            Priority.MEDIUM,
            ["Criterion 1", "Criterion 2"],
        )
        .add_non_functional("Example performance requirement")
        .add_constraint("Example constraint")
        .in_scope("What is included")
        .out_of_scope("What is explicitly excluded")
        .assume("Assumptions made")
        .open_question("Questions to be resolved")
        .depends_on("External system or service")
        .define_term("Term", "Definition of the term")
        .build()
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate structured specifications from requirements"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input file path (JSON) or use --template for empty template",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--template", "-t",
        action="store_true",
        help="Generate an empty template specification",
    )
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate the specification and report issues",
    )

    args = parser.parse_args()

    if args.template:
        spec = create_template()
    elif args.input:
        spec = SpecificationBuilder().from_file(args.input).build()
    else:
        parser.print_help()
        sys.exit(1)

    if args.validate:
        issues = spec.validate()
        if issues:
            print("Validation issues:", file=sys.stderr)
            for issue in issues:
                print(f"  - {issue}", file=sys.stderr)
            sys.exit(1)
        print("Specification is valid.", file=sys.stderr)

    output = spec.to_yaml() if args.format == "yaml" else spec.to_json()

    if args.output:
        Path(args.output).write_text(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
