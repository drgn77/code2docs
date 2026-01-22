from __future__ import annotations
from src.ai import map_imports_to_requirements
import ast
import sys
from typing import List, Set


def extract_imports(code: str) -> List[str]:
    """
    Extract top-level imported module names from valid Python import statements.

    Notes:
    - Ignores comments and docstrings automatically (AST parsing).
    - Returns only the top-level package name, e.g. "sklearn" from "sklearn.model_selection".
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    modules: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])

    return sorted(modules)


def is_stdlib_module(name: str) -> bool:
    """
    Check if module name belongs to Python standard library (Python 3.10+).
    """
    stdlib = getattr(sys, "stdlib_module_names", set())
    return name in stdlib


def generate_requirements_txt(code: str) -> str:
    """
    Create requirements.txt content from pasted code:
    - Extract imports via AST (real import/from only)
    - Remove stdlib modules
    - Use AI to map import names -> pip package names
    """
    imports = extract_imports(code)
    third_party = [m for m in imports if not is_stdlib_module(m)]
    return map_imports_to_requirements(third_party)

def generate_gitignore() -> str:
    return """
venv/
.env
.env.*
!.env.example

__pycache__/
*.pyc

.streamlit/

.idea/
.vscode/

.DS_Store
Thumbs.db

exports/
""".strip() + "\n"


def contains_single_function(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    return len(funcs) == 1
