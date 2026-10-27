# Midnight for Antigravity

The Midnight theme for Antigravity on macOS, with the same colors as the
Qt Creator version:

- **Midnight** color theme: purple-tinted panels, violet accents, and the
  Midnight syntax colors, including semantic highlighting for C++, Python,
  TypeScript and other languages whose language server supports it.
- **Glows** (optional): a violet glow behind the code, a pink glow behind
  the sidebar, and stars.

## Install

```sh
cd antigravity
./install.sh
```

Then, in Antigravity, reload the window (⌘⇧P → **Developer: Reload Window**)
and pick the theme with ⌘K ⌘T → **Midnight**.

That's the plain theme. For the glows:

```sh
./install.sh --glow
```

and reload the window again.

Antigravity has no setting for background images, so `--glow` patches the
app itself. It links `midnight-glow.css` into the app's `workbench.html`, and
it updates that file's checksum in `product.json` so Antigravity doesn't
report a corrupt install. The original `workbench.html` is kept next to it as
`workbench.html.midnight-orig`.

- macOS only lets a terminal change files inside an app if the terminal has
  **App Management** permission (System Settings → Privacy & Security). If
  `--glow` reports that it was blocked, allow it there and rerun.
- Antigravity updates replace the patched files, so rerun `./install.sh --glow`
  after each update.

To remove the glows but keep the theme: `./install.sh --no-glow`.
To remove everything: `./install.sh --uninstall`.

## Adding the picture

Follow **Adding the picture** in [`../qtcreator/README.md`](../qtcreator/README.md)
to make `bg-editor@2x.png`. If it exists, `./install.sh --glow` uses it in
place of the stars, pinned to the editor's bottom-right corner.

## Files

| File | What it is |
| --- | --- |
| `install.sh` | Installs or removes the theme and the glows |
| `extension/` | The color theme, as an extension. `install.sh` packages it as a `.vsix` and installs it |
| `extension/themes/midnight-color-theme.json` | UI colors, syntax colors and semantic token colors |
| `midnight-glow.css` | The glow stylesheet (gradients and background images) |

The star images come from `../qtcreator/` (made by `make-stars.py` there).

After changing any of these, rerun `./install.sh` (with `--glow` if you use
it) and reload the window.

## Limits

- The glow selectors depend on the class names in Antigravity's interface,
  which come from VS Code. If part of the glow stops showing after an update,
  `midnight-glow.css` needs updating.
- `--glow` patches only the main window. The Agent Manager window is a
  separate page, so it has no glows.
