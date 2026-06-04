# Results Summary

This summary uses the final balanced 90-example dataset. The dataset contains 30 acceptable, 30 depends, and 30 unacceptable examples. Each model was evaluated independently under three prompting conditions: `culture_only`, `policy`, and `few_shot_policy`.

## Dataset

| Label | Count |
|---|---:|
| acceptable | 30 |
| depends | 30 |
| unacceptable | 30 |
| total | 90 |

## Prompting Conditions

`culture_only`: The model receives the interaction and target culture only.

`policy`: The model receives the interaction, target culture, cultural value, and human-written cultural policy.

`few_shot_policy`: The model receives the same information as `policy`, plus three labeled in-context demonstrations: one acceptable example, one depends example, and one unacceptable example. The current test example is never used as its own demonstration.

Each example is evaluated in a stateless API call, so earlier predictions do not affect later predictions. The few-shot examples are included only inside the prompt as demonstrations; the models are not fine-tuned.

## Quantitative Results

| Model | Condition | N | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Llama-3.1-8B-Instruct | culture_only | 90 | 0.589 | 0.473 |
| Llama-3.1-8B-Instruct | policy | 90 | 0.689 | 0.609 |
| Llama-3.1-8B-Instruct | few_shot_policy | 90 | 0.689 | 0.646 |
| GPT-4.1 mini | culture_only | 90 | 0.700 | 0.688 |
| GPT-4.1 mini | policy | 90 | 0.778 | 0.767 |
| GPT-4.1 mini | few_shot_policy | 90 | 0.822 | 0.814 |

Policy prompting improved both models over the `culture_only` baseline. Few-shot policy prompting further improved macro-F1 for both models, especially by helping with context-dependent `depends` cases.

For Llama, accuracy improved from 0.589 in `culture_only` to 0.689 in both `policy` and `few_shot_policy`. Macro-F1 improved from 0.473 to 0.609 with policy prompting and to 0.646 with few-shot policy prompting.

For GPT-4.1 mini, accuracy improved from 0.700 in `culture_only` to 0.778 with policy prompting and 0.822 with few-shot policy prompting. Macro-F1 improved from 0.688 to 0.767 with policy prompting and 0.814 with few-shot policy prompting.

## Main Findings

GPT-4.1 mini outperformed Llama-3.1-8B-Instruct in all prompting conditions. This suggests that GPT-4.1 mini had stronger baseline social acceptability reasoning on this dataset.

Human-written cultural policies improved both models, supporting the project hypothesis that explicit cultural feedback helps models adapt to culturally dependent acceptability judgments.

The in-context learning variant, `few_shot_policy`, produced the best overall performance for GPT-4.1 mini and the best macro-F1 for Llama. This suggests that showing labeled examples helps models better understand the label schema, especially the difference between decisive labels and context-dependent cases.

The `depends` label remained the hardest class. Llama predicted `depends` zero times in the `culture_only` condition, five times in `policy`, and nine times in `few_shot_policy`. GPT-4.1 mini handled `depends` better, predicting it 23 times in `culture_only`, 22 times in `policy`, and 21 times in `few_shot_policy`.

## Confusion Matrix Notes

For Llama, policy prompting improved acceptable and unacceptable examples strongly. In the `policy` condition, Llama correctly classified all 30 acceptable examples and 28 of 30 unacceptable examples, but only 4 of 30 depends examples.

For Llama, `few_shot_policy` kept acceptable performance strong and improved depends performance from 4/30 to 8/30. However, it reduced unacceptable performance from 28/30 to 24/30, so few-shot examples improved macro-F1 without improving accuracy beyond the policy condition.

For GPT-4.1 mini, `few_shot_policy` produced the best results across all methods. It correctly classified 29 of 30 acceptable examples, 18 of 30 depends examples, and 27 of 30 unacceptable examples.

## Qualitative Analysis

Compared with `culture_only`, policy prompting changed 30 predictions across both models; 19 changes helped and 3 hurt. Few-shot policy prompting changed 35 predictions; 25 changes helped and 5 hurt.

For Llama, `policy` changed 15 predictions, with 9 helpful changes and 0 harmful changes. `few_shot_policy` changed 18 predictions, with 11 helpful changes and 2 harmful changes.

For GPT-4.1 mini, `policy` changed 15 predictions, with 10 helpful changes and 3 harmful changes. `few_shot_policy` changed 17 predictions, with 14 helpful changes and 3 harmful changes.

Representative helpful changes include cases where cultural guidance corrected the model's baseline assumption. For example, Llama initially predicted that immediately opening a gift in Tonga was acceptable, but after seeing the Tongan gift-giving policy, it changed the prediction to unacceptable. Few-shot prompting also helped Llama predict `depends` more often by showing a labeled context-dependent example before classification.

## Conclusion

The results show that explicit cultural context and human-written policies improve cross-cultural social acceptability classification for both models. The few-shot policy method, which combines cultural policy with labeled in-context demonstrations, provides the strongest overall improvement. GPT-4.1 mini is stronger overall, while Llama benefits substantially from both policy prompting and few-shot prompting. The main limitation is that both models, especially Llama, still struggle with the `depends` class.

