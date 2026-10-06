# 第三章 系统架构（System Architecture）

## 一、设计目标与约束

The architecture follows five explicit constraints, all derived from the problem statement in Chapter 2. First, public availability: the gallery must be open to anyone, so the site is static and hosted on GitHub Pages, with no server-side code. Second, zero backend: the card manifest is `cards.json`, all assets are static files, and generation runs locally, so there is nothing to maintain or pay for. Third, quality control: the four-layer asset strategy gives every layer its own validation and fallback. Fourth, audibility: the pipeline, publishing script, CI workflow, and documentation all live in the repository, inspectable line by line. Fifth, cost: per-card generation is designed to be negligible, so iteration and public use are both affordable. These constraints are not decorations; they shape every decision in the sections below.

## 二、分层架构

The system is organized as four layers, which communicate only through standard artifacts on disk: `assets/*.png`, `card.blend`, and `web/`. This makes each layer independently replaceable and debuggable.

### （一）素材层（ai_generate.py）

The asset layer turns a card configuration into four PNG layers: a transparent subject, an environment background, a line-art sheet, and a typography layer. It calls the Seedream 5.0 API, then applies rembg for matting, OpenCV for contours, and a font renderer for text. Every layer is validated before acceptance; a known limitation（已知局限）is that subject and background are independent generations, so composition is not pixel-exact by construction.

### （二）生成层（run_pipeline.py）

The generation layer consumes the four assets and produces a finished card. It validates the inputs, ensures a portable Blender build with SHA-256 verification, builds the scene and renders the hero image, exports the GLB with placeholder material slots, and assembles the per-card web page. Each step writes to disk before the next step reads, which is what makes the layer rerunnable.

### （三）发布层（publish_card.py）

The publishing layer moves a generated card into the gallery. Its operations are idempotent: verify artifacts, generate a thumbnail, archive the card with shared dependencies, rewrite the import map to the shared vendor, and update the manifest with deduplication and newest-first ordering. Re-publishing the same card converges to the same state; this is verified in practice, not assumed.

### （四）展示层（gallery/）

The presentation layer is pure front-end: a waterfall homepage driven by `cards.json`, and per-card pages that load a GLB and rebuild the holographic shader in real time with Three.js. It contains no backend logic, and any static host can serve it. The interactive viewer runs entirely in the browser.

## 三、关键设计决策

### （一）为什么素材分四层，而不是一张整图

A single full-bleed image is flat: it cannot have parallax depth, a separate foil, or pixel-exact typography. The four-layer split maps one-to-one onto the Blender material nodes: subject moves forward, background recedes, line art glows on the contour, and text sits on the surface. Because each layer is an independent PNG, each can be generated, validated, and tuned separately. This is the foundation of the whole pipeline.

### （二）为什么线稿用程序化提取，而不是让 AI 重画

An AI redraw cannot guarantee pixel-level registration with the subject: position, scale, and contour would drift. Since the line art must glow exactly along the silhouette, HoloLab extracts it from the matted subject with OpenCV: the alpha channel yields the outer contour, Canny edges on the color image yield internal detail, and both merge on the same canvas. This is a deliberate divergence from the upstream project's manual tracing, and it removes a human bottleneck from the pipeline.

### （三）为什么展厅用共享 vendor 而不是每卡自带依赖

A per-card dependency copy would make gallery size grow linearly with card count. The shared `gallery/vendor/three/` directory plus an idempotent import-map rewrite brings the archive size per card from roughly 47 MB down to roughly 14 MB. The tradeoff is a coupling between cards and the shared vendor version, which the publishing script manages by rewriting import maps deterministically.

### （四）为什么 Blender 用便携版自动下载

Blender is large and system-dependent, so manual installation is a barrier to reproducibility. The ensure step downloads the official portable package and verifies its SHA-256 checksum; in restricted networks the package can be pre-seeded into `tools/`, and the pipeline detects and reuses it. This keeps the pipeline working on machines with no system Blender.

### （五）构图一致性如何缓解

The subject and background are two independent generations, so alignment is not guaranteed. The mitigations are threefold: prompts share one style prefix and the background prompt reserves empty space; parallax occlusion hides small misalignment as natural depth; and the tradeoff is documented in code and docs. In a portfolio, honesty about a tradeoff（不足如实记录）is more credible than hiding it.

## 四、数据流（一次完整发布）

A complete publish flows through five stages. First, `card-config.json` is read by the asset layer, which writes the four PNGs. Second, the generation layer validates assets, builds the scene, renders the hero, exports the GLB, and assembles the page. Third, the publishing layer generates the thumbnail, archives the card, rewrites the import map, and updates the manifest. Fourth, the repository is pushed to GitHub. Fifth, GitHub Actions deploys the gallery directory to Pages. Each stage consumes only what the previous stage wrote, so any stage can be re-run in isolation; this is the operational definition of reproducibility.

## 五、可审计性

Auditability is a first-class property. Every card keeps its work directory with raw AI outputs and matting results, plus a `verification.json` recording the Blender version, device, materials, and parameters. The publishing script is idempotent, so re-publishing removes the old archive and deduplicates the manifest. API keys live in a `.env` file excluded by `.gitignore`, so the public repository contains no secrets. Any reviewer can walk from a card on the website back to the configuration, code, and artifacts that produced it. The next steps（下一步）— asset compression, rotating previews, and auto-classification — are prioritized in Chapter 8, and the author recommends implementing them in that order.
