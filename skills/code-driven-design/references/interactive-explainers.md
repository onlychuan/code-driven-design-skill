# Diagrams, interactive tools, and HTML presentations

Read this for an infographic, relationship/process explanation, simulation, interactive tool, or browser-based presentation.

## Match the form to the explanation

Identify what the viewer should understand or decide, the relationships to show, the source material, and the inputs or states worth exploring. Select a form that makes those relationships clear: a process diagram for sequence, a comparison for alternatives, a chart for quantitative change, or a simulation for input-dependent behavior. Use interaction only when it improves understanding.

A small static technical flow may be clearer as Mermaid or an SVG than as a full app. A complex explainer may need semantic HTML, diagram geometry, and interactive controls together. Use an available visualization skill for inline rendering when appropriate. For quantitative analysis, dashboards, or source-backed reports, use the relevant data skills rather than treating the request as pure decoration.

## Keep evidence and relationships inspectable

Use supplied data or verified sources. Record definitions, units, date/range, and assumptions that materially affect the result. Label example or synthetic data clearly. Preserve the distinction between measured observations, calculated outputs, and proposed scenarios; do not fabricate data to support the intended narrative.

In diagrams, give arrows a consistent meaning and make direction, grouping, and labels legible. Do not imply causation with an unlabeled arrow when the source only describes association. Check that displayed nodes and relationships match the actual source material and that labels are not clipped by their containers.

For a simulation, state the model's assumptions and valid input range. Implement a real computation or state mapping behind the controls. A slider should update the values, chart, geometry, or narrative it claims to influence. Use a reproducible seed for stochastic examples when needed to make comparisons interpretable. Do not imply that a simplified model predicts real outcomes beyond its stated basis.

## Make interaction explain the mechanism

Use labeled controls with units and understandable bounds. Surface the current input values and the resulting output together. Provide reset or a baseline comparison when it materially helps exploration. Avoid decorative controls that only animate a surface while the displayed information remains unchanged.

Keep source values and derived results in one data/state model. Test representative values, boundaries, and invalid input where applicable. Verify that each control affects the intended result and that combined inputs produce internally consistent output. Check the mobile layout and keyboard operation, and respect reduced-motion preference.

## HTML presentation behavior

For a browser deck, define the intended slide aspect ratio and viewing mode. Keep slide content inside that geometry while the surrounding viewer adapts to desktop/mobile. Implement the requested previous/next navigation and current-slide indication. Keyboard navigation should not intercept typing inside controls; focus and screen-reader reading order should follow the active slide.

On small screens, choose whether navigation starts the new slide at its top or restores that slide's own scroll position. Do not accidentally carry the previous slide's scroll offset into different content. Test navigation after scrolling a long slide.

Use motion to clarify sequence when it helps, with a reduced-motion alternative. A slide screenshot is not an editable deck. If the user requests PPTX or Google Slides, use the presentations skill and create the actual requested artifact; renaming an HTML file does not convert it.

## Choose export formats honestly

For scientific plots, research figures, or charts intended for publication/export, use standard plotting tools and export a standalone artifact. Keep equations, labels, source data, and numeric scales reviewable. Do not substitute generated imagery for a quantitative chart.

For an HTML explainer, deliver runnable source with the required assets and data/model notes. Use SVG for vector diagrams when appropriate and clearly label PNG as raster output. Inspect the exported artifact in its real format, including text, arrows, clipping, and any changed scaling.

Hosting follows [publishing-delivery.md](publishing-delivery.md) only when requested. Read [interaction-preview.md](interaction-preview.md) for common browser-rendering and input checks.
