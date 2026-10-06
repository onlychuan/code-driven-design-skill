# Vector artwork and factory handoff

Read this when the user requests printable files or factory production specifications.

## Export the accepted scene

Use the selected variant, exact approved copy, and verified QR target. Export SVG and PDF from the shared scene or an equivalent measured fixed layout. Do not recreate the artwork by eye from a screenshot. Keep an editable scene or source alongside outlined artwork so later copy changes remain possible.

HTML and ordinary SVG are RGB preview/source formats. Export process-CMYK PDF separately and label the difference. Browser “Print to PDF” may be suitable for an RGB review copy; it does not automatically provide controlled CMYK, press page boxes, outlined text, or PDF/X compliance.

## Set geometry before drawing

Use the printer's specified trim, bleed, safe area, and mark placement when available. If proposing values, label them as working specifications. Bleed and safe margins are not universal requirements of a particular size.

For trim `W × H`, bleed `b` on each side, and outer mark space `m`:

```text
MediaBox = (0, 0, W + 2b + 2m, H + 2b + 2m)
BleedBox = (m, m, m + W + 2b, m + H + 2b)
TrimBox  = (m + b, m + b, m + b + W, m + b + H)
```

Convert all coordinates to PDF points. Extend edge backgrounds through the bleed. Keep crop marks outside the bleed. Keep type and the entire QR quiet zone inside the declared safe area. Label front/back page order and reading orientation; do not invent imposition or duplex flipping without printer instructions.

## Fonts and artwork remain vector

Embed licensed fonts or outline correctly shaped glyphs. Preserve actual weight, kerning, tracking, and language shaping; test accented punctuation and CJK characters when used. A Latin font's missing glyphs cannot be fixed by shrinking text. Do not include proprietary local fonts in a public repository without redistribution rights.

For glyph outlines, use the font's intended contour winding and nonzero fill rule; verify counters such as the holes in `O`, `B`, and `8` after export. Keep the editable text in source even if the final print PDF is outlined. Outlining is not a substitute for checking the font license.

Keep rules, logos, and QR modules as paths wherever practical. Do not flatten the entire card into a screenshot. Check raster imagery's effective resolution at its placed physical size and disclose any material limitation.

## Color specifications need honest labels

Give the factory a table containing color role, digital HEX/RGB reference, and working process-CMYK percentages. A direct numerical RGB-to-CMYK calculation is an **unprofiled working reference**, not an exact match. Printer-selected output ICC profile, stock, finish, and a physical proof determine the final result. Keep ICC-profile names and conversion assumptions with the job record when they are actually used.

Choose fine black text and QR black as single-channel K where appropriate; choose rich-black backgrounds with the printer for the actual stock and ink limit. On ordinary white stock, a white knockout is unprinted paper, not a promise of white ink. Do not assign a Pantone match from appearance or claim PDF/X compliance from a filename, metadata tag, or DeviceCMYK colors alone.

Keep stock, finish, quantity, corner treatment, and output profile as approved values or explicitly marked suggestions/TBD. A job ticket can be in the factory's language while leaving the customer-facing card copy unchanged.

## QR sizing and verification

Preserve a four-module quiet zone on all sides. If the symbol has `n` modules and total allocated side length is `s` mm, the module pitch including that zone is `s / (n + 8)` mm. Choose physical size with symbol density, print resolution, stock, and finishing in mind. State the chosen error-correction level; do not treat ECC Q or a 25 mm square as universal defaults. Avoid logos, decoration, or rounded modules that impair the production target.

Render every final PDF page with a PDF renderer, inspect at useful zoom and actual intended scale, and decode the QR from the rendered back page. Compare the decoded full payload with the intended target. Inspect page boxes, page order, artwork bounds, vector paths, fonts, and color spaces rather than relying only on a screenshot. Recheck affected pages after a repair. A final physical sample should be scanned after finishing before a full run.

Deliver a focused package: print PDF, vector/source artwork, preview, factory/color sheet, and a manifest identifying the chosen version and remaining print assumptions. Avoid calling a package “press certified” when only local checks were performed.

## Primary references

- [DENSO WAVE: QR area and four-module margin](https://www.qrcode.com/en/howto/code.html)
- [Adobe: printer marks](https://helpx.adobe.com/indesign/desktop/print/page-set-up-and-printer-marks/set-printer-marks.html)
- [Adobe: printing with color management](https://helpx.adobe.com/ca/indesign/desktop/print/color-output-and-separations/use-color-management-when-printing.html)
