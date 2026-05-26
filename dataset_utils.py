import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "interaction",
    "cultural_context",
    "cultural_value",
    "cultural_policy",
    "ground_truth_label",
    "explanation",
]

FIELD_PREFIXES = {
    "Interaction:": "interaction",
    "Cultural context:": "cultural_context",
    "Cultural value:": "cultural_value",
    "Cultural policy:": "cultural_policy",
    "Ground-truth label:": "ground_truth_label",
    "Explanation:": "explanation",
}

LABEL_ALIASES = {
    "acceptable": "acceptable",
    "accept": "acceptable",
    "socially acceptable": "acceptable",
    "unacceptable": "unacceptable",
    "not acceptable": "unacceptable",
    "socially unacceptable": "unacceptable",
    "depends": "depends",
    "depend": "depends",
    "context-dependent": "depends",
    "context dependent": "depends",
    "uncertain": "depends",
}


def normalize_label(label: str | None) -> str:
    if not label:
        return "missing"

    cleaned = str(label).strip().lower()
    cleaned = cleaned.strip("\"'` .")
    cleaned = cleaned.replace("_", " ").replace("/", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)

    if cleaned in LABEL_ALIASES:
        return LABEL_ALIASES[cleaned]
    if "unacceptable" in cleaned or "not acceptable" in cleaned:
        return "unacceptable"
    if "acceptable" in cleaned:
        return "acceptable"
    if "depend" in cleaned or "context" in cleaned or "uncertain" in cleaned:
        return "depends"
    return cleaned


def normalize_culture(culture: str) -> str:
    cleaned = culture.strip().replace("_", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.lower()


def parse_data_entry_text(text: str) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_field: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or set(line) == {"="}:
            continue

        example_match = re.fullmatch(r"Example\s+(\d+)", line)
        if example_match:
            if current:
                examples.append(_finalize_record(current))
            current = {"example_id": int(example_match.group(1))}
            current_field = None
            continue

        if current is None:
            continue

        matched_field = None
        for prefix, key in FIELD_PREFIXES.items():
            if line.startswith(prefix):
                matched_field = key
                current[key] = line[len(prefix) :].strip()
                current_field = key
                break

        if matched_field is None and current_field:
            current[current_field] = f"{current[current_field]} {line}".strip()

    if current:
        examples.append(_finalize_record(current))

    return examples


def _finalize_record(record: dict[str, Any]) -> dict[str, Any]:
    finalized = dict(record)
    finalized["label"] = normalize_label(finalized.get("ground_truth_label"))
    culture = finalized.get("cultural_context", "")
    finalized["culture_normalized"] = normalize_culture(culture)
    return finalized


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [record.get("example_id") for record in records]

    if len(ids) != len(set(ids)):
        errors.append("Duplicate example_id values found.")

    for expected_id, actual_id in enumerate(ids, start=1):
        if expected_id != actual_id:
            errors.append(f"Expected example_id {expected_id}, found {actual_id}.")

    for record in records:
        example_id = record.get("example_id", "unknown")
        for field in REQUIRED_FIELDS:
            if not str(record.get(field, "")).strip():
                errors.append(f"Example {example_id}: missing {field}.")

        if record.get("label") not in {"acceptable", "unacceptable", "depends"}:
            errors.append(
                f"Example {example_id}: unknown label {record.get('ground_truth_label')!r}."
            )

    return errors


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()


def dataset_summary(records: list[dict[str, Any]]) -> str:
    label_counts = Counter(record["label"] for record in records)
    culture_counts = Counter(record["culture_normalized"] for record in records)

    lines = [
        f"Examples: {len(records)}",
        "Labels:",
    ]
    for label in ["acceptable", "depends", "unacceptable"]:
        lines.append(f"  {label}: {label_counts[label]}")

    lines.append("Top cultures:")
    for culture, count in culture_counts.most_common(12):
        lines.append(f"  {culture}: {count}")

    return "\n".join(lines)
