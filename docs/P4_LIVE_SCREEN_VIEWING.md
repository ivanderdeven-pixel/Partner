# P4 Design: Live Screen Viewing for Giftia

Status: design proposal only. This document does not implement capture or change the runtime.

## Goal

Let Ikari observe the laptop display as a live visual stream while the user explicitly enables screen viewing. This is not a one-shot screenshot feature and does not include mouse/keyboard control.

## Proposed pipeline

```text
Windows display
  -> ScreenCapture provider
  -> frame sampler / change detector
  -> bounded latest-frame buffer
  -> vision-capable model
  -> visual observation with timestamp + confidence
  -> Giftia context / decision pipeline
  -> speak, act, or remain silent
```

Keep capture, visual interpretation, and Giftia's decision-making separate. The capture loop must not call the LLM for every frame, block terminal input, or write directly to long-term memory.

## Runtime behavior

- Default state is OFF at startup.
- `/look on` starts live observation after an explicit command.
- `/look status` reports whether capture is active and the selected sampling interval.
- `/look off` stops capture and releases capture resources immediately.
- `/look` may be an alias for status/help; it must not silently start observation.
- Show a persistent, visible terminal indicator while capture is active.
- Stop capture on process exit or capture/vision failure. Do not silently restart it.
- Start with a modest sampling target (for example, 1 frame/second) and tune after measuring latency and GPU/CPU use. This is a design starting point, not a performance guarantee.
- Keep only the newest pending frame; discard stale frames rather than building an unbounded queue.
- Run vision inference asynchronously with a single-flight limit. If inference is still running, skip or replace pending frames instead of accumulating work.
- Use change detection to avoid asking the vision model to interpret visually identical frames repeatedly.
- Send observations to Giftia's decision layer with timestamps and confidence. Let the decision layer choose whether the change merits a response; do not narrate every frame.

## Suggested module boundaries

- `perception/screen_capture.py`: start/stop capture and provide frames through a small interface. No LLM calls and no memory writes.
- `perception/frame_sampler.py`: sampling cadence, optional downscaling, image-change checks, bounded latest-frame buffer.
- `perception/vision.py`: adapter for a verified image-capable model; returns a concise structured observation, timestamp, and uncertainty.
- `perception/screen_session.py`: session state, explicit opt-in, status, cleanup, and failure handling.
- `main.py`: routes `/look` commands and forwards observations to the existing Giftia decision pipeline without letting capture compete with terminal input/output.
- Keep perception modules isolated so the current P5/P6 behavior remains usable when viewing is off.

Names are proposals; check the current repository layout before creating modules.

## Model compatibility

Do not assume the current `qwen3:latest` chat model accepts images. Before implementation:

1. Inspect the installed Ollama models and verify image-input support for the exact model/version.
2. Test one known image directly against the model.
3. Measure inference latency and VRAM/RAM use at the chosen image size.
4. Choose an explicit vision adapter/configuration rather than silently replacing Giftia's main chat model.
5. If no compatible model is available, report that clearly and keep screen viewing disabled.

A model that can describe a single image is not automatically fast enough for frequent live observations.

## Privacy and safety requirements

- Capture only the selected display/region and only while the user has explicitly enabled the feature.
- Do not upload frames to cloud services by default; local inference is the default design.
- Do not save raw frames or screenshots to disk by default.
- Do not turn screen contents into long-term memory automatically. A separate memory/consent policy is required.
- Avoid repeated transcription or storage of sensitive visible information (passwords, private messages, account pages). Provide a quick stop command.
- Make active capture visible and easy to stop; never hide the indicator.
- Screen viewing is read-only. Mouse clicks, keyboard input, and app control are separate future capabilities requiring separate explicit permission.

## Failure handling

- Capture errors: stop the session, release resources, and explain the error.
- Vision-model errors/timeouts: keep the application responsive, discard stale frames, and report that visual interpretation is temporarily unavailable.
- Uncertain recognition: label uncertainty instead of inventing details.
- Shutdown: stop capture and inference workers cleanly.

## Acceptance tests for a later implementation

1. Starting Giftia does not capture the screen.
2. `/look on` visibly indicates that capture is active.
3. A changing test window produces timestamped observations without storing screenshots.
4. `/look off` stops new frame acquisition promptly.
5. Slow vision inference does not create an ever-growing queue or freeze chat.
6. No vision inference is run for every raw frame; sampling and change detection are applied.
7. A missing/incompatible model fails safely without changing the normal chat model.
8. The existing chat, P5 decision flow, P6 features, and terminal input remain responsive when viewing is off and while viewing is on.
9. Screen observations are not added to long-term memory unless a separate, explicit policy later permits it.

## Scope and sequencing

This is a P4 design note only. Per the Giftia roadmap, full P4 implementation and Arduino integration remain deferred until P6 is complete. This design can be reviewed now without merging runtime changes into the current P6 branch.
