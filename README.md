# NutriTimbang 🥬

A responsive Streamlit web app combining a **food / macro tracker**, an **adult calorie and protein target estimator**, and a **workout split guide**. Designed for a Philippine audience, but all labels are in English for now.

## What works in version 1

- Home screen with direct navigation to **Food & Nutrition** and **Workout Guide**
- Searchable 58-food local starter CSV with **calories, protein, carbs, fat per 100 g or 1 g**
- Build meals with unlimited individual food servings, enter grams, calculate combined totals, remove entries, clear the meal, and export CSV
- Optional **live official USDA FoodData Central search**, with individual record links and per-100-g nutrients
- Custom foods for your own recipes and packaged-food labels
- Adult energy expenditure and protein estimates with **Maintenance, Cutting, Lean bulk, Bulking** targets, showing the formula
- Workout splits: **PPL, Upper/Lower, Arnold, Hybrid PPL+UL, Full Body**, with day-by-day exercises, sets, reps, rest time, completion checkboxes, and schedule CSV export
- Sources & Credits section linking to **DOST–FNRI PhilFCT, USDA, DOH, research papers**

### Important data integrity and licensing note

**`foods.csv` contains illustrative starter estimates, *not* certified or item-by-item verified USDA/DOH/DOST-FNRI records.** The sample data is meant for demonstrating the calculator; quantities vary by preparation and recipe. Live USDA lookup fetches published food records and provides an item-specific link (FDC ID). The separate DOST–FNRI PhilFCT source is linked as a reference, but its database and logo are not embedded; permission may be needed for republication. Do not relabel the starter file as "official DOH" or "official FNRI." No institution endorses this app.

USDA FoodData Central data is [CC0 public domain](https://fdc.nal.usda.gov/api-guide/). The app is suitable for learning and prototyping; it is not medical or dietetic advice.

## Folder structure

```text
NutriTimbang/
├── app.py                      # Streamlit web interface
├── nutrition.py                # Macros, targets and USDA API access
├── workouts.py                 # Exercise schedules and training splits
├── foods.csv                   # 58 illustrative starter foods
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml             # Dark green / midnight app theme
│   └── secrets.toml.example    # Documentation only — no real key
├── tests/
│   └── test_nutrition.py       # Calculation tests
├── .gitignore
└── README.md
```

## Step-by-step: upload to GitHub (browser method)

1. **Download and extract** the `NutriTimbang.zip` bundle. It contains a `NutriTimbang` folder.
2. Log in to [GitHub](https://github.com/). Click **+ → New repository** and name it `NutriTimbang`, or open your existing repository.
3. If the repository is empty, click **uploading an existing file**. Otherwise use **Add file → Upload files**.
4. From inside the extracted `NutriTimbang` folder, upload **the contents** to the *root* of your repository, not a second nested NutriTimbang folder. Your app must be at **`app.py` in the root**.
5. Make sure the repository includes `app.py`, `nutrition.py`, `workouts.py`, `foods.csv`, `requirements.txt`, and `README.md`. Keep `.streamlit/config.toml` in the `.streamlit` directory. **Do not upload any real `secrets.toml` or API key.** GitHub's web upload can hide dotfolders on some systems; if needed, create `.streamlit/config.toml` using **Add file → Create new file** and type the full path as the new file name.
6. Scroll to the bottom, select **Commit changes**, and verify the files are visible.

## Step-by-step: publish with Streamlit Community Cloud

1. Visit **https://share.streamlit.io/** and sign in via GitHub.
2. Choose **Create app** → **Yup, I have an app** (names may vary slightly).
3. Choose the GitHub repository containing the uploaded project and your `main` branch.
4. **Main file path / entrypoint:** type `app.py` (not `NutriTimbang/app.py` if files are in the repository root).
5. Optional: choose an available app URL, like `nutritimbang-<yourname>.streamlit.app`.
6. In **Advanced settings** choose a supported Python version (3.12 is a good match). You can paste a USDA API key as a secret (see below).
7. Click **Deploy**. Once finished, copy your new `streamlit.app` link.
8. Future edits to your GitHub repository generally redeploy the app automatically.

Official docs: [Deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) · [Dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) · [Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

## Optional: unlock live USDA search at scale

The app will run *without* a personal API key. It defaults to USDA's shared `DEMO_KEY`, which has strict limits; searches may fail after multiple uses. A personal API key is strongly advised for a public deployment.

1. Get a **free API key** from [USDA FoodData Central](https://fdc.nal.usda.gov/api-key-signup/).
2. In your Streamlit Cloud app's **Settings → Secrets** (or **Advanced settings → Secrets** during deployment), paste:

```toml
FDC_API_KEY = "YOUR_ACTUAL_KEY_HERE"
```

3. Save the secret. **Do not paste the key into `app.py` or a public GitHub file.**

Live USDA lookup still depends on the USDA API being available. For a user-facing deployment, the Streamlit server makes the API requests; the browser does not receive the API key.

## Run locally on Windows, Mac or Linux (optional)

From a terminal in the extracted project directory:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit will show a URL, usually `http://localhost:8501`.

## How the calculations work

### Food portions

For a food with nutrient `N` per 100 g:

`N in your serving = N per 100 g × serving weight in g / 100`

Example: 150 g of **illustrative** cooked chicken breast at 31.0 g protein / 100 g gives **46.5 g protein**. Values vary with cooking and water loss. For consistent entries, weigh foods at the preparation state shown.

### Personal targets

Adult resting energy estimate (Mifflin–St Jeor):

- **Male published constant:** `10 × kg + 6.25 × cm − 5 × age + 5`
- **Female published constant:** `10 × kg + 6.25 × cm − 5 × age − 161`
- **Maintenance estimate (TDEE):** resting energy × activity multiplier
- Goal bands below are **illustrative, user-adjustable project assumptions**, not clinically established calorie prescriptions:
  - Maintenance: 95–105% of maintenance estimate
  - Cutting: 80–90%
  - Lean bulk: 105–110%
  - Bulking: 110–120%
- Sample protein intake band: **1.4–2.0 g/kg** for maintenance/bulking, **1.6–2.2 g/kg** for cutting/lean bulking. ISSN's widely cited position stand supports approximately **1.4–2.0 g/kg/day** for most exercising people; higher app target bands are practical extensions, not a direct quote.

No number from this estimator should be interpreted as a universally safe minimum or medical recommendation. For adults only; not intended for minors, pregnancy/breastfeeding, or clinical treatment.

Research: [Mifflin et al.](https://pubmed.ncbi.nlm.nih.gov/2305711/) · [ISSN position stand](https://pubmed.ncbi.nlm.nih.gov/28642676/)

## Data privacy and limitations

- Entries and completed workouts are saved only for the **current Streamlit browser session**; refreshing/restarting can clear them. There are no accounts or long-term workout history in v1.
- The app does not use a camera or automatically identify foods from photographs.
- Complex dishes such as adobo/sinigang depend on their individual ingredients. Enter a recipe into Custom food or add its ingredients separately.
- Always verify food data, labels and portion sizes for research, medical, or competitive-sport uses.
- Logos from government agencies are **not** included; official names and source links are provided instead.

## Potential version 2 features

Officially licensed FNRI food records, expanded Filipino recipes, food favorites, barcode lookup, long-term log-in based history, charted progress, adjustable nutrition preferences, program builder, exercise form photos/videos with source and image rights, multi-language support.
