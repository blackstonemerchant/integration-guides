#!/usr/bin/env python3
"""Generate native Zensical API reference pages from Swagger/OpenAPI."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = "https://services.bmspay.com/swagger/docs/v1"
DEFAULT_OUTPUT = Path("docs/core-apis/api-reference")
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head")

TAG_ORDER = (
    "Transactions",
    "Report",
    "Reporting",
    "Payment Links",
    "BusinessSettings",
    "Auth",
    "Recurring Billing",
    "Ach Processor",
    "Check Processor",
    "Ebt Transactions",
    "Gift Card",
    "Customers",
    "Administration",
    "Fraud Auto Deny Options",
    "Monetra Admin",
    "Signature Capture",
)

TAG_TITLES = {
    "Auth": "Authentication",
    "BusinessSettings": "Business Settings",
    "Ach Processor": "ACH Processor",
    "Ebt Transactions": "EBT Transactions",
}

TAG_DESCRIPTIONS = {
    "Transactions": "Sales, authorizations, completions, refunds, voids, tokens, and wallet payments.",
    "Report": "Transaction reports and report queries.",
    "Reporting": "Operational reporting and settlement data.",
    "Payment Links": "Create, manage, and inspect hosted payment links.",
    "BusinessSettings": "Merchant and application configuration.",
    "Auth": "Authenticate API clients and manage access.",
    "Recurring Billing": "Plans, subscriptions, and scheduled billing.",
    "Ach Processor": "ACH payment processing and reports.",
    "Check Processor": "Electronic check processing and reversals.",
    "Ebt Transactions": "EBT transaction processing.",
    "Gift Card": "Gift card sales, balances, and adjustments.",
    "Customers": "Customer records and stored payment details.",
    "Administration": "Administrative operations and account management.",
    "Fraud Auto Deny Options": "Automatic fraud-denial configuration.",
    "Monetra Admin": "Monetra administrative operations.",
    "Signature Capture": "Capture and retrieve transaction signatures.",
}

SENSITIVE_EXAMPLES = {
    "appkey": "your-app-key",
    "username": "your-username",
    "password": "your-password",
    "cardnumber": "<card-number>",
    "track1": "<encrypted-track-data>",
    "track2": "<encrypted-track-data>",
    "emvdata": "<emv-data>",
    "pinblock": "<encrypted-pin-block>",
    "ksn": "<key-serial-number>",
    "cvn": "<security-code>",
    "cvv": "<security-code>",
    "securedata": "<secure-data>",
    "digwlttoken": "<wallet-token>",
    "token": "<token>",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help="Swagger/OpenAPI URL or local JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for generated Markdown pages",
    )
    return parser.parse_args()


def load_specification(source: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = urllib.request.Request(
            source,
            headers={
                "Accept": "application/json",
                "User-Agent": "bpayd-integration-guides-build/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    else:
        payload = Path(source).read_bytes()

    spec = json.loads(payload)
    if not isinstance(spec, dict) or not (spec.get("swagger") or spec.get("openapi")):
        raise ValueError("The source is not a Swagger/OpenAPI document")
    if not isinstance(spec.get("paths"), dict):
        raise ValueError("The Swagger/OpenAPI document does not contain paths")
    return spec


def tag_title(tag: str) -> str:
    return TAG_TITLES.get(tag, tag)


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def operation_title(operation: dict[str, Any], path: str) -> str:
    if operation.get("summary"):
        return str(operation["summary"]).strip()
    action = path.rstrip("/").split("/")[-1]
    action = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", action)
    action = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", action)
    return action.strip() or path


def clean_text(value: Any) -> str:
    if not value:
        return ""
    lines = str(value).replace("\r\n", "\n").replace("\r", "\n").splitlines()
    return textwrap.dedent("\n".join(lines)).strip()


def table_text(value: Any) -> str:
    text = clean_text(value)
    text = re.sub(r"\s*\n\s*", "<br>", text)
    return text.replace("|", "\\|") or "—"


def reference_name(reference: str) -> str:
    return urllib.parse.unquote(reference.rsplit("/", 1)[-1])


def resolve_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    reference = schema.get("$ref")
    if not reference:
        return schema
    return spec.get("definitions", {}).get(reference_name(reference), schema)


def schema_label(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        name = reference_name(schema["$ref"])
        return f"[{name}](schemas.md#{slugify(name)})"
    if schema.get("type") == "array":
        return f"array of {schema_label(schema.get('items', {}))}"
    label = str(schema.get("type", "object"))
    if schema.get("format"):
        label += f" ({schema['format']})"
    enum = schema.get("enum")
    if enum:
        values = ", ".join(f"`{value}`" for value in enum)
        label += f" — {values}"
    return label


def property_rows(spec: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    resolved = resolve_schema(spec, schema)
    required = set(resolved.get("required", []))
    rows: list[str] = []
    for name, property_schema in resolved.get("properties", {}).items():
        requirement = '<span class="api-required">Required</span>' if name in required else "Optional"
        rows.append(
            f"| `{name}` | {schema_label(property_schema)} | {requirement} | "
            f"{table_text(property_schema.get('description'))} |"
        )
    return rows


def sample_string(name: str, schema: dict[str, Any]) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", name.lower())
    if normalized in SENSITIVE_EXAMPLES:
        return SENSITIVE_EXAMPLES[normalized]
    if "email" in normalized:
        return "developer@example.com"
    if normalized in {"usertransactionnumber", "transactionid", "orderreference"}:
        return "unique-transaction-id"
    if normalized in {"expdate", "expirationdate"}:
        return "MMYY"
    if "date" in normalized:
        return "2026-01-31"
    if "phone" in normalized:
        return "+1-555-0100"
    if "currency" in normalized:
        return "USD"
    if schema.get("format") == "uuid":
        return "00000000-0000-0000-0000-000000000000"
    if schema.get("format") in {"date", "date-time"}:
        return "2026-01-31T12:00:00Z" if schema["format"] == "date-time" else "2026-01-31"
    return f"<{slugify(name) or 'value'}>"


def is_sensitive_name(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", name.lower())
    sensitive_fragments = ("password", "cardnumber", "pinblock", "track1", "track2")
    return normalized in SENSITIVE_EXAMPLES or any(
        fragment in normalized for fragment in sensitive_fragments
    )


def schema_example(
    spec: dict[str, Any],
    schema: dict[str, Any],
    *,
    name: str = "value",
    depth: int = 0,
    seen: frozenset[str] = frozenset(),
    request: bool = False,
) -> Any:
    if depth > 3:
        return None

    if "$ref" in schema:
        model_name = reference_name(schema["$ref"])
        if model_name in seen:
            return None
        resolved = resolve_schema(spec, schema)
        return schema_example(
            spec,
            resolved,
            name=model_name,
            depth=depth,
            seen=seen | {model_name},
            request=request,
        )

    if schema.get("example") is not None and not is_sensitive_name(name):
        return schema["example"]
    if schema.get("enum"):
        return schema["enum"][0]

    schema_type = schema.get("type")
    if schema_type == "array":
        item = schema_example(
            spec,
            schema.get("items", {}),
            name=name,
            depth=depth + 1,
            seen=seen,
            request=request,
        )
        return [] if item is None else [item]
    if schema_type == "boolean":
        return name.lower() == "istest"
    if schema_type == "integer":
        if re.sub(r"[^a-z0-9]", "", name.lower()) == "responsecode":
            return 200
        return schema.get("minimum", 1)
    if schema_type == "number":
        return schema.get("minimum", 10.0 if "amount" in name.lower() else 1.0)
    if schema_type == "string":
        return sample_string(name, schema)

    properties = schema.get("properties", {})
    if properties:
        required = list(schema.get("required", []))
        selected = required if request and required else list(properties)
        if request and "IsTest" in properties and "IsTest" not in selected:
            selected.append("IsTest")
        if not request:
            selected = selected[:16]
        result: dict[str, Any] = {}
        for property_name in selected:
            property_schema = properties.get(property_name)
            if not property_schema:
                continue
            value = schema_example(
                spec,
                property_schema,
                name=property_name,
                depth=depth + 1,
                seen=seen,
                request=request,
            )
            if value is not None:
                result[property_name] = value
        return result
    return {}


def json_block(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def request_url(spec: dict[str, Any], path: str) -> str:
    schemes = spec.get("schemes") or ["https"]
    scheme = schemes[0]
    host = spec.get("host") or "services.bmspay.com"
    base_path = str(spec.get("basePath") or "").rstrip("/")
    return f"{scheme}://{host}{base_path}{path}"


def render_parameter_table(parameters: list[dict[str, Any]]) -> list[str]:
    non_body = [parameter for parameter in parameters if parameter.get("in") != "body"]
    if not non_body:
        return []
    lines = [
        "| Name | Location | Type | Required | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for parameter in non_body:
        required = '<span class="api-required">Required</span>' if parameter.get("required") else "Optional"
        lines.append(
            f"| `{parameter.get('name', '')}` | {parameter.get('in', '')} | "
            f"{schema_label(parameter)} | {required} | {table_text(parameter.get('description'))} |"
        )
    return lines


def render_operation(
    spec: dict[str, Any], path: str, method: str, operation: dict[str, Any]
) -> str:
    title = operation_title(operation, path)
    anchor = slugify(f"{method}-{path}")
    parameters = operation.get("parameters", [])
    body_parameter = next(
        (parameter for parameter in parameters if parameter.get("in") == "body"), None
    )
    body_schema = body_parameter.get("schema", {}) if body_parameter else None

    lines = [
        "---",
        "",
        f"## {title} {{ #{anchor} }}",
        "",
        '<div class="api-operation-route">',
        f'  <span class="api-method api-method--{method}">{method.upper()}</span>',
        f"  <code>{path}</code>",
        "</div>",
        "",
    ]

    description = clean_text(operation.get("description"))
    if description:
        lines.extend([description, ""])

    parameter_table = render_parameter_table(parameters)
    if parameter_table:
        lines.extend(["### Parameters", "", *parameter_table, ""])

    if body_schema:
        model = schema_label(body_schema)
        lines.extend(["### Request body", "", f"Schema: {model}", ""])
        rows = property_rows(spec, body_schema)
        if rows:
            lines.extend(
                [
                    "| Field | Type | Requirement | Description |",
                    "| --- | --- | --- | --- |",
                    *rows,
                    "",
                ]
            )

        sample = schema_example(spec, body_schema, request=True)
        sample_json = json_block(sample)
        content_type = (operation.get("consumes") or spec.get("consumes") or ["application/json"])[0]
        lines.extend(
            [
                '=== "cURL"',
                "",
                "    ```bash",
                f"    curl --request {method.upper()} \\",
                f"      --url '{request_url(spec, path)}' \\",
                f"      --header 'Content-Type: {content_type}' \\",
                "      --data-binary @- <<'JSON'",
                *[f"    {line}" for line in sample_json.splitlines()],
                "    JSON",
                "    ```",
                "",
                '=== "JSON"',
                "",
                "    ```json",
                *[f"    {line}" for line in sample_json.splitlines()],
                "    ```",
                "",
            ]
        )

    responses = operation.get("responses", {})
    if responses:
        lines.extend(
            [
                "### Responses",
                "",
                "| Status | Description | Schema |",
                "| --- | --- | --- |",
            ]
        )
        for status, response in responses.items():
            response_schema = response.get("schema")
            label = schema_label(response_schema) if response_schema else "—"
            lines.append(
                f'| <span class="api-response-code">{status}</span> | '
                f"{table_text(response.get('description'))} | {label} |"
            )
        lines.append("")

        success = responses.get("200") or responses.get("201")
        if success and success.get("schema"):
            example = schema_example(spec, success["schema"])
            lines.extend(
                [
                    '<details class="api-response-example">',
                    "<summary>Example response</summary>",
                    "",
                    "```json",
                    json_block(example),
                    "```",
                    "",
                    "</details>",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def grouped_operations(spec: dict[str, Any]) -> dict[str, list[tuple[str, str, dict[str, Any]]]]:
    groups: dict[str, list[tuple[str, str, dict[str, Any]]]] = defaultdict(list)
    for path, path_item in spec.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if not isinstance(operation, dict):
                continue
            tags = operation.get("tags") or ["Other"]
            groups[str(tags[0])].append((path, method, operation))
    return groups


def ordered_tags(groups: dict[str, Any]) -> list[str]:
    preferred = [tag for tag in TAG_ORDER if tag in groups]
    remaining = sorted(set(groups) - set(preferred), key=tag_title)
    return preferred + remaining


def promote_headings(markdown: str) -> str:
    lines = []
    skipping_legacy_thank_you = False
    for line in clean_text(markdown).splitlines():
        if line.strip().casefold() == "# thank you for choosing blackstone!".casefold():
            skipping_legacy_thank_you = True
            continue
        if skipping_legacy_thank_you:
            if not line.strip() or line.startswith((" ", "\t")):
                continue
            skipping_legacy_thank_you = False
        if line.startswith("    "):
            line = line[4:]
        if line.startswith("#"):
            line = "#" + line
        lines.append(line)
    return "\n".join(lines).strip()


def render_index(spec: dict[str, Any], groups: dict[str, Any], tags: list[str]) -> str:
    operation_count = sum(len(operations) for operations in groups.values())
    info = spec.get("info", {})
    cards = []
    for tag in tags:
        title = tag_title(tag)
        count = len(groups[tag])
        noun = "endpoint" if count == 1 else "endpoints"
        cards.extend(
            [
                f"-   **{title}**",
                "",
                f"    {TAG_DESCRIPTIONS.get(tag, f'{title} API operations.')}",
                "",
                f"    [{count} {noun} :octicons-arrow-right-24:]({slugify(tag)}.md)",
                "",
            ]
        )

    lines = [
        "---",
        "title: API Reference",
        "description: Native reference generated from the Bpayd Swagger/OpenAPI contract",
        "---",
        "",
        "# API Reference",
        "",
        "Explore the Bpayd REST API contract as native documentation. Every build regenerates "
        "these pages from the published Swagger/OpenAPI specification.",
        "",
        '<div class="api-reference-meta">',
        '  <code>Base URL: https://services.bmspay.com</code>',
        f"  <code>{operation_count} operations</code>",
        f"  <code>{len(spec.get('definitions', {}))} schemas</code>",
        "</div>",
        "",
        '!!! warning "Production API"',
        "    These endpoints target the production service. Use `IsTest: true` and your assigned "
        "test credentials when following the [Sandbox Guide](../../getting-started/sandbox.md).",
        "",
        "## API groups",
        "",
        '<div class="grid cards api-reference-grid" markdown>',
        "",
        *cards,
        "</div>",
        "",
        "## Schemas",
        "",
        "Browse the complete [request and response schema catalog](schemas.md).",
        "",
    ]

    source_description = promote_headings(info.get("description", ""))
    if source_description:
        lines.extend(["## Contract guide", "", source_description, ""])
    return "\n".join(lines).rstrip() + "\n"


def render_tag_page(
    spec: dict[str, Any], tag: str, operations: list[tuple[str, str, dict[str, Any]]]
) -> str:
    title = tag_title(tag)
    noun = "endpoint" if len(operations) == 1 else "endpoints"
    lines = [
        "---",
        f"title: {title}",
        f"description: {TAG_DESCRIPTIONS.get(tag, f'{title} API operations.')}",
        "---",
        "",
        f"# {title}",
        "",
        TAG_DESCRIPTIONS.get(tag, f"{title} API operations."),
        "",
        '<div class="api-reference-meta">',
        f"  <code>{len(operations)} {noun}</code>",
        '  <a href="../">All API groups</a>',
        "</div>",
        "",
    ]
    for path, method, operation in operations:
        lines.append(render_operation(spec, path, method, operation))
    return "\n".join(lines).rstrip() + "\n"


def render_schemas(spec: dict[str, Any]) -> str:
    definitions = spec.get("definitions", {})
    lines = [
        "---",
        "title: Schemas",
        "description: Bpayd API request and response models",
        "---",
        "",
        "# Schemas",
        "",
        f"{len(definitions)} request and response models generated from the API contract.",
        "",
        '<div class="api-reference-meta">',
        '  <a href="../">Back to API Reference</a>',
        "</div>",
        "",
    ]
    for name, schema in definitions.items():
        lines.extend(["---", "", f"## {name} {{ #{slugify(name)} }}", ""])
        description = clean_text(schema.get("description"))
        if description:
            lines.extend([description, ""])
        rows = property_rows(spec, schema)
        if rows:
            lines.extend(
                [
                    "| Field | Type | Requirement | Description |",
                    "| --- | --- | --- | --- |",
                    *rows,
                    "",
                ]
            )
        else:
            lines.extend([f"Type: {schema_label(schema)}", ""])
    return "\n".join(lines).rstrip() + "\n"


def write_pages(spec: dict[str, Any], output_dir: Path) -> tuple[int, int, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale_page in output_dir.glob("*.md"):
        stale_page.unlink()

    groups = grouped_operations(spec)
    tags = ordered_tags(groups)
    (output_dir / "index.md").write_text(render_index(spec, groups, tags), encoding="utf-8")
    for tag in tags:
        page = render_tag_page(spec, tag, groups[tag])
        (output_dir / f"{slugify(tag)}.md").write_text(page, encoding="utf-8")
    (output_dir / "schemas.md").write_text(render_schemas(spec), encoding="utf-8")
    operation_count = sum(len(operations) for operations in groups.values())
    return len(tags), operation_count, len(spec.get("definitions", {}))


def main() -> None:
    args = parse_args()
    spec = load_specification(args.source)
    tag_count, operation_count, schema_count = write_pages(spec, args.output_dir)
    print(
        f"Generated {tag_count} API groups, {operation_count} operations, and "
        f"{schema_count} schemas in {args.output_dir}"
    )


if __name__ == "__main__":
    main()
