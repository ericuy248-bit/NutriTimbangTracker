"""Pure nutrition calculations and USDA FoodData Central adapters.

Nutrition amounts in FDC Foundation/SR Legacy/FNDDS are per 100 g. This
module deliberately excludes Branded foods to avoid serving-size ambiguity.
"""
from __future__ import annotations

from typing import Any

import requests

FDC_URL = "https://api.nal.usda.gov/fdc/v1"
USDA_INFO = "https://fdc.nal.usda.gov/api-guide/"
NUTRIENT_IDS = {
    "protein": (1003,),
    "fat": (1004,),
    "carbs": (1005,),
    "calories": (1008, 2047, 2048),
}


def scale_nutrition(food: dict, grams: float) -> dict:
    """Scale a food's per-100-g macronutrients to the weighed portion."""
    if grams < 0:
        raise ValueError("Weight must not be negative")
    result = {"grams": float(grams)}
    for field in ("calories", "protein", "carbs", "fat"):
        result[field] = float(food.get(field) or 0) * float(grams) / 100
    return result


def meal_totals(items: list[dict]) -> dict:
    return {
        k: sum(float(item.get(k, 0) or 0) for item in items)
        for k in ("grams", "calories", "protein", "carbs", "fat")
    }


def calculate_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    equation: str,
    activity_multiplier: float,
    goal: str,
) -> dict:
    """Mifflin–St Jeor estimate for nonpregnant adults + sample goal bands.

    Goal multipliers are practical app assumptions, not clinical prescriptions.
    """
    if not (weight_kg > 0 and height_cm > 0 and age >= 18):
        raise ValueError("Enter valid adult age, height, and weight")
    if equation not in ("Male", "Female"):
        raise ValueError("Choose an equation")
    if activity_multiplier < 1.0 or activity_multiplier > 2.5:
        raise ValueError("Invalid activity multiplier")
    factors = {
        "Maintenance": ((0.95, 1.05), (1.4, 2.0)),
        "Cutting": ((0.80, 0.90), (1.6, 2.2)),
        "Lean bulk": ((1.05, 1.10), (1.6, 2.2)),
        "Bulking": ((1.10, 1.20), (1.4, 2.0)),
    }
    if goal not in factors:
        raise ValueError("Unknown goal")
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if equation == "Male" else -161)
    tdee = bmr * activity_multiplier
    energy_bounds, protein_bounds = factors[goal]
    return {
        "bmr": bmr,
        "tdee": tdee,
        "calorie_min": tdee * energy_bounds[0],
        "calorie_max": tdee * energy_bounds[1],
        "calorie_target": tdee * sum(energy_bounds) / 2,
        "protein_min": weight_kg * protein_bounds[0],
        "protein_max": weight_kg * protein_bounds[1],
        "protein_target": weight_kg * sum(protein_bounds) / 2,
        "calorie_factors": energy_bounds,
        "protein_factors": protein_bounds,
    }


def _nutrient_amounts(payload: dict) -> dict[int, float]:
    """Handle both FDC full-detail and abridged/search nutrient shapes."""
    nutrients: dict[int, float] = {}
    for record in payload.get("foodNutrients", []) or []:
        if not isinstance(record, dict):
            continue
        info = record.get("nutrient") or {}
        nutrient_id = info.get("id") or record.get("nutrientId")
        try:
            nutrient_id = int(nutrient_id)
        except (TypeError, ValueError):
            continue
        value = record.get("amount")
        if value is None:
            value = record.get("value")
        if value is None:
            continue
        try:
            number = float(value)
        except (ValueError, TypeError):
            continue
        if nutrient_id not in nutrients:
            nutrients[nutrient_id] = number
    return nutrients


def normalize_usda_food(payload: dict) -> dict:
    """Convert a detailed USDA food item to a uniform per-100-g record."""
    fdc_id = payload.get("fdcId")
    if not fdc_id:
        raise ValueError("USDA response did not include an FDC ID")
    dtype = payload.get("dataType", "")
    if dtype not in ("Foundation", "SR Legacy", "Survey (FNDDS)"):
        raise ValueError("Only per-100-gram USDA Foundation, SR Legacy, and FNDDS foods are supported")
    values = _nutrient_amounts(payload)
    result = {
        "id": f"usda:{fdc_id}",
        "name": payload.get("description", f"USDA food {fdc_id}"),
        "category": dtype,
        "source_name": f"USDA FoodData Central ({dtype})",
        "source_url": f"https://fdc.nal.usda.gov/food-details/{fdc_id}/nutrients",
        "status": "USDA record",
    }
    for field, priority_ids in NUTRIENT_IDS.items():
        value = next((values[n] for n in priority_ids if n in values), None)
        # None is distinct from 0: some records omit a nutrient completely.
        result[field] = value
    # USDA sometimes has no explicit energy entry. Avoid claiming a precise
    # derived figure when the food record doesn't provide one.
    result["missing_fields"] = [
        name for name in ("calories", "protein", "carbs", "fat") if result[name] is None
    ]
    return result


def search_usda(query: str, api_key: str = "DEMO_KEY", page_size: int = 15) -> list[dict]:
    """Official FDC food search. Caller should cache responses in Streamlit."""
    if not query.strip():
        return []
    response = requests.post(
        f"{FDC_URL}/foods/search",
        params={"api_key": api_key},
        json={
            "query": query.strip(),
            "pageSize": min(max(page_size, 1), 30),
            "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
        },
        timeout=18,
    )
    response.raise_for_status()
    records = response.json().get("foods", [])
    return [f for f in records if f.get("fdcId") and f.get("dataType") in
            ("Foundation", "SR Legacy", "Survey (FNDDS)")]


def fetch_usda_food(fdc_id: int, api_key: str = "DEMO_KEY") -> dict:
    response = requests.get(
        f"{FDC_URL}/food/{int(fdc_id)}",
        params={"api_key": api_key},
        timeout=18,
    )
    response.raise_for_status()
    return normalize_usda_food(response.json())
