# From Upstream Fork to a Standalone Project: How HoloLab Studio Grew

## Start: I borrowed a skeleton

The project didn't start from zero. I forked [EverettFish/holo-card-studio](https://github.com/EverettFish/holo-card-studio) (MIT license). The author built something interesting: one 3D holographic card = four AI-generated layers + a Blender-composited GLB + real-time Three.js rendering in the browser. Cards rotate, have parallax, feel holographic.

My reasoning for reusing it was plain:

- The rendering path (Blender → GLB → WebGL) is the slowest part to build from scratch;
- The upstream author had already made it work, so I inherited a working card pipeline;
- I wanted a product other people could use, not just another rendering demo.

## What I added

Borrowing a skeleton isn't copying homework. Compared to upstream:

| Layer | Upstream | What I did |
|---|---|---|
| Entry | Local scripts only | Web Create Studio: one sentence → auto-expanded design → submit |
| Display | Single card viewer | Exhibition hall + detail pages + curation timeline + auto tour |
| Submissions | None | Public GitHub-Issue flow; approved cards live in the hall forever |
| Language | English only | Bilingual UI; card content in 8 languages by theme |
| Privacy | None | Hidden-lock cards (password-gated, e.g. a friend's horse) |
| Quality | No hard rules | Five quality gates + 28 CI tests |
| Scale | A few sample cards | 77 cards across 11 series |

## What's upstream, what's mine

This matters because people ask. Honest split:

- **Upstream's:** the four-layer → Blender → GLB → Three.js rendering path, the initial directory layout, the MIT grant.
- **Mine:** the product shape (create studio, public submission flow, gallery interactions), most of the UI and motion, the i18n system, CI tests and quality gates, performance compression, curation and auto tour, and all 77 cards' concepts plus the tooling that makes them.

I changed far more than I kept. But I don't pretend I didn't borrow. The README has a dedicated "Upstream & Evolution" section that states the lineage — respect for the upstream author, and part of the project's credibility.

## One judgment

The holographic-card tech isn't hard. What's hard is getting a stranger to type one sentence, wait a few minutes, and leave their work in the hall. That's why most of the effort went into experience and process. Rendering is just the foundation.

The technical starting point is someone else's; the work is mine. I keep that line clear.
