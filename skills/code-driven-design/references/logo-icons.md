# Logos and icon families

Read this for an SVG logo, wordmark, brand lockup, or icon family. It is a visual-design branch, not a reason to route every coding request through this skill.

## Establish identity and intended use

Use the supplied brand name, purpose, audience, existing assets, and intended placements. Inherit an existing logo or icon system unless the brief requests a new design or redesign. Designing a card or webpage does not itself request a replacement brand identity. Preserve approved names, spelling, symbol meaning, and family conventions.

Distinguish the requested asset:

- **Mark:** the identifying symbol, usable without lettering where recognition allows.
- **Wordmark:** the brand name expressed through a specific typographic treatment.
- **Lockup:** an intentional arrangement of mark and wordmark, with documented spacing and orientation.
- **Icon family:** symbols for actions or concepts, with consistent geometry and visual weight.

Choose variants by use: navigation, favicon, app control, packaging, signage, or a larger brand presentation can require different detail and proportions. A logo and a UI icon do not need identical construction rules. Keep proposed design direction distinct from an approved final identity.

## Build suitable artwork in native code

Use SVG paths and simple geometry for marks and icons that benefit from editable vector construction. Inspect and extend an existing icon system instead of introducing a different stroke style. Reuse assets according to their actual license and attribution requirements; availability in a repository or website does not establish redistribution permission.

For rich painted textures, photographic detail, or illustrative raster art, use an available image workflow when appropriate. A raster image embedded in an SVG remains raster; do not call it a vector logo. Do not retrace arbitrary brand assets and claim the result is original.

Keep SVG source readable: useful grouping, intentional transforms, clean geometry, and no unnecessary editor metadata. Simplification must preserve shape, counters, strokes, and negative space. Avoid adding gradients or effects that cannot survive the intended small-size or monochrome use.

## Give a family coherent geometry

Define the relevant grid/viewBox, key lines, padding, stroke width, linecaps, joins, optical weight, and negative-space treatment. Follow the project's existing icon conventions when available. Use optical adjustments when equal numerical dimensions make one symbol appear heavier or off-center; document exceptions instead of forcing every silhouette into the same bounds.

Inspect at the intended rendered sizes, commonly 16, 20, 24, or 32 CSS px for UI icons. These are test examples, not required sizes for every asset. Check recognizability, stroke clarity, pixel alignment, and gaps at actual size; enlarged inspection alone is insufficient. A purpose-built smaller variant can be clearer than scaling down the detailed original.

For logos, inspect the required monochrome, reverse, small-size, horizontal, or stacked variants according to the brief. Verify them against the intended light/dark backgrounds. Define useful clear-space and minimum-use guidance from the actual geometry and tests rather than inventing a universal ratio.

## Handle lettering and SVG integration

For live-text wordmarks, identify the font, weight, shaping, license status, and runtime dependency. For portable final artwork, outline correctly shaped licensed glyphs when appropriate and retain editable text/font information in the source. Verify kerning, punctuation, and counters after conversion. Do not claim font permission merely because a local font is installed.

Deliver script-free SVG without external references. Use the intended root `viewBox` and preserve aspect ratio. Internal gradients, masks, clip paths, and titles may use local IDs; make those IDs unique per inline instance and update their references so repeated use on one page cannot collide. Verify multiple instances when the asset is intended for inline reuse.

A meaningful inline SVG needs an accessible name, such as a referenced title or a label on its containing control. Keep title/description IDs unique. A purely decorative icon should be hidden from assistive technology and should not create an extra keyboard stop. An icon inside a labeled button does not need a duplicate announced name.

Choose the embedding mode deliberately. An inline SVG can use CSS `color` and `currentColor`; a standalone export should also have a useful default color. An SVG loaded through `<img>` is a separate image document and does not inherit the page's `color`, so supply the intended variant rather than assuming an ancestor color will recolor it. Verify both modes when both are part of delivery.

## Render, export, and hand off

Render the actual SVG in a browser at target sizes and backgrounds. Inspect clipping, fills, stroke behavior, text dependencies, and repeated inline instances. Check that the vector source contains paths/geometry rather than a flattened screenshot.

Export transparent PNG only when requested or needed by the destination, with explicit dimensions and verified alpha/background behavior. Export PDF when the destination needs it; a physical print export follows [print-production.md](print-production.md), while ordinary SVG/PNG remains a digital RGB asset. Do not invent Pantone matches or certified production claims.

Deliver the editable source, clearly named approved variants, requested exports, and a concise family/usage guide. Browser downloads can be blocked inside a sandbox; write and validate actual SVG files through the available file tools rather than relying only on a preview's download buttons. Document grid, strokes, spacing, naming, font dependencies, and licenses that actually apply. A visual design does not establish trademark uniqueness or legal clearance; avoid making either claim.

For brand-source decisions, read [brand-context.md](brand-context.md). Use [interaction-preview.md](interaction-preview.md) if an interactive asset comparison helps review; the final logo or icon itself need not be an interactive page.
