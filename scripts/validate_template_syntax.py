#!/usr/bin/env python3
"""
Validate all Jinja2 template syntax for the repository.
Exits with non-zero if any template has a syntax error.
"""
import sys
from pathlib import Path

try:
    # Prefer the project's TemplateRenderer if available
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from templating.template_renderer import TemplateRenderer
except Exception:
    TemplateRenderer = None


def _collect_templates(base: Path):
    patterns = ["**/*.j2", "**/*.jinja", "**/*.jinja2"]
    files = []
    for p in patterns:
        files.extend(base.glob(p))
    return sorted(files)


def validate_with_renderer(base: Path) -> int:
    errors = 0
    try:
        renderer = TemplateRenderer(base)
    except Exception as e:
        print("Failed to initialize TemplateRenderer:", e)
        return 2

    templates = _collect_templates(base)
    for t in templates:
        rel = t.relative_to(base)
        try:
            renderer.env.get_template(str(rel))
            print(f"OK {rel}")
        except Exception as e:
            print(f"ERROR {rel}: {e}")
            errors += 1

    return errors


def validate_with_jinja(base: Path) -> int:
    try:
        from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
    except Exception as e:
        print("Jinja2 not available:", e)
        return 2

    env = Environment(loader=FileSystemLoader(str(base)))
    errors = 0
    templates = _collect_templates(base)
    for t in templates:
        rel = t.relative_to(base)
        try:
            env.get_template(str(rel))
            print(f"OK {rel}")
        except TemplateSyntaxError as ex:
            print(f"Syntax error {rel}: {ex}")
            errors += 1
        except Exception as ex:
            print(f"Error loading {rel}: {ex}")
            errors += 1

    return errors


def main():
    base = Path("src/templates")
    if not base.exists():
        print("No templates directory found at src/templates")
        return 0

    if TemplateRenderer:
        rc = validate_with_renderer(base)
        if rc == 2:
            print("Falling back to jinja2 parser")
            rc = validate_with_jinja(base)
    else:
        rc = validate_with_jinja(base)

    if rc != 0:
        print(f"Template syntax validation failed (errors={rc})")
    else:
        print("All templates parsed OK")

    return rc


if __name__ == "__main__":
    sys.exit(main())
