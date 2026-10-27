# Ink Koi for Firefox

A minimal ink-painting theme for Firefox: ink on rice paper, with vermilion
as the only colour.

- **Tabs** are plain labels on the paper with no boxes. The selected tab is
  in full-strength ink with a brushstroke of vermilion under it.
- **A red seal** from the painting sits in the empty end of the tab strip.
  New tabs cover it as the strip fills up.
- **The URL bar** is a slightly deeper tone of paper. When it's focused, a
  thin red line appears under it.
- **Menus, panels and the sidebar** use the same paper and ink.
- **The new tab page and Home** have no Firefox logo. The search box moves
  to the middle of the page, into the gap between two large, faded ink koi
  circling each other. Shortcuts are in greyscale until you hover them. In
  dark mode the ink turns pale.
- **A faint brushstroke** sweeps along the top of the window, behind the
  tabs.
- **Light and dark.** Light is ink on paper and dark is pale ink on black.
  The theme follows Firefox's own Light / Dark setting.

## Install

Tested with Firefox 158 on macOS.

1. Add the picture. See **The picture** below. Without it, the theme still
   works, but the new tab page is plain paper and the tab strip has no seal.
2. Quit Firefox (Cmd-Q).
3. Run:

   ```sh
   ./install.sh
   ```

   This installs into the profile Firefox opens by default. To pick another
   one, run `./install.sh --list`, then `./install.sh "<profile folder>"`.
   Firefox shows the profile it's using at `about:support`, under
   **Profile Folder**.
4. Start Firefox.
5. In Settings → General → **Website appearance**, choose Automatic, Light
   or Dark. On the Add-ons page (`about:addons`) → Themes, keep **System
   theme — auto** enabled. A colourful Firefox theme can show through in
   places.

The script copies `chrome/` into the profile and adds a single line to the
profile's `user.js`. That line turns on
`toolkit.legacyUserProfileCustomizations.stylesheets`, the setting that lets
Firefox load `userChrome.css` and `userContent.css`. If the profile already
has either file, the script backs it up as `*.bak-<date>` first.

### By hand

1. Open `about:config` and set
   `toolkit.legacyUserProfileCustomizations.stylesheets` to `true`.
2. Open `about:support`, then click **Open in Finder** next to Profile
   Folder.
3. Copy this folder's `chrome/` folder into the profile folder, merging it
   with any existing `chrome/` folder.
4. Restart Firefox.

### Tidier new tab page (optional)

For the plainest page, install with `./install.sh --tidy`. This turns off
stories, sponsored shortcuts and weather, and leaves only the search box,
your shortcuts and the koi. The settings go in `user.js`, which Firefox
re-applies at every start, so to bring one back, run `./install.sh` again
without `--tidy`. To do it by hand instead, click the new tab page's
customise button and turn those three off.

## Uninstall

```sh
./install.sh --uninstall
```

This removes the theme's files and the line in `user.js`. The setting
itself stays on in Firefox, which does nothing when there are no styles to
load. To turn it off, set it back to `false` in `about:config`.

## The picture

The koi are an ink painting of two koi circling each other, with a red seal,
sold as a sticker. The picture isn't included here, because it isn't ours to
redistribute. To add it:

1. Save the picture as `firefox-ink-koi/art.webp`. A `.png` or `.jpg` also
   works.
2. Run `python3 tools/make-art.py`. It needs Pillow (`pip install pillow`).
3. Run `./install.sh` again.

`make-art.py` works with any ink painting on a white background. It turns the
white paper transparent and keeps the ink's strength, so the picture sits on
the theme's paper. It also removes a sticker's grey die-cut outline if there
is one. Red stays red, and if it finds a red seal, it cuts it out for the
tab strip. The new tab page uses the painting turned on its side, faded and
without the seal.

For the stroke at the top of the window, save a single ink brushstroke on
white as `firefox-ink-koi/stroke.webp` (or `.png`/`.jpg`) before running
`make-art.py`. A fake-transparency checkerboard behind the stroke is
cleared too. Without the file, the top stays plain. The settings are at the top of the file. Raise `WHITE` if pale
washes vanish, or lower it if the paper leaves a grey haze.

The pictures, and everything built from them, are listed in `.gitignore`.
The `WIDE_*` and `STROKE_*` settings at the top of `make-art.py` control
how the new-tab koi are turned and how strong each image is.

## Wallpapers

`make-art.py` also writes `wallpaper/ink-koi-light.png` and
`wallpaper/ink-koi-dark.png`, which are 2560 × 1600 versions of the new tab
art. Use them as a desktop background,
or in Firefox's own wallpaper picker on the new tab page (gear icon →
Wallpaper → upload). That picker works without `userContent.css`, for
example in a profile where you don't want to install the styles.

## Changing it

- **Colours** are set at the top of `chrome/userChrome.css` and
  `chrome/userContent.css`, as `--koi-paper`, `--koi-ink` and `--koi-red`.
  The light set comes first, followed by a dark set under
  `prefers-color-scheme: dark`. If you change the red, also change it in
  `--koi-stroke`, which is an inline SVG with the colour written in as
  `%23c23a2b`.
- **To remove the seal from the tab strip,** set `--koi-seal: none;` in
  `userChrome.css`. To remove the stroke from the top, set `--koi-top: none;`
  in both the light and dark sets.
- **To size or move the new-tab koi,** edit `background-size` and
  `background-position` on `body` in `userContent.css`. The rule on
  `.search-wrapper` below it sets how far down the search box sits.
- **To use a different picture,** replace `art.webp` and run
  `tools/make-art.py` again.

After editing, run `./install.sh` again and restart Firefox.
`userChrome.css` is only read at startup.

## Limits

- Firefox renames internal classes from time to time. If part of the theme
  stops applying after an update, the selectors need updating.
  `userChrome.css` mostly sets Firefox's own colour variables rather than
  styling elements directly, so most of it survives.
- With vertical tabs, the selected tab gets a faint ink wash instead of the
  brushstroke, and the tab-strip seal is hidden.
- Pages that aren't Firefox's own keep their own colours. Only the new tab
  page, Home and blank tabs are themed.
- Built-in pages such as Settings and Add-ons aren't themed.
