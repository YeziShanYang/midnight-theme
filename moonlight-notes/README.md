# Moonlight notes style

A LaTeX style for math and CS notes: a frosted pink-moon night scene on every
page, with the moon at the top and a flower meadow at the bottom. It has
square-cornered boxes for theorems, problems and code, and compact spacing so
pages hold a lot. `example.tex` uses every feature, and `example.pdf` shows
the result.

> **In this repository:** `moonlight.sty` and `example.pdf` aren't included,
> because they contain a wallpaper that isn't ours to share (see the end of
> this file). To build `moonlight.sty`, run `tools/make-background.py` with a
> picture of your own, as described in **Changing the picture**.

## Use it on Overleaf

1. Upload `moonlight.sty` to your project. That's the only file you need: the
   background picture is stored inside it.
2. Load it straight after `\documentclass`:

   ```latex
   \documentclass[10pt]{article}
   \usepackage{moonlight}            % A4
   % \usepackage[letter]{moonlight}  % US Letter
   % \usepackage[nobackground]{moonlight}  % plain dark pages, faster to compile
   \renewcommand{\headertext}{MATH 61CM}
   ```

It works with pdfLaTeX (Overleaf's default), XeLaTeX and LuaLaTeX. On every
compile it writes the picture out as `moonlight-background.pdf` and places it
behind each page. The log notes this with a harmless "Writing or overwriting
file" warning.

## Reference

**Numbered boxes.** They share one counter, numbered within sections (2.1,
2.2, ...):

- `definition`, `theorem`, `example`
- `lemma`, `proposition`, `corollary`, `claim`, `conjecture`, `axiom`

Each takes an optional name, `\begin{theorem}[Cantor] ... \end{theorem}`, and
works with `\label` and `\ref`. Starred versions, like `theorem*`, are
unnumbered.

**Problems.** `problem` and `exercise` are numbered 1, 2, 3, ...; `solution`
isn't numbered.

**Asides:** `remark`, `note`, `intuition`, `tip`, `warning`, `summary`.

**Your own boxes:**

```latex
\newmoonbox{fact}{Fact}{bluebell}{moonsub}{moonthm}
```

The arguments are the environment name, its title, a palette color, the style
(`moonbase` for a main box or `moonsub` for a quieter one), and the counter
(`moonthm`, `moonprob`, or empty for no number).

**Proofs.** Use the normal `proof` environment, and `\qedhere` works. The QED
mark is a blossom.

**In text:**

- `\term{bijection}` for a word being defined
- `\hl{remember this}` to highlight text
- `\ans{x = 3}` for a boxed final answer
- `\blossom` or `\blossom[violet]` for a small flower

**Math shortcuts:**

| Kind | Commands |
| --- | --- |
| Number sets | `\N \Z \Q \R \C \F` |
| Delimiters | `\abs{x} \norm{v} \floor{x} \ceil{x} \paren{x} \inner{u}{v} \set{1,2}` |
| Set-builder | `\setof{x}{x > 0}` |
| Calculus | `\dd` (as in `\int f \dd x`), `\deriv{f}{x}`, `\pderiv{f}{x}`, `\eps` |
| Linear algebra | `A\T`, `f\inv`, `A\compl`, `\rank \tr \Span \id` |
| Operators | `\argmin \argmax \lcm \sgn` |
| Probability | `\Prob[A \given B]`, `\E`, `\Var`, `\Cov` |
| Complexity | `\bigO{n} \bigT{n} \bigOm{n} \littleo{n} \littleom{n} \poly \polylog`, `\CC` for C++ |

The delimiter commands come from `mathtools`: add `*` (`\abs*{...}`) to size
them to their contents.

**Code:**

```latex
\begin{codeblock}{main.cpp} ... \end{codeblock}                 % C++ by default
\begin{codeblock}[lang=Python]{sort.py} ... \end{codeblock}     % any listings language
\codefile{code/list.cpp}                                         % code from a project file
\codefile[lang=Java]{Main.java}
\code|std::vector<int>|                                          % inline code
\begin{terminal} $ make && ./a.out \end{terminal}
\begin{pseudo}{Binary search}
  \begin{algorithmic}[1] \State ... \end{algorithmic}
\end{pseudo}
```

**Diagrams and plots.** TikZ styles `vertex`, `node box`, `arrow`, `edge`
and `hot` (the highlighted node) are for graphs and trees. `tikz-cd`
diagrams and `pgfplots` axes use the palette automatically: write
`\addplot+[...]` (with the `+`) to keep the palette colors. In tables, use
`booktabs` rules, with `\thead{...}` for header cells.

**Colors.** Change these near the top of `moonlight.sty` to re-theme
everything:

- `moon`, `moondeep`, `petal`
- `violet`, `violetlight`, `bluebell`
- `leaf`, `ember`, `glowc`
- `textc`, `muted`, `boxbg`

## Changing the picture

`tools/make-background.py` builds the background and swaps it into
`moonlight.sty`:

```sh
pip install pillow
python3 tools/make-background.py path/to/picture.jpg
```

The settings at its top control:

- which parts of the picture are kept (`TOP`, `BOTTOM`)
- how frosted it is (`FROST`, `FROST_MIX`, `MILK`)
- how dark the veil over it is (`VEIL`)
- how much the bright parts are softened (`KNEE`, `SQUASH`)

It also saves `tools/background-preview.jpg` so you can see the result.

The current picture is
[Anime Pink Moon Cherry Blossom Night](https://www.wallpaperalchemy.com/)
from Wallpaper Alchemy. It isn't licensed for redistribution, so keep this
style to your own notes rather than publishing it.
