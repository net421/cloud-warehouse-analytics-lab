# Snowflake-Style Warehouse Design

## Conceptual Architecture

- Raw zone: source-aligned landing tables.
- Clean zone: typed, deduplicated and standardized tables.
- Mart zone: fact and dimension tables for BI.
- Access model: analyst role reads marts; engineering role maintains transformations; admin owns warehouse configuration.

## Demonstrated Concepts

- Separation of storage and compute.
- Role-based access model.
- Warehouse sizing considerations.
- Mart-first consumption layer.
