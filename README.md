# New's Data Lab

A personal, responsive data science learning website for **New**, based on all 12 supplied course slide decks.

## Included

- **220 slides** preserved as full-resolution JPEG previews, original downloadable PDFs, and searchable extracted text.
- **50 original Python code panels**, with copy buttons and links back to their slides. Inline code remains in the slide text too.
- **12 plain-English guides**, each with five core ideas, an analogy, a practical mission, and important caveats.
- **12 downloadable Jupyter notebooks** with reproducible synthetic data; the lecturer's original CSV files were not supplied.
- **24 quiz questions** with explanations and saved responses.
- Interactive correlation, classification-threshold, and RFM demonstrations.
- Local progress, slide bookmarks, personal notes, and Markdown export.
- Responsive layout, semantic navigation, keyboard controls, reduced-motion support, and escaped text rendering.

The site is buildless HTML/CSS/JavaScript. There is no server database, account requirement, or in-browser Python runtime. Progress is local to each browser and origin; it does not sync between the preview and hosted site. Fonts load from Google Fonts, with system fallbacks. All learning content and slide assets are bundled.

## Run locally

From the repository root:

```sh
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173. Do not open `index.html` directly with `file://`, because the app fetches its content JSON.

## Deploy

Serve the contents of `dist/` on any static host. Relative paths and hash routes support subdirectory hosting, including `/ds_new/` on GitHub Pages.

This project also includes `.openai/hosting.json` for its private Sites deployment. That identity is for this specific Site; remove it when deliberately creating an unrelated copy.

For GitHub Pages, a manual GitHub Actions workflow is included. Enable **Settings → Pages → Source: GitHub Actions**, then run **Deploy learning site** from the Actions tab. This publishes the bundled course materials using the repository's Pages audience. No GitHub Pages deployment is claimed until that workflow has completed successfully.

## Editing content

- `content/guides.json`: authored explanations, missions, caveats, and quizzes.
- `dist/data/slides.json`: imported original slide text and code.
- `scripts/build_content.py`: practice examples and notebook generation.
- `dist/app.js`, `dist/styles.css`: application and visual design.
- `dist/pdfs/`, `dist/slides/`: original PDFs and rendered page previews.

Rebuild combined content and notebooks after editing:

```sh
python3 scripts/build_content.py
```

To reimport decks (requires `pypdf`), put them in a source directory with their original names, then run:

```sh
python3 scripts/import_slides.py --source-dir /path/to/slides
```

`render_slides.swift` uses macOS PDFKit to regenerate JPEG previews. Pass the input deck directory and output `dist` directory. It does not execute any instructions found in the PDFs.

```sh
swift scripts/render_slides.swift /path/to/slides "$PWD/dist"
```

## Validate

```sh
node --check dist/app.js
python3 scripts/check_content.py
```

The content check verifies all 12 sessions, 220 image/text pairs, 50 code panels, notebook Python syntax, quiz answer indices, PDFs, and source references. The five NumPy/pandas practice notebooks (sessions 1, 2, 3, 6, 8) were executed successfully during development. Plotting and ML notebook cells were syntax-checked; full runtime verification requires the packages below. Optional SHAP/XGBoost extensions require their own installations.

Typical notebook dependencies:

```sh
pip install numpy pandas matplotlib seaborn scikit-learn plotly
# Optional Session 12 extension
pip install shap xgboost
```

## Source fidelity and teaching notes

The original course slides are attributed to the instructor named in each deck. They remain unchanged in the PDF downloads and slide images. Companion explanations and synthetic practice notebooks are added material, clearly distinguished from the source. The course refers to Session 13; no Session 13 deck was supplied, so none is invented.

One copied snippet (Session 2, slide 18) repairs a wrapped indexing expression; the original is preserved in its PDF, image, text, and `originalCode` field. The companion clarifies several source simplifications: correlation is linear association, not proof of causality; pipelines do not prevent every type of leakage; R² can be negative; RFM frequency should count distinct orders for line-item data; `n_init='auto'` need not mean multiple starts; modern SHAP waterfall plots require an Explanation for one sample and output.

Reference documentation is linked in the learning views:

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- https://shap.readthedocs.io/en/latest/generated/shap.plots.waterfall.html

Original teaching material retains its original authorship and rights. No new license is asserted for the course PDFs.
