#!/usr/bin/env python3
"""HoloLab Studio · ingest_card.py
接收前端"卡片包"（hololab-card-package/v1，导出自创造页"申请公开"），
把一句话创意送入标准出卡管线，输出 projects/<slug>/card-config.json。

用法：
  python scripts/ingest_card.py --package card.json
  python scripts/ingest_card.py --package card.json --model doubao-seed-2-0-mini-260428

之后按提示继续：
  python scripts/ai_generate.py projects/<slug> --model doubao-seedream-5-0-flash-260915
  python scripts/run_pipeline.py projects/<slug> --blender ../tools/blender-4.5.0-linux-x64/blender
  python scripts/publish_card.py projects/<slug> --tags <标签> --blender ../tools/blender-4.5.0-linux-x64/blender
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # generator/
sys.path.insert(0, str(HERE))

import one_shot_card as osc  # noqa: E402

DEFAULT_MODEL = osc.DEFAULT_MODEL


def load_package(path: Path) -> dict:
    """读取卡片包 JSON 并校验 schema。"""
    pkg = json.loads(path.read_text(encoding="utf-8"))
    if pkg.get("schema") != "hololab-card-package/v1":
        raise ValueError(f"不是有效的卡片包（schema 应为 hololab-card-package/v1）：{path}")
    if not pkg.get("idea") or not str(pkg["idea"]).strip():
        raise ValueError("卡片包缺少 idea（一句话创意）")
    return pkg


def main() -> int:
    parser = argparse.ArgumentParser(description="卡片包 → 出卡管线")
    parser.add_argument("--package", required=True, help="卡片包 JSON 文件路径")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"文字模型 ID（默认 {DEFAULT_MODEL}）")
    parser.add_argument("--outdir", default=None, help="输出目录（默认 projects/<slug>）")
    args = parser.parse_args()

    api_key = os.environ.get("ARK_API_KEY", "")
    if not api_key:
        print("错误：环境变量 ARK_API_KEY 未设置（可 source 项目 .env）", file=sys.stderr)
        return 2

    pkg = load_package(Path(args.package))
    idea = str(pkg["idea"]).strip()
    lang = pkg.get("lang") or osc.detect_lang(idea)
    print(f"[1/4] 卡片包校验通过 → 语言：{'中文' if lang == 'zh' else 'English'}｜创意：{idea}")

    print(f"[2/4] 调用文字模型 {args.model} 生成配置…")
    raw = osc.call_llm(idea, args.model, api_key,
                       system_prompt=osc.SYSTEM_PROMPT if lang == "zh" else osc.SYSTEM_PROMPT_EN)
    cfg = osc.extract_json(raw)

    problems = osc.validate(cfg, lang)
    if problems:
        print("校验未通过：", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(f"模型输出原文（供排查）：\n{json.dumps(cfg, ensure_ascii=False, indent=2)}", file=sys.stderr)
        return 1

    cfg["mode"] = "holographic"
    cfg["edition"] = osc.next_edition()
    cfg.update(osc.default_params())

    # 交叉核对：卡片包身份锚点 vs LLM 生成 identity（供策展人确认）
    pkg_identity = str(pkg.get("identity") or "").strip()
    llm_identity = str(cfg.get("identity") or "").strip()
    print(f"[3/4] 身份锚点交叉核对：\n  卡片包：{pkg_identity[:60] or '（无）'}\n  LLM 生成：{llm_identity[:60]}")
    if pkg_identity and llm_identity and not any(
            k in llm_identity for k in (pkg_identity.split('·')[0][:8], pkg_identity.split(';')[0][:12])):
        print("  ⚠ 提示：卡片包与 LLM 的身份锚点差异较大，策展时请人工确认。", file=sys.stderr)

    slug = cfg["slug"]
    outdir = Path(args.outdir) if args.outdir else (ROOT / "projects" / slug)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "card-config.json"
    out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[4/4] 配置已写入 → {out}")
    print(f"      主题：{cfg['title']}｜{cfg['subtitle']}｜{cfg['technique']}｜{cfg['collection']}")
    print(f"      接下来跑流水线出卡：")
    print(f"  python scripts/ai_generate.py projects/{slug} --model doubao-seedream-5-0-flash-260915")
    print(f"  python scripts/run_pipeline.py projects/{slug} --blender ../tools/blender-4.5.0-linux-x64/blender")
    print(f"  python scripts/publish_card.py projects/{slug} --tags <标签> --blender ../tools/blender-4.5.0-linux-x64/blender")
    return 0


if __name__ == "__main__":
    sys.exit(main())
