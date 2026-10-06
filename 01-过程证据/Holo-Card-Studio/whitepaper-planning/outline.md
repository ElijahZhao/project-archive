# HoloLab Studio White Paper · Outline

## 核心主张

HoloLab Studio 是一条可复现、可审计、零后端的端到端 AIGC 应用管线：从一句文本或一张照片出发，经豆包 Seedream 5.0 分层图像生成、rembg 抠图、OpenCV 线稿与程序化字体排版，组装为 Blender 3D 全息卡，导出 GLB 后在 Three.js 实时查看器中重建视差与镭射效果，最终以纯静态站点部署于 GitHub Pages 公开可玩。作者（本科人工智能专业申请者）以该工程证明「分而治之的可靠性优先系统设计」而非「单模型炫技」。

## 语气 / 作者声音

technical-but-readable；工程化、诚实、克制。陈述事实与 tradeoff 时不夸大；每一关键决策附动机、替代方案与代价。无营销腔、无空洞套话。

## 目标读者

海外 AI / AI 交叉方向硕士项目的招生官与教授（具备 ML/CS 基础，可在 15–20 分钟内读完并形成能力判断）。

## 章节规划

| 章节 | 标题 | 核心问题 | 用户收获 | 目标字数 |
|---|---|---|---|---|
| ch01 | Executive Summary | 这个项目是什么、为什么值得看、核心能力点是什么 | 5 分钟内建立对项目与作者的完整印象 | 2200 |
| ch02 | Background & Motivation | 为什么做这个项目？AIGC 现状与个人动机构成的选题依据 | 理解问题定义与选题合理性 | 3400 |
| ch03 | System Architecture | 系统如何分层、数据如何流动、关键设计约束是什么 | 看懂全链路架构与「零后端」设计取舍 | 4200 |
| ch04 | AI Generation Pipeline | 四层素材为何分而治之？每层用什么工具、为什么 | 看清图像生成/抠图/线稿/文字的具体工程做法 | 4600 |
| ch05 | 3D Rendering & Realtime Shaders | Blender 与 Three.js 双路径如何共享同一套视差/镭射数学 | 理解离线渲染与实时重建的一致性与差异 | 4600 |
| ch06 | Deployment & Operations | 如何零服务器公开上线？发布脚本与 CI 如何保证幂等与安全 | 掌握静态化部署、资产治理与密钥安全实践 | 3200 |
| ch07 | Engineering Practice & Lessons | 踩过哪些坑、如何发现与修复、可靠性如何保证 | 看到真实的工程判断力与调试能力 | 3000 |
| ch08 | Limitations, Roadmap & Contribution | 已知边界与后续路线？作者的贡献如何界定 | 形成对项目成熟度与作者潜力的最终判断 | 2800 |

## 章节依赖关系

| 章节 | 前置章节 |
|---|---|
| ch01 | — |
| ch02 | ch01 |
| ch03 | ch01, ch02 |
| ch04 | ch03 |
| ch05 | ch03 |
| ch06 | ch03, ch04 |
| ch07 | ch03, ch04, ch05, ch06 |
| ch08 | ch01, ch02, ch03, ch04, ch05, ch06, ch07 |

## 总字数目标

28000 字符（英文正文，tolerance ±20%，硬门禁 22400–33600）。各章目标之和 = 28000。
