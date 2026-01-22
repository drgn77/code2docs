import streamlit as st
from dotenv import load_dotenv

from src.core import (
    extract_imports,
    generate_requirements_txt,
    generate_gitignore,
    contains_single_function,
)
from src.ai import (
    generate_docstring,
    generate_readme,
    generate_cell_markdown,
    generate_github_tags,
    generate_github_description,
)

load_dotenv()

st.set_page_config(page_title="Code2Docs", layout="wide",page_icon="📄")

col_a, col_b = st.columns([1, 9], vertical_alignment="center")
with col_a:
    st.image("assets/logo.png", width=100)
with col_b:
    st.title("Code2Docs")
    st.caption("Turn code into documentation: README, requirements, docstrings, and GitHub metadata.")


with st.sidebar:
    pasted_code = st.text_area(
        "Paste your code here",
        height=520,
        placeholder="Paste Python code, a single function, or a notebook cell..."
    )

tabs = st.tabs([
    "Requirements",
    "Gitignore",
    "README",
    "Markdown",
    "Docstring",
    "GitHub",
])

with tabs[0]:
    st.caption("Generate a requirements.txt file from imports detected in the pasted code.")

    box = st.container(border=True)
    with box:
        btn_req = st.button("Create requirements.txt", type="primary", disabled=(not pasted_code))

        if btn_req:
            imports = extract_imports(pasted_code)
            req_text = generate_requirements_txt(pasted_code)

            with st.expander("Detected imports", expanded=False):
                st.code("\n".join(imports) if imports else "(none)")

            st.write("Generated requirements.txt:")
            st.code(req_text if req_text.strip() else "(empty)")

            st.download_button(
                label="Download requirements.txt",
                data=req_text,
                file_name="requirements.txt",
                mime="text/plain",
            )

with tabs[1]:

    st.caption(
        "Creates a ready-to-use .gitignore file for a typical Python project, "
        "including virtual environments and common IDE files."
    )

    box = st.container(border=True)
    with box:
        btn_gitignore = st.button("Create .gitignore", type="primary")

        if btn_gitignore:
            gitignore_text = generate_gitignore()
            st.toast(".gitignore generated")
            st.code(gitignore_text)

            st.download_button(
                label="Download .gitignore",
                data=gitignore_text,
                file_name=".gitignore",
                mime="text/plain",
            )

with tabs[2]:

    st.caption(
        "Generates a README.md describing the pasted code. "
        "The output is based only on what can be inferred from the code."
    )

    box = st.container(border=True)
    with box:
        btn_readme = st.button("Generate README.md", type="primary", disabled=(not pasted_code))

        if btn_readme:
            readme_text = generate_readme(pasted_code)
            st.toast("README.md generated")
            st.code(readme_text, language="markdown")

            st.download_button(
                label="Download README.md",
                data=readme_text + "\n",
                file_name="README.md",
                mime="text/markdown",
            )

with tabs[3]:

    st.caption(
        "Generates a minimal Markdown description for a single Jupyter notebook cell. "
        "The output includes only a title and a short goal."
    )

    box = st.container(border=True)
    with box:
        btn_md = st.button("Generate Markdown", type="primary", disabled=(not pasted_code))

        if btn_md:
            md_text = generate_cell_markdown(pasted_code)
            st.toast("Markdown generated")
            st.code(md_text, language="markdown")

with tabs[4]:

    st.caption(
        "Adds a Google-style docstring to a single Python function. "
        "The input must contain exactly one function definition."
    )
    box = st.container(border=True)
    with box:
        btn_doc = st.button("Generate docstring", type="primary", disabled=(not pasted_code))

        if btn_doc:
            if not contains_single_function(pasted_code):
                st.error("For docstring generation, paste exactly ONE Python function into the input box.")
            else:
                output = generate_docstring(pasted_code)
                st.toast("Docstring generated")
                st.code(output)

with tabs[5]:

    st.caption("Generate GitHub repository metadata based on the pasted code.")

    col1, col2 = st.columns(2)

    with col1:
        box = st.container(border=True)
        with box:
            btn_desc = st.button("Generate Description", type="primary", disabled=(not pasted_code))
            if btn_desc:
                description = generate_github_description(pasted_code)
                st.toast("GitHub description generated")
                st.text_area("GitHub Description", value=description, height=90)

    with col2:
        box = st.container(border=True)
        with box:
            btn_tags = st.button("Generate Topics", type="primary", disabled=(not pasted_code))
            if btn_tags:
                tags = generate_github_tags(pasted_code)
                st.toast("GitHub topics generated")
                st.text_area("GitHub Topics", value=tags, height=90)
