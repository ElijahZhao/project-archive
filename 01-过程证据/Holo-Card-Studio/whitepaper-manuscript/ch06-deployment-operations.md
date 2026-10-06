# 第六章 部署与运维（Deployment & Operations）

## 一、纯静态展厅

The public gallery is a pure static site: an HTML homepage, a JSON manifest, per-card HTML pages, shared vendor JavaScript, and image and model assets. Because there is no backend, it can be served by any static host at zero infrastructure cost, and the entire deployment is just a directory of files. This is a deliberate consequence of the zero-backend constraint in Chapter 2: the card list is data in cards.json, not rows in a database, and the interactive viewer runs entirely in the browser.

## 二、GitHub Pages 部署

The repository hosts the gallery under a subdirectory, so Pages must deploy that subdirectory rather than the repository root. The deployment uses GitHub Actions: a workflow checks out the repository, configures Pages, uploads the gallery directory as an artifact, and runs the Pages deploy action inside `deploy.yml`. Pushing to the main branch triggers the workflow automatically, and the site becomes available at the public URL after roughly one to two minutes. The workflow itself is in the repository, so the deployment procedure is auditable and reproducible.

## 三、幂等的发布脚本

Publishing a new card is a single command that runs the publish script with the project directory, the card id, and style tags. The script performs four idempotent operations: it regenerates the thumbnail at a fixed width; it archives the card into the gallery, removing any previous archive with the same id; it rewrites the card page's import map to point at the shared vendor directory instead of a per-card dependency; and it updates cards.json with deduplication and newest-first ordering, so the same card can be published repeatedly without creating duplicates or stale copies. Idempotency is verified in practice: re-publishing a card produces the same gallery state rather than an accumulating set of copies.

## 四、密钥与安全

API keys are stored in a local .env file whose key name is ARK_API_KEY, and .gitignore excludes it from version control. The repository therefore contains no secrets; the only configuration artifact that ships is a .env.example documenting the required key name. The deployment workflow never receives or forwards credentials. On the local machine, git credentials are managed separately with a credential helper, and the project repository history was checked to confirm that no key was ever committed. Security-sensitive reviews of the public repository can confirm the absence of secrets by inspection.

## 五、资产治理

Gallery size is managed by the shared vendor strategy and by archive hygiene. Each archived card keeps its five essential assets (subject, background, line art, typography, GLB) plus the thumbnail and the page; the work directory with intermediate artifacts stays out of the public gallery, in the generation workspace, so the published site carries only what the browser needs. The shared three.js bundle is hosted once in the gallery vendor directory rather than duplicated per card, which keeps the archive growth sublinear in the card count.

## 六、排障与运维实践

The project logs operational lessons as documentation. Common failure modes and their resolutions are recorded: a 404 on the site points to a wrong Pages branch or directory selection; a black card page points to missing WebGL support in the browser; slow image loading points to the full-resolution source assets, with a compression step planned; and a .env appearing in git status is treated as a stop condition with instructions not to commit. Keeping these notes in the repository turns operational knowledge into part of the codebase, so the next deployer or reviewer does not have to rediscover the same traps.
