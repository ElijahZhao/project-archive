# HoloLab Studio White Paper · Source Register

> 素材调研记录（2026-09-29）。白皮书为「项目技术白皮书」：正文核心素材来自
> 本项目真实代码与文档；外部检索用于背景章节（AIGC 趋势、开源上游、申请标准）。

## A. 项目内部素材（第一优先级，read-only 引用）

| 素材 | 用途 | 目标章节 |
|---|---|---|
| holo-lab/docs/architecture.md | 系统分层架构、设计约束、数据流、可审计性 | ch03, ch06 |
| holo-lab/docs/ai-pipeline.md | 四层生成策略、提示词工程、rembg/OpenCV/字体管线 | ch04 |
| holo-lab/docs/graphics.md | Blender Cycles + Three.js 双路径、视差/镭射数学 | ch05 |
| holo-lab/docs/DEPLOYMENT.md | 静态展厅、GitHub Pages、CI、密钥安全 | ch06 |
| holo-lab/docs/blog-001-holo-pipeline-notes.md | 踩坑记录、工程叙事 | ch07 |
| holo-lab/README.en.md | 项目英文简介、功能清单 | ch01, ch02 |
| holo-lab/generator/scripts/*.py | 真实代码（ai_generate/run_pipeline/publish_card/build_card/export_web） | ch03-05 |
| holo-lab/gallery/ | 线上展厅（index/app.js/style.css/cards.json） | ch03, ch06 |

## B. 外部检索来源（背景与佐证）

### B1. AIGC 图像生成领域趋势（ch02）
- APATERO《AI Image Generation State of the Art 2026》2026-08-11
  https://www.apatero.com/blog/ai-image-generation-state-of-the-art-2026
  要点：2026 图像生成进入"效率优先"阶段，单图 API 价格下降约 60%；统一模型替代多工具。
- Tech Insider《Qwen-Image-2.1 … 7B Params》2026-09-21
  https://tech-insider.org/qwen-image-2-1-7b-open-weight-alibaba-2026/
  要点：开源小模型追赶闭源，图像生成向低成本高效演进。
- ICLR2026 Image Generation Papers 统计（Diffusion 133 篇为最大主题）2026-09-21
  https://en.papernotes.org/ICLR2026/image_generation/
  用途：说明扩散模型仍是研究主线（可作 ch02 引用）。

### B2. 开源上游与同类（ch02 credit / ch07 差异点）
- 人人都是产品经理《4 个 GitHub 开源项目》2026-09-22
  https://www.woshipm.com/ai/6466407.html
  要点：Holo Card Studio 开源项目——文字/参考图 → 可转动 3D 闪卡；本项目基于其改造。
- tznthou.github.io/holo-card（上游 demo 站点）2026-09-21
  https://tznthou.github.io/holo-card/
  要点：上游交互原型（拖拽/翻面/滑块）；本项目新增 AI 生成管线 + 静态化部署。

### B3. AI 硕士申请作品集标准（ch01 定位 / ch08 建议）
- Research.com《How to Build a Strong Resume for AI Master's Admission》2026-08-11
  https://research.com/online-degrees/artificial-intelligence/how-to-build-a-strong-resume-for-ai-masters-admission
  要点：端到端工程（预处理→训练→验证→部署）显著提升录取机会。
- Logicmojo《Top 7 AI Courses with Projects》2026-09-25
  https://logicmojo.com/top-7-ai-courses-with-projects/
  要点：可点击 demo 链接 + 文档化 tradeoff 是成熟工程思维证据。
- AI Master Paris-Saclay《Should I apply? / How to apply well》2026
  https://ai-master.lisn.upsaclay.fr/admissions/should-i-apply/
  要点：招生方鼓励 GitHub 个人项目展示编程与 ML 热情。

## 证据缺口与补搜
- 已覆盖：行业趋势（B1）、上游背景（B2）、申请标准（B3）。
- 缺口：3D/WebGL 前端技术对比（three.js vs 其他）——以项目内实测为准，不引入外部对比（避免无实证结论）；判定无需补搜。
