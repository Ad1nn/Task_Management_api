---
name: structured-spec
description: |
  Convert loose ideas, requirements, or feature requests into clear, structured specifications.
  Produces normalized, machine-readable JSON/YAML output. Framework and technology agnostic.
  Use when: (1) User describes a vague idea or feature, (2) Requirements need formalization,
  (3) Creating a spec from conversation, (4) Normalizing existing requirements,
  (5) User says "spec", "specification", "formalize", "structure this requirement"
---

# Structured Specification Generator

Transform vague requirements into normalized, reusable specifications.

## Workflow

### Step 1: Gather Input

Accept input in any form:
- Conversational description ("I need a login system")
- Bullet points or notes
- Existing partial requirements
- User stories or feature requests

### Step 2: Extract and Clarify

Identify from the input:
1. **Core purpose** - What problem does this solve?
2. **Functional needs** - What must the system do?
3. **Quality attributes** - Performance, security, usability concerns?
4. **Constraints** - Hard rules or limitations?
5. **Boundaries** - What's in/out of scope?

Ask clarifying questions if critical information is missing.

### Step 3: Build Specification

Use the Python builder or construct manually:

```python
from spec_generator import SpecificationBuilder, Priority

spec = (SpecificationBuilder()
    .with_name("feature-name")
    .with_summary("One paragraph description")
    .add_functional("Requirement description", Priority.HIGH,
        ["Acceptance criterion 1", "Acceptance criterion 2"])
    .add_non_functional("Performance requirement")
    .add_constraint("Hard constraint")
    .in_scope("Included item 1", "Included item 2")
    .out_of_scope("Excluded item")
    .assume("Assumption")
    .open_question("Unresolved question")
    .depends_on("External dependency")
    .define_term("Term", "Definition")
    .build())
```

### Step 4: Output

Generate specification:
```bash
# Template
python scripts/spec_generator.py --template --format json

# From existing file
python scripts/spec_generator.py --input spec.json --format yaml

# Validate
python scripts/spec_generator.py --input spec.json --validate
```

Or use programmatically:
```python
print(spec.to_json())  # JSON output
print(spec.to_yaml())  # YAML output
issues = spec.validate()  # Check completeness
```

## Schema Reference

See [references/schema.md](references/schema.md) for complete schema documentation.

## Quick Reference

**Requirement Types**: `functional`, `non_functional`, `constraint`
**Priorities**: `critical`, `high`, `medium`, `low`
**ID Prefixes**: FR (functional), NFR (non-functional), CON (constraint)

## Composability

Specifications can be:
- Loaded from JSON: `SpecificationBuilder().from_file("spec.json").build()`
- Merged: Load multiple specs and combine requirements
- Extended: Add requirements to existing spec via `.add_requirement()`
- Validated: Check completeness before implementation
