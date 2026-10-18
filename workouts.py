"""Editable sample workout templates. Not a replacement for individual coaching."""

# Tuple: exercise, working sets, rep target, rest between sets, primary area.
PUSH_A = [
    ("Barbell bench press", 3, "6–10", "2–3 min", "Chest"),
    ("Incline dumbbell press", 3, "8–12", "2 min", "Upper chest"),
    ("Seated shoulder press", 3, "8–12", "2 min", "Shoulders"),
    ("Lateral raise", 3, "12–20", "60–90 sec", "Side delts"),
    ("Triceps cable pushdown", 3, "10–15", "60–90 sec", "Triceps"),
]
PUSH_B = [
    ("Incline bench press", 3, "6–10", "2–3 min", "Upper chest"),
    ("Machine chest press", 3, "8–12", "2 min", "Chest"),
    ("Dumbbell shoulder press", 3, "8–12", "2 min", "Shoulders"),
    ("Cable lateral raise", 3, "12–20", "60–90 sec", "Side delts"),
    ("Overhead triceps extension", 3, "10–15", "60–90 sec", "Triceps"),
]
PULL_A = [
    ("Lat pulldown or assisted pull-up", 3, "8–12", "2 min", "Lats"),
    ("Chest-supported row", 3, "8–12", "2 min", "Mid back"),
    ("Seated cable row", 2, "10–12", "90 sec", "Back"),
    ("Reverse pec deck", 3, "12–20", "60–90 sec", "Rear delts"),
    ("Dumbbell biceps curl", 3, "8–12", "60–90 sec", "Biceps"),
]
PULL_B = [
    ("Pull-up or pulldown", 3, "6–10", "2 min", "Lats"),
    ("One-arm dumbbell row", 3, "8–12", "2 min", "Back"),
    ("Face pull", 3, "12–20", "60–90 sec", "Rear delts"),
    ("Hammer curl", 3, "10–15", "60–90 sec", "Brachialis"),
    ("Preacher curl", 2, "10–15", "60–90 sec", "Biceps"),
]
LEGS_A = [
    ("Squat or goblet squat", 3, "6–10", "2–3 min", "Quads / glutes"),
    ("Romanian deadlift", 3, "8–12", "2 min", "Hamstrings"),
    ("Leg press", 3, "10–15", "2 min", "Quads"),
    ("Leg curl", 3, "10–15", "90 sec", "Hamstrings"),
    ("Standing calf raise", 3, "10–20", "60–90 sec", "Calves"),
]
LEGS_B = [
    ("Hack squat or split squat", 3, "8–12", "2 min", "Quads"),
    ("Hip thrust", 3, "8–12", "2 min", "Glutes"),
    ("Leg extension", 3, "10–15", "90 sec", "Quads"),
    ("Seated leg curl", 3, "10–15", "90 sec", "Hamstrings"),
    ("Seated calf raise", 3, "12–20", "60–90 sec", "Calves"),
]
UPPER_A = [
    ("Bench press", 3, "6–10", "2–3 min", "Chest"),
    ("Lat pulldown", 3, "8–12", "2 min", "Lats"),
    ("Incline dumbbell press", 2, "8–12", "2 min", "Upper chest"),
    ("Chest-supported row", 3, "8–12", "2 min", "Back"),
    ("Lateral raise", 3, "12–20", "60 sec", "Side delts"),
    ("Cable triceps pushdown", 2, "10–15", "60 sec", "Triceps"),
    ("Dumbbell curl", 2, "10–15", "60 sec", "Biceps"),
]
UPPER_B = [
    ("Overhead press", 3, "6–10", "2 min", "Shoulders"),
    ("Pull-up or pulldown", 3, "8–12", "2 min", "Lats"),
    ("Machine chest press", 3, "8–12", "2 min", "Chest"),
    ("Seated row", 3, "8–12", "2 min", "Back"),
    ("Reverse pec deck", 3, "12–20", "60 sec", "Rear delts"),
    ("Overhead triceps extension", 2, "10–15", "60 sec", "Triceps"),
    ("Hammer curl", 2, "10–15", "60 sec", "Biceps"),
]
ARNOLD_CP_A = [
    ("Flat bench press", 3, "6–10", "2–3 min", "Chest"),
    ("Incline dumbbell press", 3, "8–12", "2 min", "Chest"),
    ("Pulldown", 3, "8–12", "2 min", "Back"),
    ("Cable row", 3, "8–12", "2 min", "Back"),
    ("Cable chest fly", 2, "12–15", "60 sec", "Chest"),
]
ARNOLD_CP_B = [
    ("Incline bench press", 3, "6–10", "2–3 min", "Chest"),
    ("Machine chest press", 2, "10–12", "2 min", "Chest"),
    ("Pull-up / assisted pull-up", 3, "8–12", "2 min", "Back"),
    ("One-arm row", 3, "8–12", "2 min", "Back"),
    ("Face pull", 2, "12–20", "60 sec", "Rear delts"),
]
ARNOLD_SA_A = [
    ("Seated shoulder press", 3, "8–12", "2 min", "Shoulders"),
    ("Lateral raise", 3, "12–20", "60 sec", "Shoulders"),
    ("Reverse fly", 3, "12–20", "60 sec", "Rear delts"),
    ("Barbell curl", 3, "8–12", "60–90 sec", "Biceps"),
    ("Overhead triceps extension", 3, "10–15", "60–90 sec", "Triceps"),
]
ARNOLD_SA_B = [
    ("Dumbbell shoulder press", 3, "8–12", "2 min", "Shoulders"),
    ("Cable lateral raise", 3, "12–20", "60 sec", "Shoulders"),
    ("Face pull", 3, "12–20", "60 sec", "Rear delts"),
    ("Hammer curl", 3, "10–12", "60–90 sec", "Biceps"),
    ("Triceps rope pushdown", 3, "10–15", "60–90 sec", "Triceps"),
]
FULL_A = [
    ("Goblet squat", 3, "8–12", "2 min", "Legs"),
    ("Push-up or bench press", 3, "8–12", "2 min", "Chest"),
    ("Lat pulldown", 3, "8–12", "2 min", "Back"),
    ("Romanian deadlift", 2, "8–12", "2 min", "Hamstrings"),
    ("Plank", 2, "20–45 sec", "60 sec", "Core"),
]
FULL_B = [
    ("Leg press", 3, "10–12", "2 min", "Legs"),
    ("Dumbbell shoulder press", 3, "8–12", "2 min", "Shoulders"),
    ("Seated row", 3, "8–12", "2 min", "Back"),
    ("Leg curl", 2, "10–15", "90 sec", "Hamstrings"),
    ("Dead bug", 2, "8–12/side", "60 sec", "Core"),
]
FULL_C = [
    ("Split squat", 3, "8–12/side", "2 min", "Legs"),
    ("Incline dumbbell press", 3, "8–12", "2 min", "Chest"),
    ("Assisted pull-up", 3, "6–10", "2 min", "Back"),
    ("Hip thrust", 2, "10–15", "90 sec", "Glutes"),
    ("Side plank", 2, "20–40 sec/side", "60 sec", "Core"),
]

SPLITS = {
    "Upper / Lower (4 days)": {
        "summary": "Balanced four-day split with two upper-body and two lower-body sessions.",
        "schedule": [
            ("Monday", "Upper A", UPPER_A),
            ("Tuesday", "Lower A", LEGS_A),
            ("Wednesday", "Recovery", []),
            ("Thursday", "Upper B", UPPER_B),
            ("Friday", "Lower B", LEGS_B),
            ("Saturday", "Rest / easy cardio", []),
            ("Sunday", "Rest", []),
        ],
    },
    "Push / Pull / Legs (6 days)": {
        "summary": "Two rotations of push, pull, and legs; higher weekly time demand.",
        "schedule": [
            ("Monday", "Push A", PUSH_A),
            ("Tuesday", "Pull A", PULL_A),
            ("Wednesday", "Legs A", LEGS_A),
            ("Thursday", "Rest", []),
            ("Friday", "Push B", PUSH_B),
            ("Saturday", "Pull B", PULL_B),
            ("Sunday", "Legs B", LEGS_B),
        ],
    },
    "Arnold Split (6 days)": {
        "summary": "Chest/back, shoulders/arms, and legs, repeated twice weekly.",
        "schedule": [
            ("Monday", "Chest + Back A", ARNOLD_CP_A),
            ("Tuesday", "Shoulders + Arms A", ARNOLD_SA_A),
            ("Wednesday", "Legs A", LEGS_A),
            ("Thursday", "Rest", []),
            ("Friday", "Chest + Back B", ARNOLD_CP_B),
            ("Saturday", "Shoulders + Arms B", ARNOLD_SA_B),
            ("Sunday", "Legs B", LEGS_B),
        ],
    },
    "Hybrid PPL + Upper/Lower (5 days)": {
        "summary": "Three PPL days plus two upper/lower days for a five-day hybrid.",
        "schedule": [
            ("Monday", "Push", PUSH_A),
            ("Tuesday", "Pull", PULL_A),
            ("Wednesday", "Legs", LEGS_A),
            ("Thursday", "Rest", []),
            ("Friday", "Upper", UPPER_B),
            ("Saturday", "Lower", LEGS_B),
            ("Sunday", "Rest", []),
        ],
    },
    "Full Body (3 days)": {
        "summary": "Beginner-friendly three-day template with rest days between workouts.",
        "schedule": [
            ("Monday", "Full Body A", FULL_A),
            ("Tuesday", "Recovery", []),
            ("Wednesday", "Full Body B", FULL_B),
            ("Thursday", "Recovery", []),
            ("Friday", "Full Body C", FULL_C),
            ("Saturday", "Rest", []),
            ("Sunday", "Rest", []),
        ],
    },
}
