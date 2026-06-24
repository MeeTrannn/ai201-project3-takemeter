# Climate Discourse Classifier — Project Plan

## Community

**Community:** Reddit climate-change discourse, drawn from *The Reddit Climate Change Dataset* (posts across many subreddits where climate is discussed — e.g. r/climatechange, r/environment, r/worldnews, r/NoStupidQuestions, r/DemocraticSocialism, and others).

**Why this community:** Reddit is one of the largest open forums for climate conversation outside of news comment sections. Posts range from lay questions and personal anxiety to policy debate, disaster news, skepticism, and adaptation advice — all in informal, varied language (short posts, link shares, long rants, bot summaries).

**Why it is a good fit for classification:** The discourse is **speech-act diverse** even when the topic is the same. Two posts can both mention droughts but one *reports* what is happening (`report`), one *asks what to plant* (`inquiry`), and one *urges rooftop paint adoption* (`appeal`). That variation makes single-label intent classification non-trivial and interesting. The community also produces **commentary** (skepticism, conspiracy narratives) and **appeal** posts (surveys, persuasive articles, advocacy) that stress-test the taxonomy. After filtering low-quality rows, the corpus supports a balanced 200-example annotation set in one topical domain.

---

## Labels

> **Taxonomy (v2):** The original labels (`problem`, `solution`, `question`, `other`) mixed *topic* with *intent*. A post can be "descriptive" but mean very different things — reporting Pakistan floods vs. asserting a sun-orbit conspiracy. The revised scheme asks one question: **What is the author mainly trying to get the reader to do?**

We use **four mutually exclusive labels** assigned by **primary reader-facing intent**.

| Label | Definition |
|---|---|
| **report** | The author mainly wants the reader to **know or understand** something about climate — events, impacts, data, research, or mechanisms — without asking them to act or answer. |
| **appeal** | The author mainly wants the reader to **do something** — participate in a study, adopt a behavior, support a policy/technology, take responsibility, or engage with content meant to motivate action. |
| **inquiry** | The author mainly wants the reader to **provide** information, evidence, advice, or opinions. |
| **commentary** | The author mainly **expresses a viewpoint, argument, or narrative** without a concrete ask — includes skepticism, denial, satire, and conspiracy explanations. *(Link-only, poll, and off-topic posts are removed from the dataset — see Data Collection — rather than labeled `commentary`.)* |

**What changed from v1:**

| Old label | Problem | New home |
|---|---|---|
| `problem` | Collapsed "describes harm" with "describes any narrative" | Factual harm/event description → **`report`**; contrarian narrative → **`commentary`** |
| `solution` | Overlapped with "please do this" posts | Policy/tech/behavior advocacy → **`appeal`** |
| `question` | Clear | Renamed to **`inquiry`** |
| `other` | Dumping ground | Surveys/participation → **`appeal`**; on-topic opinion → **`commentary`**; link-only/poll/spam → **filtered out** |

**Tie-break rule (when two labels seem plausible):** `inquiry` → `appeal` → `report` → `commentary`.

### Examples

#### `report`

1. *"Rivers completely dried up in France, ancient statues were found in the bottom of rivers and lakes in China. Extreme rain and floods in Vegas. These ARE the extreme weather events we were warned about and ignore."*

2. *"Pakistan is witnessing terrible flooding that is affecting some 33 million people, while on the other end China's droughts are breaking records."*

#### `appeal`

1. *"Hello, I am conducting a survey… If you could fill in this form which is only 4 questions it would be much appreciated, thanks!"*

2. *"I've translated this article about psychological mechanisms that make people indifferent to the ecological crisis… we are all responsible because we are all involved — all eight billion of us."* (shared content structured to motivate responsibility — not neutral reporting)

3. *"When are we going to start covering all our rooftops and dark infrastructure surfaces with this [white paint]?"*

#### `inquiry`

1. *"Can Someone please give me some actual evidence of this being truth and not just political BS?"*

2. *"Any recommendations for trees to plant that will thrive in the next 100 years? How should tree planters plan for climate change??"*

#### `commentary`

1. *"It's actually the planet moving closer and closer to the sun that's why it's getting hotter… Then eventually the sun just absorbs all the planets."* (contrarian narrative — descriptive in form but not good-faith reporting)

2. *"Duh. Yes, temperatures go up and down. … Do the climate change fanatics want the temperature to stop changing? Probably, because they are that stupid."* (skeptical rant — rhetorical, no genuine ask)

### Key relabeling examples (v1 → v2)

| Row | Text (summary) | v1 label | v2 label | Why |
|---|---|---|---|---|
| 1 | Sun moving closer, planets absorbed | `other` | **`commentary`** | Contrarian narrative, not reporting |
| 8 | Translated psychology article + collective responsibility | `problem` | **`appeal`** | Purpose is to motivate responsibility and discussion |
| 13 | Survey recruitment | `other` | **`appeal`** | Explicit participation request |

---

## Hard Edge Cases

| Ambiguous between | Example type | How we handle it |
|---|---|---|
| **report ↔ appeal** | News article shared with "we must act" framing vs. neutral bot summary of flood damage | Author's **purpose is to motivate action/responsibility** → `appeal`. Purpose is to **convey what happened** → `report`. |
| **report ↔ commentary** | Sun-orbit pseudo-explanation vs. extreme-weather observation | Good-faith climate information → `report`. Viewpoint/conspiracy/skeptic narrative → `commentary`. |
| **inquiry ↔ appeal** | *"How should we think about eating and changing our lifestyle?"* vs. *"Fill out my survey on EV policy"* | Seeking community knowledge → `inquiry`. Requesting study participation → `appeal`. |
| **inquiry ↔ commentary** | Geoengineering sketch + *"is this a bad idea?"* vs. rhetorical *"why does anyone think this is a problem?"* | Genuine advice request → `inquiry`. Rhetorical rant → `commentary`. |
| **appeal ↔ commentary** | Sarcastic *"we must eat bugs"* vs. disaster preparedness guide | Sarcasm/mockery → `commentary`. Concrete behavioral recommendation → `appeal`. |
| **appeal ↔ inquiry** | *"What can we do to make government help?"* | Seeking ideas → `inquiry` (author not asking reader to do a specific thing). |

**During annotation:** Apply the decision tree below. If still ambiguous, set `review_flag` — **do not leave `label` blank**. Target ≤10% flagged on first pass.

**Decision tree:**
```
1. Link-only / poll / off-topic / no climate substance?  → exclude (do not label)
2. Primary purpose = reader provides info/advice/opinion? → inquiry
3. Primary purpose = reader acts/participates/adopts idea? → appeal
4. Primary purpose = reader understands events/science/harms? → report
5. Else (opinion, denial, satire, rhetorical narrative)   → commentary
```

---

## Data Collection Plan

### Source

| File | Description |
|---|---|
| `the-reddit-climate-change-dataset-posts.csv` | Full Reddit climate posts corpus (~979k rows), 2022 — located in Downloads |
| `the-reddit-climate-change-dataset-posts-clean.csv` | **Working labeled set — 200 rows, 50 per label** |
| `backfill_log.csv` | 62 posts added from full corpus to rebalance labels |
| `filtered_out.csv` | 62 posts removed (link-only, duplicate, poll, off-topic) |
| `the-reddit-climate-change-dataset-posts-clean-v200.csv` | Archive of labeled set before quality filtering |

### Pipeline (completed)

```
Full corpus (Downloads)
    ↓ sample 200 non-empty selftext posts
Initial labeled set (v2 labels)
    ↓ filter_dataset.py — remove link-only, duplicates, polls, off-topic
138 substantive posts (43 inquiry, 43 commentary, 31 report, 21 appeal)
    ↓ backfill_from_corpus.py — add candidates per underrepresented label
Final set: 200 posts (50 / 50 / 50 / 50)
```

### Quality filters (applied before labeling and backfill)

| Filter | Rule | Removed |
|---|---|---|
| **link_only** | Body is mostly a URL with &lt;25 chars of other text | 34 |
| **poll** | Contains `[View Poll]` or `reddit.com/poll/` | 8 |
| **duplicate** | Exact normalized text already in set | 8 |
| **off_topic** | Spam, skincare, crypto, sex posts, etc. (pattern list in `filter_dataset.py`) | 20 |

**Kept:** on-topic posts with substantive body text, including skeptic rants and debate.

### Target counts (200 total) — achieved

| Label | Target | Final |
|---|---|---|
| report | 50 | **50** |
| appeal | 50 | **50** |
| inquiry | 50 | **50** |
| commentary | 50 | **50** |

### If a label becomes underrepresented after edits

1. Re-scan full corpus with `backfill_from_corpus.py` (keyword heuristics per label).
2. Replace lowest-confidence or borderline examples of overrepresented labels (log in `annotation_log`).
3. Never include exact duplicate `text` rows.

**Minimum per label:** ≥35 examples; current set meets 50/50/50/50.

### CSV columns

| Column | Description |
|---|---|
| `text` | Post body (`selftext`) |
| `prelabel` | AI-assigned label (preserved for audit) |
| `label` | Final label (human-verified when reviewed) |
| `prelabeled_by_ai` | `true` for all rows |
| `review_flag` | Non-empty for borderline cases needing human check |
| `label_version` | `v2` |
| `original_row_id` | Source row index, or `corpus_backfill` for backfilled posts |

---

## Evaluation Metrics

Accuracy alone is misleading because some errors are costlier than others (e.g. misrouting a genuine `inquiry` to `commentary` hides community needs).

| Metric | Why it fits this task |
|---|---|
| **Macro-F1** | Averages F1 across all four labels equally. **Primary headline metric.** |
| **Per-class precision & recall** | Surfaces which speech acts we miss (e.g. low `appeal` recall = under-detect actionable posts). |
| **Confusion matrix** | Shows systematic confusions (e.g. `inquiry` ↔ `appeal`) to drive definition fixes. |
| **Cohen's κ** | Agreement beyond chance on categorical labels. Target κ ≥ 0.70 on a 30-post audit subset. |
| **Accuracy** | Reported for completeness, not used as sole success criterion. |

### Train/test protocol

- **Split:** 80/20 stratified (160 train / 40 test) — 10 examples per label in test.
- **Optional:** 5-fold CV on 160 training rows; hold out same 40-test set for final numbers.

---

## Definition of Success

### Genuinely useful (deployment in a community tool)

| Criterion | Threshold | Measurable? |
|---|---|---|
| Macro-F1 on held-out test set | **≥ 0.72** | Yes |
| Per-class F1 | **≥ 0.65 for each label** | Yes |
| `inquiry` recall | **≥ 0.75** | Yes — missing inquiries is highest product cost |
| Human audit agreement | Cohen's κ **≥ 0.70** on 30 test predictions | Yes |
| Confusion severity | **`inquiry` → `commentary` errors ≤ 3** on test set | Yes |

### "Good enough" for course / prototype

| Criterion | Threshold |
|---|---|
| Macro-F1 | **≥ 0.65** |
| Per-class F1 | **≥ 0.55 for each label** |
| Worst-class recall | **≥ 0.50** |
| Annotation set | **200 labeled posts**, ≥35 per label |

### Self-check

**Yes.** Every criterion maps to numbers from the confusion matrix, `classification_report`, and a fixed 30-post audit sheet.

---

## AI Tool Plan

### 1. Label stress-testing — **done**

Stress test passed before annotation. See [`stress_test_results.md`](stress_test_results.md).

- 32 boundary posts tested (8 per v1 label pair; definitions updated to v2 afterward).
- All resolvable with decision tree — no definition changes required at v2 cutover.

**v2 pairs to re-stress if definitions change:** report/appeal, report/commentary, inquiry/appeal, inquiry/commentary.

### 2. Annotation assistance — **done (pending human review)**

| Item | Status |
|---|---|
| Tool | Cursor AI (Claude) |
| Pre-labeling | All 200 rows labeled with v2 heuristics |
| Filtering | 62 low-quality rows removed via `filter_dataset.py` |
| Backfill | 62 rows added via `backfill_from_corpus.py` — see `backfill_log.csv` |
| Human review | **Pending** — especially backfilled rows and `review_flag` cases |
| Tracking | `prelabel` = `label` for now; diverge on human correction |
| Disclosure | Note: "200 posts AI-labeled; X% human-corrected" in evaluation write-up |

### 3. Failure analysis (after model evaluation) — **planned**

1. Export test-set errors: `{post_id, text, true_label, predicted_label}`.
2. Prompt AI to group misclassifications into error patterns.
3. Manually verify ≥2 examples per pattern.
4. Act on definition gaps or training data issues.

**Watch for:**
- `inquiry` ↔ `appeal` (advice-seeking vs. participation request)
- `report` ↔ `commentary` (factual harm vs. skeptic tone)
- `report` ↔ `appeal` (neutral news share vs. persuasive framing)
- Backfilled posts mislabeled by heuristics

---

## Project Files

| Script | Purpose |
|---|---|
| `filter_dataset.py` | Remove link-only, duplicate, poll, off-topic posts |
| `backfill_from_corpus.py` | Rebalance labels from full corpus |
| `apply_labels_v2.py` | Original 200-post v2 label map |
| `planning.md` | This document |
| `stress_test_results.md` | Label boundary stress test |
| `annotation_batch1_review.csv` | First 50 rows for spot-check review |

---

## Annotation Checklist

- [x] Run label stress-test; update definitions (v1 → v2)
- [x] Pre-label 200 posts; add `prelabel`, `prelabeled_by_ai`, `label_version`
- [x] Filter low-quality posts (link-only, duplicates, polls, off-topic)
- [x] Backfill from full corpus to 50/label balance
- [x] Dedupe exact duplicate `text` rows
- [ ] Human-review all 200 (priority: `backfill_log.csv` + `review_flag` rows)
- [ ] 80/20 stratified split; record test set IDs
- [ ] Train classifier; compute macro-F1, per-class metrics, confusion matrix
- [ ] 30-post human audit for Cohen's κ
- [ ] AI failure analysis + human verification
- [ ] Compare results to success thresholds
