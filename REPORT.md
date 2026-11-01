# Agent Zero screenshot navigation — verified, with a retry

2026-10-21 17:08 UTC. Brian was right to challenge the text-only claim.

## Results
- Live Halogen 0.17.2 health reports vision enabled. Direct OpenAI-compatible image request returned HTTP 200 and correctly identified all four randomized quadrant colors. A direct request using the actual browser screenshot also located the green circle near (148,418), versus ground-truth (150,420).
- Instance1 new context `QjEFT9FW` used the existing local model. Only this chat's model override enabled vision=true (temperature=0 and enable_thinking=false request override for a bounded test). Global presets and both previous chat metadata snapshots remained exactly unchanged.
- Actual browser task used browser open/screenshot/coordinate click or mouse and vision_load only. No DOM, accessibility, content/evaluate, OCR, code, source reads, or HTTP shortcuts by the agent. Tool trace audited programmatically.
- Loopback-only synthetic challenge rendered randomized instructions/colors as image pixels; the next step and final marker were not in HTML text. The server independently logged clicks and stage transitions.
- First attempt: four misses near (145,490), stage stayed zero. Agent correctly reported failure but incorrectly speculated a viewport offset.
- Retry: operator supplied only independently verified native screenshot dimensions 1024x768 and no chrome/offset, not coordinates or answers. Agent visually chose (145,415), advancing stage1, then (435,415), advancing stage2. Ground-truth centers were (150,420) and (440,420).
- Exact final marker `VISION-PASS-295744` matches server ground truth, agent final reply, and separately inspected final screenshot.
- Successful clicks: 17:06:53.681639 UTC and 17:07:08.211488 UTC. Final agent response: 17:07:23.001689 UTC. Six total clicks across two attempts, two correct.

## Evidence
`verification.json`, `direct-result.json`, `direct-groundtruth.json`, `direct-screenshot-coordinate.json`, `agent-trace.json`, `attempt-1-trace.json`, `tool-trace.json`, `challenge-state.json`, `challenge-groundtruth.json`, `final-screenshot.jpg`, `screenshot-manifest.json`, `before/after-{1,2}.json`, `presets-before/after.json`, `override-readback.json`, request payloads and reproducible scripts.

## Scope and limitations
This demonstrates real screenshot understanding and successful screenshot-driven interaction, not reliable unsupervised GUI operation. Global default vision remains false; no global correction, backend change, restart, model download or second-instance configuration change was performed. Existing contexts were idle before testing and preserved. Test context and its per-chat override remain available for review. Temporary server inside instance1 was stopped; follow-up verified PID absent and localhost port no longer answers. Test artifacts remain under `/a0/usr/workdir/vision-test` and the new chat's screenshots.

Harness issues: initial server health probe raced startup (later HTTP200); immediate post-kill PID probe raced process exit (follow-up confirmed stopped). Neither affected test results. Old pilot REPORT and reusable skill corrected. Canonical Obsidian not modified; this report is a pending note source.
