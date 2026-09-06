# T-shirt back print — folded cross

Vector version of the folded-cross back print, traced from the raster original.

![preview](preview.png)

## Files

| File | Page / canvas | Use |
| --- | --- | --- |
| `tshirt-back-folded-cross.svg` | 909.82 × 1320 pt | Web, digital layout — keeps the original page position |
| `tshirt-back-folded-cross.pdf` | 909.82 × 1320 pt | Print, keeps the original page position |
| `tshirt-back-folded-cross.eps` | 909.82 × 1320 pt | Screen-print / older RIPs |
| `tshirt-back-folded-cross-trimmed.svg` | 441.91 × 596.27 pt | Artwork cropped to its own bounds — place and scale on the garment |
| `tshirt-back-folded-cross-trimmed.pdf` | 441.91 × 596.27 pt | Same, for print |
| `tshirt-back-folded-cross-trimmed.eps` | 441.91 × 596.27 pt | Same, for screen print |
| `preview.png` | 921 × 1243 px | Raster preview of the trimmed artwork only |
| `source-raster.pdf` | 909.82 × 1320 pt | The raster original this was traced from |

Artwork size in the trimmed files is 155.9 × 210.4 mm (6.14 × 8.28 in) — it is
vector, so scale it to whatever the print calls for.

All vector files are pure black fills (`#000000`) on a transparent background,
no strokes. The design is one connected outline network plus 14 solid dots,
80 contours and 13,086 curve segments in total.

## How it was traced

`source-raster.pdf` is a wrapper around a single 1668 × 2420 px JPEG (132 dpi,
grayscale line art, ~3 px strokes). It contains no vector data, so the outlines
were traced rather than extracted.

1. Extract the embedded JPEG from the PDF.
2. Upsample 6× with Lanczos and threshold at 50% grey, so the trace lands on
   sub-pixel edge positions instead of the source pixel grid.
3. Trace with potrace 1.16:
   `potrace -b {svg,pdf,eps} -r 792 -a 1.0 -O 0.2 -t 2 -u 10 [--tight]`

`-r 792` is 6 × the source's 132 dpi, which reproduces the original page size
exactly. `--tight` produces the trimmed variants.

The parameters were picked by rasterising each candidate back to the source
resolution and comparing against the original:

| Upsample | Soft IoU vs. original | Ink weight |
| --- | --- | --- |
| 3× | 0.954 | 1.0030 |
| 4× | 0.958 | 1.0023 |
| **6×** | **0.971** | **1.0022** |
| 8× | 0.969 | 1.0023 |

6× is the best of the four; 8× starts fitting JPEG ringing. Varying `-a`
(0.8–1.334) and `-O` (0.1–0.3) moved IoU by less than 0.001, so the defaults
were kept. Pre-blurring the bitmap cut node count ~10% but lost fidelity, so it
was not used. Ink weight 1.0022 means the traced artwork carries 0.2% more ink
than the original — stroke weight is preserved.

Tracing an anti-aliased 3 px stroke caps IoU well below 1.0 (half a pixel of
edge error on a 3 px line costs roughly 15%), so 0.971 is a close trace, not a
loose one. Side-by-side at 4× zoom, tapers, spike tips and dots all match.
