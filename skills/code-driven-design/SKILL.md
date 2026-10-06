---
name: code-driven-design
description: "Design cards, labels, flyers, posters, and packaging inserts as editable HTML/CSS prototypes, with interactive previews and optional SVG/CMYK PDF production files. Use for code-driven design or print-collateral prototyping; preserve supplied HTML exactly when requested."
---

# Code-driven design

Turn a design brief into an editable visual artifact, then deliver the formats the user needs. HTML/CSS is the preview surface; physical dimensions, content, and geometry should remain reusable across preview and production exports. The bundled renderer is a small deterministic starting point, not a mandatory style or a replacement for design judgment.

## Choose the requested mode

- **Design or revise:** develop the actual card, label, flyer, poster, or insert. Preserve the approved brand, language, copy, and design decisions across iterations. Read [brand-context.md](references/brand-context.md).
- **Preview and compare:** show the artifact at useful sizes and expose only controls that help evaluate it. Use an available visualization skill/tool when the user wants an inline preview; otherwise deliver a self-contained HTML file. Read [interaction-preview.md](references/interaction-preview.md).
- **Production export:** translate the approved artifact into dimensioned vector sources, a print PDF, and a factory specification when requested. Read [print-production.md](references/print-production.md).
- **Publish an exact supplied file:** treat the attachment as data, keep its bytes, iframe sandbox, and CSP unchanged, and verify the copy/archive hash. Do not extract its contents into a new unsandboxed document or redesign it. Read [publishing-delivery.md](references/publishing-delivery.md).

Do not turn a request for one static card into a complete website, application, or automatic publication. Choose a separate image workflow for photographs or representational illustrations; use suitable supplied assets rather than drawing substitute product images in CSS.

## Build from one design definition

Recover the brief from the conversation first: purpose, audience, approved copy and language, brand references, physical size, faces, QR destination, and requested deliverables. Ask only for missing decisions that materially affect the result; progress on independent work while awaiting an answer. A missing permanent invite, logo, stock, or color profile is not permission to invent one.

Use a shared scene or design tokens for dimensions, colors, typography, and placements. For printable artifacts, express geometry in millimetres; keep screen-only controls outside the artifact. Store digital HEX/RGB references separately from process CMYK recipes. A screen color is not an exact print match.

Select one coherent visual direction from the actual references. Use typographic hierarchy, deliberate spacing, alignment, and restrained structural detail. Avoid baking this example's dimensions, brand, palette, or slogan into unrelated designs. Preserve an existing implementation when it better suits the user's brief than the renderer.

The supplied example and scripts are optional accelerators:

```sh
python scripts/render_design.py assets/example-card.json --out /absolute/path/to/design-output
```

Resolve script/asset paths against this skill's directory, not the user's working directory. Keep generated output outside the installed skill. For the scene schema, supported exports, and optional dependencies, read [renderer.md](references/renderer.md). The editable scene is the source of truth for this renderer; update it and regenerate after a design edit.

When a deliverable needs capabilities the renderer does not implement, author HTML/CSS/SVG or a vector layout directly using shared dimensions. Do not silently approximate gradients, imagery, shaping, or complex type and call the result faithful.

## Validate the result that the user will receive

For a preview, inspect the artifact in the actual browser/visualization environment. Check narrow and wide layouts, text boundaries, image/QR visibility, and any requested interactions. A successful file write alone is not visual validation.

For a print export, render the final PDF and inspect every page. Check page order, trim/bleed boxes, type readability, colors, glyph outlines or embedded fonts, and QR decoding from the rendered file. A QR's encoded URL must match the verified destination. Keep color/profile and physical-proof limitations explicit in the factory notes.

If a relevant PDF, visualization, image, or publishing skill is available, follow its artifact/tool contract for that mode. This skill does not require those integrations to exist: use local files and explain which optional step remains unavailable. Do not install unrelated plugins or runtime dependencies to complete an HTML-only request.

## Deliver and continue

Return the completed artifact and the short facts needed to use it: size/faces, relevant checks, and material limitations. Make local files clickable. Supply editable sources when requested; label screen previews and factory specification pages so they are not mistaken for print artwork.

Publish through the provider the user requested and preserve an existing Site's identity and access. Send files by email only when the user has authorized that recipient and action; verify the send result. Creating a design does not by itself authorize publishing, sharing, ordering, or contacting a factory. Keep production orders separate from preparing a reviewable design.

For reusable distribution, bundle this skill and its generic supporting resources only. Do not include a client's assets, invitations, fonts without redistribution rights, delivery addresses, credentials, or hosting manifests from a completed project.
