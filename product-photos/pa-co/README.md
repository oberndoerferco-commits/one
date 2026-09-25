# PA & CO — website product images

Organised like a web shop: one folder per product, one sub-folder per colour.
Inside each colour folder the files are numbered in display order — `01-front.jpg` is always the
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

`_overview.jpg` shows every folder at a glance.

## Main images (01-front)

- Every product's main image is a straight front view on the same background, same framing.
- **Mini backpack and backpack:** the main image is *the same photo* for every colour, recoloured,
  so switching colour on the product page changes only the colour — angle, size and position are
  identical.
  - Mini backpack: pink is the original (IMG_4641); black is recoloured from it.
  - Backpack: blue is the original (IMG_4712); green and black are recoloured from it.
  - Leather, zip tape and stitching are recoloured; silver zips, pullers and the silver logo are kept.

## Gallery order

Backpacks (both sizes), same order for every colour:
`01 front · 02 three-quarter · 03 side · 04 back · 05 back three-quarter · 06 interior · 07–09 details`

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
| 06-mini-backpack/black | 4641 (recoloured), 4671, 4673, 4674, 4675, 4689, 4679, 4680, 4684 |
| 06-mini-backpack/pink | 4641, 4634, 4642, 4629, 4628, 4631, 4626, 4636, 4644 |
| 07-backpack/black | 4712 (recoloured), 4753, 4754, 4755, 4756, 4745, 4750, 4764, 4749 |
| 07-backpack/blue | 4712, 4710, 4703, 4705, 4704, 4717, 4697, 4698, 4722 |
| 07-backpack/green | 4712 (recoloured), 4735, 4736, 4739, 4738, 4726, 4731, 4733, 4727 |
