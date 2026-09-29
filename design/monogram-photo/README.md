# Monogram — photo edit

`original.jpg` is the embossed damask sample. `logo-pattern.jpg` is the same
photo with the four large four-petal flowers erased and the Oberndörfer
star-cross embossed in their place (same position, same size, same top-left
lighting). Everything else in the photo is untouched.

Regenerate with `python3 design/monogram-photo/build.py` (needs numpy and
opencv-python-headless). Tweak the logo size (`logo_poly(305 …)`) or relief
strength (`light` / `dark`) in `build.py`.
