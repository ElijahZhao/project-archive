# 卡片制作全流程时间开销分析与优化方案

> 文档创建：2026-10-01
> 适用范围：HoloLab Studio 单张全息卡从配置到上线的完整流程
> 核心原则：**所有优化均不改变 card.glb 生成过程，3D 全息卡本身质量完全不受影响**

---

## 一、当前全流程时间开销

### 阶段一：本地准备（沙箱 VM）

| # | 步骤 | 耗时 | 说明 |
|---|---|---|---|
| 1 | 写 card-config.json | ~30 秒 | 手动 |
| 2 | AI 生成主体图 | ~15-30 秒 | Seedream API |
| 2.1 | ↳ rembg 抠图（含 u2net 模型下载） | ~5-25 秒 | 首次需下 ~50MB 模型 |
| 3 | AI 生成背景图 | ~15-30 秒 | Seedream API |
| 4 | 文字层排版 | ~5 秒 | fontTools，不让 AI 画字 |
| 5 | 线稿层提取 | ~2 秒 | OpenCV |
| 6 | 目检 + 可能重生成 | ~30 秒-5 分钟 | 变量大（瑕疵重跑） |
| | **阶段一小计** | **~2-8 分钟** | |

### 阶段二：云端渲染（GitHub Actions）

| # | 步骤 | 耗时 | 说明 |
|---|---|---|---|
| 7 | 准备临时素材+写 workflow+commit+push | ~1 分钟 | 每次重复劳动 |
| 8 | workflow 冷启动（checkout+setup python+pip install+apt ffmpeg） | ~1.5-2 分钟 | onnxruntime 较大 |
| 9 | **Blender 下载**（190MB） | ~1-3 分钟 | 🔴 大头 #1 |
| 10 | Blender 构建场景+烘焙顶点色+导出 GLB | ~40-80 秒 | 纯计算 |
| 11 | npm install + 复制 web 模板 | ~15 秒 | |
| 12 | publish 发布（压缩 webp+thumb+importmap+cards.json） | ~30 秒 | |
| 13 | **Blender 渲染 96 帧 preview**（360×500） | ~2-4 分钟 | 🔴 大头 #2 |
| 14 | ffmpeg 合成 webm | ~5 秒 | |
| 15 | cleanup+commit+push | ~15 秒 | |
| | **阶段二小计** | **~7-12 分钟** | |

### 阶段三：验证 + 收尾

| # | 步骤 | 耗时 | 说明 |
|---|---|---|---|
| 16 | 等 GitHub Pages 部署 | ~30-60 秒 | 每次 push 都等 |
| 17 | 线上验证 | ~30 秒 | |
| 18 | 补配置字段（slug/stats/honors/back_story）+重新 commit+push | ~1 分钟 | render 后配置被覆盖成简化版 |
| | **阶段三小计** | **~2-3 分钟** | |

### 📌 总耗时：~11-23 分钟/张（不含环境问题排查）

---

## 二、时间大头分析

### 硬时间（计算/API 固有，无法避免）~6-8 分钟
- AI 生成四层：~2-3 分钟
- Blender 构建+GLB 导出：~1-2 分钟
- 96 帧 preview 渲染：~3-5 分钟

### 软时间（工程优化可消除/减少）~9-17 分钟
- Blender 下载：~3-5 分钟 ← 缓存可消除
- 环境问题排查：~3-5 分钟 ← 一次性修复后不再犯
- workflow 冷启动：~1 分钟 ← 缓存依赖可减半
- 配置补全+多次 commit：~2-3 分钟 ← 模板化+合并提交可消除
- 目检+重生成：~1-5 分钟 ← prompt 更精准可减少
- Pages 部署等待：~0.5-1 分钟 ← 不可避免但可并行做别的

---

## 三、优化方案

### ✅ P0：缓存三件套（收益最大，完全不影响质量）

| 优化 | 缓存内容 | 节省时间 | 原理 | 状态 |
|---|---|---|---|---|
| ① Blender 缓存 | blender-4.5-linux-tools（~840MB 含解压） | ~1-3 分钟/次 | `actions/cache` 按版本号缓存，首次下载后后续直接解压恢复 | ✅ 已实施（2026-10-01 测试通过，首次建立缓存 839MB） |
| ② pip 依赖缓存 | rembg/onnxruntime/opencv 等 | ~30-60 秒/次 | setup-python cache: pip + requirements.txt | ✅ 已实施（2026-10-01 测试通过，缓存 236MB） |
| ③ u2net 模型缓存 | u2net.onnx（~50MB） | ~20 秒/次（首次） | 缓存 rembg 模型目录 ~/.u2net/ | ✅ 已实施（2026-10-01 测试通过） |

> 三项合计每次节省 ~2-4 分钟，产物完全一致（只是不重新下载）。

### ✅ P1：流程优化（完全不影响质量）

| 优化 | 说明 | 节省时间 | 状态 |
|---|---|---|---|
| ④ 通用 render-card workflow | 写一个接受 `card_id` 参数的通用 workflow，不用每次写新的一次性 workflow + 手动复制素材 | ~1 分钟/次 + 减少出错 | ✅ 已实施（.github/workflows/render-card.yml，2026-10-01 测试通过） |
| ⑤ 配置模板化 | 做一个带完整字段（slug/stats/honors/back_story）的 config 模板，消除 render 后补字段步骤 | ~1 分钟/次 | ✅ 已实施（generator/projects/config.template.json，已回写 Kenji/电车卡配置） |
| ⑥ 合并 publish 为单次 | 目前分两次 publish（第一次 --skip-preview，第二次渲染 preview），合并成一次，省一次 Blender 启动+vendor 初始化 | ~30 秒/次 | ✅ 已实施（render_preview 幂等：preview.webm 已存在则跳过，新卡自动渲染） |

### ⚠️ P2：preview 优化（只影响 hover 小窗预览，不影响 3D 卡本身）

| 优化 | 当前 | 建议 | 节省时间 | 质量影响 | 状态 |
|---|---|---|---|---|---|
| ⑦ preview 降帧 | 96 帧 | 64 帧（360°/64≈5.6°/帧，2.7秒/圈，仍流畅） | 实测省 4.5 分钟 | hover 小窗几乎察觉不到 | ✅ 已实施（2026-10-01 验证：渲染 457s→189s） |
| ⑧ preview 降分辨率 | 360×500 | 320×444（缩略图预览，用户不会放大） | 含在⑦内 | 小窗预览无感知 | ✅ 已实施（2026-10-01 验证：文件 431KB→244KB） |

> 🔑 关键：P2 只影响 hover 时的小窗预览动画，64 帧在 2-2.5 秒内旋转一圈，人眼看起来仍然流畅。3D 卡本身（card.glb）完全不受影响。

### 💡 P3：可选进一步优化

| 优化 | 说明 | 节省时间 | 状态 |
|---|---|---|---|
| ⑨ AI 四层并行生成 | 目前主体+背景串行调用 API，改造成并行 | ~15-30 秒 | ✅ 已实施（ai_generate.py threading 并行主体+背景） |
| ⑩ 本地目检提示词优化 | 更精准的 prompt 减少重生成率 | 变量，平均 ~1-2 分钟 | ✅ 已实施（docs/PROMPT-GUIDE.md 五要素/四要素+案例+排查表） |

---

## 四、优化后预期对比

| 指标 | 优化前 | P0+P1（已实施） | P0+P1+P2（已实施，实测） |
|---|---|---|---|
| 新卡总耗时（含 preview） | ~11-23 分钟 | ~8-16 分钟 | **~5-7 分钟（实测 6 分 4 秒）** |
| preview 渲染时间 | ~3-5 分钟（96帧） | ~3-5 分钟 | **~3 分钟（64帧，实测 189 秒）** |
| preview 文件大小 | ~430KB | ~430KB | **~244KB（-43%）** |
| 3D 卡质量 | 基准 | 完全不变 | **完全不变** |
| preview 质量 | 基准 | 完全不变 | 轻微（小窗无感知，实测流畅） |

---

## 五、实施建议

**第一优先级（立即实施）：P0 缓存三件套 + P1 通用 workflow + 配置模板 + 合并 publish**
- 五项合计每次节省 ~4-6 分钟
- 完全不影响任何质量
- 改动量小，风险低

**第二优先级（观察后决定）：P2 降帧降分辨率**
- 先看 P0+P1 优化后的实际耗时
- 如果仍觉得慢，再考虑 P2
- 实施前需确认 64 帧预览的流畅度可接受

**第三优先级（长期改进）：P3 并行化 + prompt 优化**
- 收益相对较小
- 可作为持续改进项

---

## 六、环境问题历史记录（已解决，不再耗时）

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 本地 Blender 下载反复失败 | 沙箱 VM 网络不稳定，镜像 403/截断 | 改用 GitHub Actions 云端渲染 |
| 云端 publish 找不到 Blender | Blender 下到 project/tools/，publish 找 repo root/tools/ | workflow 里加链接步骤 |
| 云端缺 ffmpeg | Ubuntu runner 默认无 ffmpeg | workflow 里加 apt-get install ffmpeg |
| 云端缺 three vendor | vendor 路径不匹配 | workflow 里 cp 修复 |
| 配置字段缺失 | render 后配置被覆盖成简化版 | ✅ P1 配置模板化已解决（config.template.json + 回写现有卡配置） |

---

## 七、实施记录

### 2026-10-01：P0 + P1 全部实施完成

**实施内容：**
- P0-① Blender 缓存：actions/cache@v4，key=`blender-4.5-linux-tools-v1`，path=`tools/`
- P0-② pip 依赖缓存：setup-python@v5 cache=pip，cache-dependency-path=generator/requirements.txt
- P0-③ u2net 模型缓存：actions/cache@v4，key=`u2net-onnx-v1`，path=`~/.u2net/`
- P1-④ 通用 workflow：`.github/workflows/render-card.yml`，接受 card_id/tags/date 参数
- P1-⑤ 配置模板：`generator/projects/config.template.json`（20 个完整字段）
- P1-⑥ 合并 publish：单次调用 publish_card.py，render_preview 幂等（已存在则跳过）
- 配套：ensure_blender.py 统一 Blender 下载到仓库根 tools/；.gitignore 精细化（projects/ 仅入库 assets/+config）；requirements.txt 补全；Kenji + 电车卡配置回写

**测试结果（2026-10-01，Kenji 卡试跑）：**
| 指标 | 结果 |
|---|---|
| Workflow 总耗时 | 3 分 28 秒（含首次 Blender 下载） |
| Run pipeline（含 Blender 下载） | 130 秒 |
| Publish（单次，preview 幂等跳过） | 2 秒 |
| gallery-check | 11 项全通过 |
| Blender 缓存大小 | 839 MB（已保存，下次 cache hit） |
| pip 缓存大小 | 236 MB（已保存，下次 cache hit） |
| commit + push | 成功 |

**预期第二次运行（缓存命中）耗时：**
- 已有 preview 的卡：~1.5-2.5 分钟（省 Blender 下载 ~90 秒 + pip ~20 秒）
- 新卡（需渲染 preview）：~4-6 分钟（省 Blender 下载 + pip，仍需 96 帧渲染 ~2-3 分钟）

**对比优化前：** 11-23 分钟/张 → 优化后 5-7 分钟/张（新卡），节省约 60-70%。

---

### 2026-10-01：P2 + P3 全部实施完成

**实施内容：**
- P2-⑦ preview 降帧：96→64 帧（render_preview.py + publish_card.py PREVIEW_FRAMES）
- P2-⑧ preview 降分辨率：360×500→320×444（render_preview.py）
- P3-⑨ AI 并行生成：ai_generate.py 主体图+背景图 Seedream 调用 threading 并行
- P3-⑩ prompt 最佳实践：新增 docs/PROMPT-GUIDE.md（主体五要素/背景四要素/真实案例/排查表/检查清单），config.template.json 引用指南

**P2 实测验证（Kenji 卡重新渲染 preview）：**
| 指标 | 旧版（96帧 360×500） | P2新版（64帧 320×444） | 变化 |
|---|---|---|---|
| Publish 含渲染 | 457 秒 | 189 秒 | **-59%** |
| Workflow 总耗时 | 10分47秒 | 6分4秒 | **-44%** |
| preview.webm 大小 | 431 KB | 244 KB | **-43%** |
| 分辨率 | 360×500 | 320×444 | ffprobe 验证 ✅ |
| 3D 卡质量 | 基准 | 完全不变 | ✅ |

**全部优化（P0+P1+P2+P3）完成状态：10/10 项 ✅**

---

*本文档随流程优化持续更新。实施某项优化后，请更新对应状态（⬜→✅）并记录实际节省时间。*
