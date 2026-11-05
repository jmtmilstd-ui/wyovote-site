# Background images

The home hero uses these two files:

- `red-barn-black-hills-1920.jpg` — viewports wider than 1280px
- `red-barn-black-hills-1280.jpg` — viewports of 1280px and below

Black Hills barn photograph: public domain.

Devils Tower is kept for later pages and is not used on the home hero:

- `devils-tower-1920.jpg`
- `devils-tower-1280.jpg`

Devils Tower photograph: National Park Service, public domain. Source: https://commons.wikimedia.org/wiki/File:Devils_Tower_National_Monument_(29400003663).jpg

The dark overlay that keeps the white heading readable is in `css/styles.css`, on `.hero`. Change `--hero-background-image` at the top of that file to point the hero at a different photo. A matching `@media (max-width: 1280px)` rule selects the smaller file.
