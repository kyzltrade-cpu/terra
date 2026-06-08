from backend.services.bid_estimator import calculate_issa_labor_hours


def test_issa_estimation():
    hours = calculate_issa_labor_hours(floor_type="carpet", square_footage=10000)
    assert 0.8 <= hours <= 1.2
