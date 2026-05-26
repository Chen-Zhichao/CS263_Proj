# Results Summary

This summary uses the final balanced 90-example dataset. The dataset contains 30 acceptable, 30 depends, and 30 unacceptable examples. Each model was evaluated independently under two prompting conditions: `culture_only` and `policy`.

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

Each example is evaluated in a stateless API call, so earlier examples and predictions do not affect later predictions.

## Quantitative Results

| Model | Condition | N | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Llama-3.1-8B-Instruct | culture_only | 90 | 0.589 | 0.473 |
| Llama-3.1-8B-Instruct | policy | 90 | 0.689 | 0.609 |
| GPT-4.1 mini | culture_only | 90 | 0.700 | 0.688 |
| GPT-4.1 mini | policy | 90 | 0.778 | 0.767 |

Policy prompting improved both models. Llama improved from 0.589 to 0.689 accuracy, a gain of 10.0 percentage points, and from 0.473 to 0.609 macro-F1. GPT-4.1 mini improved from 0.700 to 0.778 accuracy, a gain of 7.8 percentage points, and from 0.688 to 0.767 macro-F1.

## Main Findings

GPT-4.1 mini outperformed Llama-3.1-8B-Instruct in both prompting conditions. This suggests that GPT-4.1 mini had stronger baseline social acceptability reasoning on this dataset.

Human-written cultural policies improved both models, supporting the project hypothesis that explicit cultural feedback helps models adapt to culturally dependent acceptability judgments.

The `depends` label remained the hardest class. Llama predicted `depends` zero times in the `culture_only` condition and only five times in the `policy` condition. GPT-4.1 mini handled `depends` better, predicting it 23 times in `culture_only` and 22 times in `policy`, but still confused several context-dependent examples with acceptable or unacceptable.

## Confusion Matrix Notes

For Llama, policy prompting improved acceptable and unacceptable examples strongly. In the policy condition, Llama correctly classified all 30 acceptable examples and 28 of 30 unacceptable examples. However, it correctly classified only 4 of 30 depends examples, showing a strong tendency to force context-dependent cases into binary labels.

For GPT-4.1 mini, policy prompting improved all three label categories. In the policy condition, GPT-4.1 mini correctly classified 29 of 30 acceptable examples, 16 of 30 depends examples, and 25 of 30 unacceptable examples.

## Qualitative Analysis

Across both models, 30 predictions changed between `culture_only` and `policy`. Of these changes, 19 helped and 3 hurt. This suggests that cultural policies usually move models toward the correct answer, but occasionally cause over-application of a cultural rule.

Llama changed 15 predictions after receiving policies; 9 of these changes helped and none hurt. GPT-4.1 mini also changed 15 predictions; 10 helped and 3 hurt.

Representative helpful changes include cases where the policy corrected a model's baseline assumption. For example, Llama initially predicted that immediately opening a gift in Tonga was acceptable, but after seeing the Tongan gift-giving policy, it changed the prediction to unacceptable. Similarly, policies helped Llama identify culturally specific unacceptable cases involving Serbian dress expectations, Israeli dietary restrictions, and Serbian bill-splitting norms.

## Conclusion

The results show that explicit cultural context and human-written policies improve cross-cultural social acceptability classification for both models. GPT-4.1 mini is stronger overall, but Llama benefits substantially from policy prompting. The main limitation is that both models, especially Llama, struggle with the `depends` class. Future work should test prompts that define `depends` more explicitly and instruct models not to force uncertain or context-sensitive cases into binary acceptable/unacceptable labels.

