import argparse
from pathlib import Path

from dataset_utils import (
    dataset_summary,
    parse_data_entry_text,
    validate_records,
    write_jsonl,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert data_entry.txt into validated JSONL."
    )
    parser.add_argument("--input", default="data_entry.txt", help="Source text file.")
    parser.add_argument(
        "--output", default="data/dataset.jsonl", help="Output JSONL dataset."
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    records = parse_data_entry_text(input_path.read_text(encoding="utf-8"))
    errors = validate_records(records)

    if errors:
        print("Dataset validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    write_jsonl(args.output, records)
    print(f"Wrote {args.output}")
    print(dataset_summary(records))


if __name__ == "__main__":
    main()

