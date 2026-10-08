# Concurrent CI Engineering: How Tests Grew from 0 to 28

## There was no CI at first

Early on, this project only deployed: push to main, GitHub Actions ships to Pages. Zero tests. Changes were verified by "look at it once," which is mostly luck.

The turning point was the thumbnail bug — the publish script deleted the thumbnail it had just generated, breaking the homepage. Three lines fixed it, but I realized something: **I would make this mistake again**. Carefulness doesn't hold a pipeline together.

## How the tests grew

They weren't designed in one pass. They were fed by one card, one failure at a time. Today `gallery-check` runs **28 tests** on every push:

| Group | What it checks |
|---|---|
| Config schema | every card's fields are valid; missing field fails hard |
| Manifest consistency | cards.json matches real files, nothing dangling |
| i18n coverage | new labels must have zh/en entries or CI blocks |
| importmap idempotency | rewriting the module map twice doesn't duplicate |
| Thumbnails | every card has a real thumbnail (guards the old bug) |
| Asset validation | GLB valid, vendor present, no 404 references |
| Prompt building | generation prompts assemble correctly |
| Preflight gates | pre-render checks (model cache, keys, deps) |

Plus a **gallery health check**: all 77 cards scanned for asset existence. That used to be manual work; CI now does it on every push.

## The concurrency trap

Later, a batch meant rendering several cards at once. Concurrent workflow runs collided — two jobs writing the same project directory, stepping on each other. The fix was a concurrency group on the workflow: only one render job at a time, the rest queue.

Sounds like a downgrade (less parallelism = slower?), but the real win was **determinism**. Rendering is heavy file-writing work; one collision wastes an entire batch rerun. Queuing is the stable choice.

## One judgment

Test count is not a KPI. There are 28 because "these 28 classes of failure actually happened, or plausibly will." Every new failure class gets a test that pins it down, which is what lets the project keep growing.

Fast-without-CI is temporary fun. Slow-with-CI is the fair deal.
