# Interactive HTML/CSS previews

Read this when building or revising the browser preview.

## Keep one design scene

Represent artwork in a reusable scene with physical dimensions, named color roles, text, assets, and geometry. Millimeters work well for physical collateral; convert to PDF points with `points = mm × 72 / 25.4`. An SVG `viewBox` can share the same scene coordinates. HTML/CSS supplies the surrounding interaction and scales the artwork for viewing.

This avoids separately guessing a PDF layout from a responsive screenshot. If the existing artwork is CSS-based, establish a fixed export layout and verify it against the accepted preview before production. Responsive layout changes for a comparison panel should not change the proportions or line breaks of the physical artwork itself.

Keep copy, QR payload, asset paths, and variant choice outside duplicated markup where practical. Use the same source for front/back previews and exports. Treat line breaks as design decisions when they affect the approved composition.

## Add only interactions that aid review

Useful controls include front/back switching, variant comparison, a size indicator, and optional trim/bleed/safe-area guides. Use actual buttons with clear labels and a visible selected state. Keep controls outside the print artwork. Do not add dashboard controls, account forms, or animation unless they serve the brief.

Use a stable aspect ratio and an intentional scale for the artwork. A narrow screen can stack or scroll the comparison interface without shrinking text inside the print scene independently of other elements. Show the real final copy instead of placeholder paragraphs once it is available.

## Make the preview durable

For a portable single HTML file, embed permitted project assets as data URIs or use documented local assets. Avoid remote font and image dependencies that make the preview change or fail later. Do not add analytics, telemetry, remote upload code, or external network requests to a design preview.

When an inline-visualization environment provides a sandboxed iframe or CSP, preserve its required wrapper and security model. For an existing file the user asks to publish unchanged, follow [publishing-delivery.md](publishing-delivery.md); do not rebuild its wrapper to match a different template.

An SVG/HTML preview uses screen RGB color. Label it as a visual reference when supplying a separate process-CMYK print PDF. It is not a calibrated press proof.

## Verify observable behavior

Inspect the rendered result at a realistic desktop width and a narrow mobile width, such as 320–390 CSS px. Choose additional sizes only when the composition or interactions warrant them. Verify:

- Both sides and each selectable variant display the intended artwork.
- Headlines, body copy, footer, and QR do not overlap, clip, or escape their bounds.
- Fonts and images actually load; punctuation and non-Latin glyphs render correctly.
- Controls work using a pointer and keyboard, and the selected state is understandable.
- Guides and preview-only UI do not appear in production artwork.

Measure layout bounds when a potential collision is hard to judge, then inspect the rendered view. A DOM measurement alone cannot prove the visible result is good.

Generate a QR from the verified payload rather than drawing an imitation. Keep a clear four-module quiet zone on every side, square modules, and strong foreground/background contrast. Decode the rendered QR and compare its complete payload byte-for-byte with the intended target. A successful decode of the source PNG alone does not establish that the preview or print export is valid.

For a physical print target, also render and decode the final print PDF as described in [print-production.md](print-production.md).
