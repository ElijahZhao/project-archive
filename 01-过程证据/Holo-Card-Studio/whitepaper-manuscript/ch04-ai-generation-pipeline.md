# 第四章 AI 生成管线（AI Generation Pipeline）

## 一、四层结构与工具分工

The core idea is divide and conquer: no single model is asked to do everything, and each layer uses the tool that is best at its specific job. The subject layer needs a transparent-background character, so it uses Seedream to generate a clean figure and rembg with u2net to cut the background, because generative models do not output alpha channels. The background layer needs an environment shot that can move independently for parallax, so it is generated as a separate Seedream image with the same style prefix. The line-art layer needs a white-background black-line contour that registers pixel-exactly with the subject, so it is extracted programmatically with OpenCV rather than redrawn by a model. The typography layer needs crisp card text, so it is rendered by a font renderer from the card configuration, because generative models remain unreliable at rendering CJK glyphs; this is a documented tradeoff（已知取舍）that favors correctness over convenience.

## 二、提示词工程

### （一）共享风格前缀

The subject and background prompts share one style prefix, so both layers converge to the same visual world. The published cards use a style like "Japanese ukiyo-e and ink-wash anime collectible-card illustration, mineral-pigment texture, clear brush strokes, dramatic night lighting". The subject prompt appends the subject description plus a composition constraint: "centered, about 65% of the canvas, breathing space on all sides". The background prompt appends an environment description plus two constraints: "lower 40% stays empty for typography" and "no figures appear".

### （二）参考图模式（以图生图）

When the user provides a photo, the original image is passed as the image field to Seedream 5.0, and the prompt describes only the style and preservation constraints: "keep the pose, composition, and identity of the subject, repaint in the target style". Seedream 5.0 accepts joint text-plus-image input and can lock identity, which is one reason it was chosen. This mode is what makes personalized cards from a single photo possible.

### （三）构图一致性的缓解

Because subject and background are independent generations, pixel-level alignment is not guaranteed. The mitigations are: a shared style prefix with an explicitly quiet background; parallax occlusion in the viewer, where the subject overlaps the background; and honest documentation of the tradeoff in code and docs. In a portfolio, honesty about a limitation（局限）is more credible than perfection.

## 三、抠图（rembg）

Matting uses the u2net model, about 176 MB, chosen over the default bria-rmbg-2.0 model, about 1 GB, because u2net is far better suited to CPU inference. The input image is downsampled to half resolution before inference, then upscaled back with LANCZOS; this bounds memory and latency while keeping quality reasonable. If matting fails entirely, the pipeline degrades to a centered elliptical alpha fallback so validation can pass, but the high-quality path always prefers normal matting.

## 四、线稿提取（OpenCV）

Line-art extraction is a deterministic five-step routine. First, the alpha channel is thresholded into a subject mask. Second, Canny edges on the grayscale image extract internal detail, such as costume texture and facial features. Third, Canny on the alpha mask extracts the outer contour. Fourth, internal edges intersect the mask and union with the contour, producing a white-background black-line drawing. Fifth, a single erode pass thickens the lines; the code notes that a dilate pass would erase thin black lines into white, a real pitfall hit during development. Because the line art shares the subject's canvas and coordinates, the two layers are aligned by construction; the threshold parameters are stable for the illustration style used by the cards.

## 五、文字层（字体排版）

The typography layer reads the card configuration — title, subtitle, collection, technique, and edition number — and lays them out precisely on a transparent canvas using a system CJK serif font, with gold divider lines and stroke outlines. Text width auto-scales to prevent long titles from overflowing the card face. This guarantees that text on every card is byte-exact with the configuration, which generative models cannot yet meet reliably for Chinese text. The tradeoff is visual: programmatic text looks clean but less painterly than hand-drawn lettering; the project accepts this（接受此取舍）for correctness.

## 六、为什么这样设计（作品集叙事）

Four principles summarize the design. First, distrust the single model: image generation, matting, edge extraction, and text rendering each use the most reliable tool for the subtask, and the pipeline degrades gracefully when one tool fails. Second, reliability first: every layer has validation for real alpha, line-art extremes, and dimensions, with documented fallbacks, so the pipeline is reproducible rather than lucky. Third, explainability: every layer's product, parameters, and prompt land on disk, making the pipeline easy to debug and audit. Fourth, cost awareness: generation uses the flash tier of the image model where possible, keeping per-card cost near zero. The next enhancement（下一步建议）is a one-sentence-to-card mode in which a language model drafts the configuration, closing the loop from natural language to a published card.
