import argparse
import json
import sys

from model_api import predict


SAMPLE_INTERACTION = (
    "A student directly disagrees with a professor in front of the class."
)

SAMPLE_CULTURE_CONTEXT = (
    "In this context, public disagreement with elders or authority figures is often "
    "considered impolite unless phrased carefully and respectfully."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one social acceptability API test.")
    parser.add_argument(
        "--model",
        choices=["openai", "llama", "both"],
        default="openai",
        help="Which model to call.",
    )
    parser.add_argument(
        "--with-context",
        action="store_true",
        help="Include the cultural context in the prompt.",
    )
    args = parser.parse_args()

    culture_context = SAMPLE_CULTURE_CONTEXT if args.with_context else None
    models = ["openai", "llama"] if args.model == "both" else [args.model]

    for model_name in models:
        try:
            result = predict(model_name, SAMPLE_INTERACTION, culture_context)
        except RuntimeError as exc:
            print(f"Error while running {model_name}: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
