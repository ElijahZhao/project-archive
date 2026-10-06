# 第五章 3D 渲染与实时着色（3D Rendering & Realtime Shaders）

## 一、两条渲染路径的分工

A holographic card has two rendering paths with different jobs. The offline path uses Blender Cycles, a path tracer, for the hero image and the thumbnail: physically accurate lighting, expensive, minutes per image, run only at publish time. The online path uses Three.js with a custom GLSL shader in the browser: WebGL renders every frame as the user drags, so it must run in real time. The browser cannot replicate Cycles' offline lighting, so the viewer reconstructs the same four-layer compositing and foil effect with the same UV and parallax formulas, producing a visually similar but not identical result. This divergence is declared in the upstream project and noted in the code comments; it is a known limitation（已知局限）of the real-time path.

## 二、视差（Parallax）原理

Parallax is the visual depth effect: the subject floats in front of the card, and the background recedes behind it, as the viewing angle changes. The math is a UV transform applied per layer:

UV' = (UV − 0.5) × scale + 0.5 + viewOffset × depth

Here viewOffset is the view direction projected onto the card plane in object-local space; depth is a per-layer signed coefficient; scale is a safety expansion that prevents layer edges from showing through. In the shipped cards, the subject uses scale 1.25 and depth +0.4 (forward); the background uses depth −0.25 (backward); the text uses depth 0 (stuck to the surface). A grazing-angle guard clamps the UV offset when the view is nearly parallel to the surface, preventing the UV from blowing open at extreme angles. The Blender side implements this as a custom node group, and the Three.js side implements the identical formula in the fragment shader's parallax function; both renderers share one mathematical model.

## 三、镭射（Foil）材质

The holographic foil is a color band sweeping from pink through yellow and blue to white, with a phase driven by UV plus a view offset:

w = sin((uv.x·0.848 − uv.y·0.530)·2π·0.55 + 7·noise(uv·1.5))
color = spectrum(w + viewPhase)

In Blender, this is built with a wave texture node, a wood-grain particle texture, and a color ramp. In Three.js, the spectrum and wave functions are reimplemented in GLSL. The foil is blended OVERLAY onto the subject and background layers, and its strength is controlled by a user slider. A high-power sine creates a narrow specular sweep, so the foil appears to flow as the card moves; this effect is the visual signature of the product.

## 四、星光与辉光

Two finishing effects complete the look. Voronoi sparkles use a distance-to-edge feature with a threshold to create tiny glints, driven by four-dimensional noise so they flicker over time; both Blender and WebGL have matching implementations. A glow pass adds bloom: the Three.js path uses an UnrealBloomPass on a downsampled buffer to let foil highlights overflow, and the Blender path uses an equivalent compositor glow node. Saturation is protected by a gamma-style power and tone mapping, so the printed look is not washed out by highlights.

## 五、导出链路

The build script constructs the card scene; the export script then opens card.blend and replaces the material slots with placeholder materials named "web_front", "web_edge", "web_back", and "web_gold" before exporting the GLB with UVs and node hierarchy intact. The front-end matches these material names and attaches the real-time shader materials: web_front gets four-layer compositing plus parallax and foil; web_back gets the indigo back face; web_edge gets the card-edge foil; web_gold gets the antique-gold frame. This separation of offline and web material graphs keeps the export stable while allowing two implementations of the same visual result.

## 六、性能

Performance is bounded by design. The four textures are 1920×2880 PNGs at original resolution, which is the current main size cost and a known roadmap item. The WebGL path uses an orthographic camera and a single fullscreen compositing pass; the bloom pass runs on a downsampled buffer to keep fragment cost low. Users with the prefers-reduced-motion preference are served a version that disables auto-rotation, which respects accessibility requirements. The next steps（下一步建议）are texture compression and a hover preview per card, both scheduled in Chapter 8.
