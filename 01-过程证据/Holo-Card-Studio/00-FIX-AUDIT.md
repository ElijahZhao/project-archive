# HoloLab Studio · 全面检查与修复方案（2026-10-01）

> 触发：哈兰德多重宇宙 5 张梗卡上线后，"再检查一遍"专项审计。
> 状态：**已实施完成（2026-10-01）**。P1 用户拍板方案 A（保持现状）。

---

## 一、检查结论摘要

| 面 | 结果 |
|---|---|
| 25 张卡线上资源（index/GLB/preview/thumb ×4） | 99/100 个 200 ✅（1 个异常见 P1） |
| cards.json 字段完整性（哈兰德 5 张 13 字段） | 全部完整 ✅ |
| curation 自动化（update_curation_json） | 单测通过 ✅ |
| 锁定卡（马卡）locked/hash | 正常 ✅ |
| 本地 git 状态 | 干净 ✅ |
| README 徽章 | **过时** ❌（20 张，实际 25） |
| 渲染并发 & 部署链路 | **有根因级隐患** ❌（P3/P4） |
| CI 对 style_tags 词条覆盖 | **缺失** ❌（P5） |

---

## 二、问题清单（含根因）

### P1 · card-elijah-lin-d 缺 preview.webm（历史遗留）
- **现象**：第一张公众投稿测试卡目录无 `preview.webm`，cards.json 无 `preview` 字段，展厅退化为静态缩略图（不裂图、不报错，但无动态预览）。
- **根因**：Phase1c 上线该卡时渲染流程未产出/未提交 preview。
- **修复**：重跑 `render-card.yml`（card_id=card-elijah-lin-d），自动补齐 preview.webm + cards.json preview 字段。约 3 分钟。
- **验收**：`https://Elijah-Lin-Dancer.github.io/Holo-Card-Studio/cards/card-elijah-lin-d/preview.webm` → 200；cards.json 该卡含 preview 字段。

### P2 · README 卡数徽章过时（第二次复发）
- **现象**：README 徽章 `🃏 20 Cards - 6 Languages`，实际 25 张。此前已手动改过 18→20，证明静态徽章必然落后。
- **根因**：静态 shield badge，卡数写死。
- **修复**：卡数徽章换 **shields.io dynamic JSON badge**，从线上 `cards.json` 实时读取：
  `https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2FElijah-Lin-Dancer.github.io%2FHolo-Card-Studio%2Fcards.json&query=%24.cards.length&label=Live%20Cards&color=c9a86a`
  语言数（6）保持静态（cards.json 无语言字段，不做过度工程）。
- **验收**：README 徽章显示 25；未来新增卡无需改 README。

### P3 · render-card.yml push 无重试 → 并发渲染丢产物（哈兰德批次已踩）
- **现象**：5 张并行渲染，4 张在最后 commit+push 步骤失败（非 fast-forward），产物随 runner 销毁，只能串行重跑。
- **根因**：`git push` 无 `fetch+rebase+重试` 逻辑；并行 push 必然互相冲突。
- **修复**：Commit and push 步骤改为 **自动 fetch + rebase + 重试循环（最多 3 次）**：
  ```bash
  git push || { git pull --rebase --autostash; git push; } || { git pull --rebase --autostash; git push; }
  ```
  并打印每次冲突处理日志。此后批量渲染可安全并行，不丢卡。
- **验收**：对 2 张测试卡并行 dispatch，两 run 均 completed success，产物齐全。

### P4 · deploy 不自动 → 每次手动触发部署
- **现象**：render-card push 后 GitHub Pages 不更新，需手动 dispatch deploy workflow。
- **根因**：workflow 内 `git push` 使用 **GITHUB_TOKEN**，GITHUB_TOKEN 触发的 push **不会触发** `on: push` 的 workflow（GitHub 安全设计），deploy.yml 因此静默跳过。
- **修复**：render-card.yml 末尾新增一步，用 **GITHUB_TOKEN 调 GitHub API dispatch deploy workflow**（需在 permissions 增加 `actions: write`）：
  ```yaml
  permissions:
    contents: write
    actions: write
  ```
  ```bash
  curl -s -X POST \
    -H "Authorization: Bearer ${{ github.token }}" \
    -H "Accept: application/vnd.github+json" \
    -d '{"ref":"main"}' \
    https://api.github.com/repos/Elijah-Lin-Dancer/Holo-Card-Studio/actions/workflows/deploy.yml/dispatches
  ```
- **验收**：触发一次渲染，观察 run 末尾自动出现 Deploy run，线上 1-2 分钟内更新。

### P5 · gallery-check 缺 style_tags → i18n 词条覆盖检查（本次踩坑）
- **现象**：哈兰德新标签（梗卡/机器人/冥想/龙珠/disco/维京）未入 i18n 词典，英文模式筛选 chips 显示中文；上次英文化修复只覆盖旧标签，无机制防复发。
- **根因**：CI 不校验"manifest 中所有 style_tags 均有 i18n 词条"。
- **修复**：gallery-check 新增测试（`generator/tests/test_i18n_coverage.py`）：
  - 读取 `gallery/cards.json` 全部 style_tags 去重；
  - 读取 `gallery/i18n.js` 词典 key 集合；
  - 断言 tags ⊆ dict keys；缺失直接 FAIL（附缺失列表）。
- **验收**：本地跑 pytest 通过；故意加一个陌生 tag 应 FAIL。

---

## 三、实施顺序与依赖

```
P1（重渲染，独立） → P3/P4（workflow 改动，独立） → P2（README，独立） → P5（CI 测试，独立）
```
四者互不依赖，可并行；实施后统一 commit+push，触发 deploy，线上验证。

## 四、收尾验证清单

- [ ] P1：card-elijah-lin-d preview.webm 200 + cards.json preview 字段
- [ ] P2：README 徽章显示 25（动态）
- [ ] P3：两张卡并行渲染均 success，产物齐全
- [ ] P4：渲染 run 末尾自动触发 Deploy，线上更新
- [ ] P5：pytest 通过（含恶意 tag FAIL 用例）

## 五、自动化收益（为什么值得做）

- P3+P4：批量出卡从"串行 15 分钟 + 手动 deploy"变成"并行 5 分钟 + 全自动上线"。
- P2：徽章永不落后（第二次修同类问题的根治）。
- P5：新标签漏翻译从"用户发现"变成"CI 拦截"，零回归成本。
