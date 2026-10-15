# 07-可复现性素材

> 服务章节：可复现性附录。审稿人第一个问的就是这个（H-3 ④）。

## 已溯源素材（指针见 `00-索引.md` 2.4）
- **零漂移门禁**：`repro.yml:71-76` 用 `git diff --exit-code` 逐字节校验 `data/bias/{propagation,injection,boundary}.json`。
- **依赖锁定**：numpy `2.3.5`；`bias-experiments` 仅 numpy（证明研究路径零重依赖）；在线侧断言不加载 torch。
- **脚本参数**：`run_bias_experiments.py`（`--items 60 / --requests 600 / --slots 5 / --seed 42`）；`n_seeds = max(20, requests//20)=30`。
- **测试**：`pytest` 全量 + ruff + mypy 入 CI。

## 能支撑的论点
- 「文档里引用的每个数字都可在干净机器上一键复算」——这是本项目相对多数工作的可复现性强项（M4⑤）。

## 需补（待补测）
- 主仓库代码 **tag / DOI**（H-5：代码引用需打 tag 或申请 DOI，否则审稿人 clone 到的非论文描述版本）。
- 硬件信息（CPU / 内存峰值）已在 `data/bench.json`，可补入附录。
