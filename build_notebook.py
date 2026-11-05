"""Build the single-file Colab notebook. The package is embedded as a zip so the notebook needs no other file."""
import base64, io, os, sys, zipfile
import nbformat as nbf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marsad_analytics.registry import CARDS, MODULES, PRESETS

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk("marsad_analytics"):
        for f in files:
            if "__pycache__" in root or f.endswith(".pyc"):
                continue
            z.write(os.path.join(root, f))
b64 = base64.b64encode(buf.getvalue()).decode()

rows = "\n".join(f"| {cid} | {c['name']} | {c['question']} | {', '.join(c['legacy_ids'][:8])}{' ...' if len(c['legacy_ids']) > 8 else ''} |"
                 for cid, c in CARDS.items())
presets = "\n".join(f"| {v['name']} | {', '.join(v['cards'])} | {v['for_']} |" for v in PRESETS.values())

intro = f"""# MARSAD Analytics (v1.4)

Analyses for social media datasets: CrowdTangle, Meltwater, Meta Content Library, X, Reddit (Communalytic), or any CSV, Excel, JSON or Parquet file with a text column. Built for Arabic and English; each card shows a language badge saying whether it works for any language, languages with spaces between words, the Arabic and English lexicons, or a model's languages.

This notebook runs the same code as the MARSAD dashboard (package `marsad_analytics`, embedded below), so results match between the two.

**How to use**
1. Run cell 1 once.
2. Run cell 2 and pick your file(s) with *Choose Files* (several files can be compared). For big files, tick *MOUNT_DRIVE* instead and type the Drive path in the dashboard.
3. Run cell 3. Your files are listed and selected; check the time zone and weekend settings and press *Load and scan*. The scan shows which cards your file supports and names the missing field for the others.
4. Optional: tick INSTALL_MODEL_LIBS in cell 1, switch to a GPU runtime (Runtime > Change runtime type), then open *Enrich* to add sentiment (DistilBERT multilingual), emotions (XLM-EMO), toxicity (Detoxify and TextDetox), hate speech (DE-LIMIT, Arabic and English) and dialect labels. Each post goes to a model that covers its language; other posts are skipped and counted. The *Sentiment, emotion and toxicity* package then shows the results. The MARSAD platform analyses (propaganda, propaganda techniques, political bias, check-worthiness, claims, fact verification) run once you type your API URL or model id next to them in *Enrich*; the *MARSAD platform analyses* package groups them.
5. Start from *Packages* (Basic, Narrative, Audience, Advanced): each says how many of its analyses will run on your file and which are skipped and why, and a suggested starting point is shown. Or use *Research presets*, *Choose your own insights* (by category), *Concordance (KWIC)* or *Search*. *Run and pin* adds a card to the report; *Check robustness* re-runs it without duplicates, without the most active accounts and on random halves.
6. Click any bar, point, heatmap cell or word in a chart to see the posts behind it (matched words highlighted); *Posts for* does the same for table rows. Hover a column header or a headline number to see how it is calculated.
7. Each card has a download bar: Excel (all tables, with an About and an Explanations sheet), CSV per table, and the chart as PNG, SVG or interactive HTML.
8. TOPIC-1 is a topic analyzer (clusters, silhouette score, run history, 3D map) and WHO-4 a network analyzer (reply, quote, mention, link and hashtag networks, with a GraphML download and a standalone network explorer).
9. To compare files, upload them together in cell 2 (or select several in the Files list): each file becomes a dataset, DATA-6 compares them, and most cards can split by dataset.
10. Export the report as an interactive HTML file (clickable charts and tables, works offline), PDF, LaTeX, CSV or JSON.

Cards are named by the question they answer: DATA, TIME, WHO, WORDS, TOPIC, FRAME, REACT, SPREAD, PAPER, plus a number in reading order (1 = look at this first). Old ids such as A1 or C1 still work.

Only a text column is required. Cards that need a missing field stay greyed out and name the field.

Lexicon-based cards are marked exploratory until the lexicon has been validated (cell 5).
"""
setup = f'''#@title 1. Install (run once) {{ display-mode: "form" }}
HIGH_QUALITY_PDF_CHARTS = False #@param {{type:"boolean"}}
import sys, subprocess, base64, io, zipfile, os
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "plotly>=5", "duckdb", "pyarrow", "arabic-reshaper",
                "python-bidi", "openpyxl", "reportlab", "networkx", "kaleido", "matplotlib", "wordfreq", "anywidget", "regex"], check=False)
INSTALL_MODEL_LIBS = False #@param {{type:"boolean"}}
if INSTALL_MODEL_LIBS:   # transformers and torch are already in Colab; these add toxicity, topics, FastText and sentence embeddings
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "detoxify", "sentence-transformers", "umap-learn",
                    "bertopic", "gensim", "sentencepiece"], check=False)
PKG_DIR = os.path.abspath("marsad_pkg")
PKG_B64 = "{b64}"
zipfile.ZipFile(io.BytesIO(base64.b64decode(PKG_B64))).extractall(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.insert(0, PKG_DIR)
try:
    from google.colab import output
    output.enable_custom_widget_manager()
except Exception:
    pass
if HIGH_QUALITY_PDF_CHARTS:
    try:
        import kaleido; kaleido.get_chrome_sync()
    except Exception as e:
        print("Chrome for chart export not installed; PDF charts will use matplotlib.", e)
import marsad_analytics
print("marsad_analytics", marsad_analytics.__version__, "ready")
'''
upload = '''#@title 2. Upload files {{ display-mode: "form" }}
MOUNT_DRIVE = False #@param {{type:"boolean"}}
import os
UPLOAD_DIR = "/content/marsad_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
try:
    from google.colab import files, drive
    if MOUNT_DRIVE:
        drive.mount("/content/drive")   # then type e.g. /content/drive/MyDrive/data/export.csv in the dashboard
        print("Drive mounted at /content/drive")
    else:
        up = files.upload()             # Colab's own file picker: click "Choose Files"
        for name, data in up.items():
            with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
                f.write(data)
        print("Saved", len(up), "file(s) to", UPLOAD_DIR)
except ImportError:
    print("Not in Colab: put files in ./marsad_uploads or type a path in the dashboard.")
'''.replace("{{", "{").replace("}}", "}")
launch = '''#@title 3. Open the dashboard
from marsad_analytics.ui import Dashboard
dash = Dashboard()
dash.show()
'''
ref = f"""## Card reference

Old indicator ids (F1 to F138 and the primary analyses) are listed so earlier results can be traced.

| Card | Name | Question | Replaces |
| --- | --- | --- | --- |
{rows}

**Presets**

| Preset | Cards | For |
| --- | --- | --- |
{presets}

**Validation and annotation.** Cell 5 checks a lexicon's precision. For a full annotation round use card PAPER-2 (stratified sample, one sheet per annotator), then `validation.agreement([...sheets])` for Cohen's kappa, Fleiss' kappa and Krippendorff's alpha. Card PAPER-3 drafts the dataset's datasheet.

The Palestine/Gaza topic pack (tick it under *Topic packs* before loading) adds 12 lexicons and 18 preset cards that reproduce the notebook's Gaza-specific indicators.
"""
script = '''#@title 4. Scripted use (optional): run cards from code on the data loaded above
s = dash.session            # or: from marsad_analytics import load, Session, Settings; s = Session(load("file.csv"), Settings(analysis_tz="Asia/Qatar"))
r = s.run("FRAME-2", lex_a="hope", lex_b="despair", by="time")
r.figure.show() if r.figure is not None else None
display(r.main_table())
print("\\n".join(r.caveats))
# More: s.run("REACT-2", feature="hashtags", outcome="shares"); s.run("TIME-4", events=[{"name": "Event", "date": "2024-01-26"}])
# Corpus tools: s.run("WORDS-3", target="group:page", group="owner_type", reference="rest"); s.kwic("غزة"); s.run("WORDS-5", node="غزة")
# Posts behind a chart point: s.examples(r.figure.data[0].customdata[0][0])
# s.add_lexicon("my_terms", ["term one", "كلمة"]); s.run("FRAME-1", lexicons=["my_terms"])
# Models (GPU): from marsad_analytics import enrich; enrich.run_classifier(s, "toxicity"); s.run("FRAME-9", threshold=0.7)
# Topics: s.run("TOPIC-1", min_cluster_size=20, min_samples=10, epsilon=0.1); s.run("TOPIC-1", use_run=1)
# Network: s.run("WHO-4", kind="reply", search="name", hide_pendants=True, date_from="2024-01-01", toxic_only=True)
# from marsad_analytics.cards import network; network.save_graphml(s, "net.graphml"); network.explorer_html(s, "net.html")
'''
valid = '''#@title 5. Validate a lexicon (precision on sampled matches)
LEXICON = "hope" #@param {type:"string"}
N = 200 #@param {type:"integer"}
from marsad_analytics import validation
sheet = validation.sample_matches(dash.session, LEXICON, n=N, path=f"validate_{LEXICON}.xlsx")
print(f"Wrote validate_{LEXICON}.xlsx with {len(sheet)} posts. Two annotators fill the 'correct' column (1 or 0),")
print("then run: res = validation.score(['validate_hope_A.xlsx', 'validate_hope_B.xlsx'], dataset='name', annotators=['A','B'])")
try:
    from google.colab import files; files.download(f"validate_{LEXICON}.xlsx")
except Exception:
    pass
'''
nb = nbf.v4.new_notebook()
nb.cells = [nbf.v4.new_markdown_cell(intro), nbf.v4.new_code_cell(setup), nbf.v4.new_code_cell(upload), nbf.v4.new_code_cell(launch),
            nbf.v4.new_code_cell(script), nbf.v4.new_code_cell(valid), nbf.v4.new_markdown_cell(ref)]
nb.metadata = {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
               "language_info": {"name": "python"}}
out = sys.argv[1] if len(sys.argv) > 1 else "MARSAD_Analytics.ipynb"
nbf.write(nb, out)
print(out, os.path.getsize(out) // 1024, "KB")
