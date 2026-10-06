# CineRec 提升方案 / Improvement Roadmap

> 面向 **海外授课型 AI 硕士申请作品集** 的工程与实验深度提升方案。
> 定位：**诚信可信 + 工程规范 + 实验有深度 + 有 live demo + 可一键复现**。
> 状态：**代码层与公网部署均已完成** — Phase 0–6 主体全部落地。双模式已上线：`lite` 产品站 https://cinerec-rfew.onrender.com · `full` Streamlit 伴生 https://cinerec-movie-recommend.streamlit.app；联网复核两者可达（lite `/api/health` → 200 `{"status":"ok"}`，full → 303 跳 `share.streamlit.io` 鉴权，属正常唤醒）。验证：本沙箱 `pytest` 105 passed / 5 deselected（5 个浏览器 e2e 由 CI 的 `e2e` job 单独跑；神经模型用例已装 CPU torch 实跑）、全量覆盖率 92%（`evaluation/runner.py` 100%、`evaluation/visualize.py` 100%、`models/explain.py` 99%；神经三项 94–96%）、`ruff check` 零错误、lite 模式实测可用（鉴权 403 / 路径穿越 404 / 缓存真实分数）。CI 作业：`test`（ruff + 全量测试）、`e2e`（Playwright 旅程 + axe 无障碍断言；该 job 不装 torch，`evaluation.runner` 相关用例经 `pytest.importorskip` 跳过）、`docker`（lite/full 镜像构建 + `/api/health` 冒烟），另有周定时 `loadtest`；最新一次 push 三 job 全绿。前端文案（hero / `meta` / i18n）已与 README 口径统一，去除 "cutting-edge" 一类空洞形容词。
> **Phase 3.5（公网部署）与 3.7（Live Demo 链接）已完成**；**4.2 LightGCN 已完成**（算法阶梯升至 6 个：UserCF → ItemCF → SVD → NeuMF → LightGCN → MultiModalNCF，已接入评测/前端/测试/lite 缓存）；**Phase 5 MLOps 已完成**（LRU 推理缓存 + `/api/metrics` 指标 + Locust 压测 → `reports/loadtest.md`）。
> 计划条目仍以 `[ ]` 列出（作为方案清单保留）；实际完成状态以本行与仓库提交记录为准。
> 修订：v3.1 — 定向补审（新增 A6 鉴权宣称不实/A7 SVD 名不副实、XSS 气味、算法实现真伪核验、部署条款联网复核）。
> 修订：v3 — 基于 v2 的二次全仓复测（新增安全缺陷 S 类、上修 Phase 0.1 可行性结论、精确化 A4/B5、标注 optional 阶段）。
> 修订：v2 — 基于全仓库深度审计重写（修正 v1 的错误假设，新增完整性修复阶段）。

---

## 0. 目标与预期

让评审者在 5 分钟内确认三件事：

1. **系统真的跑得起来** —— 有公网链接、有截图、有真实数据。
2. **代码是专业工程师写的** —— 有测试、有 CI、结构清晰、可复现。
3. **作者懂推荐系统的门道** —— 能讲清算法取舍，有消融与冷启动实验，且**宣称与实现一致**。

**不做**：不追 SOTA、不写学术论文、不上大规模数据集、不引入重型基础设施。

---

## 1. 硬性约束

| 约束 | 说明 |
|------|------|
| 预算 | **$0，且无可用信用卡**（Oracle Always Free 需真实卡片验证，排除） |
| 沙箱算力 | 3 vCPU / ~5.8GB RAM / 无 GPU / 无 Docker |
| 目标区域 | 欧洲（德/荷）+ 英国/港新，1 年制授课型 MSc |
| 尺度 | 本科生作品集，**有上限，不做无限加码** |

---

## 2. 现状体检（v3.1 · 基于实测复现）

### 🟣 S 类：安全缺陷（v3 新增 · 与 A 类同级最高优先级）

> **实测确认，非推断。** 启动服务后 `curl --path-as-is` 复现成功。

| # | 问题（已实测确认） | 证据 |
|:-:|------|------|
| S1 | **任意文件读取（路径穿越）**：`api/main.py` 的 catch-all 路由直接 `os.path.join(FRONTEND_DIR, path)` 且无校验，`../` 可逃逸出前端目录 | 实测 `GET /../.env` 返回 **真实 `TMDB_API_KEY`**；`GET /../db/database.py` 返回完整源码（HTTP 200） |

**影响**：一旦按 Phase 3 部署到公网，等于公开泄露 `.env` 密钥、数据库与源码。**必须在任何公网暴露之前修复**，优先级等同诚信问题。
**修复思路**：先 `os.path.realpath` 规范化，再断言结果位于 `FRONTEND_DIR` 之内（`commonpath` 校验），越界即 404；仅对已知 index 走 SPA fallback。

---

### 🔴 A 类：诚信/一致性缺陷（最高优先级）

这类问题**直接影响作品集可信度**，一个细心的评审者发现后会大幅减分。

| # | 问题（已实测确认） | 证据 |
|:-:|------|------|
| A1 | **"多模态"名不副实**：`text_embeddings.npy` 与 `image_embeddings.npy` **全为 0**（实测 `nonzero=0/1682`）。所谓 Sentence-BERT 文本、ResNet-50 图像融合实际不存在，MultiModalNCF 只吃到了 genre + 行为 | 实测 npy 全零 |
| A2 | **README 宣称与实现不符**：① "fuses Sentence-BERT(384d), ResNet-50(2048d)" 不成立；② "Rigorous Evaluation" 不严谨（见 B4）；③ "Docker Ready 一键部署" 全新 clone 无法启动（见 B1/B2） | README vs 代码 |
| A3 | **冷启动声明未实现**：README/注释称"新物品走 content_emb，GMF 用零向量"，但 `MultiModalNCFNet.forward()` 无任何零向量分支 | `models/multimodal_ncf.py` |
| A4 | **误导性 fallback**：① 未知/缺失模型 → 随机电影 + **伪造分数**（0.95/0.92…）+ 由 explainer 附带的**貌似合理的解释**，界面不标注为"随机"；② **当前沙箱 torch 未安装**，请求 `NeuMF`/`MultiModalNCF` 实测返回 **HTTP 500**（`_load_model` 的 import 未包 try/except），并非走 fallback | `api/recommend.py` fallback；实测未知算法 / NeuMF |
| A5 | `docs/ablation_study.png` 基于**占位数据**（`ablation_results.json` 根本不存在）；而 `/api/eval/results` 因 `eval_results.json` 存在而返回**真实**数据，两者口径不一致 | `api/eval_api.py` |
| A6 | **"JWT-like" 鉴权宣称不实**：README 架构图写 `Auth Service (JWT-like)`，但全仓**无任何 JWT/token**，前端仅把 `user_id` 存入 localStorage；且 `/api/recommend?user_id=X` **无身份校验** → 猜 id 即可读任意用户推荐（越权） | README:97；`api/auth.py`；`frontend/js/app.js`；`api/recommend.py` |
| A7 | **"SVD/ALS" 名不副实**：README 称 k=64 隐因子"via alternating least squares"，实际 `models/svd_als.py` 用 `scipy.sparse.linalg.svds`（**截断 SVD**），`lambda_reg` 参数**完全未使用**；类 docstring 自述"truncated SVD" | README:136；`models/svd_als.py` |

> ✅ A1 好消息：`movies_enriched.json` 中 **1400/1682 条有 overview、1366/1682 条有 poster_url**，所以文本/图像特征**可以真算出来**，只是从没算过。

### 🟠 B 类：工程/部署缺陷

| # | 问题 | 证据 |
|:-:|------|------|
| B1 | **产物全部未入库**：`.gitignore` 排除 `*.pkl`/`*.pt`/`*.npy`/`data/processed/*.json`(除 eval_results)/`*.db`/`data/raw/*.csv`。实测 `git ls-files` 仅跟踪 `eval_results.json` 与 `docs/*.png` | `git ls-files` |
| B2 | **全新 clone 无法启动**：`api/main.py` 在 import 时执行 `init_db()`，会对**不存在的 `ratings` 表**建索引 → `OperationalError: no such table` | `db/database.py` |
| B3 | `docker-compose.yml` 依赖 `env_file: .env`，但 `.env` 被 gitignore → 全新 clone 直接报错 | 实测 `.env` 存在但被忽略 |
| B4 | **评测协议不严谨且模型间不一致**：未排除训练集；测试集每用户仅 1 项 → `HR@K ≡ Recall@K`（实测数值完全相同）；NeuMF/MultiModalNCF 未排除已交互，与 UserCF/SVD 不一致 | `evaluation/runner.py`/`metrics.py` |
| B5 | **新注册用户拿不到推荐**：模型 `num_users=944`（合法下标 0–943），凡 `user_id ≥ 944` 一律返回空列表。实测 `user_id=9999 → "total":0`；且**现有最大用户 944 本身也会失败**，范围比 v2 描述更大 | `api/auth.py` + 模型；实测 |
| B6 | `id_map.json` 是**死代码且与其他模块 ID 空间矛盾**（全仓无引用） | grep 确认 |
| B7 | 无 CI、无 lint 配置、测试仅 `tests/test_metrics.py` 一个文件 | 目录 |
| B8 | Dockerfile **已是两阶段构建**，但 runtime 仍完整拷贝训练依赖（torch/torchvision/sentence-transformers）→ 镜像臃肿；无 non-root；healthcheck 指向业务接口而非专用 `/api/health` | `Dockerfile` |
| B9 | `auth.py` 用**明文 sha256 无盐**，且错误信息区分"用户不存在/密码错误" | `api/auth.py` |
| B10 | **前端 XSS 气味**：`recommend.js` 用 `innerHTML` 直接拼接后端字段（title/poster_url/reason），未转义；数据虽多为自控来源，但属不良实践 | `frontend/js/recommend.js` |

### ✅ 已确认正常（无需修）

- 5 个模型文件**都在**（`ls` 实测：usercf/itemcf/svd 的 pkl + neumf/multimodalncf 的 pt）—— **v1 方案说"缺两个模型文件"是错的，此处二次更正。**
- ID 空间实际自洽：模型 `num_users=944 / num_items=1683`，索引即 MovieLens 原始 ID（0 号未用），与 `movies.id` 一致，推荐结果能正确映射到电影。
- **README 评测表的数字与 `eval_results.json` 逐项一致**（并非编造）；问题只在于**评测协议不严谨**（B4），不在数据真实性。
- 基线测试 `pytest -q`：**8 passed**（仅 `tests/test_metrics.py`）。
- 沙箱规格复核：**3 vCPU / 5.8GB RAM / 磁盘 1.3T 可用 / 无 GPU / 无 Docker**；**torch 系列当前未安装**。
- **算法实现已核验为真材实料**：UserCF 为向量化 Pearson、ItemCF 为向量化 adjusted cosine、NeuMF 为真 GMF+MLP 双路（含负采样与早停）；SVD 亦为真实矩阵分解（仅**命名/宣称**有误，见 A7）。→ **算法层不含水分，无需重复投入**，问题集中在"宣称"与"工程化"。
- **SQL 注入面已排查**：全仓数据库查询均为参数化，无 f-string 拼接注入。（纯前端项目，不做服务端渲染，SSR 类风险不适用。）

---

## 3. 总体架构决策：双模式部署

一套代码，`APP_MODE` 环境变量切换：

| 模式 | 运行时依赖 | 数据来源 | 宿主 |
|------|-----------|---------|------|
| **full** | torch + 模型文件 | 实时模型推理 | Streamlit Community Cloud（`streamlit_app.py` 伴生应用） |
| **lite** | 无 torch（numpy + fastapi） | 预计算 `recs_cache.json` | Render 免费 Web 服务（产品主站，常驻保活） |

```
沙箱训练（一次）→ GitHub 仓库（代码 + 模型产物）
                    ├── Render   (APP_MODE=lite)  → 产品主站（现有 FastAPI 前端）
                    └── Streamlit(APP_MODE=full)  → 实时推理伴生应用（六模型阶梯/多模态/冷启动）
```

> **产品前端不迁移到 Streamlit**：双语 FastAPI 前端仍是产品本体，由 Render 以 lite 模式承载；
> Streamlit 只是只读伴生，用来现场演示 full 模式。取舍见 [ADR 0001](adr/0001-dual-mode-deployment.md)。

---

## 4. 部署目标（$0 / 无卡）

| 平台 | 模式 | 规格 | 备注 |
|------|:---:|------|------|
| Render | lite | 0.1 CPU / 512MB | 产品主站；15min 休眠，**需保活**（`keepalive.yml`） |
| Streamlit Community Cloud | full | ~2.7GB / 2 vCPU（每应用独立） | 只读伴生应用；公开应用不限量，无自定义域名 |

> 已排除：**Hugging Face Spaces**（免费 Docker 层已取消）、**Northflank / Koyeb**（免费计划仍需绑卡）。
> ⚠️ 关键前提：平台从 GitHub 拉代码，**因此 B1（产物未入库）必须先解决**，否则线上是一套没有模型和数据的空壳。

---

## 5. 实施阶段

### Phase 0 · 完整性与安全修复（最高优先级）

**目标**：让"宣称"与"实现"一致（消除诚信风险），并堵死公网暴露前的安全漏洞。

- [ ] **0.1 真正计算多模态特征（对齐 A1/A2）—— 主路径，已确认可行**
  - **可行性已实测**：沙箱有网（走代理）；`huggingface.co` 不可达(000)，但 **`hf-mirror.com` 可达(200)**；`download.pytorch.org` 权重可达(200)；海报主机 **`m.media-amazon.com` 可达(200)**；pypi 可达(200)；磁盘 1.3T 空闲。**torch 系列当前未安装，需 pip 安装 CPU 版**。
  - 修改：`data/preprocess.py`（文本默认计算；图像改为按海报可用性默认计算）
  - 执行：文本用 Sentence-BERT（`movies_enriched.json` 的 overview，**1400 条**），设置 `HF_ENDPOINT=https://hf-mirror.com`；图像用 ResNet-50（**1366 条** poster_url，域名 `m.media-amazon.com`）
  - 产出：**非零的** `text_embeddings.npy`、`image_embeddings.npy`
  - **降级兜底（仅当上述路径失败时启用）**：README 如实改写为"genre + 行为"，不再宣称文本/图像 —— 绝不保留虚假宣称
- [ ] **0.2 实现或删除冷启动声明（对齐 A3）**
  - 二选一：在 `MultiModalNCFNet.forward()` 实现"新物品零向量 GMF 分支"，或删除 README 相关描述
- [ ] **0.3 消除误导性 fallback（对齐 A4）**
  - 修改：`api/recommend.py` —— 模型缺失/未知算法时返回**明确错误/提示**，禁止伪造分数；**且不得对随机结果附加"相似度"解释**；`_load_model` 的 import 包 try/except，torch 缺失时给出可读错误而非 **HTTP 500**
- [ ] **0.4 消融数据落地或撤回图表（对齐 A5）**
  - 由 Phase 4 产出真实 `ablation_results.json`；在此之前从 README/docs 撤下基于占位数据的图（`docs/ablation_study.png`）
- [ ] **0.5 修正 README 宣称（对齐 A2/A6/A7）**
  - 逐条把宣称与实现对齐：① 多模态特征（A1/A2）；② **删除/改写 "JWT-like"** —— 实际无 token，二选一：如实描述为"无状态演示级登录"，或补齐真实鉴权（推荐前者）；③ **"SVD/ALS" → "SVD（truncated SVD）"**，或改写成真实 ALS（推荐前者，成本低）；④ "Rigorous Evaluation" 措辞随 B4 修正
- [ ] **0.6 修复路径穿越漏洞（对齐 S1）**
  - 修改：`api/main.py` 的 `serve_frontend` —— `os.path.realpath` 规范化后用 `os.path.commonpath` 校验必须位于 `FRONTEND_DIR` 内，越界返回 404；补一条回归测试断言 `GET /../.env` 不可读
  - **注**：`.env` 中的 TMDB key 既然已进入 git 历史之外的工作区，修复后应**轮换该 key** 并改由环境变量注入

**验收标准**：① README 任意一条宣称，都能指出对应实现与数据；② `text/image_embeddings.npy` 非零（或已如实降级）；③ `GET /../.env` 与 `GET /../db/database.py` 均返回 404；④ 不再存在 "JWT-like"、"ALS" 等与实现不符的表述。
**停止线**：不做超参调优，不追指标。

---

### Phase 1 · 可复现性修复（原 v1 Phase 0+2 的部署前提）

- [ ] **1.1 修复全新 clone 无法启动（B2）**
  - 修改：`db/database.py` 的 `init_db()` → 改为幂等建表（`CREATE TABLE IF NOT EXISTS`），不再对不存在的表建索引
- [ ] **1.2 产物入库策略（B1）**
  - 方案：解除对**必要产物**的忽略并提交（模型 + 特征 + `movies_enriched.json` + 种子数据）
  - **实测体积**：合计约 **76MB**（`model_itemcf.pkl` 35MB、`model_usercf.pkl` 20MB、`image_embeddings.npy` 13.8MB、`text_embeddings.npy` 2.6MB、`model_svd.pkl` 2.5MB、两个 `.pt` 各 <1MB 等）；**单文件最大 35MB < GitHub 100MB 上限**，故 **LFS 非必需**，先做**瘦身**（pkl 内 float64 → float32、去冗余矩阵）即可
  - 决策点：产出 ADR 记录取舍
- [ ] **1.3 修复 docker-compose（B3）**
  - 修改：`docker-compose.yml` 改为 `env_file` 可选 / 提供 `.env.example` 自动复制
- [ ] **1.4 依赖拆分**
  - 新建：`requirements-train.txt`（迁出 `torch`/`torchvision`/`sentence-transformers`/`matplotlib`/`seaborn`）
  - `requirements.txt` 仅保留运行时（numpy/pandas/scipy/scikit-learn/fastapi/uvicorn/pydantic/requests/python-dotenv）
- [ ] **1.5 修复 Dockerfile（B8）**
  - 已是两阶段；进一步**非 root、按 `APP_MODE` 安装**（lite 不装 torch）、healthcheck 指向 `/api/health`、支持 amd64/arm64
- [ ] **1.6 基线测试**
  - 命令：`pytest -q`（当前基线：**8 passed**）

**验收标准**：`docker-compose up` 全新 clone 可启动并出推荐。
**停止线**：不做无关重构。

---

### Phase 2 · 工程规范

- [ ] **2.1 工具配置**：`pyproject.toml`（ruff + black + pytest + coverage）、`.pre-commit-config.yaml`
- [ ] **2.2 测试补齐**：`tests/test_api_auth.py`、`test_api_movies.py`、`test_api_recommend.py`、`test_api_eval.py`、`test_models.py`、`test_preprocess.py`，核心路径覆盖 ~50–60%
- [ ] **2.3 CI**：`.github/workflows/ci.yml`（ruff → pytest --cov → docker build）
- [ ] **2.4 修 B5（新用户无推荐）**：凡 `user_id ≥ num_users`（含现有最大用户 944）定义明确行为 —— 要么映射到可用推荐主体（冷启动走热门/内容兜底），要么返回带**明确说明**的降级结果；允许为此在 `frontend/js/recommend.js` 加一句提示（仅此一处放宽"不改前端"）
- [ ] **2.5 修 B6（删除死代码 `id_map.json` 及其生成逻辑）**
- [ ] **2.6 修 B9（密码加盐；统一错误信息）**
- [ ] **2.7 修 B10（前端 XSS 加固）**：`recommend.js` 渲染改用 `textContent`/`createElement`，或对不可信字段统一转义
- [ ] **2.8 修 A6 越权（与 0.5 配套）**：`/api/recommend` 增加演示级身份校验（会话 user_id 与请求一致）；若不实现，则 README 不得宣称有鉴权

**验收标准**：CI 全绿；`ruff check` 零错误。
**停止线**：不追 90% 覆盖率、不做端到端 UI 测试。

---

### Phase 3 · 部署上线

- [ ] **3.1 预计算脚本**：`scripts/precompute.py` → `data/processed/recs_cache.json`（**全部现有用户 id 1–944** × 6 算法；新注册用户走 Phase 2.4 定义的兜底）
- [ ] **3.2 双模式改造**：`api/recommend.py` 按 `APP_MODE` 分流；lite 模式对**无缓存/无 torch 的算法**返回明确提示而非 HTTP 500；新增 `/api/health`（修复 B8 healthcheck）
- [ ] **3.3 集中配置**：`config.py`（路径/模式/缓存开关）
- [ ] **3.4 部署配置**：`render.yaml`（lite 主站），`deploy/streamlit/`（full 伴生）
- [ ] **3.5 实际部署**：Render(lite，新账号) + Streamlit Community Cloud(full，现有账号)
- [ ] **3.6 保活**：`.github/workflows/keepalive.yml`
- [ ] **3.7 README 增加 Live Demo 区**

**验收标准**：≥2 个公网链接可打开、可登录、可出推荐。
**停止线**：不买域名、不配 CDN/HTTPS 自动化。

---

### Phase 4 · 模型层深度（有限度）

- [ ] **4.1 修正评测协议（B4）** —— 统一排除训练集；补充候选集说明；使 HR/Recall 不再等价
  - 修改：`evaluation/runner.py`、`evaluation/metrics.py`
- [ ] **4.2 现代 baseline**：`models/lightgcn.py` —— *（optional：加分项，时间不足可砍）*
- [ ] **4.3 冷启动实验**：`scripts/coldstart_experiment.py` → `coldstart_results.json` + `docs/coldstart.png`
- [ ] **4.4 消融实验**：`scripts/ablation_experiment.py` → 真实 `ablation_results.json`（同时兑现 Phase 0.4）
- [ ] **4.5 更新结果与图表**：`eval_results.json`、`docs/*.png`

**验收标准**：一张"冷启动下多模态领先"图 + 真实消融表 + 协议说明（LightGCN 对比行若做 4.2 则含）。
**停止线**：不做多 seed + t-test、不做超参搜索、不加第 7 个模型。

---

### Phase 5 · MLOps 与性能（*optional：授课型 MSc 非必需*）—— ✅ 已完成

- [x] 推理缓存（LRU，full 模式，键 = 算法 × 用户 × 已评分集）、调用量/延迟指标（`api/metrics.py` + `/api/metrics`）、Locust 压测（`scripts/locustfile.py`）→ [`reports/loadtest.md`](../reports/loadtest.md)
  - 实测：lite 模式 30 用户 / 30s → **913 请求、0 失败、≈30.8 req/s**；`/api/recommend` p50=5ms / p95=10ms。

**停止线**：不搭 MLflow、不做自动重训、不上 K8s。

---

### Phase 6 · 文档与呈现

- [ ] README 升级（徽章 + Live Demo + 实验表 + 一键复现）
- [ ] ADR（`docs/adr/`）：双模式部署、产物入库策略、算法选型
- [ ] `Makefile`（`make setup/train/test/serve`）

---

## 6. 明确不做

- 不上 25M/Amazon 数据集；**不重构前端**（仅允许 Phase 2.4 的降级提示与 Phase 2.7 的 XSS 加固）；不追 SOTA/写论文/多 seed 显著性检验
- 不引入 Spark/Flink/K8s/MLflow
- 不迁移到 Streamlit（现架构工程含金量更高）
- **不保留任何无法被代码/数据支撑的宣称**

---

## 7. 风险与对策

| 风险 | 对策 |
|------|------|
| 文本/图像特征计算需联网下载模型权重 | **已实测**：`hf-mirror.com` 可达、PyTorch 权重与海报主机可达 → 主路径设 `HF_ENDPOINT=https://hf-mirror.com`；若仍失败，如实改写 README，不造假 |
| `.env` 密钥已可经路径穿越读取 | Phase 0.6 修复后**轮换 TMDB key**，改环境变量注入；`.env` 保持不入库 |
| 产物入库体积大 | 实测约 76MB、单文件 <100MB → 瘦身（float32/去冗余）即可，LFS 非必需；ADR 记录 |
| Streamlit 伴生应用无自定义域名 | 用 `*.streamlit.app` 子域；产品主站域名仍由 Render 提供 |
| Render 休眠冷启动 | 定时保活（`keepalive.yml`）；Streamlit 伴生应用访问时自动唤醒 |
| 免费层文件系统临时 | 启动时 seed；或用平台免费 DB |

---

## 8. 执行顺序与评估

```
Phase 0（完整性与安全）→ 1（可复现）→ 2（工程规范）→ 3（部署）→ 4（模型深度）→ 5（性能，optional）→ 6（文档）
```
每阶段完成后给验收点；执行时再展开为细粒度 TDD 任务（先测试、后实现、频繁提交）。

> **v3.2 宿主定案**：联网复核后，**Hugging Face Spaces 免费 Docker 层已取消**，**Northflank / Koyeb 免费计划仍需绑卡**，故最终宿主定为 **Render（lite 产品主站，新账号）+ Streamlit Community Cloud（full 伴生应用）**；产品前端**不迁移**到 Streamlit。理由与取舍见 [ADR 0001](adr/0001-dual-mode-deployment.md)。
>
> **v3.1 相对 v3 的修正**：定向补审后新增 **A6**（"JWT-like" 宣称不实 + 无鉴权越权）与 **A7**（"SVD/ALS" 名不副实），并入 Phase 0.5；新增 **B10**（前端 XSS 气味）并入 Phase 2.7；新增 Phase 2.8（`/api/recommend` 越权）；补充"算法实现已核验为真材实料"与"SQL 注入面已排查"两条 ✅ 结论；联网复核 Northflank/HF/Render 免费额度与方案假设一致（**方向不变**）。
>
> **v3 相对 v2 的修正**：新增 **S 类安全缺陷**（实测路径穿越可读 `.env`）并纳入 Phase 0.6；**上修 Phase 0.1 可行性**（沙箱可经 `hf-mirror.com` 等下载，真算特征列为主路径）；精确化 A4（含伪造解释、torch 缺失返 500）与 B5（含现有用户 944）；订正 overview 数量、海报域名、产物体积与用户数；将 LightGCN 与 MLOps 标为 optional。
>
> **v2 相对 v1 的修正**：删除"补训缺失模型"（模型其实都在）；新增 Phase 0 诚信修复；把"产物入库/全新 clone 可启动"提到部署之前；补入评测协议、死代码、新用户无推荐、密码安全等实测发现。