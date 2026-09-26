# PA & CO — website product images

Organised like a web shop: one folder per product, one sub-folder per colour.
Inside each colour folder the files are numbered in display order — `01-…` is always the
main (listing) image, followed by the gallery images.

```
01-briefcase/black/            9 images
02-document-folio/black/       7
03-watch-case/black/           8
04-pouch/black/                8
04-pouch/pink/                 7
05-jewellery-box/black/       10
06-mini-backpack/black/        9
06-mini-backpack/pink/         9
07-backpack/black/             9
07-backpack/blue/              9
07-backpack/green/             9
```

`_overview.jpg` shows every folder at a glance; `_backpacks_main.jpg` shows the backpack main images side by side.

## Main images (01)

- Briefcase, folio, watch case, pouch, jewellery box: `01-front` — straight front view.
- Mini backpack and backpack: `01-three-quarter` — a 3/4 view shows the volume, side zip and
  pocket while keeping the logo readable. Both backpacks face the same direction so they sit
  together cleanly in the collection grid. The front view follows as `02-front`.
- **Large backpack uses one photo, recoloured for each colour**, so switching colour on the
  product page changes only the colour — angle, size and position are identical:
  - Backpack: 3/4 from blue IMG_4711, front from blue IMG_4712; green and black are recoloured.
  - Leather, zip tape and stitching are recoloured; silver zips, pullers and the silver logo are kept.
- **Mini backpack uses real photos of each colour** (pink 4625 / 4641, black 4670 / 4668), chosen
  for the closest matching angle. Recolouring the pink photo could not reproduce the black
  patent leather's gloss, so the real black photos are used for their true shine.

## Gallery order

Backpacks (both sizes), same order for every colour:
`01 three-quarter · 02 front · 03 side · 04 back · 05 back three-quarter · 06 interior · 07–09 details`

Other products: front → angles → open/interior → close-up details.

## Look & specs

- Background: warm stone `#EDEAE4` with a soft contact shadow (benchmark: Hermès, Connolly,
  Métier, Valextra all use toned light greys/greiges rather than pure white). Set the theme's
  product-image background to `#EDEAE4` so images blend into the page.
- Close-up detail shots are full-bleed square crops (colour-balanced), like the benchmarks.
- 2048 × 2048 px (details: 1280 × 1280 native), sRGB JPEG quality 95, no chroma subsampling.
- Source photos in the Drive folder are 1920 × 1280. To stay sharp, products are never enlarged
  more than 1.5× — small items (e.g. the watch case) sit slightly smaller in the frame instead of
  being blown up. If the full-resolution camera originals exist, re-running on those will give
  sharper results.

## Source photos

| Folder | Images (IMG_ numbers, in order) |
|---|---|
| 01-briefcase/black | 4772, 4768, 4767, 4775, 4779, 4776, 4769, 4784, 4774 |
| 02-document-folio/black | 4484, 4488, 4486, 4493, 4496, 4497, 4491 |
| 03-watch-case/black | 4503, 4532, 4513, 4520, 4521, 4523, 4526, 4499 |
| 04-pouch/black | 4545, 4549, 4554, 4564, 4550, 4555, 4569, 4539 |
| 04-pouch/pink | 4655, 4648, 4658, 4651, 4666, 4659, 4660 |
| 05-jewellery-box/black | 4592, 4590, 4583, 4603, 4605, 4610, 4606, 4595, 4600, 4615 |
| 06-mini-backpack/black | 4670, 4668, 4673, 4674, 4675, 4689, 4679, 4680, 4684 |
| 06-mini-backpack/pink | 4625, 4641, 4642, 4629, 4628, 4631, 4626, 4636, 4644 |
| 07-backpack/black | 4711 (recoloured), 4712 (recoloured), 4754, 4755, 4756, 4745, 4750, 4764, 4749 |
| 07-backpack/blue | 4711, 4712, 4703, 4705, 4704, 4717, 4697, 4698, 4722 |
| 07-backpack/green | 4711 (recoloured), 4712 (recoloured), 4736, 4739, 4738, 4726, 4731, 4733, 4727 |
