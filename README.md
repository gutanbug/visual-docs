# visual-docs

A Claude Code plugin that turns plans, designs, reports and guides into a clean one-page visual document (HTML Artifact).

![visual-docs demo](docs/demo.gif)

**[Live demo →](https://gutanbug.github.io/visual-docs/)**

- One design language: generous whitespace, gray hierarchy, a single blue accent, rounded surfaces
- Ready-made components: hero, flow, bento, stats, layers, tables, API list, decisions, roadmap
- Light / dark mode and mobile layout out of the box
- `vdoc.py` builds and lints the page using only the Python standard library
- Output text is written in Korean (해요체)

## Install

In Claude Code:

```
/plugin marketplace add gutanbug/visual-docs
/plugin install visual-doc@visual-docs
```

## Usage

```
/visual-doc:make Summarize docs/notify-design.md as a one-page design doc
```

Or just ask: "이 기획 내용을 아티팩트로 깔끔하게 정리해줘".
The page is written to `./visual-doc/<slug>/page.html` and published as an Artifact when the `Artifact` tool is available.

## Examples

| Page | Source (body) |
|---|---|
| [visual-docs intro](https://gutanbug.github.io/visual-docs/) | [`examples/visual-docs/body.html`](examples/visual-docs/body.html) |
| [Wiki intro](https://gutanbug.github.io/visual-docs/intro.html) | [`intro.body.html`](plugins/visual-doc/skills/visual-doc/examples/intro.body.html) |
| [Notification design](https://gutanbug.github.io/visual-docs/design.html) | [`design.body.html`](plugins/visual-doc/skills/visual-doc/examples/design.body.html) |

Rendered pages live in [`docs/`](docs) (GitHub Pages); only the body fragments ship with the plugin.

<details>
<summary>Full page (dark)</summary>

![visual-docs dark preview](docs/preview-dark.png)

</details>

## vdoc.py

```bash
python3 vdoc.py build --title "Notify design" --body body.html --out page.html [--css extra.css]
python3 vdoc.py check page.html        # or a body.html fragment
python3 vdoc.py serve page.html --port 8765
```

`check` catches missing titles, bento rows that don't sum to 6, flow/roadmap count mismatches, missing eyebrow/h2,
the same component three sections in a row, body section count outside 2–8, a hero mock without its "example" label,
a missing or misplaced `.start` block, unknown icons, raw color values (hex, `rgb()`/`hsl()`/`oklch()`…, named colors),
disallowed external assets and unwrapped tables.

To rebuild the demo pages after changing `base.css`:

```bash
S=plugins/visual-doc/skills/visual-doc
python3 $S/scripts/vdoc.py build --title "visual-docs 소개" --body examples/visual-docs/body.html --out docs/index.html
python3 $S/scripts/vdoc.py build --title "사내 지식 wiki 소개" --body $S/examples/intro.body.html --out docs/intro.html
python3 $S/scripts/vdoc.py build --title "알림 서비스 설계" --body $S/examples/design.body.html --out docs/design.html
```

## License

[MIT](LICENSE)
