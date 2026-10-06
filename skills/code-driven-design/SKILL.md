---
name: code-driven-design
description: "Create and refine visual designs in code: logos and icon systems, responsive websites and interface prototypes, diagrams and infographics, interactive explainers, HTML presentations, cards and brand/print collateral. Use for code-driven visual design with editable source and real previews; not routine nonvisual coding, data analysis alone, or bitmap-only image editing."
---

# Code-driven design

Turn a visual brief into a designed, editable artifact by using code as the authoring medium. Connect visual choices to the audience's task, expose meaningful interactions, inspect the rendered result, and keep revisions in the source. HTML/CSS, SVG, canvas or an existing component framework can all serve this method. The physical scene renderer is an optional print helper, not the architecture for every design.

## Route by the artifact and its purpose

- **Logos, symbols and icon families:** design or refine brand marks, wordmarks, lockups, app/UI icons, or a consistent set of symbols. Distinguish using an existing identity, extending its icon family, and an authorized redesign. Read [logo-icons.md](references/logo-icons.md).
- **Websites and interface prototypes:** landing pages, product pages, app screens, components, or working surfaces. Reuse an existing project and design system; model the requested states and behavior. Read [digital-interfaces.md](references/digital-interfaces.md).
- **Diagrams, infographics and interactive explanations:** communicate relationships, processes, mechanisms or comparisons. Build real input-to-output behavior when interaction helps. This includes small calculators/simulations and HTML presentation decks. Read [interactive-explainers.md](references/interactive-explainers.md).
- **Brand and print collateral:** cards, labels, posters, invitations, flyers, packaging inserts and similar visual pieces. Read [print-production.md](references/print-production.md) only when physical output or factory specifications are requested.
- **Preview and comparison:** use the actual artwork, screen or visualization as the primary surface. Use an available visualization skill/tool for inline review; otherwise deliver a runnable local artifact. Read [interaction-preview.md](references/interaction-preview.md).
- **Publish an exact supplied file:** treat the attachment as data, keep its bytes, iframe sandbox, and CSP unchanged, and verify the copy/archive hash. Do not extract its contents into a new unsandboxed document or redesign it. Read [publishing-delivery.md](references/publishing-delivery.md).

Read [brand-context.md](references/brand-context.md) when a design needs brand evidence or a brief. Preserve approved language, copy, visual direction and decisions across revisions. Combine routes only when the deliverable calls for them; do not load every reference.

Match scope to the request. A website should be the requested website, a tool should expose its actual controls and outputs, and a poster should remain a poster. A logo/icon request needs usable assets, not only a picture inside a mockup. Screen and ordinary SVG asset work do not require trim, bleed, CMYK, factory notes or a QR code. Use image tools for photographs or rich representational illustrations; use code-native SVG geometry for vector marks and functional icons when appropriate.

## Use the same design method across formats

Recover the brief from the conversation: purpose, audience, content and language, brand/reference material, display context, meaningful interactions and requested deliverables. Add physical size, sides, QR destination and print conditions only for an applicable brief. Ask only for missing decisions that materially change the result; continue independent work while awaiting an answer.

Choose one concise visual thesis before authoring, then carry it through hierarchy, typography, color roles, spacing, grids, imagery and motion. Use shared design tokens plus structured content/state instead of duplicating layouts or hardcoding unrelated views. For logos/icons, keep reusable vector geometry and a consistent visual grammar; for websites, prefer responsive CSS/components; for diagrams, encode relationships/data consistently; for physical art, a millimetre scene can be appropriate. Use the renderer only when its geometry model fits.

Make controls change meaningful state or results. Keep design-review controls separate from the finished product. Do not invent backend persistence, live data, working checkout or successful submissions for a visual prototype; distinguish its implemented behavior from illustrative content. Do not add live services merely because they are common.

Select the smallest suitable starting point:

- [logo-icon-study.html](assets/logo-icon-study.html): vector asset study with actual-size previews and standalone mark/icon SVG exports.
- [interactive-interface.html](assets/interactive-interface.html): a self-contained responsive interface with working state.
- [interactive-explainer.html](assets/interactive-explainer.html): an SVG-based mechanism whose controls change the visualization.
- [example-card.json](assets/example-card.json) and the physical renderer: small dimensioned print pieces.

These are examples, not a universal theme, fixed screen structure or requirement to use a template. Copy/adapt only relevant files into the user's project. Keep generated artifacts outside the installed skill. For the physical helper:

```sh
python scripts/render_design.py assets/example-card.json --out /absolute/path/to/design-output
```

Resolve script/asset paths against this skill directory. Read [renderer.md](references/renderer.md) only when using the physical scene/schema/exports. Its JSON is the source of truth for that helper; for screen work the source of truth is the actual components, styles, content and state.

Use a specialist workflow when the requested final format or runtime calls for it: a full product website, motion, Figma editing, source-backed analytical charts, scientific figures, PPTX, DOCX or PDF. Apply this design method to its visual decisions, while following that workflow's tool/artifact contract. Do not fake a requested format by renaming an HTML file. Optional integrations should not block a local HTML/CSS design when they are unnecessary.

## Validate the result that the user will receive

Inspect the artifact in the actual browser/visualization environment. For logos/icons, open the standalone vectors, compare optical weight/spacing at their intended small sizes, inspect monochrome/background variants when needed, and identify text/font dependencies. For screens, check narrow/wide layouts, readable hierarchy, keyboard/focus and states. For explainers, verify relationships, results and source/assumption labels. For HTML decks, check navigation and requested export. A file write, DOM count or screenshot alone does not prove that interactions work.

When physical output is requested, additionally render every final PDF page and check order, trim/bleed boxes, physical type readability, colors and glyphs. Decode any requested QR from the export against the verified destination. Label print profile/proof assumptions. Do not apply these print checks to a screen-only artifact.

Recheck the changed behavior and affected views after an edit. Summarize the checks actually performed and any unimplemented behavior. Use available tools or local files as appropriate; do not claim visual, data or print verification that did not occur.

## Deliver and continue

Return the requested artifact and the short facts needed to use it: entry point, supported behavior/formats, relevant checks and material limitations. Make files clickable. Logo/icon work should include the requested individual vector files and any family/use notes, rather than only an HTML board. Supply editable source when requested; screen designs need not include factory files, and factory instruction pages should remain distinct from print artwork.

Publish through the provider the user requested and preserve an existing Site's identity and access. Send files by email only when the user has authorized that recipient and action; verify the send result. Creating a design does not by itself authorize publishing, sharing, ordering, or contacting a factory. Keep production orders separate from preparing a reviewable design.

For reusable distribution, bundle this skill and its generic supporting resources only. Do not include a client's assets, invitations, fonts without redistribution rights, delivery addresses, credentials, or hosting manifests from a completed project.
