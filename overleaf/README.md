# Midnight for Overleaf

The Midnight theme as a browser style for Overleaf:

- a violet interface
- Midnight syntax colors for LaTeX
- a violet glow with stars behind the editor
- a pink glow with stars behind the file tree

## Install

1. Install the **Stylus** extension for Chrome, Edge or Firefox.
2. In Stylus, open **Manage**, then create a new style (**Write new style**)
   and paste in the whole of
   [`midnight-overleaf.user.css`](midnight-overleaf.user.css). Save it.
   - Alternatively, open the file's **Raw** view on GitHub, and Stylus
     offers to install it.
3. In an Overleaf project, open Menu → Settings → **Overall theme** and
   pick Dark.

The style applies on overleaf.com only, and only in browsers where it's
installed. Collaborators still see normal Overleaf.

## Adding the picture

The picture is a blossoming tree peeking in from the editor's right edge,
over a misty lake.

1. Follow **Adding the picture** in [`../qtcreator/README.md`](../qtcreator/README.md)
   to save `art.jpg`.
2. In `qtcreator/`, run `python3 make-art.py --overleaf`.
3. Here, run `python3 build.py`. As well as the normal style, it now writes
   `midnight-overleaf-custom.user.css`, which has the picture in it.
4. Install that file in Stylus, in place of the normal one.

The `--overleaf` settings sit at the bottom of `make-art.py`:

- `CUT_RIGHT`: how much of the tree is hidden past the right edge.
- `ART_BOTTOM`: lower values move it further down.
- `OPACITY` and `LAKE_OPACITY`: how strong the tree and the lake are.

## Changing the style

- Edit `midnight-overleaf.css`, not the `.user.css` files, which are
  generated.
- Run `python3 build.py`, then paste the new `.user.css` over the old one in
  Stylus.

`build.py` embeds the images in the style, so nothing needs hosting. If
`cwebp` is installed (`brew install webp`), it shrinks them first.

## Limits

- Overleaf sometimes renames its internal CSS classes. If part of the theme
  stops applying after an Overleaf update, the selectors in
  `midnight-overleaf.css` need updating.
- The PDF itself isn't themed, only the area around it.
- Code Editor mode is fully themed. Visual Editor mode is only partly themed.
- Safari has no Stylus. You'd need a user-style app for it instead.
