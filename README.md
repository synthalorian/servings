# servings

Scale a recipe and convert common staples to grams. The gram table is for staples, not for every ingredient.

Author: synthalorian

## Build

No build step. Python 3 standard library only.

## Test

```bash
python -m unittest discover -s tests
```

## Usage

Read ingredient lines on stdin. A line is `<quantity> <unit> <name...>`.

```bash
python -m servings scale --from 4 --to 6 <<'EOF'
2 cups flour
1 tsp salt
EOF
```

```text
3 cups flour (360 g)
1.5 tsp salt
```

`1 cup sugar` scaled from 2 to 1 prints `0.5 cups sugar (100 g)`.

`--from` must be greater than 0. A bad line, including an unknown unit, exits 2 and names the line number on stderr.

Units are `cup`, `cups`, `tbsp`, `tsp`, and `g`. Cup amounts of flour, sugar, butter, rice, milk, and water also print grams. The staple name must match exactly, ignoring case.
