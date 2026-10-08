# How One Card Is Made: The Four-Layer Pipeline

## Why four layers, not one image

A card ends up as a GLB rendered in the browser with Three.js — it rotates, has parallax, feels holographic. But the GLB isn't generated directly. Blender composites it from four PNGs:

1. **Subject layer**: the person/object, centered, filling most of the frame
2. **Background layer**: the environment, giving depth and mood
3. **Lineart layer**: a glowing outline tracing the subject
4. **Text layer**: title, subtitle, series number, rarity badge

The reason: each layer sits on its own plane at a slightly different depth in WebGL, so rotation produces real parallax. A single flat image can't do this — at best you get a fake shift.

A separate text layer has a second benefit: changing language doesn't require redrawing the subject. The Ray card in Bengali, the horse card in Danish, the Reus card in German — all swapped only the text layer.

## Generation order and idempotency

The pipeline roughly runs:

```
one sentence → AI expands it into a design → four layers generated
→ matting (background removal) → text composited → Blender builds GLB
→ compression → publish to gallery
```

Every step must be idempotent: rerunning must not corrupt state. That rule was learned from actual failures.

## Real failures (kept on record)

- **make_thumb ordering bug**: the publish script generated the thumbnail, then cleared the old archive — so it deleted the thumbnail it just made. Broken thumbnails on the homepage. Our first real bug. The thumbnail function was fine; the call order was wrong. Three lines fixed it.
- **u2net model cache**: matting depends on a u2net model; sandbox caches get wiped, then it redownloads, a few minutes each time. Cache checks now live in the preflight script.
- **importmap idempotency**: the front-end module map was rewritten automatically, but the rewrite wasn't idempotent — running twice duplicated entries. Now it checks "if the key exists, skip," and CI has a dedicated test for it.
- **AI generation recovery**: a mid-pipeline generation failure used to abort everything, wasting the layers already done. Now it skips only the failed layer and regenerates.

## One judgment

Four layers buy a lot of freedom (each layer is tunable), at the cost of 4× the generation work. When producing cards in batches, I prioritize style consistency across layers over per-layer single-image quality — if consistency breaks, the whole batch is trash.

Layering is right, but you need batches and CI to hold it together. Freedom without constraint becomes chaos.
