from __future__ import annotations
import os
from typing import Iterable, List
from openai import OpenAI


def _clean_lines(text: str) -> List[str]:
    """Clean model output into a list of package lines."""
    text = text.strip()

    text = text.replace("```", "")

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # ignore bullets if model adds them
        if line.startswith(("-", "*")):
            line = line.lstrip("-* ").strip()
        lines.append(line)

    seen = set()
    out = []
    for x in lines:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def map_imports_to_requirements(imports: Iterable[str]) -> str:
    """
    Map python import module names -> pip package names using AI.
    Input should already exclude stdlib (we do that in core.py).
    Output is requirements.txt content (one package per line).
    """
    imports_list = sorted(set([i.strip() for i in imports if i and i.strip()]))

    if not imports_list:
        return ""

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    prompt = (
        "You generate requirements.txt for a Python project.\n\n"
        "INPUT: A list of top-level imported modules extracted ONLY from valid Python "
        "import statements (import X / from X import Y).\n\n"
        "RULES (MANDATORY):\n"
        "- Include ONLY third-party pip packages required to install the project.\n"
        "- Do NOT guess packages not present in the input list.\n"
        "- Do NOT add version numbers.\n"
        "- Output ONLY the requirements.txt content, one package per line.\n"
        "- If an import name differs from its pip package name, map it correctly "
        "(examples: sklearn -> scikit-learn, dotenv -> python-dotenv, PIL -> Pillow, cv2 -> opencv-python).\n\n"
        f"Imported modules:\n{chr(10).join(imports_list)}\n"
    )

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )

    text = (resp.output_text or "").strip()
    lines = _clean_lines(text)

    return "\n".join(lines) + ("\n" if lines else "")

def generate_docstring(function_code: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    prompt = (
        "- You are helpful developer \n"
        "You add a Python docstring to a single function.\n\n"
        "RULES (MANDATORY):\n"
        "- Do NOT change the function logic.\n"
        "- Do NOT rename variables.\n"
        "- Insert a triple-quoted docstring right after the function definition line.\n"
        "- If something is unclear, write TODO in the docstring instead of guessing.\n"
        "- Output ONLY valid Python code of the function (no explanations, no markdown).\n\n"
        "Function code:\n"
        "- Use Google-style docstring\n"
        "- Do NOT use TODO if function is obvious\n"
        "- Describe parameters and return on code base\n"
        "- Use TODO only if you didnt know something\n"
        f"{function_code}\n"
    )

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )

    return (resp.output_text or "").strip()


def generate_readme(code_input: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    prompt = f"""
    You are generating a README.md file for the user's project based ONLY on the provided code.

    GENERAL RULES (MANDATORY):
    - Write in English.
    - Use ONLY "##" for section headers.
    - Do NOT use emojis.
    - Do NOT invent files, folders, or project structure.
    - Do NOT add a footer or acknowledgements.
    - Keep the text clear, technical, and copy-friendly.
    - Do NOT mention any tool that generated this README.
    - Base your claims ONLY on what can be reasonably inferred from the code.

    TASK:
    - Infer what the code likely represents (e.g., Python script, Jupyter notebook workflow, data analysis, Streamlit app, CLI tool).
    - If the code is too small or ambiguous, keep the README generic and state assumptions in the Notes section.

    CODE:
    {code_input}

    REQUIRED SECTIONS AND CONTENT:

    ## Description
    Write a detailed description of what this project/code does and who it is for.
    Be specific when possible, based on the code, and avoid generic filler.

    ## Features
    List the key capabilities implied by the code as bullet points.

    ## Tech Stack
    List the main technologies and libraries actually used or imported in the code.
    If few or none are visible, mention Python and keep this section minimal.

    ## Setup
    Explain how to install dependencies using:
    pip install -r requirements.txt
    Do not list individual packages.

    ## Usage
    Explain how to run or use the project based on what the code suggests.
    Examples:
    - If it looks like a script: python your_script.py
    - If it looks like a notebook workflow: run cells in Jupyter
    - If it looks like a Streamlit app: streamlit run app.py
    If uncertain, describe the most likely usage and clearly state the assumption.

    ## Screenshots
    Mention that screenshots (if any) can be found in the `assets/` directory.

    ## Notes
    Include important notes, limitations, and assumptions.
    If something is unclear from the code, explicitly state what is assumed.

    OUTPUT:
    Return ONLY valid Markdown content for README.md.
    """

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )

    return (resp.output_text or "").strip()

def generate_cell_markdown(code_input: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    prompt = f"""
    You are generating a short Markdown description for a single Jupyter notebook cell.

    RULES (MANDATORY):
    - Write in English.
    - Output ONLY Markdown.
    - Do NOT use emojis.
    - Do NOT add explanations outside the Markdown.
    - Do NOT invent behavior not visible in the code.
    - Keep it very short and clear.

    FORMAT (EXACT):
    ## <Title>

    **Goal:** <One-sentence description of what this cell does.>

    GUIDELINES:
    - Title should be concise (2–6 words).
    - Goal should describe the main purpose of the code cell.
    - If the code is ambiguous, keep the description generic.

    CODE:
    {code_input}
    """

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )
    return (resp.output_text or "").strip()


def generate_github_description(code_input: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()
    prompt = f"""
    You are generating a short GitHub repository description based ONLY on the provided code.

    RULES (MANDATORY):
    - Write in English.
    - Output ONLY plain text (no Markdown).
    - Do NOT use emojis.
    - Do NOT add quotes.
    - Keep the description concise and technical.
    - Maximum length: 160 characters.
    - Base the description ONLY on what can be inferred from the code.
    - If the code is ambiguous, keep the description generic but accurate.

    CODE:
    {code_input}

    OUTPUT:
    Return a short GitHub repository description suitable for the GitHub "About" section.
    """

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )

    return (resp.output_text or "").strip()

def generate_github_tags(code_input: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()
    prompt = f"""
    You are generating GitHub repository topics based ONLY on the provided code.

    RULES (MANDATORY):
    - Write in English.
    - Output ONLY a single line of text.
    - Use lowercase letters only.
    - Use kebab-case for multi-word topics.
    - Separate topics with commas.
    - Do NOT use hashtags (#).
    - Generate between 5 and 10 topics.
    - Base topics ONLY on technologies, concepts, or domains visible in the code.
    - Do NOT invent unrelated topics.

    CODE:
    {code_input}

    OUTPUT FORMAT (EXACT):
    topic-one, topic-two, topic-three
    """

    resp = client.responses.create(
        model=model,
        input=prompt,
        temperature=0,
    )
    return (resp.output_text or "").strip()