# Release validation

Version 1.0.0 uses behavioral checks instead of tests that only match wording.

## Local checks

- Official Skill Creator validator: valid frontmatter and finished scaffold.
- Portable plugin manifest: validated against the Agent Plugins 1.0 JSON schema.
- UTF-8 UI metadata: Chinese display name verified.
- Installer tests: fresh install, scope and hidden files, existing-install refusal, explicit update with preserved backups, incomplete-package refusal, unsafe destination refusal, existing-file refusal, Windows wrapper arguments.
- Windows PowerShell 5.1, PowerShell 7 and Git Bash exercised with directories containing spaces and Chinese characters.
- Renderer tests: escaped content, rejected active URLs and unsupported fields, finite geometry, QR capacity, Reed-Solomon parity, deterministic output, explicit overwrite, exact-file preservation and detection of changed bytes.
- Independent ZXing decoding: short URLs, multiple QR versions, and Unicode URL payloads.
- PDF checks: actual physical boxes, vector glyph paths, no RGB/text/image paint operators, process channels in 0–1, repeatable export and preservation after a failed required-font check.

## Independent workflow test

A separate agent used the skill to produce a **70 × 45 mm** two-sided support card with a blue/white palette, English front, Chinese back, **3 mm** bleed and QR target `https://example.org/manual`.

Both PDF pages were rendered and visually inspected. QR payloads decoded from the final PDF and narrow/wide browser previews. The Chinese factory note identified the CMYK values as unprofiled references. Font files were referenced locally and were not copied into the repository.

The first pass found a missing renderer reference; the reference was added and package links were then revalidated.

## CI

The GitHub workflow runs installer, renderer and PDF checks on Windows, macOS and Linux. Check the current commit's Actions result for its platform status. CI output is not an ICC proof, PDF/X certification or a physical finishing/transport test.
