# Performance: Squeezing a Card from 47MB to 14MB

## Where the bloat came from

Cards are the heaviest thing in this project. One card = GLB (3D model) + four layers + thumbnail + preview video. Early on, a full card's asset set was about **47MB**. A dozen cards in the hall and the first screen collapsed — mobile users stared at a spinner for 10 seconds.

The framing that mattered: we weren't optimizing "one image," we were optimizing an *asset chain*. Every link slightly fat, and the sum explodes.

## What I did

Prioritized by *user perception*, not file size:

| Step | Change | Result |
|---|---|---|
| Background/lineart | WebP compression, drop wasted alpha | much smaller per layer |
| GLB | Simplify meshes + clean materials | noticeably smaller 3D |
| Thumbnail | Separate small-size version | instant homepage |
| Preview video | Load on demand, never blocks first screen | fetched only on detail pages |

Overall: **47MB → 14MB per card**, roughly 1/3.3. Today the 77 cards in the hall average **55KB per asset** online (post-WebP/GLB), the homepage renders small thumbnails, and everything else lazy-loads.

The repo itself was the other big line item. Historic asset revisions pushed `.git` to **996MB**; one `git gc` brought it to **124MB** — the gain was mostly dropping stale big-file references, not routine tidying.

## Failures I keep on record

- **Vendor over-deletion**: I trimmed front-end dependencies to slim the repo and nearly shipped a broken page because one page wasn't covered by CI. Since then, "deleting anything requires a CI pass" is a rule.
- **Compression isn't just resizing**: blindly shrinking images makes them blur. WebP parameters were tuned per layer — the text layer stays sharp at the cost of size, backgrounds can be crushed.

## One judgment

Optimize for the moment the user gives up. First screen is the lifeline; detail-page quality is the dignity line. Thumbnails + lazy loading on the home, full quality on detail — that trade-off is the most valuable step.

Numbers are results, not goals. The 47→14MB story isn't "we compressed"; it's "mobile users can actually open it."
