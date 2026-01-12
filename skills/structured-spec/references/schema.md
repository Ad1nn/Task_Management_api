# Specification Schema Reference

## Table of Contents
- [Root Structure](#root-structure)
- [Requirements](#requirements)
- [Boundaries](#boundaries)
- [Enumerations](#enumerations)
- [Best Practices](#best-practices)

---

## Root Structure

```json
{
  "name": "string (required)",
  "summary": "string (required)",
  "requirements": [Requirement],
  "boundaries": Boundary,
  "external_dependencies": ["string"],
  "glossary": {"term": "definition"},
  "metadata": {
    "version": "string",
    "created": "ISO datetime",
    "status": "draft|review|approved|deprecated"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Short kebab-case identifier |
| summary | string | Yes | One paragraph describing purpose |
| requirements | array | No | List of requirements |
| boundaries | object | No | Scope definitions |
| external_dependencies | array | No | External systems/services |
| glossary | object | No | Domain term definitions |
| metadata | object | No | Version and status info |

---

## Requirements

```json
{
  "id": "FR-001",
  "description": "What the system must do",
  "type": "functional|non_functional|constraint",
  "priority": "critical|high|medium|low",
  "acceptance_criteria": ["Testable condition"],
  "dependencies": ["REQ-ID"],
  "notes": "Additional context"
}
```

### Requirement Types

| Type | Prefix | Use For |
|------|--------|---------|
| functional | FR | What the system does |
| non_functional | NFR | Quality attributes (performance, security) |
| constraint | CON | Hard limitations or rules |

### Writing Good Requirements

- Start with a verb: "Allow", "Display", "Calculate", "Prevent"
- Be specific and measurable
- One requirement per entry
- Include acceptance criteria for testability

**Good**: "Allow users to reset password via email link that expires in 24 hours"
**Bad**: "Handle passwords properly"

---

## Boundaries

```json
{
  "in_scope": ["What is included"],
  "out_of_scope": ["What is explicitly excluded"],
  "assumptions": ["What we assume to be true"],
  "open_questions": ["Unresolved items"]
}
```

### Purpose of Each Field

| Field | Purpose |
|-------|---------|
| in_scope | Explicit inclusions to prevent scope creep |
| out_of_scope | Explicit exclusions to set expectations |
| assumptions | Conditions assumed true (document for validation) |
| open_questions | Items needing resolution before implementation |

---

## Enumerations

### Priority Levels

| Value | When to Use |
|-------|-------------|
| critical | System cannot function without this |
| high | Core functionality, needed for MVP |
| medium | Important but can be deferred |
| low | Nice to have, future enhancement |

### Status Values

| Value | Meaning |
|-------|---------|
| draft | Work in progress |
| review | Ready for stakeholder review |
| approved | Signed off, ready for implementation |
| deprecated | No longer valid |

---

## Best Practices

### Naming Conventions
- Use kebab-case for `name`: `user-authentication`, `payment-processing`
- Use prefixed IDs: `FR-001`, `NFR-001`, `CON-001`

### Acceptance Criteria
Write criteria that are:
- **Testable**: Can be verified as pass/fail
- **Specific**: Clear conditions and values
- **Independent**: Each criterion standalone

Example:
```json
"acceptance_criteria": [
  "Returns 200 OK with user object on valid credentials",
  "Returns 401 Unauthorized on invalid credentials",
  "Locks account after 5 failed attempts within 15 minutes"
]
```

### Scope Boundaries
Be explicit about exclusions:
```json
"in_scope": ["Email/password login", "Password reset", "Session management"],
"out_of_scope": ["Social OAuth", "Two-factor authentication", "Biometric login"]
```

### Dependencies
Reference by requirement ID:
```json
"dependencies": ["FR-001", "NFR-003"]
```

### Glossary
Define domain terms to prevent ambiguity:
```json
"glossary": {
  "User": "Registered account holder with verified email",
  "Session": "Authenticated state lasting 24 hours from last activity"
}
```
