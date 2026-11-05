# marsad-analytics 1.4

The analysis code behind the MARSAD dashboard. The Colab notebook and the MARSAD web app import the same package, so they give the same numbers.

It replaces the 171 analyses of `Unified_Social_Analytics_Dashboard_Beta_FIXED_3.ipynb` with 39 cards in 9 modules, plus a Palestine/Gaza topic pack with 18 preset cards. `docs/marsad_indicator_mapping.csv` maps every old indicator to its card. Version 1.1 added 13 cards and a robustness check. Version 1.2 added a corpus-linguistics module (8 cards, absorbing the old D1 to D3), click-through from every chart and table row to the posts, a one-sentence explanation for every output, and portal packages: 57 registry entries in all (56 cards and the export action). Version 1.4 added language routing, sentiment, emotion, toxicity and hate-speech cards, a Communalytic-style topic analyzer and network analyzer, an emoji cloud, and six cards for the MARSAD platform analyses that run on a model or API you connect: 83 registry entries (82 cards and the export action), including 17 society measures.

## Additions in 1.4

### Which cards work in which languages

Every post gets a language guess (`lang` column: script first, then common function words for Latin-script
languages; short or mixed Latin posts stay `und-latn`). Cards fall into four groups, shown as a badge on each card
and in `registry.CARD_LANG`:

| Scope | Cards | Notes |
| --- | --- | --- |
| Any language (33) | DATA-1, DATA-3, DATA-6, all TIME, all WHO (including WHO-4 networks), WORDS-9 Emoji, REACT-1, 2, 4 to 10, SPREAD-2 to 6, all PAPER | Counts, dates, accounts, engagement, links, hashtags, emoji. DATA-3 dialect labels and Arabizi markers are Arabic only. |
| Languages with spaces between words (15) | DATA-2, DATA-4, DATA-5, WORDS-1 to 8, TOPIC-1, TOPIC-2, FRAME-6, SPREAD-1 | Any language that separates words with spaces. Not Chinese, Japanese or Thai. Arabic gets extra normalization and clitic handling; stopwords exist for Arabic, English and French. TOPIC-1 with sentence-transformers covers about 50 languages by meaning. |
| Arabic and English lexicons (6) | FRAME-1 to 5, REACT-3 | The MARSAD lexicons are Arabic and English. For other languages, give your own word list (FRAME-6). |
| Model languages (12) | FRAME-7 to 14, SPREAD-7 to 9, TOPIC-3 | Posts in languages a model does not cover are skipped and counted, never forced through. |

A card warns when 20% or more of the posts are outside the lexicon languages, or 10% or more are Chinese,
Japanese or Thai for word-based cards.

### Sentiment, emotions, toxicity, hate speech

Run them from the Enrich panel (GPU recommended) or `enrich.run_classifier(session, task)`. Each task routes every
post to a model that covers its language:

| Card | Task | Default model | Languages |
| --- | --- | --- | --- |
| FRAME-7 Sentiment | sentiment | lxyuan/distilbert-base-multilingual-cased-sentiments-student (positive, neutral, negative) | ar, zh, en, fr, de, hi, id, it, ja, ms, pt, es |
| FRAME-10 Emotions | emotion | MilaNLProc/xlm-emo-t (anger, fear, joy, sadness) | 19 training languages, including Arabic and English |
| FRAME-9 Toxicity | toxicity | Detoxify multilingual (toxicity, severe toxicity, obscene, threat, insult, identity attack, sexual explicit), and textdetox/xlmr-large-toxicity-classifier for the languages Detoxify lacks (toxicity only) | Detoxify: en, fr, es, it, pt, tr, ru. TextDetox: ar, de, uk, am, hi, zh |
| FRAME-11 Hate speech | hate | Hate-speech-CNERG/dehatebert-mono-arabic and dehatebert-mono-english (hate, not hate) | ar, en |

The cards follow Communalytic's layout: a stacked distribution bar, counts over time, the mix per language, and a
coverage table ("based on N of M posts", which model scored which language). Toxicity shows the average of each
attribute over time with the share of posts that have scores, the posts at or above a threshold (0.7 by default),
and the score spread. Every bar, point and segment opens its posts; the highest-scoring posts come first. Swap a
model with `run_classifier(s, task, model_id=...)` or pass your own `predictor`.

### MARSAD platform analyses: connect your model or API

The older MARSAD platform offers propaganda detection, propaganda techniques, check-worthiness, claim extraction,
fact verification and veracity, and political bias. Each now has a card that runs on whatever model or service you
connect; nothing is hard-wired.

| Card | Task name | What the service returns per text |
| --- | --- | --- |
| FRAME-12 Propaganda | `propaganda` | `{"label": "propaganda", "score": 0.91}` |
| FRAME-13 Propaganda techniques | `propaganda_technique` | `{"labels": ["loaded language", "doubt"], "scores": {"loaded language": 0.8}}` |
| FRAME-14 Political bias | `political_bias` | `{"label": "left", "score": 0.7}` (any label set) |
| SPREAD-7 Check-worthy posts | `checkworthiness` | `{"label": "check-worthy", "score": 0.83}` |
| SPREAD-8 Claims | `claims` | `{"claims": ["claim one", "claim two"]}` |
| SPREAD-9 Fact verification | `fact` | `{"label": "refuted", "score": 0.77, "evidence": "...", "claim": "..."}` |

Three ways to connect one:

```python
from marsad_analytics import enrich
enrich.set_api("propaganda", "https://api.marsadlab.com/propaganda", headers={"Authorization": "Bearer KEY"})
# the service gets POST {"task": "propaganda", "texts": [...]} and returns {"results": [one item per text]};
# other request or response shapes: set_api(..., request=fn, parse=fn)
enrich.run_classifier(session, "checkworthiness", model_id="your-org/arabic-checkworthiness")   # a Hugging Face model
# or load a file that already has label_<task> (and score_<task>, labels_propaganda_technique, claims_list) columns
```

In the notebook, type the API URL or model id next to the task in the Enrich panel (API keys go in the API headers
box). Until one is connected, each card says how to connect it. `run_classifier(session, "propaganda", zero_shot=True)`
(and the same for check-worthiness) labels posts with the multilingual zero-shot model, for trying a card before the
API is ready; those labels are exploratory. The web dashboard cannot call outside services (the page is not allowed
to), so there these cards work only on files that already have the labels.

### Society measures (SOCIETY-1 to 7)

For social science users. SOCIETY-1 **Social cohesion** scores up to seven parts from 0 (divided) to 100 (cohesive),
each only when the file supports it: Connected (share of accounts in the largest connected part of the reply, quote or
mention network), Bridging (share of links between Louvain communities), Shared agenda (overlap of the top 30
hashtags or words of the most active accounts), Us, not them (ingroup over ingroup plus outgroup word matches),
Humanizing (humanizing over humanizing plus dehumanizing matches), Civil tone (share of posts not labelled toxic or
hate) and Audience agreement (1 minus normalized reaction entropy). The index is the mean of the parts found; set
`cards.society.COHESION_FORMULA = my_function` (parts dict to score) to use MARSAD's own formula.
SOCIETY-2 **Emotional intensity** counts exclamation marks, stretched letters, words in capitals, emoji, intensifier and
emotion words per 10 words. SOCIETY-3 to 7 are lexicon themes built on the MARSAD lists: distress and resilience,
economic concern, calls to action, blame and accountability, identity and belonging (exploratory until the lists are
validated). The dashboard also shows placeholders for trust in institutions, moral values and wellbeing.

### Help center (documentation)

`marsad_analytics/docs.py` holds the user documentation: guides, placeholders for parts not built yet (data
collection, accounts, MARSAD services), a FAQ, and one page per analysis generated from the same catalog the
dashboard shows (`plain.py`, `registry.py`, `explain.py`), so the two cannot disagree. `docs.write_site(folder)`
writes `docs.json`, `help.js`, `help.css` and `docs.html`:

* the dashboard loads `docs.json` and shows the Help center (menu: Help center; top bar: Help; each analysis:
  Full guide), even before the analysis engine has started;
* `docs.html` is the same Help center as one standalone page for the documentation section of the website
  (`standalone_html(dashboard_url=...)` sets where "Open in the dashboard" goes).

Page status: ready, server (Colab or MARSAD server), service (MARSAD service), planned, placeholder (Coming soon).
To write a placeholder page, replace its `placeholder(...)` call with `art(...)` and run `docs.write_site` again.

### Several files: combine or compare

Load any number of files at once (web dashboard: Change or add files; Python: `webapp.load_files(paths, settings,
platform, labels, mode)`). Every post keeps the name of its file (`dataset_id`), and files given the same name form
one group (for example three monthly exports all named "2025").

* **Combine** (default): one dataset. A post found in more than one file (same post id, or same text, author and time)
  is kept once, and the number removed is reported. Any analysis can still be split by file.
* **Compare**: each file keeps all its posts. The 39 analyses that can split results split by file automatically; the
  others run on one file at a time (All files, file A, file B) with a table of their key numbers for each file
  (`webapp.compare_summary`). Posts behind a chart come from the file shown. DATA-6 gives the detailed comparison.

Compare up to about six groups: beyond that, charts are hard to read, so group files by giving them the same name.
In the browser, keep the total under about 50,000 posts; larger collections go to the notebook or the MARSAD server.
When files come from different platforms, compare shares (%), not engagement counts.

### Society word lists (SOCIETY-8 to 17, seed lexicons v0.1)

Ten more Society cards run on 46 new Arabic and English word lists (about 2,200 terms) in `lexicons/core/`:
trust in institutions (trust, distrust, institutions named), moral values (virtue and vice lists for the five Moral
Foundations), wellbeing (the five PERMA parts), stress and coping, certainty and self-focus (certainty, doubt, I, we),
economic mood (worries, shortages, good news), boycotts and buy-local calls, health talk (help seeking, vaccine
mentions, pro- and anti-vaccine phrases), misinformation signals (conspiracy talk, miracle cures) and issue attention
(13 issues after the Comparative Agendas Project major topics). Arabic covers standard Arabic and common Gulf, Egyptian,
Levantine and Maghrebi forms. The lists were written for MARSAD (not translated from LIWC or the Moral Foundations
Dictionary). They avoid words that are common names (سعيد, وفاء, نزيه) or have a second common meaning (القضاء, الاعلام,
واجب, الرياضة), and were checked against the test files and real MCL posts for false hits. They are **not validated**:
run `validation.py` (precision on a sample of matched posts) before using them in a paper.

Two matching rules are new and optional per list (`negatable`, `yields_to` in the JSON): a match right after a
negation word is not counted ("not happy", "مش مبسوط", "لا نثق"), and a match inside a phrase of the opposing list
counts only for that list ("فقدنا الثقة" is distrust, not trust). Paired lists give a balance: the share of posts on
the first side among posts with either side (trust share, care share, coping share, certainty share, good news share,
pro-vaccine share). `docs/lexicons_society_v0.1.csv` holds every term; edit it and load it back as a custom lexicon
file (term, category, lang): edited lists keep their matching rules.

### Topic analyzer (TOPIC-1)

As in Communalytic: sentence embeddings (multilingual sentence-transformers when installed, LSA offline), UMAP,
then HDBSCAN with `min_cluster_size` (auto: 0.5% of posts, at least 10), `min_samples` (10) and
`epsilon` (0.1). Each run reports the silhouette score (above 0.5 good, 0.25 to 0.5 fair, below weak) and the number
of outliers, and is added to a history table; `use_run=n` restores run n. Clusters are numbered by size and named by
their most distinctive words (class-based TF-IDF), or by your own `label_fn(texts, keywords)` (for example an LLM).
Views: the 10 largest clusters, sentiment within each cluster, clusters over time, and a 3D similarity map where
each dot is a post. Every bar and dot opens its posts. `method="nmf"` or `"bertopic"` gives the old topic models.
Up to 50,000 posts are clustered (random sample above that).

### Network analyzer (WHO-4)

Network types: `reply`, `quote` (needs a quoted-post id column), `mention`, `link` (author to web domain) and
`hashtag` (co-occurrence); the card lists which ones the data supports. Louvain communities, weighted in- and
out-degree, PageRank, betweenness, density and modularity; ForceAtlas2 layout. Filters: `search` (3+ characters,
shows the match and its neighbours), `min_degree`, `max_degree`, `hide_pendants`, `communities`, edge
`date_from` and `date_to`, and `toxic_only` with `toxicity_threshold` (after FRAME-9). Clicking a node opens the
posts it sent and received. Isolated nodes never appear. The figure draws the 300 largest nodes; the tables keep
the whole network.

Downloads: `cards.network.save_graphml(session, "net.graphml")` for Gephi, and
`cards.network.explorer_html(session, "net.html")`, a standalone page (works offline) with search, size by
in-degree, out-degree or PageRank, degree range, pendant toggle, community checkboxes, edge date range, toxicity
filter and a panel with the posts each node sent and received. Both are buttons on the card in the notebook.

### Emoji cloud (WORDS-9)

Emoji sized by use, as in Communalytic, with flags, skin tones and joined sequences kept whole; the bar chart is
the second view. Click an emoji for its posts.

## Card IDs (1.3)

Each card id is a plain word for the question it answers, plus a number: `TIME-2`, `WORDS-4`. The word is also the chip
users see in the portal, so the id and the chip match. Within a group, 1 is the card to look at first; general cards
come before specialised ones, and cards that need one platform's fields or a GPU come last. The letters used up to
1.2 (A1, B2, ..., L8, and D1 to D3) still work: `session.run("A1")` runs DATA-1, and `docs/marsad_indicator_mapping.csv`
gives old and new ids side by side.

| Group | Chip | Question | Cards |
| --- | --- | --- | --- |
| DATA | Data | What is in my data? | DATA-1 Dataset overview, DATA-2 Text statistics, DATA-3 Languages and dialects, DATA-4 Duplicates, DATA-5 Off-topic check, DATA-6 Compare files |
| TIME | Time | When did it happen? | TIME-1 Posts over time, TIME-2 Posting hours and days, TIME-3 Spikes, TIME-4 Before and after an event |
| WHO | Who | Who is posting? | WHO-1 Top accounts, WHO-2 Concentration, WHO-3 Posting regularity, WHO-4 Network analyzer, WHO-5 Unusual accounts, WHO-6 Countries, WHO-7 Page categories, WHO-8 Page age |
| WORDS | Words | Which words, in which contexts? | WORDS-1 Word list, WORDS-2 Word cloud, WORDS-3 Keywords, WORDS-4 Concordance (KWIC), WORDS-5 Collocates, WORDS-6 Phrases around a word, WORDS-7 Term over time, WORDS-8 Vocabulary variety, WORDS-9 Emoji |
| TOPIC | Topics | What is it about? | TOPIC-1 Topics, TOPIC-2 Word similarity map, TOPIC-3 Posts close to a concept |
| FRAME | Framing | How is it said? | FRAME-1 Lexicon use over time, FRAME-2 Two lexicons compared, FRAME-3 Lexicons in the same post, FRAME-4 Pronouns and certainty, FRAME-5 Language profile by group, FRAME-6 Your own word list, FRAME-7 Sentiment, FRAME-8 Stance toward a target, FRAME-9 Toxicity, FRAME-10 Emotions, FRAME-11 Hate speech, FRAME-12 Propaganda, FRAME-13 Propaganda techniques, FRAME-14 Political bias |
| REACT | Reactions | How did people react? | REACT-1 Engagement overview, REACT-2 What gets engagement, REACT-3 Lexicon and engagement, REACT-4 Engagement mix, REACT-5 Reaction types, REACT-6 Reaction sentiment, REACT-7 Engagement rate, REACT-8 Views, REACT-9 Overperforming posts, REACT-10 Video performance |
| SPREAD | Spread | How did it spread, and was it coordinated? | SPREAD-1 Repeated claims, SPREAD-2 Linked websites, SPREAD-3 Coordinated posting, SPREAD-4 Reply threads, SPREAD-5 Crosspost reach, SPREAD-6 Meltwater reach and sources, SPREAD-7 Check-worthy posts, SPREAD-8 Claims, SPREAD-9 Fact verification |
| PAPER | Paper | How do I use it in a paper? | PAPER-1 Report export, PAPER-2 Annotation sample, PAPER-3 Datasheet |

## Downloads (1.3)

Every card can be downloaded on its own: `res.to_excel("x.xlsx")` (one sheet per table, plus an About sheet with the
settings, method and notes, and an Explanations sheet with the hover text), `res.to_csv("x.zip")` or
`res.to_csv("x.csv", table="keywords")` (UTF-8 with BOM, so Excel shows Arabic correctly), and
`res.save_figure("x.png")` (also `.svg`, `.pdf`, or `.html` for an interactive chart). The Colab dashboard has a
download bar under each card; the interactive HTML report has Excel, CSV and PNG/SVG buttons. For the portal, the same
functions return bytes when no path is given (`GET /runs/{id}/download?format=xlsx|csv|png|svg|html`).

## Size limits and speed (1.3)

Measured on a 200,000-post CrowdTangle-format file (83 MB) on a 2-core cloud machine, no GPU:

| Step | Time |
| --- | --- |
| Load and clean | 9 s |
| Session (tokenize, time features) | 15 s |
| Most cards | under 1 s |
| Text cards (word list, keywords, collocates, lexicons, duplicates) | 5 to 20 s |
| Interaction network (WHO-4), repeated claims (SPREAD-1) | 20 to 32 s |
| Word similarity map (TOPIC-2, trained on a 50,000-post sample) | 40 s |
| Basic and Narrative packages together (20 cards) | 107 s |
| Opening the posts behind a click | 0.01 to 2 s |
| Interactive HTML report of those 20 cards | 107 s, 9.5 MB |
| Peak memory | about 2.3 GB |

Uploads have no row limit in the code; memory grows roughly with the number of posts, so a free Colab runtime (12 GB)
is comfortable up to about 500,000 posts. The stored corpus path runs cards on a random sample of at most 500,000
posts (exact daily counts on the full match set).

What is drawn, shown and stored:

| Output | Limit |
| --- | --- |
| Bar charts of words, accounts, keywords, collocates, clusters | top 25 to 30 |
| Word cloud | 80 words |
| Scatter charts of accounts (WHO-3, WHO-8) | the 1,000 largest accounts; the table has all |
| Dispersion plot (WORDS-7) | 2,000 marks per term, spread evenly in time; counts use every post |
| Concentration curve (WHO-2) | 500 points |
| Network (WHO-4) | 150 most central nodes |
| Concordance (WORDS-4) | 300 lines shown, every hit counted (`max_lines`) |
| Tables on screen | 25 rows in Colab, 40 in the HTML report, 500 in the portal JSON |
| Downloads (CSV, Excel) | every row (Excel's own limit is 1,048,576 rows per sheet; 20,000 in the HTML report's built-in buttons) |
| Clicks in Colab and the portal | every point and row, computed on demand: the 10 (Colab) or 20 (API) posts with most interactions, each repeated text once, and the total count |
| Clicks in the HTML report | up to 200 points per chart and the first 100 rows per table, 6 posts each, stored when the report is written |

## Comparing two or more files

Upload several files at once (the Colab upload accepts several; in code, `combine([load(a), load(b)])`). Each file
becomes a dataset named after the file, and every card can split by it:

- DATA-6 Compare files: posts, accounts, length, engagement, lexicon use per file, and shared accounts and hashtags.
- WORDS-3 Keywords: `target="dataset:<file>", reference="rest"` for one file against the other, or
  `target="each_group", group="dataset"` for every file against the rest.
- Any card with a split or group setting: `split="dataset"` (TIME-1), `feature="dataset"` (REACT-2),
  `group="dataset"` (FRAME-5, WORDS-8, ...).

Files may mix time zones: timestamps with a zone are converted, those without are read in the source time zone
setting. Engagement numbers from different platforms are not on the same scale; compare them within a file.

## Additions in 1.2

**Corpus and lexical tools (AntConc-style), now the WORDS group.** The v1.1 cards D1, D2 and D3 open WORDS-1, WORDS-3 and WORDS-7.

| Card | What it does |
| --- | --- |
| WORDS-1 Word list | frequency, per 10,000 words, range (posts, accounts), Gries' DP across accounts; words, light stems, bigrams, trigrams, hashtags or mentions |
| WORDS-3 Keywords | target vs reference: general language (wordfreq, simple maths), the rest of the data, a group, a period, posts using a lexicon, the top 10% by engagement, or another dataset (log-likelihood, Log Ratio, %DIFF, Bonferroni); positive and negative keywords |
| WORDS-4 Concordance (KWIC) | key word in context for a word, phrase, wildcard or lexicon, sorted by the word after or before, date, engagement or account; RTL-aware layout |
| WORDS-5 Collocates | window collocates with MI, t-score, logDice and log-likelihood, before/after position |
| WORDS-6 Phrases around a word | n-grams that start or end with a word |
| WORDS-7 Term over time | rate per period, a dispersion plot with one mark per post, DP across periods and accounts |
| WORDS-8 Vocabulary variety | MATTR with bootstrap intervals, TTR, hapax share, word and post length, content-word share, by group |
| WORDS-2 Word cloud | clickable word cloud by frequency or keyness; its table feeds the portal's Word Cloud tab |

Repeated posts are counted once on WORDS-1, WORDS-3, WORDS-5, WORDS-6 and WORDS-2 when they make up 5% or more of the data (`dedup="auto"`), so one copied post cannot fill a word list. WORDS-4 and WORDS-7 keep every post.

**Click-through.** Every chart point carries a filter in its plotly `customdata` (and every table row one in `result.table_drill`). `session.examples(filter)` returns the posts behind it with matched words highlighted. Filter keys are documented in `drill.py`. The portal endpoint is `POST /datasets/{id}/examples` with the filter as body. `html_report.export_html(basket, session, path)` writes a self-contained interactive report that does this offline.

**Explanations.** `result.explain` holds one sentence for the chart, each table, each column and each headline number (hover text). `docs/explanations.csv` lists all of them for the web developer. A test fails if any output lacks one.

**Packages for the portal.** `registry.PACKAGES` (Basic, Narrative, Audience, Advanced), `registry.CATEGORIES` (the chip names; rename the labels to match the portal), `registry.PLATFORM_BADGES` ("CrowdTangle only" and similar), `registry.package_status(caps, history)` (what will run, what is skipped and why, whether to dim), `registry.suggest(caps)` (a suggested starting point from the detected columns) and `session.history` (which cards have been run). `registry.to_json(caps, history)` returns all of it.

## Additions in 1.1

| Card | What it does | Needs |
| --- | --- | --- |
| DATA-5 Off-topic check | share of posts with a visible collection keyword; on-topic share from an annotated sample (Wilson CI); optional zero-shot estimate | text |
| DATA-3 Languages and dialects | script mix, Arabizi, code-switching; dialect regions after enrichment | text (+ dialect model) |
| WHO-4 Network analyzer | reply, mention or hashtag graph; communities, PageRank, bridges | author, or hashtags only |
| WHO-5 Unusual accounts | volume, regularity, repeated text per account (context, not bot detection) | author |
| TOPIC-1 Topics | BERTopic, or NMF offline; topics become a split on every card | text |
| WORDS-9 Emoji | emoji use overall and by group | emoji in text |
| FRAME-7 Sentiment, hate and other classifiers | sentiment, hate or any Hugging Face classifier; examples per label | text + model |
| FRAME-8 Stance toward a target | zero-shot NLI stance toward a typed target; macro-F1 against annotations | text + model |
| SPREAD-2 Linked websites | linked domains, shorteners, optional credibility list | links |
| SPREAD-1 Repeated claims | near-duplicate (and optional paraphrase) clusters with first seen, spread in 24 h, accounts | text |
| SPREAD-4 Reply threads | reply trees: size, depth, labels by depth | parent or thread id |
| PAPER-2 Annotation sample | stratified sample, one sheet per annotator; `validation.agreement()` for kappa and alpha | text |
| PAPER-3 Datasheet | draft datasheet (Gebru et al. 2021) from the data plus author fields | text |
| Robustness | `session.robustness(card_id, ...)`: dedup, no top 1% authors, random halves, other settings | any card |

Enrichment (`enrich.py`) runs once per dataset and stores columns (`dialect_region`, `label_<task>`, `topic_label`) that every card can split by. Defaults, checked on Hugging Face on 2026-11-04: dialect `CAMeL-Lab/bert-base-arabic-camelbert-mix-did-madar-corpus26` (mapped to MSA, Gulf, Yemen, Iraq, Levant, Egypt-Sudan, Maghreb), sentiment `CAMeL-Lab/bert-base-arabic-camelbert-mix-sentiment`, hate `wetey/MARBERT-LHSAB` (label order undocumented; name the labels from the FRAME-7 examples), zero-shot `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`. Emotion, sarcasm and hope have no verified default; set a model id. For the stored corpus, run `enrich.enrich_dataframe()` in the ETL before `write_corpus_parquet()`.

The model calls were tested with stand-in predictors only (`tests/fakes.py`); the real models have not been run in this build.

## Use

```python
from marsad_analytics import load, Session, Settings

s = Session(load("export.csv"), Settings(analysis_tz="Asia/Qatar"))
s.caps.summary()                       # what the file supports
r = s.run("FRAME-2", lex_a="hope", lex_b="despair")
r.tables, r.figure, r.caveats          # or r.to_json() for the web app
s.basket.append(r)

from marsad_analytics import report
report.export_pdf(s.basket, "report.pdf")
report.export_latex(s.basket, "report.tex")   # compiles with XeLaTeX when installed
```

Colab: `from marsad_analytics.ui import Dashboard; Dashboard().show()`.

## Stored corpus

```python
from marsad_analytics.sources import CorpusSource, write_corpus_parquet

write_corpus_parquet(adapted_df, "s3://bucket/posts")          # ETL: canonical schema + text_norm, by year/month
src = CorpusSource("s3://bucket/posts/**/*.parquet")
q = src.query(date_from="2024-01-01", date_to="2024-06-30", keywords=["غزة", "gaza"], platforms=["x"])
s = q.session(Settings(analysis_tz="Asia/Qatar"))              # cards run on a sample above corpus_sample_cap
q.daily_counts                                                 # exact counts on the full match set
```

Keyword filtering is a substring prefilter in DuckDB, then the same whole-word check the cards use.

## Web app integration

| Endpoint (suggested) | Call |
| --- | --- |
| card list for a dataset | `registry.to_json(session.caps)` (names, questions, params, choices, availability and the missing field) |
| run a card | `session.run(card_id, **params).to_json()` (tables, Plotly figure JSON, caveats, methods) |
| presets | `registry.PRESETS`, `registry.pack_presets("palestine_gaza")` |
| export | `report.export_pdf / export_latex / export_csv_zip / export_json` on a list of results |

Keep one `Session` per dataset in memory or cache `session.df` and `session.hits` (Parquet); the lexicon scan is the slow step (about 10 s per 100,000 posts).

## Lexicons

`marsad_analytics/lexicons/core/*.json` (63 generic lexicons) and `lexicons/packs/palestine_gaza/` (12 lexicons, extensions to 10 core lexicons, events, presets). `docs/lexicon_changes.csv` lists every term moved out of the core. Custom lexicons: JSON in the same format, or CSV `term,category`.

Validation: `validation.sample_matches(session, "hope", n=200, path="hope.xlsx")`, annotate the `correct` column, then `validation.score(["hope_A.xlsx", "hope_B.xlsx"])`. The result goes into `lexicons/validation.json` (or `$MARSAD_VALIDATION_FILE`) and every card using that lexicon shows precision, interval and kappa. Until then the card says the lexicon is exploratory.

## Tests

`pytest -q tests/` (41 tests) runs one test per fix from the audit, tests each addition, and runs every card on five synthetic exports (CrowdTangle, Meltwater with empty engagement, Meta Content Library, text-only, Reddit JSONL).

## What changed from the notebook

1. Lexicon matching is whole-word with Arabic clitic rules (was substring: الم matched inside المدرسة).
2. Rates are per 1,000 tokens as a ratio of totals (were per character, averaged per post).
3. `reactions_total` is always the raw sum of the six reactions.
4. One reaction sentiment formula for CrowdTangle and Meta; the sensitivity table perturbs that formula.
5. Timestamps are converted to an analysis time zone; weekend is Friday-Saturday or Saturday-Sunday from the posts' countries.
6. Meltwater reach used as engagement is flagged per row, captioned on every card, and never averaged with real interactions.
7. Facebook page category, Meltwater source and Meta owner type are separate columns.
8. Group comparisons report median, log mean and within-author z-score with a rank test, not raw means.
9. Each indicator has one implementation; the structural copies are gone.

Also: missing metrics are left empty instead of zero; Meta interactions = reactions + comments + shares, as in CrowdTangle.
