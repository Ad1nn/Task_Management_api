# Project Structure Templates

## Table of Contents
- [Web Applications](#web-applications)
- [APIs and Microservices](#apis-and-microservices)
- [CLI Tools](#cli-tools)
- [Libraries/Packages](#librariespackages)
- [Common Add-ons](#common-add-ons)

---

## Web Applications

### React (Minimal)
```
project-name/
├── src/
│   ├── components/
│   ├── App.jsx
│   └── main.jsx
├── public/
│   └── index.html
├── package.json
├── vite.config.js
└── .gitignore
```

### React (Standard)
```
project-name/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── utils/
│   ├── App.jsx
│   └── main.jsx
├── public/
├── package.json
├── vite.config.js
├── .gitignore
└── README.md
```

### React (Full-featured)
```
project-name/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── utils/
│   ├── types/
│   ├── App.jsx
│   └── main.jsx
├── tests/
│   └── setup.js
├── public/
├── .github/
│   └── workflows/
│       └── ci.yml
├── package.json
├── vite.config.js
├── vitest.config.js
├── .eslintrc.json
├── .prettierrc
├── .gitignore
├── Dockerfile
└── README.md
```

### Next.js (Standard)
```
project-name/
├── src/
│   ├── app/
│   │   ├── layout.js
│   │   └── page.js
│   ├── components/
│   └── lib/
├── public/
├── package.json
├── next.config.js
├── .gitignore
└── README.md
```

### Django (Standard)
```
project-name/
├── project_name/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── core/
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       └── urls.py
├── templates/
├── static/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Flask (Standard)
```
project-name/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── templates/
├── tests/
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## APIs and Microservices

### Express.js (Standard)
```
project-name/
├── src/
│   ├── routes/
│   ├── controllers/
│   ├── middleware/
│   ├── models/
│   ├── utils/
│   └── index.js
├── tests/
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

### FastAPI (Standard)
```
project-name/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   └── services/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Go API (Standard)
```
project-name/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handlers/
│   ├── models/
│   └── services/
├── pkg/
├── go.mod
├── go.sum
├── Makefile
├── .gitignore
└── README.md
```

---

## CLI Tools

### Python CLI (Standard)
```
project-name/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── cli.py
│       └── commands/
├── tests/
├── pyproject.toml
├── .gitignore
└── README.md
```

### Node CLI (Standard)
```
project-name/
├── src/
│   ├── index.js
│   └── commands/
├── bin/
│   └── cli.js
├── package.json
├── .gitignore
└── README.md
```

### Go CLI (Standard)
```
project-name/
├── cmd/
│   └── project-name/
│       └── main.go
├── internal/
│   └── commands/
├── go.mod
├── Makefile
├── .gitignore
└── README.md
```

---

## Libraries/Packages

### npm Package (Standard)
```
project-name/
├── src/
│   └── index.js
├── tests/
├── package.json
├── .npmignore
├── .gitignore
└── README.md
```

### Python Package (Standard)
```
project-name/
├── src/
│   └── project_name/
│       └── __init__.py
├── tests/
├── pyproject.toml
├── .gitignore
└── README.md
```

---

## Common Add-ons

### Testing Setup
```
tests/
├── __init__.py (Python) or setup.js (JS)
├── unit/
└── integration/
```

### Docker
```
Dockerfile
docker-compose.yml
.dockerignore
```

### CI/CD (GitHub Actions)
```
.github/
└── workflows/
    ├── ci.yml
    └── deploy.yml
```

### Documentation
```
docs/
├── getting-started.md
├── api.md
└── contributing.md
```

### Linting/Formatting
JavaScript/TypeScript:
- .eslintrc.json
- .prettierrc

Python:
- pyproject.toml (ruff config)
- .pre-commit-config.yaml

### Environment Management
- .env.example
- .env.local (gitignored)
