# Interactive HTML/CSS previews

Read this when building or revising the browser preview.

## Keep one source for design and behavior

Keep content, assets, named design tokens, selected variant, and interaction state in a reusable source. Screen interfaces use semantic HTML and responsive CSS in the existing code architecture. Fixed compositions such as diagrams, slides, and print artwork can use a shared scene and SVG `viewBox` for consistent geometry across outputs.

Use the medium's units: CSS/rem and responsive constraints for screens; explicit aspect ratio for slides; physical units for print. Reflow digital interfaces intentionally rather than fixing them to a card-shaped canvas. For print exports, use the same geometry or a measured fixed export layout; do not guess a PDF from a responsive screenshot.

Keep repeated copy and values outside duplicated markup where practical. Controls should update actual state and output. Preserve intentional line breaks for fixed artwork without forcing those breaks on unrelated responsive text.

## Add only interactions that aid review

Choose controls that serve the brief: a state/variant switch for a component, an input for a simulator, slide navigation, or front/back and guide toggles for print. Use actual buttons and labeled inputs with understandable selected states. Keep review controls outside exported artwork. Do not add unrelated dashboard controls or animation.

Use the intended screen reading order and touch behavior. A fixed slide or print scene may scale or scroll within the review interface without distorting its geometry. Show final copy and real data when available; clearly mark demo values.

## Make the preview durable

For a portable single HTML file, embed permitted assets as data URIs or use documented local assets. Avoid accidental remote font/image dependencies. Do not add telemetry or upload code to a design preview. An existing website may retain its required approved APIs and asset pipeline; do not make it self-contained at the expense of its architecture.

When an inline-visualization environment provides a sandboxed iframe or CSP, preserve its required wrapper and security model. For an existing file the user asks to publish unchanged, follow [publishing-delivery.md](publishing-delivery.md); do not rebuild its wrapper to match a different template.

HTML and ordinary SVG use screen RGB. Only the print branch needs a separately labeled process-CMYK PDF; the browser preview is not a calibrated press proof.

## Verify observable behavior

Inspect a realistic desktop width and a narrow mobile width, such as 320–390 CSS px, or the specified device/slide target. Exercise relevant states and viewport transitions. Verify:

- Each variant, screen, slide, or side displays the intended content.
- Text, diagrams, controls, and required assets do not collide or clip unintentionally.
- Fonts and images actually load; punctuation and non-Latin glyphs render correctly.
- Controls work with pointer and keyboard; focus is visible and input changes affect the result.
- Required states survive resizing, and reduced-motion preference is respected when animation is used.
- Screen reading order remains coherent; slide navigation works; preview-only controls stay out of exports.

Measure layout bounds when a potential collision is hard to judge, then inspect the rendered view. A DOM measurement alone cannot prove the visible result is good.

When the brief includes a QR, generate it from the verified payload rather than drawing an imitation. Preserve a clear four-module quiet zone, square modules, and strong contrast. Decode the rendered QR and compare its complete payload with the target. A successful source-PNG decode does not validate the final preview or export.

For medium-specific checks, read [digital-interfaces.md](digital-interfaces.md), [interactive-explainers.md](interactive-explainers.md), or [print-production.md](print-production.md) as relevant.
