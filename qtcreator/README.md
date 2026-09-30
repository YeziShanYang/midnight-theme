# Midnight for Qt Creator

A dark violet theme for Qt Creator on macOS, built on Qt Creator's
Dark (2024) theme:

- **Midnight**: the UI theme, with purple-tinted panels and violet accents.
- **Midnight** color scheme: syntax colors for the code editor.
- **Midnight Glow** color scheme: the same colors on a see-through
  background. With the glow launcher it shows a violet glow behind the code,
  a pink glow behind the sidebar's file tree, and stars.

## Install

```sh
cd qtcreator
./install.sh
```

Then, in Qt Creator:

1. Settings → Environment → Interface → **Theme: Midnight**, then restart
   Qt Creator.
2. Settings → Text Editor → Font & Colors → **Color Scheme: Midnight**.

That's the plain theme. For the glows:

3. Pick the **Midnight Glow** color scheme instead.
4. Quit Qt Creator (⌘Q) and start it from **`Qt Creator (Glow).command`**:
   double-click it in Finder, or run it in Terminal. It passes the glow
   stylesheet to Qt Creator, which only reads stylesheets at launch.

`install.sh` copies your installed Qt Creator's own Dark (2024) files so the
theme matches your version. If it can't find Qt Creator, it uses the copies in
`fallback/`.

To remove everything: `./install.sh --uninstall`.

If the glows don't show, run `./install.sh --test-qss` and relaunch with the
launcher. The status bar turns red if the stylesheet is loading. Then rerun
`./install.sh` to remove the test.

## Adding the picture

1. Download the
   [wallpaper](https://www.wallpaperalchemy.com/wallpaper/anime-mystical-blossom-tree-wallpaper-at-night-2583),
   or pick any tall picture, and save it here as `art.jpg`.
2. Run `python3 make-art.py`. It writes `bg-editor.png` and `bg-editor@2x.png`
   and takes about 20 seconds.
3. Run `./install.sh` again and relaunch with the launcher.

`make-art.py` needs only macOS's built-in `sips` and Python 3. The settings
at its top control:

- how strong the picture is (`OPACITY`)
- how its misty background fades into the glow (`AURA_*`, `HAZE_*`)
- how the lake is continued to the left (`LAKE_*`, `MIST_*`)

With a different picture, set `TRUNK` to where its subject is and
`WATER_TOP` to where its water starts (or past the bottom, if it has none).

## Files

| File | What it is |
| --- | --- |
| `install.sh` | Installs or removes everything |
| `midnight-colors.ini` | UI colors, merged into Dark (2024) by `install.sh` |
| `midnight.xml`, `midnight-glow.xml` | Editor color schemes |
| `midnight-glow.qss` | The glow stylesheet (gradients and background images) |
| `Qt Creator (Glow).command` | Launches Qt Creator with the glow stylesheet |
| `make-stars.py` | Draws the `stars-*.png` starfields |
| `make-art.py` | Builds the picture background from `art.jpg` (`--overleaf` builds the Overleaf version) |
| `fallback/` | Qt Creator's Dark (2024) theme files, from Qt Creator (GPL-3.0) |

After changing any of these, rerun `./install.sh` and restart Qt Creator.
