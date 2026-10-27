# Starlight notes style

A LaTeX style for math and CS notes: a starry night sky on every page,
dark navy at the top and fading to a soft lavender glow at the bottom. It
has the same square-cornered boxes for theorems, problems and code as
[`moonlight-notes`](../moonlight-notes/), and the same compact spacing.
`example.tex` uses every feature, and `example.pdf` shows the result.

The sky is drawn as vector art (a gradient, a glow and a few thousand
stars), so it stays sharp at any zoom and adds only about 70 KB to the
`.sty`. No photo is embedded, so everything here can be shared freely.

## Use it on Overleaf

1. Upload `starlight.sty` to your project. That's the only file you need:
   the sky is stored inside it.
2. Load it straight after `\documentclass`:

   ```latex
   \documentclass[10pt]{article}
   \usepackage{starlight}            % A4
   % \usepackage[letter]{starlight}  % US Letter
   % \usepackage[nobackground]{starlight}  % plain dark pages
   \renewcommand{\headertext}{MATH 61CM}
   ```

It works with pdfLaTeX (Overleaf's default), XeLaTeX and LuaLaTeX. On every
compile it writes the sky out as `starlight-sky.pdf` and places it behind
each page. The log notes this with a harmless "Writing or overwriting file"
warning.

## Reference

Every environment and macro works as in
[moonlight-notes](../moonlight-notes/README.md#reference), with these names
changed:

| moonlight | starlight |
| --- | --- |
| `\blossom`, `\blossom[violet]` | `\twinkle`, `\twinkle[sky]` (a four-pointed star, also the QED mark) |
| `\newmoonbox{...}{...}{...}{moonbase}{moonthm}` | `\newskybox{...}{...}{...}{skybase}{skythm}` |
| `moonsub`, `moonprob` | `skysub`, `skyprob` |

So a box of your own is

```latex
\newskybox{fact}{Fact}{ice}{skysub}{skythm}
```

with the environment name, its title, a palette color, the style (`skybase`
for a main box or `skysub` for a quieter one), and the counter (`skythm`,
`skyprob`, or empty for no number).

**Colors.** Change these near the top of `starlight.sty` to re-theme
everything:

| Color | Used for |
| --- | --- |
| `horizon`, `horizondeep` | theorems, headings, problems |
| `lilac` | lemmas, propositions, solutions |
| `sky`, `skylight` | definitions, `\term` |
| `ice` | examples, remarks, code |
| `leaf`, `ember`, `glowc` | tips, warnings, highlights |
| `textc`, `muted`, `boxbg`, `bgc` | text, secondary text, box fill, page |

## Changing the sky

`tools/make-sky.py` draws the sky and swaps it into `starlight.sty`, leaving
the rest of the file alone. It needs only the Python standard library:

```sh
python3 tools/make-sky.py
```

The settings at its top control:

- the gradient, top to bottom (`STOPS`)
- how far it fades toward the page color, which keeps the bottom of the
  page readable (`FADE`)
- the glow low on the left (`GLOW`)
- how many stars there are (`FAINT_STARS`, `STARS`, `BRIGHT_STARS`), their
  tints (`STAR_COLOURS`), and where they fall (`SEED`)

The gradient colors were sampled from
[Gradient Night Sky](https://picography.co/) on Picography.
