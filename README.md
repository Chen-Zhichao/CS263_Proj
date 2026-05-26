# Cross-Cultural Social Acceptability Classification

This project evaluates whether explicit cultural feedback improves social acceptability classification across cultural contexts.

We compare two models:

- GPT-4.1 mini through the OpenAI API
- Llama-3.1-8B-Instruct through Hugging Face Inference Providers

The final dataset contains 90 examples with balanced labels:

| Label | Count |
|---|---:|
| acceptable | 30 |
| depends | 30 |
| unacceptable | 30 |

## Project Structure

```text
data_entry.txt
data/dataset.jsonl
model_api.py
prepare_dataset.py
evaluate_dataset.py
score_results.py
analyze_results.py
results/
analysis_combined/
```

Important final files:

```text
results/llama_3_1_8b_instruct_90_balanced_all_conditions.jsonl
results/gpt_4_1_mini_90_balanced_all_conditions.jsonl
analysis_combined/results_summary.md
analysis_combined/metrics_by_condition.csv
analysis_combined/confusion_by_condition.csv
analysis_combined/changed_predictions.csv
analysis_combined/error_examples.json
analysis_combined/combined_90_balanced_results.jsonl
```

## Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Add local API keys to `.env`:

```bash
OPENAI_API_KEY=sk-...
HF_TOKEN=hf_...
```

Optional provider/model overrides:

```bash
OPENAI_MODEL=gpt-4.1-mini
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct:cerebras
HF_BASE_URL=https://router.huggingface.co/v1
```

Do not commit `.env`.

## Prompting Conditions

The experiment compares two conditions:

`culture_only`: The model receives the interaction and target culture only.

`policy`: The model receives the interaction, target culture, cultural value, and human-written cultural policy.

Each example is evaluated independently in a stateless API call. Earlier examples and predictions are not included in later prompts.

## Reproduce Dataset

Convert the generated text dataset into JSONL:

```bash
python prepare_dataset.py
```

Expected output:

```text
Examples: 90
acceptable: 30
depends: 30
unacceptable: 30
```

## Run Experiments

Preview prompts without API calls:

```bash
python evaluate_dataset.py --model llama --condition all --limit 2 --dry-run
```

Run the full Llama evaluation:

```bash
python evaluate_dataset.py \
  --model llama \
  --condition all \
  --output results/llama_3_1_8b_instruct_90_balanced_all_conditions.jsonl \
  --resume
```

Run the full GPT-4.1 mini evaluation:

```bash
python evaluate_dataset.py \
  --model openai \
  --condition all \
  --output results/gpt_4_1_mini_90_balanced_all_conditions.jsonl \
  --resume
```

The evaluator writes each prediction immediately. If a run stops because of quota or a network error, rerun the same command with `--resume`.

## Score Results

Score each model:

```bash
python score_results.py results/llama_3_1_8b_instruct_90_balanced_all_conditions.jsonl
python score_results.py results/gpt_4_1_mini_90_balanced_all_conditions.jsonl
```

Build combined analysis:

```bash
mkdir -p analysis_combined
cat results/llama_3_1_8b_instruct_90_balanced_all_conditions.jsonl \
    results/gpt_4_1_mini_90_balanced_all_conditions.jsonl \
    > analysis_combined/combined_90_balanced_results.jsonl

python analyze_results.py \
  analysis_combined/combined_90_balanced_results.jsonl \
  --output-dir analysis_combined
```

## Final Results

Final 90-example balanced dataset results:

| Model | Condition | N | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Llama-3.1-8B-Instruct | culture_only | 90 | 0.589 | 0.473 |
| Llama-3.1-8B-Instruct | policy | 90 | 0.689 | 0.609 |
| GPT-4.1 mini | culture_only | 90 | 0.700 | 0.688 |
| GPT-4.1 mini | policy | 90 | 0.778 | 0.767 |

Main finding: policy prompting improved both models. GPT-4.1 mini performed best overall, while Llama showed a large improvement from policy prompting but struggled with the `depends` label.

Use `analysis_combined/results_summary.md` for the final report and presentation.

## Push Changes

After editing code, commit and push with:

```bash
./push_changes.sh "Describe what changed"
```

Example:

```bash
./push_changes.sh "Finalize 90-example evaluation"
```

The script checks that `.env` is ignored before committing anything.

## Troubleshooting

If OpenAI returns `insufficient_quota`, your OpenAI API account or project does not currently have usable API credits. ChatGPT Pro does not include API credits. Add billing or credits here:

https://platform.openai.com/account/billing/overview

If Hugging Face returns HTTP 402 for Inference Providers, the included monthly credits are depleted. You can wait for the monthly reset, buy prepaid credits, subscribe to Hugging Face PRO, use a custom provider key, or run Llama locally with vLLM.

