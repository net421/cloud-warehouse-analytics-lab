# Package notes — Run 003

Converted the repository from conceptual scaffolding into an executable local warehouse plus cloud-specific SQL patterns.

## Suggested commit

```text
Add executable cross-platform cloud warehouse lab
```

## Validation

- executable DuckDB build;
- nine in-database checks;
- six exported-output checks;
- three pytest tests including byte-for-byte reproducibility;
- clean-checkout generation and byte-for-byte export reproducibility.


## Executed result summary

- Order-grain mart rows: 2,400
- Average order fill rate: 96.68%
- OTIF: 62.33%
- Carriers scored: 4
- In-database quality checks passed: 9 of 9
- Automated tests passed: 3
