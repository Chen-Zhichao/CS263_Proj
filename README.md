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

## Troubleshooting

If OpenAI returns `insufficient_quota`, your API account or project does not currently have usable API credits. A ChatGPT Pro subscription does not include OpenAI API credits. Add API billing or credits here:

https://platform.openai.com/account/billing/overview

Then retry after a few minutes. If it still fails, check that your `.env` key belongs to the same OpenAI project where billing is enabled.
