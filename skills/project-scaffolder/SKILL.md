---
name: project-scaffolder
description: |
  Dynamically create project structures by asking clarifying questions. Use when the user wants to:
  (1) Start a new project from scratch
  (2) Scaffold a new application or codebase
  (3) Create project boilerplate or starter template
  (4) Initialize a new web app, API, CLI tool, or any software project
  Triggers on: "create a project", "scaffold", "new project", "initialize project", "start a new app", "project structure"
---

# Project Scaffolder

Create customized project structures by gathering requirements through targeted questions.

## Workflow

### Step 1: Ask Clarifying Questions

Use the AskUserQuestion tool to ask these questions (adjust based on context):

**Question 1 - Project Type:**
- Web Application (Frontend, Backend, Fullstack)
- API/Microservice
- CLI Tool
- Library/Package
- Desktop Application
- Mobile Application

**Question 2 - Technology Stack:**
Based on project type, offer relevant options:
- Web: React, Vue, Angular, Next.js, Django, Flask, Express, FastAPI
- API: Node/Express, Python/FastAPI, Go, Rust
- CLI: Python, Node, Go, Rust

**Question 3 - Project Complexity:**
- Minimal (bare essentials only)
- Standard (common patterns and structure)
- Full-featured (comprehensive with testing, CI/CD, docs)

**Question 4 - Additional Features (multiSelect):**
- Testing setup
- Docker configuration
- CI/CD pipeline
- Documentation structure
- Linting/formatting config
- Environment management

**Question 5 - Project Name:**
Ask for the project name if not already provided.

### Step 2: Generate Structure

Based on answers, create the appropriate structure. See [references/templates.md](references/templates.md) for structure patterns.

### Step 3: Create Files

1. Create the root project directory with the given name
2. Create all subdirectories
3. Generate starter files with appropriate boilerplate:
   - Package manifests (package.json, pyproject.toml, go.mod, etc.)
   - Entry point files (index.js, main.py, main.go, etc.)
   - Configuration files (.gitignore, .editorconfig, etc.)
   - README.md with project name and basic instructions

### Step 4: Summary

After creation, display:
1. Tree view of created structure
2. Next steps for the user (install dependencies, run dev server, etc.)

## Key Principles

- Always ask questions BEFORE creating anything
- Adapt questions based on context (skip if already answered)
- Create only what's necessary - avoid over-engineering
- Include helpful starter content in files, not empty placeholders
- Use current best practices for the chosen stack
