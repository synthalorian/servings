"""Scale one ingredient line."""

from decimal import ROUND_HALF_UP, Decimal

STAPLES_G_PER_CUP = {
    "flour": 120,
    "sugar": 200,
    "butter": 227,
    "rice": 185,
    "milk": 240,
    "water": 240,
}

UNITS = frozenset({"cup", "cups", "tbsp", "tsp", "g"})

_TWO_PLACES = Decimal("0.01")
_ONE = Decimal("1")


class LineError(ValueError):
    """An ingredient line cannot be scaled."""


def parse_quantity(token):
    sign = ""
    body = token
    if body[:1] in "+-":
        sign, body = body[0], body[1:]
    if not body or body.count(".") > 1:
        raise LineError("bad line")
    whole, sep, frac = body.partition(".")
    if sep:
        if not whole and not frac:
            raise LineError("bad line")
        if whole and not whole.isdigit():
            raise LineError("bad line")
        if frac and not frac.isdigit():
            raise LineError("bad line")
    elif not whole.isdigit():
        raise LineError("bad line")
    return Decimal(sign + body)


def parse_line(line):
    stripped = line.strip()
    if not stripped:
        raise LineError("bad line")
    parts = stripped.split(None, 2)
    if len(parts) != 3:
        raise LineError("bad line")
    quantity_token, unit, name = parts
    if unit not in UNITS:
        raise LineError("unknown unit")
    return parse_quantity(quantity_token), unit, name


def format_quantity(value):
    rounded = value.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    if rounded == 0:
        return "0"
    text = format(rounded, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def output_unit(unit, scaled):
    if unit not in ("cup", "cups"):
        return unit
    rounded = scaled.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    if rounded == 1:
        return "cup"
    return "cups"


def grams_suffix(unit, name, scaled):
    if unit not in ("cup", "cups"):
        return ""
    grams_per_cup = STAPLES_G_PER_CUP.get(name.casefold())
    if grams_per_cup is None:
        return ""
    grams = (scaled * Decimal(grams_per_cup)).quantize(_ONE, rounding=ROUND_HALF_UP)
    return f" ({int(grams)} g)"


def scale_line(line, from_servings, to_servings):
    quantity, unit, name = parse_line(line)
    scaled = quantity * to_servings / from_servings
    rendered = format_quantity(scaled)
    return f"{rendered} {output_unit(unit, scaled)} {name}{grams_suffix(unit, name, scaled)}"
