# Style-mimic 多文风论文展示 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline static showcase and a locally compiled LaTeX PDF that present one style-mimic paper in 11 clearly labeled teaching pastiches.

**Architecture:** Store the five semantic units and all 11 voice variants in `examples/style-paper/data/styles.json`. The browser reads that one data source through `app.js`; a small Python generator converts the same data into LaTeX-safe content for `style-mimic-paper.tex`. Generated metrics are recorded in the data and verified against the repository's style tools before compilation.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, JSON, Python 3 standard library, XeLaTeX (with a documented fallback), existing `style_analyze.py` and `style_review.py`.

## Global Constraints

- The page must work offline with no CDN, package manager, or build step.
- The 11 versions are teaching pastiches, never presented as original or official author text.
- The semantic units and claims remain constant across voices; only voice/register choices change.
- The PDF must be compiled locally and committed with its source and build log.
- All quantitative scores are heuristic review signals, not authorship or AI-generation verdicts.
- Do not add React/Vite or copy long copyrighted passages.

---

### Task 1: Create the shared paper dataset

**Files:**
- Create: `examples/style-paper/data/styles.json`
- Create: `examples/style-paper/data/README.md`
- Test: `examples/style-paper/tests/test_data.py`

**Interfaces:**
- Produces JSON object `{title, thesis, units, voices, metrics, ethics}`.
- Each `voice` has `{id, name, language, era, register, living_author, disclaimer, sections}`.
- `sections` always has exactly `abstract`, `method`, `case`, `limits`, `conclusion` strings.

- [ ] **Step 1: Write the failing data contract test**

```python
def test_dataset_has_eleven_voices_and_five_shared_sections():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert len(data["voices"]) == 11
    expected = {"abstract", "method", "case", "limits", "conclusion"}
    assert {"abstract", "method", "case", "limits", "conclusion"} == expected
    for voice in data["voices"]:
        assert set(voice["sections"]) == expected
        assert voice["disclaimer"]
```

- [ ] **Step 2: Run the test and verify it fails because the dataset is absent**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_data.py -v`

Expected: FAIL with a missing `styles.json` file.

- [ ] **Step 3: Add the canonical thesis and 11 concise voice variants**

Use the same five claims in every voice: measurable style distributions; six-layer profile; tail-aware review; content/style separation; ethical limits. Label Barbara as Barbara Oakley and mark Oakley, Trump, and Obama as living-author teaching pastiches.

- [ ] **Step 4: Run the contract test**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_data.py -v`

Expected: PASS, with all 11 IDs unique and all section strings non-empty.

- [ ] **Step 5: Commit the dataset**

```bash
git add examples/style-paper/data examples/style-paper/tests/test_data.py
git commit -m "添加多文风论文共享数据集"
```

### Task 2: Build the offline showcase page

**Files:**
- Create: `examples/style-paper/index.html`
- Create: `examples/style-paper/styles.css`
- Create: `examples/style-paper/app.js`
- Modify: `examples/style-paper/data/styles.json` only if Task 2 reveals a contract issue
- Test: `examples/style-paper/tests/test_page.py`

**Interfaces:**
- `app.js` exports no framework API; it reads `data/styles.json`, renders `#voice-grid`, `#section-tabs`, and `#voice-detail`, and updates `aria-selected` state.
- Every voice card exposes `data-voice-id`; every section tab exposes `data-section`.

- [ ] **Step 1: Write the failing static-page checks**

```python
def test_page_has_required_mounts_and_local_assets():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'id="voice-grid"' in html
    assert 'id="section-tabs"' in html
    assert 'src="app.js"' in html
    assert 'href="styles.css"' in html
```

- [ ] **Step 2: Run the test and verify the page files are absent**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_page.py -v`

Expected: FAIL on missing `index.html`.

- [ ] **Step 3: Implement the page shell and data-driven renderer**

Use the “文体实验室” visual system from the design spec: ink background, paper reading surface, vermilion active state, serif display type, monospace metrics. Include language/era/register filters, five section tabs, copy action, PDF action, explicit pastiche notice, empty state, visible focus rings, and reduced-motion CSS.

- [ ] **Step 4: Run static checks and a local HTTP smoke test**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_page.py -v
python3 -m http.server 8765 --directory examples/style-paper >/tmp/style-paper-http.log 2>&1 & echo $! >/tmp/style-paper-http.pid
curl --fail --silent http://127.0.0.1:8765/index.html | grep -q '文体实验室'
kill "$(cat /tmp/style-paper-http.pid)"
```

Expected: test PASS and HTTP response contains the page title.

- [ ] **Step 5: Commit the page**

```bash
git add examples/style-paper/index.html examples/style-paper/styles.css examples/style-paper/app.js examples/style-paper/tests/test_page.py
git commit -m "构建离线多文风论文展示页"
```

### Task 3: Add metric generation and LaTeX source

**Files:**
- Create: `examples/style-paper/scripts/generate_latex.py`
- Create: `examples/style-paper/tex/styles.tex`
- Create: `examples/style-paper/tex/references.bib`
- Create: `examples/style-paper/tex/style-mimic-paper.tex`
- Create: `examples/style-paper/tex/build.sh`
- Create: `examples/style-paper/tests/test_latex_generator.py`

**Interfaces:**
- `generate_latex.py --data DATA --out TEX` reads the shared JSON and writes deterministic LaTeX sections.
- `build.sh` runs `xelatex -interaction=nonstopmode -halt-on-error style-mimic-paper.tex` twice from the `tex/` directory.

- [ ] **Step 1: Write the failing generator test**

```python
def test_generator_emits_all_voice_ids_and_escapes_latex():
    out = subprocess.check_output([sys.executable, str(GENERATOR), "--data", str(DATA), "--out", str(TEX)], text=True)
    assert "\\section{苏轼" in out
    assert "Barbara Oakley" in out
    assert r"\&" not in out or "\\&" in out
```

- [ ] **Step 2: Run it and verify the generator is absent**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_latex_generator.py -v`

Expected: FAIL with a missing generator file.

- [ ] **Step 3: Implement deterministic JSON-to-LaTeX generation**

Escape `\`, `{}`, `%`, `&`, `#`, `_`, and Unicode punctuation; generate an ethics note, canonical method section, voice sections, metrics table, and bibliography references. Keep the source data as the only editable prose source.

- [ ] **Step 4: Add the XeLaTeX document and build script**

Use `ctexart` when available; define a fallback message in `build.sh` if `xelatex` is missing. Include the generated voice material via `\\input{generated-voices.tex}` so the source remains inspectable.

- [ ] **Step 5: Run generator and LaTeX source tests**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_latex_generator.py -v`

Expected: PASS and generated output contains all 11 voices.

- [ ] **Step 6: Commit LaTeX sources**

```bash
git add examples/style-paper/scripts examples/style-paper/tex examples/style-paper/tests/test_latex_generator.py
git commit -m "添加共享数据驱动的 LaTeX 论文源稿"
```

### Task 4: Compile, measure, and verify the deliverables

**Files:**
- Modify: `examples/style-paper/data/styles.json` to add measured metrics
- Create: `examples/style-paper/tex/generated-voices.tex`
- Create: `examples/style-paper/tex/style-mimic-paper.pdf`
- Create: `examples/style-paper/tex/build.log`
- Create: `examples/style-paper/tests/test_artifacts.py`

**Interfaces:**
- `scripts/style_analyze.py` receives one text file per voice section and returns JSON metrics.
- `scripts/style_review.py aiflavor` and `sim` output review metrics used as page badges and appendix values.

- [ ] **Step 1: Write artifact acceptance tests**

```python
def test_pdf_exists_and_is_nontrivial():
    pdf = ROOT / "tex/style-mimic-paper.pdf"
    assert pdf.exists() and pdf.stat().st_size > 10_000

def test_metrics_cover_all_voices():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert all("metrics" in voice for voice in data["voices"])
```

- [ ] **Step 2: Run the tests and verify they fail before compilation**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest examples/style-paper/tests/test_artifacts.py -v`

Expected: FAIL because the PDF and metric fields do not exist yet.

- [ ] **Step 3: Generate short per-voice plain-text files and run the style tools**

For each voice, write the five section strings to a temporary text file, run `style_analyze.py --json`, run `aiflavor`, and compare each voice with the canonical academic version using `sim`. Store only rounded, reproducible fields needed by the page and appendix.

- [ ] **Step 4: Generate the LaTeX body and compile locally**

Run: `cd examples/style-paper/tex && ./build.sh`

Expected: exit code 0, `style-mimic-paper.pdf` exists, and the log has no `Fatal error`.

- [ ] **Step 5: Verify the PDF and page together**

Run:

```bash
pdfinfo examples/style-paper/tex/style-mimic-paper.pdf | grep Pages
pdftotext examples/style-paper/tex/style-mimic-paper.pdf /tmp/style-paper.txt
grep -q 'Barbara Oakley' /tmp/style-paper.txt
curl --fail --silent http://127.0.0.1:8765/data/styles.json | grep -q 'style-mimic'
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples/style-paper/tests -v
```

Expected: PDF has more than one page, extracted text contains all voice names, and all tests pass.

- [ ] **Step 6: Commit and push the completed artifact**

```bash
git add examples/style-paper
git commit -m "交付多文风论文网页与本地编译 PDF"
git push origin master
```
