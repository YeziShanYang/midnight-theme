# Ink Koi for Claude

The Ink Koi theme as a browser style for claude.ai:

- **New chat.** Two large ink koi circle the prompt box. They fade out
  where the box and the greeting sit, so they never cross what you're
  typing.
- **Conversations.** The same koi, very faint and blurred, as if seen
  through frosted glass, so they don't get in the way of reading.
- **Greeting.** The new-chat greeting is lettered in Liu Jian Mao Cao, a
  brush font in the style of Chinese "grass script", with a stroke of
  vermilion beneath it. Claude still writes the words.
- **Prompt box.** Flat paper instead of a floating card: a shade deeper
  than the page, with a thin ink edge and small corners. While you type,
  a red line runs along its bottom edge.
- **Send button.** A worn, round red seal stamp with 送 ("send") in a brush
  hand. It fades while there's nothing to send.
- **Vermilion.** Claude's logo and its other clay-orange touches turn
  vermilion, the theme's one colour.
- **Sidebar.** Flat on the page's own colour, with no card or shadow. The
  open chat is marked by a brushstroke of vermilion beneath it instead of
  a grey highlight.
- **Motion.** The koi circle slowly: once every three minutes on the new
  chat page, and once every four and a half in conversations. The new-chat
  greeting writes itself out from the left as the page opens, and then the
  brushstroke beneath it grows out from its middle like spreading ink. The
  sidebar's stroke grows the same way when you open a chat. The prompt
  box's red line draws in from the left when you click into it. Clicking
  into the box sends a faint ripple out from its edge, and sending a
  message sends a red one, from the box and from the seal. It's all off
  when the system's "reduce motion" setting is on, and all but the koi's
  turning when Claude's is. The turning happens inside the picture, which
  can only see the system setting. `TURN` and `TURN_CHAT` in `build.py`
  set its speed in seconds per turn, and 0 stops it.
- **Light and dark.** It follows Claude's own appearance setting
  (Settings → Appearance), including **System**.

## Install

1. Install the **Stylus** extension for Firefox, Chrome or Edge.
2. Build the style. The koi come from the Firefox theme, so first follow
   **The picture** in [`../firefox-ink-koi/README.md`](../firefox-ink-koi/README.md)
   to build them. Then, here, run:

   ```sh
   python3 build.py
   ```

   This writes `ink-koi-claude-custom.user.css`, with the koi in it.
3. Copy it: `pbcopy < ink-koi-claude-custom.user.css`.
4. In Stylus, open **Manage**, choose **Write new style**, select all and
   paste. Stylus recognises it as a user style and fills in the name. Save
   it.
5. Reload claude.ai.

Without the koi, `build.py` writes only `ink-koi-claude.user.css`, which
has the vermilion but no koi. Install that the same way.

## Settings

In Stylus's popup or on the Manage page, click the gear next to the style:

- **Koi strength, new chat** and **Koi strength, conversations**: how dark
  the koi are, from 0 (gone) to 100.
- **Frosting, conversations**: how much the koi are blurred.
- **Koi size, new chat**: the koi's height, as a percentage of the window.
  The default, 76, keeps them inside the window as they turn; above about
  78 they're cut off at the top and bottom when they stand on end.
- **Koi shift right, new chat**: moves the koi sideways. They're already
  centred on the chat pane to the right of the sidebar, and they follow it
  when the sidebar opens or collapses, so this is only for fine-tuning.

## Changing the style

- Edit `ink-koi-claude.css`, not the `.user.css` files, which are
  generated.
- Run `python3 build.py`, then paste the new `.user.css` over the old one in
  Stylus.

The pictures are the Firefox theme's `koi-wide-light.png` and
`koi-wide-dark.png`, so they follow its `make-art.py` settings. If `cwebp`
(`brew install webp`) or Pillow is installed, `build.py` converts them to
WebP first, which makes the style much smaller.

`ink-koi-claude-custom.user.css` contains the painting, so it's listed in
`.gitignore`.

The greeting font and the seal are in `assets/`, made by
`python3 tools/make-assets.py` (it needs Pillow, fontTools and Brotli). It
cuts Liu Jian Mao Cao down to Latin letters, which keeps the style small,
and draws the seal with 送 in Ma Shan Zheng. Its settings, such as the
ring's thickness and how worn the stamp looks, are at the top of the
file. Both fonts are from Google Fonts under the SIL Open Font License,
which is in `assets/`. The font is built into the style so that it
doesn't depend on claude.ai allowing fonts from other sites.

## How it works

The style hardly depends on claude.ai's page structure, which changes
often:

- The colours are changed through Claude's own colour variables, in both of
  its design systems: the older `--brand-*` and `--accent-brand` and the
  newer `--cds-*`.
- The koi are one layer over the chat pane that clicks pass through. It
  starts where Claude's pane starts, using Claude's `--df-sidebar-clearance`
  variable (the open sidebar's width, or 0 when it's collapsed). If that
  pane disappears in a redesign, the layer covers the whole window
  instead.
  Which koi appear depends only on the address: `claude.ai/new` (and
  `claude.ai/`) or `claude.ai/chat/…`.
- The greeting, prompt box, send button and sidebar are found by
  Claude's own markers: the greeting text's `data-new-page-greeting-text`
  attribute, the composer's `shadow-composer` class, the `.dframe-sidebar`
  rows marked `data-selected`, and the send button's label "Send
  message". A redesign that renames one of them turns that part back to
  Claude's own look, without breaking anything else.

## Limits

- The koi layer sits over everything, menus and dialogs included. That's
  barely noticeable in conversations. On the new chat page, menus that
  open over the koi show them faintly.
- Projects (`claude.ai/project/…`) and other pages get the vermilion but
  no koi.
- Claude's own colours (cream and dark grey) are kept, and only the orange
  changes.
- The greeting font covers Latin letters only. A greeting in another
  script falls back to Claude's serif.
