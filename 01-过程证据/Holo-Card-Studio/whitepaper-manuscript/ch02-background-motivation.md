# 第二章 背景与动机（Background and Motivation）

## 一、为什么还要做一个图像生成 demo

By 2026, text-to-image models have become fast, cheap, and widely accessible. Per-image API prices have fallen by roughly 60% within a year, and efficient open-weight models have begun to close the gap with closed leaders. Public reports and conference statistics agree that diffusion-based image generation remains the dominant research line in the field. In this landscape, generating a single pretty picture is no longer a hard engineering problem — almost anyone can prompt a model and get a usable image. What remains genuinely hard is turning generative models into reliable, composable, product-grade systems: keeping identity consistent across layers, keeping text legible, keeping assets aligned, and keeping the whole pipeline reproducible.

HoloLab Studio was designed against that harder problem. The goal was never "make an AI draw a card". It was "build a system in which an AI-generated picture becomes a physical-looking object with parallax depth, holographic foil, crisp text, and a public URL — and do it in a way that can be rerun, audited, and extended". This framing matches what the author wants to prove in graduate applications: not fluency with one API, but the ability to design and ship an end-to-end AI application with engineering judgment.

## 二、个人动机

The author is an undergraduate in artificial intelligence, applying for AI and AI-adjacent master's programs. In application guidance from multiple universities, the recurring advice is that applicants should demonstrate real projects on public platforms such as GitHub, with an end-to-end workflow (preprocessing, modeling, validation, deployment) and a clickable demo link. A single classifier notebook is the baseline; a deployed, documented, reproducible system is the differentiator.

The author's motivation was therefore threefold. First, to exercise the full AI application stack — image generation APIs, computer vision preprocessing (matting and contour extraction), 3D graphics, real-time shaders, and static web deployment — in one coherent project. Second, to practice engineering honesty: the project records its own tradeoffs, failures, and workarounds rather than presenting only the finished result. Third, to create a public artifact that is both a portfolio piece and a genuinely usable tool: anyone can browse the gallery, interact with the cards, and read how they were made.

## 三、上游项目与署名边界

HoloLab Studio is a re-engineering of an open-source project, holo-card-studio, which is MIT-licensed. The upstream project already demonstrated a beautiful core idea: a card whose foil and parallax respond to the viewing angle, with drag-to-rotate and flip interactions. The upstream version, however, depends on a human artist or manual pipeline to prepare the layered assets — there is no automatic way to go from a sentence or a photo to a finished card.

The author's contribution is to close exactly that gap. HoloLab replaces the manual asset preparation with an automated, four-layer AI pipeline, adds idempotent publishing and static deployment so the result is publicly reachable, and re-implements the shader mathematics so the offline Blender render and the in-browser Three.js preview share one formula. Everything inherited from the upstream MIT project is preserved and credited; the codebase additions — the generation pipeline, the build and export scripts, the publishing workflow, the gallery front-end, and the documentation — are the author's own work.

## 四、问题定义

Formally, the project addresses the following problem. Given a short natural-language description or a reference photo of a subject, produce a complete holographic trading card (front face, back face, edge, foil, and typography) and publish it on the public web, subject to four constraints. The first constraint is reliability: the pipeline must either succeed with validated assets or fail with a clear reason; it must never silently emit broken output. The second is reproducibility: rerunning the same configuration must produce the same card, and every intermediate artifact must remain on disk for inspection. The third is cost: the per-card cost must be negligible, so the pipeline can be run many times during development and by other users. The fourth is a zero-backend constraint: the public gallery must be static — no server, no database — so hosting is free and the deployment is auditable end to end.

Chapters 3 through 6 show how each constraint is enforced in the architecture, the generation pipeline, the rendering path, and the deployment workflow.
