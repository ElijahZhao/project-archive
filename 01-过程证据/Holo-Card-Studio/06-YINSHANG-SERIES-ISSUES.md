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
