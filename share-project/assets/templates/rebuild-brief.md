# Rebuild: {{project name}}

The promise is a working equivalent of the main flows, not an identical copy.

## What it does

{{One paragraph in plain words.}}

### Observed behaviour

- {{What the original does today, read from the code and the owner. Each item cites a file in project/.}}

### Intended behaviour (confirmed by the owner)

- {{What the owner says it should do, where that differs from or adds to the observed behaviour.}}

### Known problems not to copy

- {{Defects the owner or the reading found; "none known" if none.}}

### Unknowns

- {{What could not be established, and what would settle it.}}

## Exact rules

| Rule | Exact value or formula | Where it comes from | How sure |
|---|---|---|---|
| {{rounding, threshold, default, unit, date grouping, formula}} | {{exact}} | {{project/<file>: function or line}} | {{read from code / confirmed by owner / inferred}} |

## Checks that define done

| # | Input (invented) | Expected result | How the expected result was worked out | Run by the sender? |
|---|---|---|---|---|
| 1 | {{exact input or the stand-in file}} | {{exact output}} | {{independent calculation, not the original's output}} | not run |

Where the original's result differs from the intended one because of a known problem, give both and say which one a rebuild must match.

## Free choices

The receiver may choose any database, language and tools. Required: the behaviour and exact rules above. Free: {{storage, framework, layout details, hosting}}.

## About project/

`project/` is how the original did it. Use it for exact formulas and layout; you do not have to copy it. It is a cleaned copy: data files are stand-ins and keys are placeholders.

## Build order

1. {{First step}} — check: {{what to check}}
2. {{...}}
