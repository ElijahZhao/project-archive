# Holo-Card-Studio · 殷商纪制作过程坑（06）

> 日期：2026-10-07 ｜ 批次：Yin-Shang Chronicles Vol.I（妇好 / 武丁 / 甲骨文）

## 坑 A：run_pipeline 首次运行卡死 ~10 分钟（DNS 挂起）

**现象**：`run_pipeline.py --project generator/projects/shang-fu-hao --skip-npm` 启动后无任何输出，
进程 `S` 睡眠态、CPU 时间几乎不涨，`/proc/<pid>/wchan` 显示 `request_wait_answer`（glibc DNS 解析等待），
无 blender 子进程，log 0 字节。

**根因链**：
1. `ensure_blender.find_blender()` 找不到 `tools/blender-4.5.14-linux-x64/blender`（可执行文件缺失）。
2. 于是走 `pick_mirror()` 联网下载流程 → 沙箱对 download.blender.org 的 DNS 解析挂起（无超时上限）。
3. 更早一次的下载已把 378MB 的 `blender-4.5.14-linux-x64.tar.xz` 下载完，但只**部分解压**（只有 `4.5/` 子目录，
   缺根目录 `blender` 主程序）——所以 find_blender 继续扑空。

**修复**：
```bash
rm -rf tools/blender-4.5.14-linux-x64          # 删残缺目录
tar -xJf tools/blender-4.5.14-linux-x64.tar.xz -C tools/   # 完整解压（约 1-2 分钟，856MB）
```
解压后 `tools/blender-4.5.14-linux-x64/blender`（163MB 可执行）存在，find_blender 命中本地包，不再联网。
实测每卡 build+export ≈ 3-4 分钟（hero 渲染 2 分钟）。

**教训**：
- 首次跑管线前先 `find tools/blender-4.5.14-linux-x64 -name blender` 验证主程序在位，不要在不确定时直接跑。
- `pick_mirror()` 无整体超时（urlopen 有 25s/120s 超时但 DNS 阶段不受控），沙箱内不要依赖外网下载 Blender。

## 坑 B：`cd X && nohup A & nohup B &` 的 cwd 陷阱

**现象**：一行内并行启动两个管线，第二个 `nohup python3 run_pipeline.py ...` 报
`can't open file '.../generator/scripts/run_pipeline.py': No such file or directory`。

**根因**：Bash 中 `&&` 优先级高于 `&`。`cd X && nohup A > log & nohup B &` 被解析为
`(cd X && nohup A) &` + `nohup B &`——`cd` 只对 A 生效，B 在默认 cwd（/home/user/Doubao/chats/...）启动。

**修复**：并行任务各自独立 `cd`：
```bash
cd /path && nohup cmd1 &   # 第一个
cd /path && nohup cmd2 &   # 第二个单独一行
```

**教训**：涉及 cwd 的并行后台命令，每行各自带 cd；不要用 `&&` 链 + `&` 混排。

## 坑 C（环境）：u2net 抠图模型缓存缺失

- 首次从 huggingface 源下载返回 29 字节假文件（应为 ~170MB）→ 校验失败。
- 正确源：`https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx`（167MB）。
- rembg 运行时会自动下载到 rembg 模型缓存，可先行预下载到 `~/.u2net/u2net.onnx` 省一次下载。

---

# 第二批 11 张（Vol.I 余 3 + Vol.II + Vol.III）· 新坑记录

> 日期：2026-10-07 ｜ commit 8875f77 ｜ 56 卡上线

## 坑 D：背景图"空镜"难纯净（重生成 3 次的教训）

**现象**：为后母戊鼎/妇好鸮尊/商汤生成的背景图，模型反复塞入器物
（鼎、鸟形尊、神兽雕塑）或文字（竖排篆字、血迹战场）。

**对策**：prompt 显式负面清单："画面中绝对没有任何文字、字符、铭文，也没有
人物、武器和血迹，是纯净的自然空景 / 暗色空景"。商汤 bg 2 次、后母戊鼎 bg 1 次、
鸮尊 bg 3 次后才干净。鸮尊 bg 最终用"纯光影氛围空镜：只有光与阴影与纹理"成功。

**教训**：器物类卡的背景 prompt 必须同时禁"器物类名 + 场景物 + 文字"三类；
纯氛围（光锥/渐变/暗纹）是最可靠的空镜配方。

## 坑 E：stats/honors 为 falsy 导致 CI 失败

**现象**：批量建 config 时 stats={}、honors=[]，`pytest test_config_schema.py`
报 `缺少必填字段 ['stats','honors']` 与 `honors 应为非空列表`。

**根因**：测试用 `if not cfg.get(k)` 判缺失——`{}`/`[]` 是 falsy。

**对策**：stats 用非空字符串 `"Yin-Shang Chronicles · 殷商纪 · NNN/014"`，
honors 填 5 条真实荣誉。源 config 与 gallery/cards/<id>/ 归档副本双写。

**教训**：批量生成 config 的脚本里直接按旧卡格式（stats=str、honors=list[5]）
预填，不要留空壳。

## 坑 F：generate_typography 的 CWD 敏感

传 `generator/projects/<slug>` 全路径可跑；只传 slug 会 FileNotFoundError。
与 run_pipeline（--project 也吃全路径）一致。

## 坑 G：generator/projects/_preview/ 临时检查图入库

旧卡检查图（shang-fu-hao_check.png 等）在 `generator/projects/_preview/`，
需追加到 .gitignore（`generator/projects/_preview/`），否则污染提交。

## 实测节奏（沙箱）
- image_gen 22 张分 4 批 ≈ 10 分钟（含 4 次背景重生成）
- 四层处理 + 排版 11 卡 ≈ 4 分钟
- Blender build+export 11 卡 ≈ 30 分钟（2.5min/卡）
- publish（preview.webm 96 帧）11 卡 ≈ 68 分钟（6min/卡）
- 合计 ≈ 1 小时 50 分钟（不含等待 Actions）

---

# GTA Vice City Nights Vol.II（场景文化 8 张）· 新坑记录

> 日期：2026-10-07 ｜ commit 7989e54 ｜ 64 卡上线

## 坑 H：场景卡主体被模型塞入异物（骷髅事件）

**现象**：Vercetti Estate 施工地主体图，模型自己加了一个巨大的骷髅骨架（"奇幻反差"）。
**对策**：prompt 显式负面清单 "absolutely no skeleton, no skull, no bones"，重生成一次通过。
**教训**：场景卡（非人物卡）主体图必须显式列出可能被"氛围化"塞入的异物清单。

## 坑 I：publish_card --tags 覆盖 config.style_tags

**现象**：config 里 style_tags 写了 3 个（vice-city, 80s, 场景），publish 后 cards.json 只剩
--tags 传入的 2 个。
**对策**：发布后手动把维度标签补回 cards.json（或 publish 时 --tags 直接传全 3 个）。
**教训**：publish_card.py 的 --tags 是覆盖语义，不是合并。

## 坑 J：edition 前导序号必须三位数

**现象**：写了 "57 / 008"，测试 test_edition_format 断言 `^\d{3} / \d{3}$` 失败。
**对策**：源 config + 归档副本 + cards.json 三处统一改为 "057 / 008"。
**教训**：批量建 config 时 edition 直接按 `f"{n:03d} / 008"` 格式化。

## 坑 K：Blender 自动备份 card.blend1 入库

**现象**：run_pipeline 产生 card.blend1（Blender 自动备份），git add -A 时被提交。
**对策**：.gitignore 补 `generator/projects/*/card.blend1`，git rm --cached 移出。
**教训**：批量渲染后 git status 前先 grep 备份文件后缀。

---

# 殷商纪 Vol.IV-VI（13 张扩展）· 新坑记录

> 日期：2026-10-07 ｜ commit f2fb2dd ｜ 77 卡上线（殷商纪 27 张）

## 坑 L：run_pipeline --project 必须传全路径

**现象**：`--project shang-bi-gan`（slug）直接 FileNotFoundError "Write card-config.json
from references/config.example.json first"；之前 generate_typography 传 slug 也有过同款报错。
**对策**：`--project /abs/path/generator/projects/<slug>` 全路径即通。
**教训**：generator 系脚本 root 全部 `Path(a.project).resolve()`，一律传全路径。

## 坑 M：背景空镜反复被模型塞器物/文字（本批 9 次重生成）

**现象**：微子背景两次被塞礼器供桌香炉；龙虎尊/乳钉鼎背景被塞展柜浮雕；
妇好钺背景被画军帐长矛；贞人背景两次被画篝火（第二次还带"甲子壬寅"刻字）；
干支背景被画古籍书页繁体字。
**对策**：终极配方 = "极简单色背景：X色到Y色的平滑渐变，没有任何……，只有干净的渐变色块"
（"纯抽象光影背景"配方仍会被塞意象，单色渐变配方最可靠）。
**教训**：背景 prompt 中不要出现任何具象名词（陶器/烛台/篝火），名词即召唤意象；
文字必须用 "没有任何文字" 显式封锁。

## 坑 N：publish --tags 传全 3 标签可避免覆盖（正面验证）

**现象**：本次 publish 时 --tags 直接传 config 的完整 3 个标签（如"殷商,三仁,忠臣"），
发布后 style_tags 无丢失，无需事后手动补回（对比坑 I 的教训）。
**对策**：publish 命令的 --tags 永远照抄 config.style_tags 全量。

---

# 卡片质量缺陷 · 改进方案（坑 O）

> 日期：2026-10-07 ｜ 用户反馈确认

## 坑 O：人物缺胳膊少腿 / 器物车辆透明化（生成 + 抠图缺陷，非卡特色）

**现象**：
1. 部分人物卡缺一条胳膊或少一条腿（古风长袍/复杂姿态下 flash 模型生成不完整，
   rembg 再把与背景同色的肢体误抠）。
2. 部分器物/车辆卡"透明"——正视角看不见主体，转动出视差才显形
   （主体与背景同色系 + 抠图半透明边缘共同导致）。

**用户判断**：明确这不是 3D 全息卡特色（特色=多层视差/折光/旋转），是真缺陷。

**改进方案（已写入铁律 5，约束新卡）**：
1. 人物卡 prompt 显式「四肢完整、全身可见、无残缺、无遮挡切割」。
2. 器物/车辆 prompt「主体与背景强对比，亮色主体配深色背景，主体完全不透明、轮廓清晰」。
3. 背景空镜不得与主体同色系；继续用「单色渐变 + 无任何实体名词」终极配方。
4. 抠图后自检 subject.png 透明通道（孔洞/半透明边缘即重生成）。
5. 渲染后正视角抽检：不旋转必须能辨认主体，否则重做。
6. 豁免：存量 77 张不做全量重检（工程量过大，用户明确豁免）。

**教训**：批量提速不得牺牲质量自检；"赶批量"是缺陷温床。
