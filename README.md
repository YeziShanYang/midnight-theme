# Themes

## Introduction

A dark violet theme with soft background glows and a starry sky, for two
editors, plus a matching LaTeX style for notes:

## Contents

### Midnight

| Folder | For | How it's applied |
| --- | --- | --- |
| [`qtcreator/`](qtcreator/) | Qt Creator on macOS | An install script adds a UI theme, two editor color schemes, and an optional glow stylesheet |
| [`antigravity/`](antigravity/) | Antigravity on macOS | An install script adds a color theme as an extension, and optionally patches in the glows |
| [`overleaf/`](overleaf/) | Overleaf, in the browser | A user style for the Stylus extension |
| [`moonlight-notes/`](moonlight-notes/) | LaTeX notes for math and CS | A `.sty` file with theorem, problem and code boxes over a night-sky background |
| [`starlight-notes/`](starlight-notes/) | LaTeX notes for math and CS | The same boxes over a starry gradient sky, drawn as vector art |

### Ink Koi

Ink on rice paper, with vermilion as the only colour.

| Folder | For | How it's applied |
| --- | --- | --- |
| [`firefox-ink-koi/`](firefox-ink-koi/) | Firefox | An install script adds `userChrome.css` and `userContent.css` to a profile, theming the tabs, toolbars, menus and new tab page |
| [`claude-ink-koi/`](claude-ink-koi/) | claude.ai, in the browser | A user style for the Stylus extension, with koi around the new-chat prompt and vermilion in place of Claude's orange |

Each folder has its own README with install steps.

## Midnight's background picture

The Midnight Qt Creator, Antigravity and Overleaf versions can also show a painting
behind the code: a blossoming tree by a lake at night, pinned to the
editor's bottom-right corner and faded into the glow. It was made with this
wallpaper:

**[Anime Mystical Blossom Tree Wallpaper at Night](https://www.wallpaperalchemy.com/wallpaper/anime-mystical-blossom-tree-wallpaper-at-night-2583)**
(Wallpaper Alchemy)

The picture isn't included here, because it isn't ours to redistribute. The
theme works without it: you get the glows and stars. To add it, download it
yourself, or use any other picture you like, and follow **Adding the picture**
in each folder's README.

The picture and every image built from it are listed in `.gitignore`, so
they can't be committed by accident.
