"""Build the executable local analytical warehouse."""

from __future__ import annotations
import argparse
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "source"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
SQL_DIR = Path(__file__).resolve().parent / "sql"

SOURCE_FILES = {
    "customers":"customers.csv","suppliers