import os
import json
import zipfile
import io
import re
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from typing import Optional

from app.core.config import settings

DEFAULT_AI_CONTEXT = {
    "test_cases": [],
    "test_results": [],
    "test_cases_str": "",
    "test_results_str": "",
    "test_plan": "",
    "test_report": "",
    "record": "",
}


def _get_default_context() -> dict:
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
    }


def _safe_render(doc: DocxTemplate, context: dict):
    """Render template with silent undefined — missing variables render as empty."""
    context_with_defaults = {**DEFAULT_AI_CONTEXT, **context}
    doc.render(context_with_defaults)


def resolve_template_path(template_path: str) -> str:
    if os.path.isabs(template_path):
        return template_path
    template_dir = Path(settings.TEMPLATE_DIR)
    return str(template_dir / template_path)


def generate_single_document(
    template_path: str,
    context: dict,
    output_filename: str,
) -> str:
    """Generate a single Word document, return the output path."""
    full_path = resolve_template_path(template_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"模板文件不存在: {full_path}")

    doc = DocxTemplate(full_path)
    full_context = {**_get_default_context(), **context}
    _safe_render(doc, full_context)

    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = str(output_dir / output_filename)
    doc.save(output_path)
    return output_path


def resolve_naming_rule(naming_rule: str, field_values: dict) -> str:
    """Replace {field_key} placeholders with actual field values.
    Sort by key length desc to avoid substring collision (e.g. 'class' matching inside 'class_num')."""
    result = naming_rule
    keys = sorted(field_values.keys(), key=len, reverse=True)
    for key in keys:
        value = field_values[key]
        replacement = str(value or "")
        # Only strip Windows-invalid filename characters
        replacement = re.sub(r'[\\/:*?"<>|]', '', replacement)
        replacement = replacement.strip()
        placeholder = f"{{{key}}}"
        if placeholder in result:
            result = result.replace(placeholder, replacement)
    return result


def batch_generate_documents(
    templates: list[dict],
    base_context: dict,
    field_values: dict,
    naming_rule: str,
):
    """
    Generate documents and return a list of {path, template_id} dicts.
    templates: [{id, name, file_path, doc_type}, ...]
    base_context: shared context (project info, ai result, etc.)
    field_values: form field values for naming
    naming_rule: e.g. "{project_name}_{doc_type}"
    """
    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    seen_filenames: set[str] = set()

    for tmpl in templates:
        try:
            doc_path = tmpl["file_path"]
            if not os.path.exists(doc_path):
                continue

            doc = DocxTemplate(doc_path)
            full_context = {**_get_default_context(), **base_context}
            # Merge form field values into template context so {{ field_key }} works
            full_context.update(field_values)
            if "doc_type" in tmpl:
                full_context["doc_type"] = tmpl["doc_type"]
            _safe_render(doc, full_context)

            # Resolve filename from naming rule
            naming_vars = {
                **field_values,
                "doc_type": tmpl.get("doc_type", "document"),
                "template_name": tmpl.get("name", "document"),
            }
            # Always append template_name if not already in naming rule
            effective_rule = naming_rule
            if "{template_name}" not in effective_rule:
                effective_rule = effective_rule.rstrip("_") + "_{template_name}"
            doc_filename = resolve_naming_rule(effective_rule, naming_vars)
            if not doc_filename.endswith(".docx"):
                doc_filename += ".docx"

            # Avoid filename collisions
            if doc_filename in seen_filenames:
                base, ext = os.path.splitext(doc_filename)
                counter = 2
                while f"{base}_{counter}{ext}" in seen_filenames:
                    counter += 1
                doc_filename = f"{base}_{counter}{ext}"
            seen_filenames.add(doc_filename)

            output_path = str(output_dir / doc_filename)
            doc.save(output_path)
            generated_files.append({
                "path": output_path,
                "template_id": tmpl["id"],
                "doc_type": tmpl.get("doc_type", "document"),
            })
        except Exception as e:
            print(f"Template {tmpl.get('name', 'unknown')} failed: {e}")

    if not generated_files:
        raise ValueError("没有成功生成的文档")
    return generated_files


def pack_to_zip(file_paths: list[str]) -> bytes:
    """Pack multiple files into a ZIP archive, return bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fp in file_paths:
            zf.write(fp, os.path.basename(fp))
    buf.seek(0)
    return buf.getvalue()


def re_render_documents(
    doc_template_pairs: list[dict],
    base_context: dict,
    ai_context: dict,
    field_values: dict,
    naming_rule: str,
):
    """
    Re-render existing documents with AI data merged in.
    doc_template_pairs: [{doc_id, doc_path, template_id, template_path, doc_type}, ...]
    Returns list of {doc_id, path} for the updated files.
    """
    output_dir = Path(settings.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    seen_filenames: set[str] = set()

    for pair in doc_template_pairs:
        try:
            tmpl_path = pair["template_path"]
            if not os.path.exists(tmpl_path):
                continue

            full_context = {**_get_default_context(), **base_context, **ai_context}
            full_context.update(field_values)
            if "doc_type" in pair:
                full_context["doc_type"] = pair["doc_type"]

            doc = DocxTemplate(tmpl_path)
            _safe_render(doc, full_context)

            naming_vars = {
                **field_values,
                "doc_type": pair.get("doc_type", "document"),
                "template_name": pair.get("template_name", "document"),
            }
            effective_rule = naming_rule
            if "{template_name}" not in effective_rule:
                effective_rule = effective_rule.rstrip("_") + "_{template_name}"
            doc_filename = resolve_naming_rule(effective_rule, naming_vars)
            if not doc_filename.endswith(".docx"):
                doc_filename += ".docx"

            if doc_filename in seen_filenames:
                base, ext = os.path.splitext(doc_filename)
                counter = 2
                while f"{base}_{counter}{ext}" in seen_filenames:
                    counter += 1
                doc_filename = f"{base}_{counter}{ext}"
            seen_filenames.add(doc_filename)

            output_path = str(output_dir / doc_filename)
            doc.save(output_path)
            results.append({"doc_id": pair["doc_id"], "path": output_path})
        except Exception as e:
            print(f"Re-render doc {pair.get('doc_id')} failed: {e}")

    return results
