# OM — the pair, constructed

O and M as a pair, in a face built to carry the gold reference's character.
Nothing here is traced: every outline is straight lines, circular arcs and
splines whose tangents were chosen, so the curves are smooth because of how they
are defined rather than how hard they were filtered.

![preview](preview.png)

| File | What it is |
| --- | --- |
| `OberndorferOM-Regular.otf` | The font — installs, maps to O and M, sets and spaces |
| `OberndorferOM-Regular.woff2` | The same for the web, under 1 kB |
| `om-om.pdf` / `.svg` | The pair |
| `om-o.*`, `om-m.*` | Each letter on its own |
| `om-lockup-3mm/4mm/5mm.*` | Cross, O, M, cross — for the ring, at three sizes |
| `specimen.pdf` | Set in the font itself |

```sh
python3 scripts/om_mark.py assets/om-mark --cap-mm 3 --cap-mm 4 --cap-mm 5
```

## Why this was started over

Every earlier version derived the letters from the photograph and then tried to
clean up what the scan left behind — trace, smooth, trim, refit, symmetrise. That
cannot work, and the repeated dents were the proof. A dent in a casting is a
**low-frequency** deviation: smoothing follows it and curve fitting reproduces
it. Stacking more passes made each version slightly cleaner and still wrong,
because the method carried the scan's noise floor through to the output.

There is no sampled data in this pipeline at all. Dents are not filtered out —
they are impossible.

## What gives the letters their character

A plain Didone O and a plain slab M come out clean but generic, which was the
first mistake after the reset. The reference's interest lives in specific
features, so they are drawn deliberately:

- **The O's faceted flanks.** Each side runs dead straight for a stretch and
  meets its opposite number in a shallow vertex — a real straight line between
  two tangent points, not a curve that happens to flatten.
- **The O's waisted counter.** It pinches at half height. Built as a pair of
  vertical-tangent nodes with an S between them.
- **The M's bracketed slab serifs**, with the ends softly swollen — the bracket
  radius is what makes it read as Clarendon rather than a plain slab.
- **The M's thick-left, thin-right V**, from putting the inner apex right of
  centre.

## Deliberately not copied

Contrast is **lower** than the gold reference's. At three millimetres the thin
part of a high-contrast letter is the first thing to disappear, and this mark
has to survive being struck into metal. Fidelity to the photograph would be the
wrong call here.
