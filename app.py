"""NutriTimbang: food tracking + strength-training templates.

Run: streamlit run app.py
Deploy: upload this entire repository, set entrypoint to app.py.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from nutrition import calculate_targets, fetch_usda_food, meal_totals, scale_nutrition, search_usda
from workouts import SPLITS

BASE_DIR = Path(__file__).resolve().parent
st.set_page_config(
    page_title="NutriTimbang | Nutrition + Fitness",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family: 'DM Sans', sans-serif;}
[data-testid="stAppViewContainer"] {background: #0c1421;}
.block-container {max-width: 1260px; padding-top: 1.4rem; padding-bottom: 5rem;}
[data-testid="stHeader"] {background: transparent;}
h1,h2,h3 {letter-spacing: -.025em;}
h1 {font-weight: 800 !important;}
div[data-testid="stMetric"] {background: #132238; padding: 1rem 1.25rem; border: 1px solid #26394e; border-radius: 17px;}
div[data-testid="stMetricValue"] {color: #adf0d5; font-weight: 800;}
div[data-testid="stMetricLabel"] {color: #afc1d3;}
.stButton > button[kind="primary"] {background: #72e4bc; color: #102323; border: none; font-weight: 800;}
.stButton > button {border-radius: 11px; font-weight: 650;}
div[data-baseweb="tab-list"] {gap: 10px;}
button[data-baseweb="tab"] {font-weight: 700;}
.smallcaps {font-size: .78rem; text-transform: uppercase; font-weight: 800; color: #72e4bc; letter-spacing: .14em;}
.hero {padding: 34px 32px; border-radius: 25px; background: linear-gradient(120deg, #133f43 0%, #1c3d51 57%, #223048 100%); border: 1px solid #356667; margin: 15px 0 25px 0;}
.hero-title {font-size: clamp(2.1rem, 5vw, 4.3rem); line-height: 1.07; font-weight: 800; letter-spacing: -.055em; color: #effff9; margin: 14px 0;}
.hero-body {font-size: 1rem; max-width: 760px; line-height: 1.7; color: #d2e4ec;}
.hero-chip {display: inline-block; border-radius: 50px; padding: 5px 12px; background: #18494c; border: 1px solid #518b7c; color: #b8fbe3; font-size: .75rem; font-weight: 700;}
.card {min-height: 130px; border-radius: 18px; border: 1px solid #2b4557; background: #15263a; padding: 22px; margin: 9px 0;}
.card-title {font-size: 1.25rem; color: white; font-weight: 800; margin-bottom: 6px;}
.card-copy {color: #b4c5d5; font-size: .91rem; line-height: 1.65;}
.soft-note {background: #102936; border: 1px solid #315869; border-radius: 12px; padding: 12px 16px; color: #c0dce8; font-size: .9rem; margin: 14px 0;}
.section-intro {color: #b8cbd8; margin-top: -6px; margin-bottom: 16px;}
footer {visibility:hidden;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_foods(include_unverified: bool = False) -> list[dict]:
    """Curated USDA-linked records by default; legacy estimates only by opt-in."""
    frame = pd.read_csv(BASE_DIR / "foods.csv").fillna("")
    if include_unverified:
        estimates = pd.read_csv(BASE_DIR / "foods_estimates.csv").fillna("")
        estimates["source_url"] = ""  # a generic search page is not proof of the value
        estimates["fdc_id"] = ""
        estimates["usda_description"] = ""
        frame = pd.concat([frame, estimates], ignore_index=True)
    # Use text FDC IDs even when legacy rows have blanks; never show 171477.0.
    frame["fdc_id"] = frame["fdc_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    for field in ("calories", "protein", "carbs", "fat"):
        frame[field] = pd.to_numeric(frame[field], errors="coerce").fillna(0)
    return frame.to_dict("records")


@st.cache_data(ttl=3600, show_spinner=False)
def cached_search(query: str, api_key: str) -> list[dict]:
    return search_usda(query, api_key=api_key)


@st.cache_data(ttl=86400, show_spinner=False)
def cached_food(fdc_id: int, api_key: str) -> dict:
    return fetch_usda_food(fdc_id, api_key=api_key)


def api_key() -> str:
    """Never hardcode credentials into public GitHub source."""
    if os.environ.get("FDC_API_KEY"):
        return os.environ["FDC_API_KEY"]
    try:
        return st.secrets.get("FDC_API_KEY", "DEMO_KEY")
    except (FileNotFoundError, KeyError):
        return "DEMO_KEY"


def safe_number(number: float, precision: int = 1) -> str:
    return f"{float(number):,.{precision}f}"


def ensure_state() -> None:
    defaults = {
        "page": "🏠 Home",
        "meal": [],
        "usda_results": [],
        "targets": None,
        "completed_workouts": {},
        "usda_query": "",
    }
    for name, value in defaults.items():
        if name not in st.session_state:
            st.session_state[name] = value


def nav_to(page: str) -> None:
    st.session_state.page = page


def subsection(title: str, subtitle: str = "") -> None:
    st.subheader(title)
    if subtitle:
        st.markdown(f'<div class="section-intro">{subtitle}</div>', unsafe_allow_html=True)


def metric_row(cal: float, pro: float, carb: float, fat: float) -> None:
    a, b, c, d = st.columns(4)
    a.metric("Calories", f"{cal:,.0f} kcal")
    b.metric("Protein", f"{pro:,.1f} g")
    c.metric("Carbs", f"{carb:,.1f} g")
    d.metric("Fat", f"{fat:,.1f} g")


def add_food(food: dict, grams: float) -> None:
    # Strictly reject unreported nutrients from external USDA records: absence ≠ zero.
    missing = [k for k in ("calories", "protein", "carbs", "fat") if food.get(k) is None]
    if missing:
        st.error(
            f"That USDA food record does not report {', '.join(missing)} per 100 g. "
            "Try a different result to avoid silently counting missing nutrients as zero."
        )
        return
    row = scale_nutrition(food, grams)
    row.update(
        uid=f"meal-{st.session_state.get('next_meal_id', 0)}",
        name=food["name"],
        origin=food.get("status", "Unknown source"),
        source=food.get("source_url", ""),
        fdc_id=food.get("fdc_id", ""),
    )
    st.session_state.next_meal_id = st.session_state.get("next_meal_id", 0) + 1
    st.session_state.meal.append(row)
    st.toast(f"Added {safe_number(grams, 0)} g to your meal", icon="✅")


def home() -> None:
    st.markdown(
        """
<div class="hero">
  <span class="hero-chip">NUTRITION × TRAINING · PH FRIENDLY</span>
  <div class="hero-title">Eat smarter.<br>Train with purpose.</div>
  <div class="hero-body">One place to look up foods, calculate the macros on your plate,
  estimate daily nutrition targets, and explore gym training splits.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            '<div class="card"><div class="smallcaps">01 / Nutrition</div>'
            '<div class="card-title">🥗 Food & Nutrition</div>'
            '<div class="card-copy">Browse 26 USDA-linked offline foods, weigh several portions, trace their references, and set nutrition goals.</div></div>',
            unsafe_allow_html=True,
        )
        st.button("Open food tracker →", key="home_food", use_container_width=True,
                  type="primary", on_click=nav_to, args=("🥗 Food & Nutrition",))
    with right:
        st.markdown(
            '<div class="card"><div class="smallcaps">02 / Workout</div>'
            '<div class="card-title">🏋️ Workout Guide</div>'
            '<div class="card-copy">Explore PPL, upper/lower, Arnold, hybrid, and full-body splits, with exercises, sets, and reps for every day.</div></div>',
            unsafe_allow_html=True,
        )
        st.button("Explore workout splits →", key="home_workout", use_container_width=True,
                  on_click=nav_to, args=("🏋️ Workout Guide",))
    st.write("")
    st.markdown("#### How it works")
    cols = st.columns(3)
    for col, emoji, title, desc in zip(
        cols,
        ["🔎", "⚖️", "📈"],
        ["Find your food", "Enter serving grams", "See your totals"],
        ["Browse the starter library or search official USDA records.",
         "Choose several foods and enter each serving weight.",
         "See calories and macros, and compare with your own estimated targets."],
    ):
        with col:
            st.markdown(
                f'<div class="card"><div class="card-title">{emoji} {title}</div>'
                f'<div class="card-copy">{desc}</div></div>', unsafe_allow_html=True
            )
    st.info("The default offline food list now has **26 entries mapped to specific USDA FoodData Central records**. "
            "The previous 58 estimates are available only if you choose to include unverified foods. "
            "Foods still vary by cooking method and product.")


def food_library(foods: list[dict]) -> None:
    subsection("Food library", "Nutrients per gram or 100 g, with food-specific USDA record IDs and links. Match the preparation before weighing.")
    left, right, third = st.columns([2, 1.4, 1.2])
    phrase = left.text_input("Find a food", placeholder="chicken, pork, rice, bangus...", key="library_filter")
    categories = ["All categories"] + sorted({food["category"] for food in foods})
    category = right.selectbox("Food category", categories)
    display_units = third.selectbox("Show nutrients per", ["100 g", "1 g"])
    selected = [f for f in foods if phrase.casefold() in f["name"].casefold() and
                (category == "All categories" or f["category"] == category)]
    multiplier = 1 if display_units == "100 g" else 0.01
    display = pd.DataFrame([{
        "Food / preparation": f["name"],
        "Category": f["category"],
        "Calories (kcal)": round(f["calories"] * multiplier, 2),
        "Protein (g)": round(f["protein"] * multiplier, 3),
        "Carbs (g)": round(f["carbs"] * multiplier, 3),
        "Fat (g)": round(f["fat"] * multiplier, 3),
        "Record ID": f.get("fdc_id", "") if f.get("fdc_id", "") != "" else "—",
        "Data status": f.get("status", ""),
        "Publisher / source": f.get("source_name", ""),
        "USDA food record": f.get("source_url", ""),
    } for f in selected])
    verified_count = sum(str(f.get("id", "")).startswith("usda:") for f in selected)
    st.caption(f"{len(selected)} foods · {verified_count} mapped to USDA FDC IDs · {len(selected)-verified_count} legacy estimates")
    if display.empty:
        st.info("No matches. Try another search.")
    else:
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            column_config={"USDA food record": st.column_config.LinkColumn("Open source")},
        )
        st.download_button("Download displayed food list (CSV)", data=display.to_csv(index=False),
                           file_name="nutritimbang_food_library.csv", mime="text/csv")
    st.info("USDA-linked foods include a unique FDC ID and source link. Values are rounded from public "
            "USDA-derived listings, not measurements of your exact meal. Optional older entries are labelled "
            "'Starter estimate' and have no certified food-specific source. DOST–FNRI content is not copied.")


def meal_builder(foods: list[dict]) -> None:
    subsection("Build your meal", "Select multiple foods and enter their weights. Each added serving stays in this browser session.")
    source = st.radio(
        "How would you like to add food?",
        ["Offline food library", "Live USDA lookup", "Custom food"],
        horizontal=True,
    )
    if source == "Offline food library":
        names = {f["id"]: f for f in foods}
        q = st.text_input("Filter options", placeholder="Type chicken, tofu, beef...", key="quick_search")
        ids = [k for k, v in names.items() if q.lower() in v["name"].lower()]
        if ids:
            selected_id = st.selectbox("Choose food", ids, format_func=lambda k: names[k]["name"])
            food = names[selected_id]
            st.caption(
                f"Per 1 g: {food['calories']/100:.2f} kcal · "
                f"{food['protein']/100:.3f} g protein · "
                f"{food['carbs']/100:.3f} g carbs · "
                f"{food['fat']/100:.3f} g fat"
            )
            if str(food.get("id", "")).startswith("usda:"):
                st.caption(f"USDA FoodData Central · SR Legacy · FDC ID {food['fdc_id']} · "
                           f"[Open matching source record]({food['source_url']})")
                with st.expander("Exact source food description"):
                    st.write(food.get("usda_description", food["name"]))
                    st.caption("Publicly listed values are rounded to the displayed precision. "
                               "Cooking oil, sauces and other ingredients are not included unless named in the record.")
            else:
                st.warning("Unverified legacy estimate — there is no individual USDA/FNRI reference for these numbers. "
                           "Use an official record or your product label for stronger evidence.")
            grams = st.number_input("Weight of your portion (g)", min_value=1.0, max_value=10000.0,
                                    value=100.0, step=5.0, key="quick_grams")
            if st.button("＋ Add serving to meal", type="primary", key="add_quick"):
                add_food(food, grams)
        else:
            st.info("No matching offline foods. Enable legacy estimates, try USDA search, or enter a custom food.")
    elif source == "Live USDA lookup":
        st.caption("Official USDA FoodData Central: Foundation Foods, SR Legacy, and FNDDS. Requires internet access. "
                   "Uses a low-limit DEMO_KEY unless you configure your own free API key.")
        key = api_key()
        if key == "DEMO_KEY":
            st.warning("Demo API key active. Searches may be rate-limited. For a public app, configure FDC_API_KEY in Streamlit secrets.")
        with st.form("usda_search_form"):
            search_phrase = st.text_input("Search official USDA records", value=st.session_state.usda_query,
                                          placeholder="chicken breast cooked / beef raw / brown rice")
            submitted = st.form_submit_button("🔎 Search USDA")
        if submitted:
            st.session_state.usda_query = search_phrase
            if search_phrase.strip():
                try:
                    with st.spinner("Searching USDA FoodData Central..."):
                        st.session_state.usda_results = cached_search(search_phrase, key)
                    if not st.session_state.usda_results:
                        st.info("No results. Try shorter keywords or a different preparation.")
                except requests.RequestException as exc:
                    st.session_state.usda_results = []
                    st.error(f"USDA lookup was unavailable ({type(exc).__name__}). Try again later, or use starter foods.")
            else:
                st.session_state.usda_results = []
                st.info("Enter a food name first.")
        if st.session_state.usda_results:
            options = st.session_state.usda_results
            idx = st.selectbox(
                "Select matching USDA food",
                range(len(options)),
                format_func=lambda n: f"{options[n].get('description', 'Food')} · {options[n].get('dataType')} · ID {options[n]['fdcId']}",
                key="usda_index",
            )
            record = options[idx]
            st.caption(f"Source: USDA FoodData Central · FDC ID {record['fdcId']} · "
                       f"[Open record](https://fdc.nal.usda.gov/food-details/{record['fdcId']}/nutrients)")
            grams = st.number_input("Weight of your portion (g)", min_value=1.0, max_value=10000.0,
                                    value=100.0, step=5.0, key="usda_grams")
            if st.button("＋ Add USDA serving", type="primary", key="add_usda"):
                try:
                    with st.spinner("Loading verified source record..."):
                        food = cached_food(int(record["fdcId"]), key)
                    add_food(food, grams)
                except (requests.RequestException, ValueError) as exc:
                    st.error(f"Could not add food: {exc}")
    else:
        st.caption("For recipes, label estimates, or custom foods. You are responsible for the entered values.")
        with st.form("custom_food_form"):
            name = st.text_input("Food name", placeholder="Homemade chicken adobo")
            grams = st.number_input("Serving weight (g)", min_value=1.0, value=100.0, max_value=10000.0)
            st.markdown("**Nutrition per 100 g** (from your recipe or label)")
            a, b, c, d = st.columns(4)
            cal = a.number_input("Calories (kcal)", min_value=0.0, value=0.0)
            pro = b.number_input("Protein (g)", min_value=0.0, value=0.0)
            carb = c.number_input("Carbs (g)", min_value=0.0, value=0.0)
            fat = d.number_input("Fat (g)", min_value=0.0, value=0.0)
            source_link = st.text_input("Source URL (optional, http/https only)")
            submitted = st.form_submit_button("＋ Add custom food")
        if submitted:
            if not name.strip():
                st.error("Enter a food name.")
            elif source_link and not source_link.startswith(("https://", "http://")):
                st.error("Only http/https source URLs are supported.")
            elif len(name) > 160:
                st.error("Please shorten the food name.")
            else:
                add_food({"name": name.strip(), "calories": cal, "protein": pro,
                          "carbs": carb, "fat": fat, "status": "User entered",
                          "source_url": source_link}, grams)

    st.divider()
    subsection("Your meal", "Calculated from grams entered for each ingredient, not a photo estimate.")
    meal = st.session_state.meal
    if not meal:
        st.info("Your meal is empty. Choose a food above and add a serving.")
        return
    totals = meal_totals(meal)
    metric_row(totals["calories"], totals["protein"], totals["carbs"], totals["fat"])
    table = pd.DataFrame([{
        "Food": item["name"],
        "Serving (g)": round(item["grams"], 1),
        "Calories (kcal)": round(item["calories"], 1),
        "Protein (g)": round(item["protein"], 1),
        "Carbs (g)": round(item["carbs"], 1),
        "Fat (g)": round(item["fat"], 1),
        "Data status": item["origin"],
        "Source": item["source"],
    } for item in meal])
    st.dataframe(table, use_container_width=True, hide_index=True,
                 column_config={"Source": st.column_config.LinkColumn("Source / lookup")})
    col_a, col_b, col_c = st.columns([1.6, 1, 1.2])
    with col_a:
        selected_remove = st.selectbox(
            "Select one entry to remove",
            range(len(meal)),
            format_func=lambda i: f"{i+1}. {meal[i]['name']} · {meal[i]['grams']:.0f}g",
        )
    with col_b:
        st.write("")
        st.write("")
        if st.button("Remove selected", use_container_width=True):
            st.session_state.meal.pop(selected_remove)
            st.rerun()
    with col_c:
        st.write("")
        st.write("")
        if st.button("Clear entire meal", use_container_width=True):
            st.session_state.meal = []
            st.rerun()
    st.download_button("⬇️ Export meal as CSV", data=table.to_csv(index=False),
                       file_name="nutritimbang_meal.csv", mime="text/csv")
    if st.session_state.targets:
        targets = st.session_state.targets
        st.markdown("#### Your progress against estimated daily targets")
        calorie_frac = min(max(totals["calories"] / max(targets["calorie_target"], 1), 0), 1)
        protein_frac = min(max(totals["protein"] / max(targets["protein_target"], 1), 0), 1)
        st.caption(f"Calories: {totals['calories']:.0f} / {targets['calorie_target']:.0f} kcal")
        st.progress(calorie_frac)
        st.caption(f"Protein: {totals['protein']:.1f} / {targets['protein_target']:.0f} g")
        st.progress(protein_frac)
        st.caption("Progress is capped visually at 100%; a higher intake may still be shown in totals above.")


def fitness_calculator() -> None:
    subsection("Personal nutrition targets", "Estimate daily calories and a protein range for different fitness goals. Adults 18+ only.")
    with st.form("targets_form"):
        c1, c2, c3 = st.columns(3)
        weight = c1.number_input("Body weight (kg)", 20.0, 350.0, 70.0, 0.5)
        height = c2.number_input("Height (cm)", 100.0, 230.0, 170.0, 1.0)
        age = c3.number_input("Age (years)", 18, 100, 25, 1)
        d1, d2 = st.columns(2)
        equation = d1.selectbox("Mifflin–St Jeor equation", ["Male", "Female"],
                                help="The published equation uses different constants for males and females; estimates are imperfect for individuals.")
        activity_map = {
            "Sedentary (×1.20)": 1.20,
            "Lightly active (×1.375)": 1.375,
            "Moderately active (×1.55)": 1.55,
            "Very active (×1.725)": 1.725,
            "Extremely active (×1.90)": 1.90,
        }
        activity = d2.selectbox("Activity level", list(activity_map), index=2)
        goal = st.selectbox("Your goal", ["Maintenance", "Cutting", "Lean bulk", "Bulking"], index=2)
        done = st.form_submit_button("Calculate my targets", type="primary")
    if done:
        try:
            st.session_state.targets = calculate_targets(
                float(weight), float(height), int(age), equation, activity_map[activity], goal
            )
            st.session_state.goal_label = goal
            st.session_state.calculator_inputs = (weight, height, age, equation, activity, activity_map[activity], goal)
        except ValueError as exc:
            st.error(str(exc))
    targets = st.session_state.targets
    if not targets:
        st.info("Fill out the form and click Calculate my targets.")
        return
    st.markdown("#### Estimated daily intake")
    a, b, c = st.columns(3)
    a.metric("Maintenance energy", f"{targets['tdee']:,.0f} kcal/day")
    b.metric("Suggested calorie range", f"{targets['calorie_min']:,.0f}–{targets['calorie_max']:,.0f}")
    c.metric("Suggested protein range", f"{targets['protein_min']:,.0f}–{targets['protein_max']:,.0f} g")
    with st.expander("See exactly how we calculated these targets", expanded=True):
        input_weight, input_height, input_age, input_equation, input_activity, input_multiplier, input_goal = st.session_state.calculator_inputs
        correction = "+ 5" if input_equation == "Male" else "− 161"
        cmin, cmax = targets["calorie_factors"]
        pmin, pmax = targets["protein_factors"]
        st.markdown(
            f"**Mifflin–St Jeor:** `10 × {input_weight:g} + 6.25 × {input_height:g} − 5 × {input_age} {correction}` "
            f"= **{targets['bmr']:.0f} kcal/day** (estimated resting energy).\n\n"
            f"**Maintenance:** `{targets['bmr']:.0f} × {input_multiplier:g}` = **{targets['tdee']:.0f} kcal/day**.\n\n"
            f"**{input_goal} calorie band:** `TDEE × {cmin:.2f} to {cmax:.2f}`.\n\n"
            f"**Protein band:** `{input_weight:g} kg × {pmin:.1f} to {pmax:.1f} g/kg` per day."
        )
    st.warning("Estimates are not minimum safe calorie requirements or medical prescriptions. "
               "Activity multipliers and goal adjustments are general assumptions. "
               "If you're underweight, pregnant/breastfeeding, under 18, have a medical condition, or a history of disordered eating, seek individualized advice.")
    st.caption("Evidence: Mifflin et al. 1990 (PubMed 2305711); International Society of Sports Nutrition protein position stand (2017). See Sources.")


def sources() -> None:
    subsection("Data sources & credits", "Each curated offline food and official live USDA food links to a unique FDC record.")
    st.markdown("""
**USDA FoodData Central — curated offline and live searchable records**  
[FoodData Central](https://fdc.nal.usda.gov/food-search) · [API guide](https://fdc.nal.usda.gov/api-guide/) · [API key](https://fdc.nal.usda.gov/api-key-signup/)  
U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. Data are published under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

**DOST–FNRI Philippine Food Composition Tables (PhilFCT®)**  
[Official Philippine food database](https://i.fnri.dost.gov.ph/login/fct)  
Published by the Department of Science and Technology – Food and Nutrition Research Institute. The app links to this reference but **does not reproduce or claim to license PhilFCT's database, logo, or content**. Ask FNRI for permission before incorporating bulk data or logos.

**Philippine Department of Health (DOH)**  
[DOH official website](https://doh.gov.ph/)  
A public-health reference, **not the attributed source of the starter CSV**. The official Philippine food-composition resource above is from DOST–FNRI.

**Fitness calculations and protein recommendations**  
[Mifflin–St Jeor research paper](https://pubmed.ncbi.nlm.nih.gov/2305711/) · [ISSN protein position stand](https://pubmed.ncbi.nlm.nih.gov/28642676/) · [NIH/NIDDK adult body weight planner](https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner)

**Offline food library (v2)**  
The default `foods.csv` contains **26 USDA SR Legacy-associated entries**, each with its specific FoodData Central ID, detailed food description and official link. The rounded macronutrients were cross-checked against public USDA-derived listings; we did **not** download USDA's full official archive directly when preparing this package. Confirm the original linked record for high-stakes use. USDA's SR Legacy is a 2018 final release, so it is not newly sampled 2026 nutrition data. [USDA downloadable datasets](https://fdc.nal.usda.gov/download-datasets/).

**Previous sample estimates, optional**  
The old 58 entries now live in `foods_estimates.csv`. They are **not individual USDA or DOST–FNRI-backed records**, are hidden by default, and become visible only if you check the explicit unverified-food option. Generic lookup-page links have been removed to avoid suggesting that they verify the numbers. Food names, ingredients, preparation and brand affect actual nutrition.

**Affiliation and logos**  
NutriTimbang is an independent learning project. USDA, DOH, and DOST–FNRI do **not** sponsor, certify or endorse this app. Their official logos are not used.
""")


def nutrition_page() -> None:
    st.markdown('<div class="smallcaps">NUTRITION / EAT WELL</div>', unsafe_allow_html=True)
    st.title("🥗 Food & Nutrition")
    show_estimates = st.checkbox(
        "Also show 58 unverified sample foods (not source-backed)",
        value=False,
        help="Default: 26 USDA-indexed food references. If enabled, older approximate values are also offered and labelled as estimates.",
    )
    foods = load_foods(show_estimates)
    tabs = st.tabs(["🍽️ Meal builder", "📚 Food library", "🎯 My targets", "🔗 Sources & credits"])
    st.caption(f"Offline foods available: {len(foods)} · "
               "No API key is needed for the offline foods or workout guide.")
    with tabs[0]:
        meal_builder(foods)
    with tabs[1]:
        food_library(foods)
    with tabs[2]:
        fitness_calculator()
    with tabs[3]:
        sources()


def workout_page() -> None:
    st.markdown('<div class="smallcaps">FITNESS / TRAIN SMART</div>', unsafe_allow_html=True)
    st.title("🏋️ Workout Guide")
    st.markdown('<div class="section-intro">Choose a split, explore the week, then open each day for the full workout routine.</div>',
                unsafe_allow_html=True)
    split_name = st.selectbox("Choose your workout split", list(SPLITS), key="workout_split")
    selected = SPLITS[split_name]
    st.info(selected["summary"])
    schedule = selected["schedule"]
    training_days = sum(bool(steps) for _, _, steps in schedule)
    a, b, c = st.columns(3)
    a.metric("Training days / week", training_days)
    b.metric("Rest / recovery days", 7 - training_days)
    c.metric("Sample program", "1 week")
    st.markdown("#### Weekly schedule")
    week_frame = pd.DataFrame([{"Day": d, "Session": s, "Type": "Training" if ex else "Recovery"}
                               for d, s, ex in schedule])
    st.dataframe(week_frame, hide_index=True, use_container_width=True)
    st.markdown("#### Day-by-day sessions")
    for day, name, exercises in schedule:
        with st.expander(f"{day}  ·  {name}" + (f"  ·  {len(exercises)} exercises" if exercises else ""),
                         expanded=(day == "Monday")):
            if not exercises:
                st.markdown("**Recovery day.** Walk, do comfortable mobility work, or rest fully if needed.")
                continue
            table = pd.DataFrame(exercises, columns=["Exercise", "Sets", "Reps", "Rest", "Focus"])
            st.dataframe(table, hide_index=True, use_container_width=True)
            flag = f"{split_name}:{day}"
            checked = st.checkbox("I completed this workout", key=f"complete:{flag}")
            st.session_state.completed_workouts[flag] = checked
    progress = sum(bool(st.session_state.completed_workouts.get(f"{split_name}:{day}", False))
                   for day, _, exercises in schedule if exercises)
    st.caption(f"Workout days completed this session: {progress} / {training_days}")
    st.progress(min(progress / max(training_days, 1), 1.0))
    st.download_button("⬇️ Download weekly schedule (CSV)", week_frame.to_csv(index=False),
                       file_name="nutritimbang_workout_week.csv", mime="text/csv")
    with st.expander("How to follow the program safely", expanded=True):
        st.markdown("""
- Begin with 5–10 minutes of easy movement and warm-up sets before challenging lifts.
- Choose loads you can control with good form. A practical starting point is to stop with 1–3 reps still possible.
- Add reps or small amounts of weight as movements become comfortable; don't chase weight at the expense of technique.
- The exercises and volumes are **sample templates**, not personalized prescriptions. Beginners can start with fewer sets and fewer weekly days.
- Swap exercises when equipment is unavailable. Stop if you feel sharp pain, dizziness, or unusual symptoms.
- Sleep, nutrition, and rest days matter. A qualified coach or clinician can help adapt exercises for injuries or conditions.
""")


def main() -> None:
    ensure_state()
    left, right = st.columns([1, 2])
    with left:
        st.markdown("### 🥬 NutriTimbang")
    with right:
        st.segmented_control(
            "Main navigation",
            options=["🏠 Home", "🥗 Food & Nutrition", "🏋️ Workout Guide"],
            key="page",
            label_visibility="collapsed",
        )
    if st.session_state.page == "🥗 Food & Nutrition":
        nutrition_page()
    elif st.session_state.page == "🏋️ Workout Guide":
        workout_page()
    else:
        home()
    st.divider()
    st.caption("NutriTimbang · Independent educational app · Nutrition and exercise guidance are estimates, not medical advice. "
               "Meal entries and workout checkmarks are held only in your current Streamlit session.")


if __name__ == "__main__":
    main()
