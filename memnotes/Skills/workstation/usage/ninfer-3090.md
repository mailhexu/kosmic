---
type: Domain Topic
id: workstation/usage/ninfer-3090
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Build ninfer-3090 on Ubuntu 25.10 with an RTX 3090 using a user-prefix CUDA 13.1.2 toolkit, pin the fork-compatible Qwen artifact, and wire the server into omp.
triggers: [ninfer, ninfer-3090, RTX 3090, Qwen3.8, omp model, reasoning effort]
source_project: native
source_sha256: empty
aliases: [ninfer setup]
---

# ninfer-3090 on Ubuntu 25.10 / RTX 3090

ninfer-3090 is the `Don-Chad/ninfer-3090` fork. Build it natively, then expose its OpenAI-compatible server as an omp model.

## Build constraints

- The fork requires CUDA Toolkit >= 12.8. The Ubuntu `nvcc` 12.4 fails at CMake configure. Install a user-prefix CUDA 13.1.2 toolkit under `/scratch`; the CUDA apt repository has no Ubuntu 25.10 target.
- Use GCC 15 for C, C++, the CUDA host compiler, and final links. GCC 13 can compile, but its private libstdc++ lacks `CXXABI_1.3.15`, which Ubuntu 25.10 `libsrt-gnutls` requires.
- Configure `CMAKE_CUDA_ARCHITECTURES=86` (Ampere SM86), `NINFER_BUILD_APPS=ON`, tests and benchmarks off. Patch only the isolated toolkit copy of `targets/x86_64-linux/include/crt/math_functions.h`: add `noexcept` to the `rsqrt(double)` and `rsqrtf(float)` declarations (glibc 2.42 conflict). Do not use `-U_GNU_SOURCE`; it breaks libstdc++ headers.

## Layout

```text
/scratch/ninfer/
  ninfer-3090/                 # source
  cuda-13.1.2/                 # user-prefix toolkit
  models/qwen3_8_27b.ninfer    # pinned artifact
  env.sh
```

## Artifact selection

Pin the pre-DFlash2 Hugging Face revision `18dfc887423fa5aabf3cb56fac41490e462b3fab` of `neroued/Qwen3.8-27B-NInfer`; expected size 18,210,531,328 bytes. The current `main` artifact contains DFlash2/sm_120a objects for upstream RTX 5090 builds; this fork rejects it.

## Server profile

`scripts/run-qwen38-c1.sh` runs `ninfer-serve` with: host 127.0.0.1, port 54321, `--max-context 150000 --kv-capacity 150000`, `--max-concurrency 1`, `--prefill-chunk 1024`, `--kv-dtype int8`, `--spec mtp --draft-tokens 3 --lm-head-draft`.

## omp configuration

Create `~/.omp/agent/models.yml` with a `ninfer` provider: `baseUrl http://127.0.0.1:54321/v1`, api `openai-completions`, auth none, model id `qwen3.8-27b`, `reasoning: true`, `contextWindow: 150000`.

Wire these thinking fields exactly (wire-verified 2026-09-20): `thinkingFormat: openai` (the `qwen` dialect emits only `enable_thinking`, never an effort field); `reasoningDisableMode: none-effort` (maps `:off` to `reasoning_effort: "none"`); `effortMap: {high: xhigh}`; `defaultLevel: xhigh`; `qwenPreserveThinking: true` (emits `chat_template_kwargs.preserve_thinking`, which ninfer accepts).

ninfer's Qwen3.8 template accepts exactly `none`, `low`, `medium`, `xhigh`. `minimal`, `high`, and `max` return HTTP 400 `reasoning_effort_not_supported`.

Persist the default role with the complete object: `omp config set modelRoles '<complete role map with default set to ninfer/qwen3.8-27b>'`. Keep the other roles (`tiny`, `smol`, task, plan, vision) on their models.

## Verification

The server log prints one `[req N] ... reasoning_effort=<requested>-><resolved>` line per request; use it as ground truth:

```bash
for sel in xhigh low off medium; do
  omp -p --no-session --no-tools --model "ninfer/qwen3.8-27b${sel:+:$sel}" "Reply with exactly: OK-$sel"
done
```

Expected wire efforts: `xhigh->xhigh`, `low->low`, `none->none`, `medium->medium`.
