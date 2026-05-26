import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from dataset_utils import append_jsonl, load_jsonl, normalize_label
from model_api import predict


def build_condition_context(record: dict[str, Any], condition: str) -> str | None:
    culture = record["cultural_context"]

    if condition == "no_context":
        return None
    if condition == "culture_only":
        return f"Target culture: {culture}"
    if condition == "value_only":
        return (
            f"Target culture: {culture}\n"
            f"Cultural value: {record['cultural_value']}"
        )
    if condition == "policy":
        return (
            f"Target culture: {culture}\n"
            f"Cultural value: {record['cultural_value']}\n"
            f"Cultural policy: {record['cultural_policy']}"
        )

    raise ValueError(f"Unknown condition: {condition}")


def evaluate_record(
    record: dict[str, Any],
    model_name: str,
    condition: str,
    dry_run: bool,
) -> dict[str, Any]:
    context = build_condition_context(record, condition)

    result = {
        "example_id": record["example_id"],
        "model": model_name,
        "condition": condition,
        "culture": record["cultural_context"],
        "culture_normalized": record["culture_normalized"],
        "gold_label": record["label"],
        "interaction": record["interaction"],
    }

    if dry_run:
        result["prompt_context"] = context
        result["prediction"] = {
            "label": "dry_run",
            "explanation": "No API call was made.",
        }
        result["predicted_label"] = "dry_run"
        result["correct"] = False
        return result

    prediction = predict(model_name, record["interaction"], context)
    predicted = prediction.get("prediction", {})
    predicted_label = normalize_label(predicted.get("label"))

    result["prediction"] = predicted
    result["predicted_label"] = predicted_label
    result["correct"] = predicted_label == record["label"]
    return result


def result_key(record: dict[str, Any]) -> tuple[str, str, int]:
    return (record["model"], record["condition"], int(record["example_id"]))


def task_key(model_name: str, condition: str, record: dict[str, Any]) -> tuple[str, str, int]:
    return (model_name, condition, int(record["example_id"]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run baseline and policy-augmented model evaluation."
    )
    parser.add_argument("--input", default="data/dataset.jsonl")
    parser.add_argument(
        "--model", choices=["openai", "llama", "both"], default="llama"
    )
    parser.add_argument(
        "--condition",
        choices=["no_context", "culture_only", "value_only", "policy", "all"],
        default="culture_only",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompt contexts without making API calls.",
    )
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Append to an existing output file and skip completed records.",
    )
    args = parser.parse_args()

    records = load_jsonl(args.input)
    if args.limit is not None:
        records = records[: args.limit]

    models = ["openai", "llama"] if args.model == "both" else [args.model]
    conditions = (
        ["culture_only", "policy"]
        if args.condition == "all"
        else [args.condition]
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output
    if output_path is None:
        suffix = "dry_run" if args.dry_run else "predictions"
        output_path = f"results/{suffix}_{timestamp}.jsonl"

    output_file = Path(output_path)
    completed_keys = set()
    if output_file.exists():
        if not args.resume:
            raise SystemExit(
                f"{output_path} already exists. Use --resume to append and skip "
                "completed predictions, or choose a new --output path."
            )
        completed_keys = {result_key(record) for record in load_jsonl(output_file)}
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)

    tasks = [
        (model_name, condition, record)
        for model_name in models
        for condition in conditions
        for record in records
        if task_key(model_name, condition, record) not in completed_keys
    ]

    total = len(tasks)
    if not total:
        print("No remaining records to evaluate.")
        print(f"Output file: {output_path}")
        return

    for current, (model_name, condition, record) in enumerate(tasks, start=1):
        print(
            f"[{current}/{total}] {model_name} {condition} "
            f"example {record['example_id']}"
        )
        try:
            output_record = evaluate_record(record, model_name, condition, args.dry_run)
        except RuntimeError as exc:
            print(f"Stopped before writing this record: {exc}")
            print(f"Completed predictions are saved in {output_path}")
            raise SystemExit(1) from exc

        append_jsonl(output_path, output_record)
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Wrote {output_path}")
    print(json.dumps({"new_records": total}, indent=2))


if __name__ == "__main__":
    main()
