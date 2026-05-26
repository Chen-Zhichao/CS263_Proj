import argparse
from collections import Counter, defaultdict

from dataset_utils import load_jsonl


LABELS = ["acceptable", "depends", "unacceptable"]


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def compute_metrics(records: list[dict]) -> dict[str, float]:
    correct = sum(1 for record in records if record.get("correct"))
    accuracy = safe_divide(correct, len(records))

    f1_values = []
    for label in LABELS:
        tp = sum(
            1
            for record in records
            if record["gold_label"] == label and record["predicted_label"] == label
        )
        fp = sum(
            1
            for record in records
            if record["gold_label"] != label and record["predicted_label"] == label
        )
        fn = sum(
            1
            for record in records
            if record["gold_label"] == label and record["predicted_label"] != label
        )
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)
        f1_values.append(f1)

    return {
        "accuracy": accuracy,
        "macro_f1": sum(f1_values) / len(f1_values),
    }


def print_group_metrics(records: list[dict], group_name: str) -> None:
    groups = defaultdict(list)
    for record in records:
        key = tuple(record[field] for field in group_name.split(","))
        groups[key].append(record)

    for key, group_records in sorted(groups.items()):
        metrics = compute_metrics(group_records)
        key_text = " / ".join(key)
        print(
            f"{key_text}: n={len(group_records)} "
            f"accuracy={metrics['accuracy']:.3f} macro_f1={metrics['macro_f1']:.3f}"
        )


def print_confusion(records: list[dict]) -> None:
    counts = Counter(
        (record["gold_label"], record["predicted_label"]) for record in records
    )

    print("\nConfusion matrix")
    print("gold\\pred\t" + "\t".join(LABELS))
    for gold in LABELS:
        row = [str(counts[(gold, predicted)]) for predicted in LABELS]
        print(f"{gold}\t" + "\t".join(row))


def print_confusion_by_group(records: list[dict], fields: list[str]) -> None:
    groups = defaultdict(list)
    for record in records:
        key = tuple(record[field] for field in fields)
        groups[key].append(record)

    for key, group_records in sorted(groups.items()):
        print(f"\nConfusion matrix for {' / '.join(key)}")
        print("gold\\pred\t" + "\t".join(LABELS))
        counts = Counter(
            (record["gold_label"], record["predicted_label"])
            for record in group_records
        )
        for gold in LABELS:
            row = [str(counts[(gold, predicted)]) for predicted in LABELS]
            print(f"{gold}\t" + "\t".join(row))


def main() -> None:
    parser = argparse.ArgumentParser(description="Score prediction JSONL output.")
    parser.add_argument("results_file")
    args = parser.parse_args()

    records = [
        record
        for record in load_jsonl(args.results_file)
        if record.get("predicted_label") != "dry_run"
    ]
    if not records:
        raise SystemExit("No scored records found. Did you pass a dry-run file?")

    overall = compute_metrics(records)
    print(
        f"Overall: n={len(records)} "
        f"accuracy={overall['accuracy']:.3f} macro_f1={overall['macro_f1']:.3f}"
    )

    print("\nBy model / condition")
    print_group_metrics(records, "model,condition")
    print_confusion(records)
    print_confusion_by_group(records, ["model", "condition"])


if __name__ == "__main__":
    main()
