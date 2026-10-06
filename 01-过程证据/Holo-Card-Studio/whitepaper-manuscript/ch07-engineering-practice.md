# 第七章 工程实践与踩坑（Engineering Practice & Lessons）

## 一、一个真实的发布级 Bug：缩略图自删

The first published bug was discovered during a full-site audit: thumbnails were being deleted as soon as they were generated, leaving broken images on the homepage. The root cause was a call-order error in the publishing script — the archive step cleared the destination directory before the thumbnail generation step wrote into it, so the freshly created thumbnail was removed immediately. The fix reordered the pipeline to clear the archive first, then generate the thumbnail, then rewrite the import map, then write back the card id, and then update the manifest. After the fix, the live thumbnail returned HTTP 200 with the expected dimensions. The lesson recorded in the codebase is that idempotent scripts must specify the order of destructive and non-destructive steps explicitly, and that a verification pass over the live site — not just local generation — is what catches this class of bug.

## 二、前后端契约 bug：网格选择器失效

A front-end refactor replaced the gallery grid element's id, breaking the JavaScript lookup that renders cards: the homepage silently rendered zero cards while the console stayed clean. The fix added a fallback selector so the rendering code binds to the grid whether it is addressed by the old or the new id. A second layer of the same incident was browser caching: after the fix was deployed, the live page still showed zero cards until a cache-busting query parameter forced the browser to fetch the new script. Both lessons — resilient DOM bindings and cache-busting on static deployments — are documented as deployment practice.

## 三、资产路径与依赖的坑

A card page initially reported a 404 for its GLB model. Inspection showed the path was simply wrong in the card page: the GLB lived at the archived assets path, not the path the page was requesting. Correcting the URL restored the model. A related pitfall is the shared vendor strategy: when the import map rewrite is not idempotent, re-publishing the same card can accumulate broken dependency pointers; the rewrite function was verified to be idempotent so re-runs converge to the same correct state. These cases reinforce the rule that archive content, manifest content, and page content must be verified against each other after every publish.

## 四、环境与依赖的坑

Two environment-level lessons are recorded. First, the sandbox browser has no WebGL, so the 3D card page shows a fallback state; this is an environment limitation, not a project bug, and must be verified in a real browser. Second, background shell tasks in the build environment were terminated after a timeout, which silently interrupted a long render; the workaround is to split long tasks into foreground segments with bounded time each. Third, the background-removal stack hit a CPU performance wall with the default model; switching to u2net and downsampling before inference made matting feasible on CPU without a GPU. Each lesson is written into the project notes so the next operator does not re-discover it.

## 五、模型与 API 的坑

The image generation endpoint returned a 404 for the flash model name until the complete model id including its version date suffix was used; the documented model id in the official model list is the authoritative value, and the pipeline now accepts the model as an overridable parameter. A download endpoint for a portable Blender build returned HTTP 403 in a restricted network, so the pipeline was changed to reuse a pre-seeded portable package when present, and to verify SHA-256 checksums when downloading. These cases illustrate a general reliability rule: external dependencies must have a local fallback and a checksum, because network and API behavior is outside the project's control.

## 六、可靠性机制总结

Across the project, reliability comes from four mechanisms rather than from luck. Validation gates check real alpha, dimensions, and line-art extremes before a card can proceed. Fallbacks keep the pipeline alive when a single tool fails, while still preferring the high-quality path. Idempotent scripts and manifest deduplication make repeated publishing converge. And a written audit trail — verification.json per card, work directories retained, and documented bug fixes — makes every step inspectable. The combination is what allows the pipeline to be described as reproducible rather than merely working once.
