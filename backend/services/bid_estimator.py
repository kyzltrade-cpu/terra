ISSA_PRODUCTION_RATES = {
    "carpet": 10000,
    "terrazzo": 12000,
    "tile": 8000,
    "hardwood": 9000,
    "restroom": 1500,
}


def calculate_issa_labor_hours(floor_type: str, square_footage: int) -> float:
    rate = ISSA_PRODUCTION_RATES.get(floor_type.lower(), 5000)
    return round(float(square_footage) / rate, 2)
