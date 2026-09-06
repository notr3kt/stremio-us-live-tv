# US Live TV (iptv-org) — Stremio addon

A fully static Stremio addon listing free US live TV channels from the public
[iptv-org](https://github.com/iptv-org/iptv) index, grouped into category catalogs
(News, Sports, Entertainment, Movies, Series, Kids, Music, Documentary, General).

**Install:** open Stremio, go to Addons → Add addon, and paste

```
https://notr3kt.github.io/stremio-us-live-tv/manifest.json
```

or click `stremio://notr3kt.github.io/stremio-us-live-tv/manifest.json`.

The channel list is regenerated every Monday by GitHub Actions (`build.py`), so dead
streams drop out and new ones appear without any manual work. Stream availability and
licensing are those of the upstream iptv-org index; this project only reformats it.

`server.cjs` is an optional local static server for testing (`node server.cjs 7101 docs`).
