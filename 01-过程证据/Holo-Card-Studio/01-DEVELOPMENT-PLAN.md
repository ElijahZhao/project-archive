# HoloLab Studio · 后续开发计划（DEVELOPMENT PLAN）

> 基于 docs/TOOLKIT-ROADMAP.md 的工具清单展开：每一阶段点名使用的工具、
> 具体任务、产出物与验收标准。原则：**L1（项目本体增强）优先于 L2（展示传播）**。
> 更新日期：2026-09-29

## 已完成（P0 闭环）

| 项 | 状态 | 说明 |
|---|---|---|
| 问题 A 缩略图 bug | ✅ | 已修复并线上验证（thumb.jpg 200 / 420×583） |
| 问题 B 空 web/ 目录 | ✅ | 已删除 |
| 问题 C git 零提交 | ✅ | 已 commit（2e2eb1c、0b3bfe1）并推送 |
| 问题 D _card_id 写回 | ✅ | 归档 config 已带标记 |
| GitHub Pages 上线 | ✅ | https://Elijah-Lin-Dancer.github.io/Holo-Card-Studio/ |

---

## P1 · 展厅主视觉 + 架构信息图（L1 项目本体） ✅ 2026-09-29 完成

**目的**：展厅第一眼专业度 + 申请叙事可视化。

- 工具：**doubao-creative-design**（主视觉/KV、系列海报）、**doubao-visualization**（架构图/SVG 信息图）、**html**（展厅首页改版落地）
- 任务：
  1. 用 doubao-creative-design 生成展厅主视觉（品牌色、全息卡主题 KV，含"Hololab Studio"字样）
  2. 用 doubao-visualization 把管线架构图升级为正式信息图（可直接放 README / How-it-works 页）
  3. 用 html 技能把首页 index.html 改版：Hero 区 + 主视觉 + 信息图入口
- 产出：gallery/index.html 新首页、docs/ 下架构信息图、主视觉图（同步进仓库）
- 验收：首页在真实浏览器无报错；主视觉与卡面风格统一；信息图在窄屏不溢出

## P2 · 第二张卡（生成管线自用 + 验证 E） ✅ 2026-09-29 完成

**目的**：展厅多卡化；顺带验证 u2net 模型重下（问题 E）。

- 工具：豆包 API 流水线（ai_generate / run_pipeline / publish_card）
- 任务：
  1. 确定卡主题（用户提供，或我推荐：风格与前卡区分度大，如"水墨锦鲤"）
  2. 建 card-config → 生成四层素材（此处验证 u2net 重下）→ Blender 渲染 → 发布
  3. 推送上线
- 产出：gallery 新增一张卡 ✅「流行之王」MJ（002/002），线上双卡 ✓
- 验收：✅ 新卡线上可打开、缩略图 420px、清单置顶；问题 E u2net 176MB 自动重下成功
- 验收：新卡在线上可打开、缩略图正常、清单新增条目

## P3 · 卡片动态预览（L2→L1 转化） ✅ 2026-09-29 完成

**目的**：让视频工具变成产品功能，而非纯展示——每张卡生成自动旋转 3D 预览，
首页缩略图 hover 播放，提升展厅互动感。

- 工具：**方案 B：Blender 旋转序列 + ffmpeg**（`render_preview.py`：360×500、Cycles 16 samples、96 帧；ffmpeg libvpx-vp9 crf42 合成 webm，<2MB/卡）。注：早期方案 A（image_to_video 视频生成）因 Seedance 2.0 fast 未开通、且 3D 旋转可控性差而弃用
- 任务：
  1. 用 hero 渲染图 + Blender 卡片场景生成 4 秒旋转预览（96 帧 @24fps）
  2. 压缩为 webm，接入首页缩略图 hover（app.js + style.css）
  3. 适配多卡：四卡均生成 preview.webm（messi 628KB / mj 488KB / taikonaut 427KB / wukong 573KB）
- 产出：✅ gallery 每卡 preview.webm + 首页 hover 播放 + cards.json preview 字段
- 验收：✅ 线上四卡 preview.webm 全部 200；文件体积均 <2MB/卡

## P3.5 · 素材压缩 + 预览动画自动化入发布流水线（L1 工程化） ✅ 2026-09-29 完成

**目的**：用户一句话出卡后，发布无需任何手动步骤——压缩与预览渲染全部自动化。

- 工具：`publish_card.py`（`compress_assets` + `find_blender` + `render_preview`）
- 任务：
  1. `compress_assets`：四层贴图 PNG→WebP（保留 alpha，前端零改动），幂等（已有 webp 跳过）
  2. `find_blender`：自动定位便携版 Blender（无需手传 --blender）
  3. `render_preview`：96 帧分段渲染（每段 40 帧、已渲染帧复用）→ ffmpeg 合成 preview.webm → 自动更新 cards.json preview 字段；幂等（webm 存在跳过）
  4. 发布流程升级：[1/5]初始化→[2/5]复制（保留已有 webm）→[3/6]缩略图→[4/7]压缩→[5/7]渲染预览→[6/7]importmap→[7/7]清单；支持 `--skip-preview` / `--blender`
- 修了两个集成 bug：①清空归档删掉已有 webm → 暂存还原；②`update_cards_json` 重建条目丢 preview → 合并保留
- 成果：✅ commit `f6cfcc3` 已推送；重跑 publish 全链路幂等实测通过（webm 保留、渲染跳过、压缩跳过、preview 保留）

## P4 · 项目白皮书（作品集交付物） ✅ 2026-09-29 完成

**目的**：给教授/招生办看的完整技术手册（含架构、AI 管线、图形学、踩坑、路线图）。

- 工具：**doubao-book-writer**（长文档工作台）
- 任务：
  1. 基于 docs/*.md + 博客整合为白皮书正文（约 8–12 页）
  2. 输出可交付文档（本地 markdown/PDF）
- 产出：docs/WHITEPAPER.md ✅（英文正文 + 中文编号标题，28000 字符契约，8 章）已交付飞书 https://my.feishu.cn/docx/QhWedX9tzoCrFvx2f8cce5Pvnzc
- 工具：doubao-book-writer 全流程（prepare → write → quality → deliver），质量分 8.34/10（8 章全过 7.5 门槛），飞书读回 96.9%
- 验收：✅ 可直接发导师/招生办（P4.5 精修已按用户决定取消）

## P5 · demo 视频（L2 展示）

**目的**：作品集置顶 30–60 秒演示视频（生成全流程 + 3D 交互）。

- 工具：**doubao-creative-video**（视频生成）、**text_to_audio_plus**（中英旁白）、**byted-mediakit**（剪辑/字幕）
- 任务：脚本规划 → 分镜生成 → 配音 → 合成
- 产出：demo.mp4（30–60 秒）
- 验收：完整讲述"一句话→四层素材→3D 卡→在线展厅"；音画同步

## P6 · 行业/产品/论文研究（申请季佐证）

**目的**：为 PS/研究陈述提供佐证材料。

- 工具：**doubao-industry-analysis**（AIGC 行业）、**doubao-product-analysis**（HoloLab 竞品/差异）、**doubao-academic-researcher**（相关工作）
- 任务：按需产出 3 份研究摘要，纳入作品集叙事
- 产出：docs/research/ 下三份摘要
- 验收：事实可溯源；区分已查证/一方说法

---

## 执行顺序与依赖

```
P1（主视觉+信息图）→ P2（第二张卡，含验证 E）→ P3（动态预览）→ P3.5（压缩+预览自动化）→ P4（白皮书）→ P7（一句话出卡）→ P5（demo 视频）→ P6（研究）
```

依赖关系：P1/P2 可并行；P3 依赖 P1/P2 的卡资产；P3.5 依赖 P3 的渲染脚本；P4 依赖 docs 定稿；P5 依赖流水线视频源（Seedance 2.0 fast 开通）。

## 工具启用清单（对照 TOOLKIT-ROADMAP）

| 阶段 | 实际调用的工具/技能 |
|---|---|
| P1 | doubao-creative-design、doubao-visualization、html |
| P2 | 豆包 API（已有）+ rembg/Blender 流水线 |
| P3 | Blender 渲染序列 + ffmpeg（方案 B，弃用视频生成方案 A） |
| P3.5 | publish_card.py 工程化（compress_assets / find_blender / render_preview） |
| P4 | doubao-book-writer（+ doubao-human-signal） |
| P5 | doubao-creative-video + text_to_audio_plus + byted-mediakit |
| P6 | doubao-industry-analysis、doubao-product-analysis、doubao-academic-researcher |

## P7 · 一句话自动出卡（One-Sentence Card Generator） ✅ 2026-09-29 完成
- 工具：generator/scripts/one_shot_card.py（一句话 → card-config.json → 校验/编号/渲染参数 → 接入流水线）
- 文字模型：Doubao-Seed-2.0-mini-260428（2.1-lite 长文本请求服务端断连，实测后降级到 2.0-mini，长文本正常且更便宜 0.0002-0.0008 元/千tokens）
- 图片模型适配：CANVAS 1920×2880 → 1728×2592（flash 模型面积上限 4,624,220 px，1920×2880 超限 400）
- 成果：第三张卡「星辰远征」由一句话全自动生成并上线（三卡展厅，含 hover preview.webm 427KB）
- 线上：https://Elijah-Lin-Dancer.github.io/Holo-Card-Studio/
