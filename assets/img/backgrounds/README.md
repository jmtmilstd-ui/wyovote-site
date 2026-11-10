# Background images

The home hero uses these two files:

- `red-barn-black-hills-1920.jpg` — viewports wider than 1280px
- `red-barn-black-hills-1280.jpg` — viewports of 1280px and below

Black Hills barn photograph: public domain.

The dark overlay that keeps the white heading readable is in `css/styles.css`, on `.hero`. Change `--hero-background-image` at the top of that file to point the hero at a different photo. A matching `@media (max-width: 1280px)` rule selects the smaller file.
