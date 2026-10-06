# Websites, interfaces, and component states

Read this for a webpage, landing page, screen interface, or interactive component.

## Extend the real project when one exists

Inspect the repository's entry points, framework, routing, tokens, shared components, asset pipeline, and related views. Implement within those conventions. Reuse an existing component or flow before adding a parallel one. Do not replace a requested screen with an unrelated standalone app or change site-wide styling to satisfy one local view.

For a standalone concept, choose the smallest implementation that expresses the requested behavior. HTML/CSS with modest JavaScript is often enough. A production app request may require its existing framework and real integration. Keep a prototype's simulated persistence, API calls, or authentication clearly identified; do not present them as implemented services.

For a composed product website or campaign, use an available product-website workflow when it improves structure and implementation. If the user chooses Sites, use its installed building/hosting skills and tools. Local design work does not itself authorize deployment; read [publishing-delivery.md](publishing-delivery.md) when hosting is requested.

## Design in screen units and tokens

Use named CSS variables or repository tokens for color roles, spacing, type, radius, and elevation. Use rem/CSS sizing and responsive constraints appropriate to the interface; millimeters, bleed, crop marks, and CMYK are irrelevant unless a separate print deliverable is requested.

Let the layout reflow around its content and intended viewport. Prefer Grid/Flexbox and intrinsic sizing over reproducing every desktop coordinate with absolute positioning. Preserve the supplied information hierarchy and the site's navigation conventions. QR codes are optional content, not a default digital call to action.

For landing pages, connect sections into a coherent journey with a working primary action. Use supplied brand/product facts; distinguish hypothetical marketing copy and demo testimonials from factual claims. Do not insert invented customer counts, reviews, logos, or certifications to make the page appear complete.

## Implement relevant behavior and states

Map the requested interaction to state transitions before styling all its states. For example, a filter changes visible results; a quantity control changes the calculated total; a form distinguishes validation and submission outcomes. A button that only looks actionable is insufficient for a behavioral prototype.

Implement loading, empty, error, success, selected, disabled, or focus states when they occur in the requested flow. Do not add every state to a purely static component. Keep input and state in one source so the displayed result cannot drift from the control values. Preserve values on resize and make reset/undo behavior deliberate when offered.

Use semantic elements: buttons for actions, links for navigation, associated form labels, and headings in a meaningful order. Provide visible focus, usable keyboard interaction, readable contrast, and text alternatives for meaningful imagery. Do not rely solely on hover or color to reveal essential information. Respect reduced-motion preferences where motion is present.

## Verify the experience

Run the project's relevant existing checks and exercise the changed flow in a browser. Test the intended desktop/mobile viewports and the states that materially change geometry or behavior. Include long text, empty results, and validation errors when those can affect this flow.

- Confirm actions change the actual result, navigate to the intended target, or invoke the declared integration.
- Verify keyboard reachability, visible focus, labels, and logical reading order.
- Check responsive reflow, overflow, sticky/fixed elements, and modal/menu containment.
- Inspect rendered fonts/assets and loading/failure behavior where relevant.
- Use geometry assertions for suspected overlap, bounds, or offscreen controls; pair them with rendered inspection.

Choose automated tests for meaningful regressions, such as calculation, filtering, or state transition behavior. Do not create tests that merely repeat class names or the implementation. Report concrete validation and any simulated integration in the handoff.
