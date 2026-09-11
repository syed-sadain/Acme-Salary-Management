import pytest

from app import crud


def test_group_salary_stats_raises_on_mixed_currency_within_a_group():
    rows = [("India", 1_000_000, "INR"), ("India", 80_000, "USD")]
    with pytest.raises(ValueError):
        crud._group_salary_stats(rows)


def test_group_salary_stats_handles_single_currency_group():
    rows = [("India", 1_000_000, "INR"), ("India", 2_000_000, "INR")]
    result = crud._group_salary_stats(rows)
    assert len(result) == 1
    assert result[0].avg_salary == 1_500_000
    assert result[0].currency == "INR"


def test_group_pay_index_stats_is_currency_agnostic():
    rows = [("Engineering", 1.0), ("Engineering", 3.0)]
    result = crud._group_pay_index_stats(rows)
    assert result[0].avg_pay_index == 2.0
    assert result[0].median_pay_index == 2.0


def test_build_histogram_handles_empty_input():
    assert crud._build_histogram([]) == []


def test_build_histogram_handles_degenerate_single_value():
    # All identical values shouldn't produce a zero-width bucket / division by zero.
    buckets = crud._build_histogram([5.0, 5.0, 5.0], num_buckets=4)
    assert sum(b.count for b in buckets) == 3


def test_build_histogram_distributes_values_across_buckets():
    values = list(range(10))  # 0..9
    buckets = crud._build_histogram([float(v) for v in values], num_buckets=5)
    assert len(buckets) == 5
    assert sum(b.count for b in buckets) == 10
