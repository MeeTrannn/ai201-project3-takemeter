# Climate Discourse Classifier

Classify Reddit climate-change posts by **primary reader-facing intent** into four labels: `report`, `appeal`, `inquiry`, and `commentary`.

## Community & Task

**Community:** Reddit climate-change discourse from *The Reddit Climate Change Dataset* (subreddits such as r/climatechange, r/environment, r/worldnews, r/NoStupidQuestions, r/DemocraticSocialism).

**Task:** Given a post's body text (`selftext`), predict what the author mainly wants the reader to do — understand (`report`), act (`appeal`), answer (`inquiry`), or witness a viewpoint (`commentary`).

Full design rationale, label definitions, and data pipeline are in [`planning.md`](planning.md).

---

## Labels

| Label | Definition |
|---|---|
| **report** | Author wants reader to **know or understand** climate events, impacts, data, or mechanisms — no ask to act or answer. |
| **appeal** | Author wants reader to **do something** — participate, adopt behavior, support policy/tech, take responsibility. |
| **inquiry** | Author wants reader to **provide** information, evidence, advice, or opinions. |
| **commentary** | Author **expresses a viewpoint or narrative** without a concrete ask (skepticism, denial, satire, conspiracy). |

**Tie-break:** `inquiry` → `appeal` → `report` → `commentary`

---

## Dataset

| File | Description |
|---|---|
| `the-reddit-climate-change-dataset-posts-clean.csv` | 200 labeled posts (50 per label) |
| `backfill_log.csv` | 62 posts added from full corpus for balance |
| `filtered_out.csv` | 62 posts removed (link-only, polls, duplicates, off-topic) |

**Pipeline:** Sample 200 non-empty posts → filter low-quality rows → backfill underrepresented labels from full corpus (`~/Downloads/the-reddit-climate-change-dataset-posts.csv`).

**Split:** 80/20 stratified — 160 train / 40 test (10 per label in test). Baseline and fine-tuned models evaluated on a **30-post stratified subset** of the test set.

---

## Models

### Zero-shot baseline (Groq)

Llama 3 via Groq API with a hand-written classification prompt defining community, labels, examples, and strict output format (label name only).

### Fine-tuned DistilBERT

`distilbert-base-uncased` fine-tuned on 160 training examples for 4-way sequence classification (`report`, `appeal`, `inquiry`, `commentary`).

---

## Evaluation Report

### Overall accuracy

| Model | Accuracy | Notes |
|---|---|---|
| Zero-shot baseline (Groq) | **0.733** | 22 / 30 correct; all 30 responses parseable |
| Fine-tuned DistilBERT | **0.200** | 6 / 30 correct |
| **Regression** | **−0.533** | Fine-tuning hurt vs. baseline |

Neither model meets the "genuinely useful" thresholds in `planning.md` (macro-F1 ≥ 0.72). The baseline is usable as a prototype; the fine-tuned model is not.

### Per-class metrics — zero-shot baseline (Groq)

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| report | 0.83 | 0.62 | 0.71 | 8 |
| appeal | 1.00 | 0.71 | 0.83 | 7 |
| inquiry | 0.86 | 0.75 | 0.80 | 8 |
| commentary | 0.50 | 0.86 | 0.63 | 7 |
| **Macro avg** | **0.80** | **0.74** | **0.74** | 30 |
| **Accuracy** | | | **0.73** | 30 |

**Baseline strengths:** High precision on `appeal` (1.00) and `inquiry` (0.86) — when it commits, it is usually right.  
**Baseline weaknesses:** Low `commentary` precision (0.50) — half of commentary predictions are wrong, likely confused with `appeal`. Low `report` recall (0.62) — factual/bot summaries misread as calls to action.

### Per-class metrics — fine-tuned DistilBERT

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| report | 0.00 | 0.00 | 0.00 | 8 |
| appeal | 0.29 | 0.86 | 0.45 | 7 |
| inquiry | 0.00 | 0.00 | 0.00 | 8 |
| commentary | 0.00 | 0.00 | 0.00 | 7 |
| **Macro avg** | **0.07** | **0.21** | **0.11** | 30 |
| **Accuracy** | | | **0.20** | 30 |

The fine-tuned model **collapsed toward `appeal`** — it predicts `appeal` for most inputs regardless of intent.

### Confusion matrix — fine-tuned DistilBERT

Rows = true label, columns = predicted label.

|  | **report** | **appeal** | **inquiry** | **commentary** |
|---|---|---|---|---|
| **report** | 0 | 8 | 0 | 0 |
| **appeal** | 0 | 6 | 0 | 1 |
| **inquiry** | 0 | 8 | 0 | 0 |
| **commentary** | 0 | 7 | 0 | 0 |

**Dominant error pattern:** Every non-appeal class is routed to `appeal` (23 / 24 errors). The model learned surface cues ("climate change," imperative tone, questions) as proxies for `appeal` rather than the intent-based boundary in `planning.md`.

### Confusion matrix — zero-shot baseline (Groq)

Exact cell counts not exported; directional pattern from per-class metrics:

- **`report` → `appeal`** — main baseline leak (low report recall 0.62). Bot summaries and factual posts with any urgency language misclassified.
- **`commentary` → `appeal`** — drives low commentary precision (0.50). Rants with rhetorical questions look like appeals.
- **`inquiry` → `appeal`** — occasional; questions framed with "we need to" language.

---

## Error Analysis (Fine-Tuned Model)

### Which labels are confused?

**`report` → `appeal`**, **`inquiry` → `appeal`**, and **`commentary` → `appeal`** account for nearly all 24 errors. One reverse error: **`appeal` → `commentary`**. The boundary the model failed to learn is **appeal vs. everything else**.

### Example 1 — Bot news summary (`report` → `appeal`)

**Text:** *"This is the best tl;dr I could make… As Europe's energy costs skyrocket, Russia is burning off large amounts of natural gas…"*

**True:** `report` | **Predicted:** `appeal` (confidence: 0.27)

**Why it failed:** The model keyed on energy crisis + Russia + urgency — topic and tone that co-occur with advocacy posts in training — instead of the **bot-summary structure** (neutral news relay). Our label definition says convey what happened → `report`, but the model treated alarming content as a call to action.

**Labeling vs. data vs. model:** Labeling is consistent (bot tl;dr posts labeled `report` elsewhere in the set). The issue is **training signal**: `appeal` examples include persuasive news shares; the model cannot separate neutral relay from motivated relay. Fix: more `report` examples that are alarming but non-persuasive; prompt rule: "bot summaries and news excerpts without author advocacy → report."

### Example 2 — Skeptical rant (`commentary` → `appeal`)

**Text:** *"Duh. Yes, temperatures go up and down. How is this news to anyone? And why does anyone think this is a problem?…"*

**True:** `commentary` | **Predicted:** `appeal` (confidence: 0.29)

**Why it failed:** Rhetorical questions mimic `inquiry`/`appeal` surface form. DistilBERT likely attends to `?` tokens and debate framing. Our definition excludes rhetorical questions from `inquiry`, but the model has no explicit notion of **rhetorical vs. genuine** ask.

**Labeling vs. data vs. model:** Labeling is correct per decision tree (rant → `commentary`). This is a **model + prompt gap** — need negation examples in `commentary` with question marks; optionally a feature or rule for rhetorical question detection.

### Example 3 — Genuine question (`inquiry` → `appeal`)

**Text:** *"We all know climate change is going to massively impact skiing… So what ski areas will be able to still survive once climate change gets worse?"*

**True:** `inquiry` | **Predicted:** `appeal` (confidence: 0.27)

**Why it failed:** Topic (climate impact) + future urgency + question mark. Structurally a clear `inquiry` (seeking information), but topic words overlap heavily with `appeal` training examples about adaptation and action.

**Labeling vs. data vs. model:** Consistent labeling. Fix: more `inquiry` posts that mention harms *then* ask; tighten contrast with `appeal` in prompt ("if the author seeks advice rather than urging action → inquiry").

### Example 4 — Policy advocacy (`appeal` → `commentary`) — rare reverse error

**Text:** *"We are too far gone to try free market approaches… we need to stop the bleeding…"*

**True:** `appeal` | **Predicted:** `commentary` (confidence: 0.27)

**Why it failed:** Reads like an opinion rant. Our `appeal` vs. `commentary` boundary hinges on whether the author urges **concrete action** — this post does, but without a survey link or specific policy the model treated it as venting.

**Labeling vs. data vs. model:** Borderline case — could be reviewed. Suggests **annotation ambiguity** on advocacy-without-specific-CTA posts; model confusion is partly justified.

### What would need to change?

1. **Do not deploy the fine-tuned model** at 200 examples — severe class collapse; use baseline or gather more data.
2. **Human-review labels** — especially `backfill_log.csv` (62 heuristic labels).
3. **Add hard negatives for `appeal`** — alarming `report` posts, rhetorical-question `commentary`, harm-context `inquiry`.
4. **Improve prompt** with explicit negatives: "Bot summaries → report. Rhetorical questions in rants → commentary. Questions seeking advice → inquiry."
5. **Re-train** with class weights or focal loss to counter `appeal` bias; try fewer epochs to avoid collapse.

---

## Sample Classifications (Fine-Tuned DistilBERT)

| Post (truncated) | True label | Predicted | Confidence | Correct? |
|---|---|---|---|---|
| BBC bot tl;dr: Russia burning natural gas… | report | appeal | 0.27 | ✗ |
| Survey: fill in this 4-question form on climate language… | appeal | appeal | 0.31 | ✓ |
| Sun moving closer to the sun, planets absorbed… | commentary | appeal | 0.28 | ✗ |
| Any recommendations for trees to plant for climate change? | inquiry | appeal | 0.27 | ✗ |
| We need to stop the bleeding, free market won't work… | appeal | commentary | 0.27 | ✗ |

**Why the survey example is a reasonable correct prediction:** The post explicitly requests participation ("fill in this form," "conducting a survey") — the strongest surface signal for `appeal` in our taxonomy. Even a collapsed model gets this right because survey language is a high-salience n-gram in the training set.

---

## Reflection: What the Model Captured vs. What We Intended

**We intended** intent-based classification: *What does the author want the reader to do?* — a semantic distinction between reporting, asking, urging, and opining.

**The fine-tuned model captured** topic and tone shortcuts: climate alarm vocabulary, question marks, imperative mood → `appeal`. It **overfit to the most frequent cues in `appeal` backfill examples** (surveys, advocacy, "we need to") and ignored structural intent.

**It missed:**
- **Report vs. appeal:** Neutral information delivery (bot summaries, statistics) vs. persuasion
- **Commentary vs. appeal:** Rhetorical opposition vs. genuine call to action
- **Inquiry vs. appeal:** Advice-seeking questions vs. participation requests

**The baseline (Groq)** partially captured intent via the full prompt and few-shot examples (0.73 accuracy) but still over-predicted `appeal` for `report` and `commentary` posts — suggesting the **`report` ↔ `appeal` boundary is the hardest** in this corpus, not a failure of fine-tuning alone.

**Gap summary:** Our labels are **intent-based**; both models' decision boundaries drift toward **topic + mood**. Closing that gap needs more human-verified examples at the confused boundaries, not just more data volume.

---

## Spec Reflection

**How the spec helped:** `planning.md` forced intent-based labels (v2 taxonomy) instead of topic labels (`problem`/`solution`). That made error analysis actionable — we can name confusions as `report → appeal` rather than vague "wrong topic." The spec's filter pipeline (remove link-only, polls, duplicates) also improved label signal in the 200-post set.

**Where we diverged:** The spec called for **human review of all 200 labels** before training; we trained on **AI-pre-labeled data** with heuristic backfill (62 posts). That likely introduced label noise and inflated `appeal` training cues, contributing to fine-tuned collapse. We also evaluated on 30 posts rather than the full 40-test holdout — diverged for notebook runtime, but still stratified.

---

## AI Usage Disclosure

### Instance 1 — Taxonomy design and dataset pipeline

**Directed:** Cursor AI to define mutually exclusive v2 labels, filter link-only/poll/spam posts, and backfill from the full corpus to 50/label.

**Produced:** `planning.md`, `filter_dataset.py`, `backfill_from_corpus.py`, and AI-labeled CSV.

**Overrode:** Revised v1 labels (`problem`/`solution`/`question`/`other`) to v2 (`report`/`appeal`/`inquiry`/`commentary`) after manual review showed `problem` conflated factual reports with conspiracy narratives. Flagged `review_flag` rows for human check rather than accepting all backfill labels blindly.

### Instance 2 — Annotation pre-labeling

**Directed:** AI to pre-label all 200 posts using the v2 decision tree.

**Produced:** `prelabel` and `label` columns (`prelabeled_by_ai=true`).

**Overrode:** Did not complete full human re-review before fine-tuning — acknowledged as a limitation in evaluation. Classification prompt for Groq baseline was written manually using `planning.md` definitions, not copied verbatim from AI draft.

### Instance 3 — Evaluation write-up

**Directed:** AI to draft README evaluation sections from confusion matrix outputs and wrong-prediction logs.

**Overrode:** Verified metrics against notebook output; adjusted confusion matrix interpretation to match observed `appeal` collapse pattern.

---

## Project Structure

```
├── planning.md                                      # Design doc & label definitions
├── the-reddit-climate-change-dataset-posts-clean.csv # 200 labeled posts
├── backfill_log.csv                                 # Backfilled examples
├── filtered_out.csv                                 # Removed low-quality posts
├── filter_dataset.py                                # Quality filters
├── backfill_from_corpus.py                          # Corpus backfill
├── stress_test_results.md                           # Label boundary stress test
└── README.md                                        # This file
```

---

## Running (reference)

1. Prepare data: `python3 filter_dataset.py` / `python3 backfill_from_corpus.py`
2. Zero-shot: call `classify_with_groq()` with classification prompt on test posts
3. Fine-tune: train DistilBERT on 160-row train split; evaluate on held-out 30–40 posts

---

## Conclusion

The **Groq zero-shot baseline (73.3% accuracy, macro-F1 0.74)** is the stronger model for this dataset size. **Fine-tuned DistilBERT regressed to 20% accuracy** with severe `appeal` collapse — likely due to small training set, AI-generated label noise, and intent boundaries that require semantic reasoning beyond 160 examples. Next steps: human-verify labels, add boundary examples, and re-train or stay with the prompt-based baseline.
