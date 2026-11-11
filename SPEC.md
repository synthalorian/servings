# servings

Python 3 stdlib only. No network.

## Test command

`python -m unittest discover -s tests`

## Command

`servings scale --from 4 --to 6` reads ingredient lines on stdin.

A line is `<quantity> <unit> <name...>`. Quantity is an integer or a decimal. Unit is one of `cup`, `cups`, `tbsp`, `tsp`, `g`. Name is the rest of the line.

Scaled quantity = quantity * to / from, printed with up to 2 decimal places and trailing zeros stripped. Keep the unit. If the unit is cup/cups and the name is in the staple table, append ` (N g)` where N is the scaled cups times grams-per-cup, rounded to the nearest integer. `1 cup` stays singular when the scaled quantity is 1, otherwise use `cups`.

Staple grams per cup:

- flour 120
- sugar 200
- butter 227
- rice 185
- milk 240
- water 240

Match staple names case-insensitively, exact name only. `all-purpose flour` does not match `flour`.

`--from` must be > 0. A bad line exits 2 and names the line number on stderr.

## Tests

`2 cups flour` from 4 to 6 becomes `3 cups flour (360 g)`. `1 cup sugar` from 2 to 1 becomes `0.5 cups sugar (100 g)`. An unknown unit exits 2.
