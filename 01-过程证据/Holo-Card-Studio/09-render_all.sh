#!/bin/bash
set -e
BLENDER=projects/messi-demo/tools/blender-4.5.9-linux-x64/blender
cd /home/user/Doubao/chats/38444574205007618/holo-lab/generator
echo "== messi 渲染开始 $(date +%T) =="
$BLENDER --background --python scripts/render_preview.py -- projects/messi-demo work/preview-frames/messi > work/render-messi.log 2>&1
echo "== messi 完成 $(date +%T)，帧数：$(ls work/preview-frames/messi | wc -l) =="
echo "== mj 渲染开始 $(date +%T) =="
$BLENDER --background --python scripts/render_preview.py -- projects/mj-demo work/preview-frames/mj > work/render-mj.log 2>&1
echo "== mj 完成 $(date +%T)，帧数：$(ls work/preview-frames/mj | wc -l) =="
