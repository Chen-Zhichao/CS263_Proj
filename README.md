# Cross-Cultural Social Acceptability Classification

This project compares GPT-4.1 mini and Llama-3.1-8B-Instruct on social acceptability classification with and without cultural context.

## Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Add your local secrets to `.env`:

```bash
OPENAI_API_KEY=sk-...
HF_TOKEN=hf_...
```

Optional Hugging Face settings:

```bash
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct:cerebras
HF_BASE_URL=https://router.huggingface.co/v1
```

## Smoke Test

Run GPT-4.1 mini without cultural context:

```bash
python run_sample.py --model openai
```

Run GPT-4.1 mini with cultural context:

```bash
python run_sample.py --model openai --with-context
```

Run both selected models:

```bash
python run_sample.py --model both --with-context
```

## Evaluation Workflow

Convert the generated text dataset into JSONL:

```bash
python prepare_dataset.py
```

Preview the baseline and policy prompts without API calls:

```bash
python evaluate_dataset.py --model llama --condition all --limit 2 --dry-run
```

Run a small paid/free-quota test:

```bash
python evaluate_dataset.py --model llama --condition all --limit 5
```

If a run stops because of quota or an API error, resume it with the same output file:

```bash
python evaluate_dataset.py --model llama --condition all --output results/YOUR_RESULT_FILE.jsonl --resume
```

Run the full Llama evaluation:

```bash
python evaluate_dataset.py --model llama --condition all
```

Run the full GPT-4.1 mini evaluation after OpenAI billing is available:

```bash
python evaluate_dataset.py --model openai --condition all
```

Score a saved result file:

```bash
python score_results.py results/YOUR_RESULT_FILE.jsonl
```

For the final report, compare `culture_only` against `policy`. The main question is whether adding the human-written cultural policy improves accuracy and macro-F1.

## Push Changes

After editing code, commit and push with:

```bash
./push_changes.sh "Describe what changed"
```

Example:

```bash
./push_changes.sh "Update model prompt"
```

Before the first push, create an empty GitHub repo and connect it:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

The script checks that `.env` is ignored before it commits anything.

## Troubleshooting

If OpenAI returns `insufficient_quota`, your API account or project does not currently have usable API credits. A ChatGPT Pro subscription does not include OpenAI API credits. Add API billing or credits here:

https://platform.openai.com/account/billing/overview

Then retry after a few minutes. If it still fails, check that your `.env` key belongs to the same OpenAI project where billing is enabled.

If Hugging Face returns HTTP 402 for Inference Providers, the included monthly credits are depleted. You can wait for the monthly reset, buy prepaid credits, subscribe to Hugging Face PRO, use a custom provider key, or run Llama locally with vLLM. Completed predictions are saved incrementally, so resume later with:

```bash
python evaluate_dataset.py --model llama --condition all --output results/YOUR_RESULT_FILE.jsonl --resume
```
