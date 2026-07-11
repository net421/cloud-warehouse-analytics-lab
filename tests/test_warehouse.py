from pathlib import Path
import sys

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.generate_synthetic_data import generate
from duckdb_local_simulator.build_warehouse import build_warehouse
from validation.validate_duckdb_outputs import validate_outputs


@pytest.fixture(scope="module")
def generated_source(tmp_path_factory: pytest.TempPathFactory) -> Path:
    source_dir = tmp_path_factory.mktemp("source")
    generate(source_dir)
    return source_dir


def test_build_and_quality_gates(tmp_path: Path, generated_source: Path) -> None:
    database = build_warehouse(
        generated_source,
        tmp_path / "outputs",
        tmp_path / "warehouse.duckdb",
    )
    with duckdb.connect(str(database), read_only=True) as connection:
        failures = connection.execute(
            "select count(*) from quality.data_quality_report where status <> 'PASS'"
        ).fetchone()[0]
        order_count = connection.execute(
            "select count(*) from analytics.mart_order_fulfillment"
        ).fetchone()[0]
    assert failures == 0
    assert order_count == 2400


def test_exported_outputs(tmp_path: Path, generated_source: Path) -> None:
    output_dir = tmp_path / "outputs"
    build_warehouse(generated_source, output_dir, tmp_path / "warehouse.duckdb")
    assert all(result[1] for result in validate_outputs(output_dir))
    detail = pd.read_csv(output_dir / "mart_order_fulfillment.csv")
    assert detail["order_id"].is_unique
    assert detail["unit_fill_rate"].between(0, 1).all()


def test_exports_are_byte_reproducible(
    tmp_path: Path,
    generated_source: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    build_warehouse(generated_source, first, tmp_path / "first.duckdb")
    build_warehouse(generated_source, second, tmp_path / "second.duckdb")

    first_files = sorted(path.name for path in first.glob("*.csv"))
    second_files = sorted(path.name for path in second.glob("*.csv"))
    assert first_files == second_files
    for filename in first_files:
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
