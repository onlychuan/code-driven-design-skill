# Renderer: one scene, multiple outputs

Use this optional helper for typography, rules, rectangles and vector QR artwork. It does not implement product photography, gradients, arbitrary icons, paragraph layout, or complex text shaping; use an appropriate shared vector/layout source for those tasks.

## Commands

Resolve paths relative to this skill folder:

```sh
python scripts/render_design.py assets/example-card.json --out /absolute/output/directory
python scripts/render_design.py /absolute/design.json --validate
python scripts/render_design.py /absolute/design.json --out /absolute/output/directory --pdf --outline-svg --bleed-svg
```

The first command needs only Python 3.10+ standard library. PDF needs `reportlab` and `fonttools`; outlined SVG needs `fonttools`. Install optional packages in the appropriate task runtime, not during skill installation. WOFF2 fonts require fontTools' WOFF/Brotli support.

An existing output is protected by default. Use `--overwrite` only when replacing that output is intended. The renderer validates the scene and print requirements before writing.

## Scene format

See [example-card.json](../assets/example-card.json) for a complete two-face example. Root fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | `1` |
| `title` | Nonempty design title |
| `size_mm` | `[trim_width, trim_height]` |
| `bleed_mm` | Bleed per edge; defaults to 0 |
| `safe_mm` | Safe inset for warnings; defaults to 4 |
| `colors` | Named roles with `hex`, optional `cmyk` percentage array, optional `note` |
| `fonts` | Named roles with CSS `family`, optional `path`, `weight`, `font_index`, variable-font `axes` |
| `faces` | Ordered artwork faces: unique `id`, optional `name`, `background` color, `elements` |

All geometry uses millimetres, with origin at the top left of the trimmed face. Text `y` is a **baseline**, and `size_pt` uses points. A background automatically extends through the declared bleed. Negative coordinates are permitted within that bleed.

Elements use these fields:

- `rect`: `x`, `y`, `width`, `height`, and `fill` and/or `stroke`; optional `stroke_mm`, `radius_mm`.
- `line`: `x1`, `y1`, `x2`, `y2`, `stroke`; optional `stroke_mm`.
- `text`: `x`, `y`, `text`, `font`, `size_pt`, `fill`; optional `tracking_mm`, `align` (`left`, `center`, `right`), `line_height_mm`. Explicit newlines create additional lines.
- `qr`: `x`, `y`, `size_mm`, `url`, `dark`, `light`; optional `quiet_modules` (at least 4). `size_mm` includes the quiet zone. HTTP(S) destinations must have no embedded credentials.

For example:

```json
{
  "type": "text", "x": 5, "y": 12,
  "text": "BUILD WITH CONFIDENCE.", "font": "body",
  "size_pt": 12, "fill": "ink", "tracking_mm": 0
}
```

Every used color needs a four-element `cmyk` array for PDF, in order C/M/Y/K with percentages 0–100. These are declared working recipes, not an automatic ICC conversion. Use separate K100 and white roles for QR artwork where appropriate.

## Font fidelity and limitations

For `--pdf` or `--outline-svg`, supply local font paths for named fonts. Relative paths resolve beside the scene JSON, not beside the script. `font_index` selects a face in a TTC/OTC font collection, defaulting to 0. Font files stay external to the distributable skill. Missing glyphs or font paths cause an error rather than substitution.

The simple outline renderer places individual glyphs. It supports ordinary Latin and unshaped CJK text, but does not apply kerning, ligatures or full shaping. It rejects detected combining marks, bidi and several complex scripts for outlined output. Use a shaping-capable layout engine when the brief needs those features; do not transliterate or rasterize silently. Choose explicit line breaks and inspect actual outline boundaries, especially with negative tracking.

An ordinary HTML/SVG preview uses CSS/system fonts. `--outline-svg` also uses outlines inside the HTML preview, making those glyphs consistent with PDF. Inspect this version before accepting a print layout.

The built-in QR encoder uses byte mode, ECC Q, and versions 1–10. It raises a clear error for unsupported lengths. Use another verified encoder for larger payloads or a different correction level. Decode the final rendered output independently; producing a matrix is not a scanning test.

## Outputs and review

- `preview.html`: self-contained browser review, face switching and geometry guides.
- `<face-id>.svg`: vector RGB source, optionally outlined and including bleed.
- `artwork.pdf`: optional CMYK vector artwork with outlined text and page boxes; not PDF/X certified.
- `factory-spec.json`: dimensions, color roles, face order and production assumptions.
- `manifest.json`: export record and content hashes.

The PDF adds 5 mm outside the bleed for marks. `safe_mm` and small-type/module checks create warnings; they do not prove that the artwork is legible or in bounds. Render and inspect every final page, and decode the QR. Create a readable factory sheet from the specification when requested; the JSON is not a finished job-ticket PDF.

## Exact-file publication helper

```sh
python scripts/preserve_artifact.py /absolute/supplied.html --out /absolute/static-directory
python scripts/preserve_artifact.py /absolute/supplied.html --out /absolute/static-directory --verify
```

This copies bytes into `index.html` and records/verifies SHA256; it does not execute or sanitize the supplied document. Preserve the user's sandbox/CSP and use the chosen provider's publishing workflow. The helper grants no new permission to publish.
