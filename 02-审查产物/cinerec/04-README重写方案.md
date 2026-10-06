# 仓库展示页重写方案 — CineRec（任务④）

- 仓库：`ElijahZhao/cinerec` @ `e4dbcba`
- 依据：修缮审查（任务③）结论 + 实测数据
- **状态：方案（未覆盖 `README.md`）** —— 遵守行为准则第 2 条「重写/覆盖类任务先出方案，经确认后执行」

> ⚠️ 前置依赖：本方案已按"修缮后"口径编写（D4 措辞、部署项、诚实口径对齐）。
> 但**展示截图（`screenshots/*.png`）仍是 2026-07-19 旧版**——需先按 M3 用当前 UI 重截，README 才算真正"基于最新版本"。本方案已在预览区标注该状态。

---

## 一、重写原则（事实先行）

**【事实】** 本页所有事实性陈述均已对照代码/数据核验，逐项依据见文末《事实性陈述与代码依据对照表》。版本号、功能、目录、命令、评测数字**全部以代码/JSON 为准**。

**本次相较现版的关键改动：**
1. D4：`Rigorous Evaluation` → `Reproducible Offline Evaluation`（对齐 ROADMAP B4 决策与正文诚实口径）。
2. D1/D3：删除 `cutting-edge` 等空洞形容词。
3. 技术栈部署项补全 Render(`lite`) + Streamlit(`full`)。
4. 新增「常见问题 FAQ」「更新日志」两节（现版缺失）。
5. 补 TMDB 署名（合规，S6，**待你核实条款后落地**）。
6. 用 `<details>` 折叠长内容，避免大段纯文字。

---

## 二、拟定 README 全文（供审阅）

```markdown
<div align="center">

<img src="https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=flat&logo=pytorch&logoColor=white" alt="PyTorch">
<img src="https://img.shields.io/badge/FastAPI-0.100-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/License-MIT-F5C518?style=flat" alt="License">

<br><br>

# 🎬 CineRec

**Multi-Modal Movie Recommendation System**

*Six recommenders on one codebase — from UserCF to a multi-modal NCF — with an offline evaluation whose numbers are reported as measured.*

[中文文档](#-项目简介) · [Live Demo](#-live-demo--在线演示) · [Demo](#-demo-preview) · [Quick Start](#-quick-start--快速开始)

</div>

---

## 🔗 Live Demo / 在线演示

One codebase, two runtime modes (`APP_MODE`), each on the free tier it fits
([ADR 0001](docs/adr/0001-dual-mode-deployment.md)):

| Mode | What it shows | Link |
|------|---------------|------|
| **`lite`** — product | The bilingual FastAPI web app. Recommendations come from a precomputed cache, so it runs in 512 MB. No account needed: click **游客体验 / Try as Guest**. | **https://cinerec-rfew.onrender.com** |
| **`full`** — companion | A Streamlit app that loads the trained PyTorch models and runs them live: live inference, the six-model comparison, the modality ablation, the cold-start study. | **https://cinerec-movie-recommend.streamlit.app** |

> Both are on free tiers and sleep when idle — the first visit can take a few
> seconds to wake. The companion lives in [`deploy/streamlit/`](deploy/streamlit/).

---

## 📖 项目简介

CineRec is a full-stack movie recommender that implements six models in ascending
order of complexity and evaluates all of them on the same leave-last-5-out split.
It ships a bilingual dark-cinema web frontend, a REST API, and a Docker build that
serves either mode.

CineRec 是一个全栈电影推荐系统，实现了 6 个复杂度递进的模型，并在同一个
leave-last-5-out 划分上统一评测。它包含双语暗色 Web 前端、REST API，以及可服务
两种模式的 Docker 构建。

---

## ✨ 核心亮点 / Key Features

- **6 个模型，一个真相源** — UserCF → ItemCF → SVD → NeuMF → LightGCN → MultiModalNCF；算法集合与加载方式集中在 [`models/registry.py`](models/registry.py)。
- **多模态融合（核心创新）** — Multi-Modal NCF 在 MLP 路径用 Content Tower 融合 Sentence-BERT 文本(384d)、ResNet-50 图像(2048d)、类型(18d)。
- **诚实的离线评测** — 单一 leave-last-5-out 划分，候选集剔除训练已见条目；正文明确标注 single-seed、不作显著性声明。
- **可解释 + 双语 + 双模式** — 每条推荐给出理由；EN/ZH；`lite`（预计算缓存）与 `full`（实时推理）同仓。
- **可观测** — 推理 LRU 缓存、`/api/metrics` 进程内延迟/吞吐、实测 Locust 报告 → [`reports/loadtest.md`](reports/loadtest.md)。

---

## 🖼 Demo Preview / 效果预览

> ⚠️ **待更新（M3）**：以下截图为 2026-07-19 版本，早于 2026-10-05 的 UI 改版。
> 执行本方案前需用当前前端重新截取，否则展示效果与产品不符。

### Recommendation Engine / 推荐引擎
<details><summary>展开查看</summary>

<img src="screenshots/recommend.png" width="800" alt="CineRec Recommendation Page">
</details>

### Movie Library / 电影库
<details><summary>展开查看</summary>

<img src="screenshots/movies.png" width="800" alt="CineRec Movie Library">
</details>

### Evaluation Dashboard / 评测看板
<details><summary>展开查看</summary>

<img src="screenshots/dashboard.png" width="800" alt="CineRec Evaluation Dashboard">
</details>

---

## 🏗 系统架构（节选）

```
Browser (dark/light, i18n, ECharts, GSAP + Lenis, canvas star field)
        │
   FastAPI REST  ── /api/auth · /api/movies · /api/recommend · /api/eval · /api/metrics
        │
   Model Layer (6, via models/registry.py)
        │
   Data Layer: SQLite + MovieLens 100K (100,000 ratings · 943 users · 1,682 movies)
```
（完整 ASCII 架构图沿用现版 `README.md:99-147`，此处折叠以缩短首屏。）

---

## 🚀 Quick Start / 快速开始

> **零训练启动**：训练产物、内容特征与 MovieLens 种子已随仓提交
> （[ADR 0002](docs/adr/0002-artifact-storage.md)），数据库首次启动自动 seed —— 全新 clone
> 无需下载或训练即可提供真实推荐。

### Docker（推荐）
```bash
git clone https://github.com/ElijahZhao/cinerec.git
cd cinerec
docker compose up --build        # APP_MODE=full by default
# Visit http://localhost:8000
```

### 本地
```bash
git clone https://github.com/ElijahZhao/cinerec.git
cd cinerec
make setup && make serve         # runtime deps only, no torch
# Visit http://localhost:8000
```
`APP_MODE=lite make serve` 完全跳过 torch，直接服务预计算的 `recs_cache.json` —— 即
免费常驻档所用的模式。

<details>
<summary>从零复现全部实验（可选）</summary>

```bash
make setup-train                 # torch + vision stack
make data                        # MovieLens 100K + enriched metadata
make features                    # Sentence-BERT + ResNet-50 content features
make train && make eval          # train all 6 models → eval_results.json
make ablation && make coldstart  # modality ablation + cold-start study
make charts                      # regenerate docs/*.png from measured results
make test                        # pytest suite
```
</details>

---

## 📊 Evaluation / 评测结果

（沿用现版三张表：模型对比 / 消融 / 冷启动，数字不变，逐项已核验。）

### Model Comparison on MovieLens 100K (leave-last-5-out)
| Model | HR@10 | NDCG@10 | HR@20 | NDCG@20 | Train Time |
|:-----:|:-----:|:-------:|:-----:|:-------:|:-----------:|
| UserCF | 0.0191 | 0.0035 | 0.0477 | 0.0060 | 0.1s |
| ItemCF | 0.0721 | 0.0142 | 0.1283 | 0.0199 | 0.25s |
| SVD | 0.2534 | 0.0532 | 0.3542 | 0.0664 | 0.47s |
| NeuMF | **0.3775** | 0.0838 | **0.5164** | 0.1121 | 48.4s |
| LightGCN | 0.2789 | 0.0615 | 0.4210 | 0.0804 | 16.4s |
| **MultiModalNCF** | 0.3627 | **0.0850** | 0.5133 | **0.1123** | 93.5s |

> **Honest reading**（保留现版）：单一划分上命中率最强的是 NeuMF；MultiModalNCF
> 仅在 NDCG 上领先——内容特征主要提升排序而非召回。single-seed，不作"最优模型"声明。

（消融表、冷启动表与两处 Honest reading 原样保留，见现版 `README.md:233-267`。）

---

## 🔧 Tech Stack / 技术栈

| Layer | Technologies |
|-------|-------------|
| **ML Models** | PyTorch, scikit-learn, `scipy.sparse.linalg`, Sentence-BERT, ResNet-50 |
| **Backend** | Python, FastAPI, SQLite, Uvicorn |
| **Frontend** | Vanilla JS (SPA), GSAP 3, Lenis, Canvas star field, ECharts |
| **Data** | MovieLens 100K + enriched metadata (plot summaries & posters) |
| **Deployment** | Docker / docker-compose · **Render free tier (`lite`)** · **Streamlit Community Cloud (`full`)** |
| **Quality** | ruff, black, pytest + coverage, pre-commit, GitHub Actions CI |

---

## 📁 Project Structure / 项目结构

（沿用现版 `README.md:334-381`，补 `deploy/hf-space/` 一行说明为"已否决方案记录"。）

---

## ❓ FAQ / 常见问题

<details><summary><b>为什么有 lite 和 full 两种模式？</b></summary>

`full` 需要 torch 并实时推理，`lite` 用预计算 `recs_cache.json` 换取极小内存占用——两者是同一代码库，由 `APP_MODE` 切换。详见 [ADR 0001](docs/adr/0001-dual-mode-deployment.md)。
</details>

<details><summary><b>新注册用户的推荐为什么是热门榜？</b></summary>

预计算缓存只覆盖已有用户；新用户不在缓存内，接口会回退到热门推荐并**显式标注**，而非报错。见 ADR 0001「Consequences」。
</details>

<details><summary><b>评测为什么只有 single split / single seed？</b></summary>

这是刻意的取舍：项目目标是展示算法取舍与工程规范，而非追求 SOTA。正文所有结论均标注 single-seed、不作显著性声明；如需多 seed，可改 `evaluation/runner.py` 重跑。
</details>

<details><summary><b>SVD 用的是 ALS 吗？</b></summary>

不是。文件名 `models/svd_als.py` 是历史命名，实现是 truncated SVD（`scipy.sparse.linalg.svds`），[ADR 0003](docs/adr/0003-algorithm-ladder.md) 已说明。
</details>

---

## 📄 License

MIT — see [LICENSE](LICENSE).

> Poster/overview metadata provided by the TMDB API. *(待核实条款后定稿 — S6)*

---

## 📝 Changelog / 更新日志

<details><summary>展开</summary>

- **2026-10-05** — UI：aurora 背景 + canvas 星空 + 字体改版；Streamlit 伴生应用独立目录与主题。
- **2026-10-05** — 部署：Render(`lite`) + Streamlit(`full`) 双档免费部署定稿（ADR 0001）。
- **2026-10-04** — 评测：6 模型统一评测 + 消融 + 冷启动实验；MLOps：LRU 缓存 + `/api/metrics` + Locust 压测。
- **2026-07-19** — 初始版本：UserCF / ItemCF / SVD / NeuMF + 前端 + 数据库。

> 详细过程记录见 [`docs/ROADMAP.md`](docs/ROADMAP.md)。
</details>
```

---

## 三、自查：本页所有事实性陈述及其代码依据

| # | README 陈述 | 依据（实测） | 判定 |
|---|---|---|---|
| 1 | 6 个模型，链序 UserCF→…→MultiModalNCF | `models/registry.py:13` `ALGORITHMS` | ✅ |
| 2 | 文本 384d / 图像 2048d / 类型 18d | `models/multimodal_ncf.py` 头注释 | ✅ |
| 3 | 100,000 ratings · 943 users · 1,682 movies | `wc -l data/raw/ratings.csv`=100000；unique users=943；`movies_enriched.json`=1682 | ✅ |
| 4 | 6 模型 HR/NDCG 表 | `data/processed/eval_results.json` 逐项一致 | ✅ |
| 5 | 消融 / 冷启动表 | `ablation_results.json` / `coldstart_results.json` 逐项一致 | ✅ |
| 6 | Python 3.10 badge | `.github/workflows/ci.yml:16` `python-version: "3.10"` | ✅ |
| 7 | PyTorch / FastAPI / MIT | `requirements-train.txt:6`；`requirements.txt:6`；`LICENSE:1` | ✅ |
| 8 | `make setup && make serve` / `make setup-train` 等命令存在 | `Makefile:28,60,31,...` | ✅ |
| 9 | Docker 多阶段 + 非 root + healthcheck | `Dockerfile:8-39` | ✅ |
| 10 | lite 用 `recs_cache.json`、full 实时推理 | `config.py:27`；ADR 0001 | ✅ |
| 11 | "零训练启动、首次 seed" | `api/main.py:70-72`；ADR 0002 | ✅ |
| 12 | 前端技术栈（GSAP/Lenis/ECharts/Canvas star field） | `frontend/index.html:12-13,14-15`；`frontend/js/particles.js` | ✅ |
| 13 | `/api/metrics` 与 Locust 报告 | `api/main.py:29-42`；`reports/loadtest.md` | ✅ |
| 14 | Live Demo 两个 URL | `README.md:29-30`（沿用现版，**未联网验证可达性**） | ⚠️ 未核实 |
| 15 | TMDB 署名 | `data/enrich_tmdb.py` 使用 TMDB；条款原文未核实 | ⚠️ 待核实 |
| 16 | Changelog 日期 | `git log --date=short` 各文件提交时间 | ✅ |

---

## 四、执行说明

- 本方案经你确认后，我将：
  1. （可选，建议先做）按 M3 重新截取三张截图；
  2. 用上述内容覆盖 `README.md`；
  3. 一并落地任务⑤的 D1–D6 去味改动；
  4. 视你指示提交并推送。
- **确认前不覆盖任何文件。**