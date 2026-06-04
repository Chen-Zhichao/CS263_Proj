import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from dataset_utils import load_jsonl
from score_results import LABELS, compute_metrics


def group_records(records: list[dict], fields: list[str]) -> dict[tuple, list[dict]]:
    groups = defaultdict(list)
    for record in records:
        groups[tuple(record[field] for field in fields)].append(record)
    return groups


def write_metrics_csv(records: list[dict], output_dir: Path) -> None:
    rows = []
    for key, group in sorted(group_records(records, ["model", "condition"]).items()):
        metrics = compute_metrics(group)
        rows.append(
            {
                "model": key[0],
                "condition": key[1],
                "n": len(group),
                "accuracy": f"{metrics['accuracy']:.3f}",
                "macro_f1": f"{metrics['macro_f1']:.3f}",
            }
        )

    path = output_dir / "metrics_by_condition.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["model", "condition", "n", "accuracy", "macro_f1"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {path}")


def write_confusion_csv(records: list[dict], output_dir: Path) -> None:
    rows = []
    for key, group in sorted(group_records(records, ["model", "condition"]).items()):
        counts = Counter((r["gold_label"], r["predicted_label"]) for r in group)
        for gold in LABELS:
            row = {"model": key[0], "condition": key[1], "gold_label": gold}
            for predicted in LABELS:
                row[f"pred_{predicted}"] = counts[(gold, predicted)]
            rows.append(row)

    path = output_dir / "confusion_by_condition.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "model",
            "condition",
            "gold_label",
            "pred_acceptable",
            "pred_depends",
            "pred_unacceptable",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {path}")


def write_changed_predictions(records: list[dict], output_dir: Path) -> None:
    by_example = defaultdict(dict)
    for record in records:
        by_example[(record["model"], record["example_id"])][record["condition"]] = record

    rows = []
    for (model, example_id), conditions in sorted(by_example.items()):
        baseline = conditions.get("culture_only")
        if not baseline:
            continue

        for condition, comparison in sorted(conditions.items()):
            if condition == "culture_only":
                continue
            if baseline["predicted_label"] == comparison["predicted_label"]:
                continue

            rows.append(
                {
                    "model": model,
                    "example_id": example_id,
                    "culture": comparison["culture"],
                    "gold_label": comparison["gold_label"],
                    "comparison_condition": condition,
                    "culture_only_prediction": baseline["predicted_label"],
                    "comparison_prediction": comparison["predicted_label"],
                    "comparison_helped": (not baseline["correct"]) and comparison["correct"],
                    "comparison_hurt": baseline["correct"] and (not comparison["correct"]),
                    "interaction": comparison["interaction"],
                    "comparison_explanation": comparison["prediction"].get(
                        "explanation", ""
                    ),
                }
            )

    path = output_dir / "changed_predictions.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "model",
            "example_id",
            "culture",
            "gold_label",
            "comparison_condition",
            "culture_only_prediction",
            "comparison_prediction",
            "comparison_helped",
            "comparison_hurt",
            "interaction",
            "comparison_explanation",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {path}")


def write_error_examples(records: list[dict], output_dir: Path, limit: int) -> None:
    errors = [record for record in records if not record["correct"]]
    errors = sorted(errors, key=lambda r: (r["condition"], r["example_id"]))[:limit]
    path = output_dir / "error_examples.json"
    path.write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create report-ready analysis files from model predictions."
    )
    parser.add_argument("results_file")
    parser.add_argument("--output-dir", default="analysis")
    parser.add_argument("--error-limit", type=int, default=20)
    args = parser.parse_args()

    records = [
        record
        for record in load_jsonl(args.results_file)
        if record.get("predicted_label") != "dry_run"
    ]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_metrics_csv(records, output_dir)
    write_confusion_csv(records, output_dir)
    write_changed_predictions(records, output_dir)
    write_error_examples(records, output_dir, args.error_limit)


if __name__ == "__main__":
    main()
