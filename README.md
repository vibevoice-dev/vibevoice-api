# VibeVoice API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/xiaomi/mimo-tts?utm_source=github&utm_medium=ugc&utm_campaign=vibevoice-dev&utm_content=readme-badge&utm_term=tier-a)

VibeVoice is Microsoft's open text-to-speech model for long, multi-speaker conversational audio such as podcasts and audiobooks. This package is a Python client that gives you a VibeVoice API for the same kind of work, expressive narration, voice cloning from a short clip and style-directed delivery, with `pip install vibevoice-api` and no GPU of your own.

You get a blocking `run()` that returns the finished audio, a submit-and-poll path for long scripts, webhook delivery for servers that must not block, and a single runtime dependency (`requests`). It is meant for content pipelines, backend services and notebooks that need speech synthesis as a function call rather than a model checkout.

> **Try it now:** [https://synexa.ai/explore/xiaomi/mimo-tts](https://synexa.ai/explore/xiaomi/mimo-tts?utm_source=github&utm_medium=ugc&utm_campaign=vibevoice-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About VibeVoice](#about-vibevoice)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **The 7B model wants a serious GPU.** VibeVoice-Large is a 7B parameter LLM plus a diffusion head; the bf16 weights alone are around 14 GB and comfortable inference needs a 24 GB-class card. The hosted endpoint runs on hardware sized for it.
- **Long scripts are slow locally.** VibeVoice generates speech at a 7.5 Hz token rate through an autoregressive backbone, so an hour of audio on one GPU is a long job; a hosted queue lets you run many scripts in parallel.
- **No cold start.** Loading the backbone, the acoustic and semantic tokenizers and the diffusion head takes time before the first second of audio; hosted runs start warm.
- **Per-run pricing.** `xiaomi/mimo-tts` is $0.02 per run and `elevenlabs/tts-v3` is $0.05 per run. There is no instance to keep alive between requests.

## Installation

```bash
pip install git+https://github.com/vibevoice-dev/vibevoice-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=vibevoice-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import vibevoice_api

output = vibevoice_api.run({
    "text": "Hello, this is a test of MiMo speech synthesis."
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from vibevoice_api import Client

client = Client(api_key="sk-...")
output = client.run({"text": "Hello, this is a test of MiMo speech synthesis."})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`xiaomi/mimo-tts`](https://synexa.ai/explore/xiaomi/mimo-tts?utm_source=github&utm_medium=ugc&utm_campaign=vibevoice-dev&utm_content=readme-models&utm_term=tier-a) | text-to-audio | Xiaomi MiMo V2.5 text-to-speech. Speaks text with one of 9 built-in voices, clones a voice from a reference clip, or invents a new voice from a written description. | $0.02 |
| [`elevenlabs/tts-v3`](https://synexa.ai/explore/elevenlabs/tts-v3?utm_source=github&utm_medium=ugc&utm_campaign=vibevoice-dev&utm_content=readme-models&utm_term=tier-a) | text-to-audio | Eleven v3 reads text aloud with expressive, emotionally aware delivery across dozens of languages. | $0.05 |

The default model is **`xiaomi/mimo-tts`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `xiaomi/mimo-tts`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `text` | string | yes | `Hello, this is a test of MiMo speech syn…` | — | Text to speak. A style tag may lead the text, e.g. '(happy)Hello there'; inline tags such as '(sigh)' are also supported. Tags are never spoken out loud. |
| `voice` | string | no | `Dean` | mimo_default, 冰糖, 茉莉, 苏打, 白桦, Mia, Chloe, Milo, Dean | Built-in voice. Mutually exclusive with reference and description |
| `reference` | file | no | — | — | A .wav/.mp3 clip whose voice gets cloned (Optional). 10-30 seconds of clean speech works best. Mutually exclusive with voice and description |
| `description` | string | no | — | — | A sentence that invents a new voice, e.g. 'man in his forties, deep and raspy, speaks slowly' (Optional). Every call invents a slightly different voice. Mutually exclusive with voice and reference |
| `instructions` | string | no | — | — | Plain-language style note, e.g. 'slow down, sound tired' (Optional). Never spoken out loud. Not allowed together with description, which already carries the style |
| `audio_format` | string | no | `wav` | wav, mp3 | Output audio format |

### `elevenlabs/tts-v3`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `text` | string | yes | `The quiet part of the morning is the onl…` | — | The text to convert to speech |
| `voice` | string | no | `Rachel` | — | The voice to use for speech generation |
| `stability` | number | no | `0.5` | 0, 1 | Voice stability (0-1) |
| `timestamps` | boolean | no | `False` | — | Whether to return timestamps for each word in the generated speech |
| `language_code` | string | no | — | — | Language code (ISO 639-1) used to enforce a language for the model. |
| `apply_text_normalization` | string | no | `auto` | auto, on, off | This parameter controls text normalization with three modes: 'auto', 'on', and 'off'. When set to 'auto', the system will automatically decide whether to apply text normalization (e.g., spelling out numbers). With 'on', text normalization will always be applied, while with 'off', it will be skipped. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from vibevoice_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About VibeVoice

VibeVoice was released by Microsoft Research in August 2025 as an open framework for generating expressive, long-form, multi-speaker conversational audio. Its two main ideas are continuous speech tokenizers (one acoustic, one semantic) that run at an unusually low 7.5 Hz frame rate, which keeps hour-long audio inside a manageable sequence length, and a next-token diffusion design in which a large language model reads the script and dialogue structure while a lightweight diffusion head renders the acoustic detail. The backbone is Qwen2.5-based, and checkpoints were published at 1.5B and 7B parameters under the MIT licence.

The headline capability is scale: a single generation can run to about 90 minutes of speech with up to four distinct speakers, with turn-taking handled by the model rather than by stitching clips together. Speaker identity comes from short reference samples, delivery is natural and conversational, and the model was trained primarily for English and Chinese. A smaller streaming variant was added later for real-time use.

Limits are worth knowing before you build on it. It is not designed for sound effects, singing or background music; cross-lingual and code-switched input can produce unexpected accents; overlapping speech is not supported; and Microsoft ships it for research with a built-in audible disclaimer and imperceptible watermark, which matters if you intend to deploy it commercially.

The hosted endpoint used by this client is `xiaomi/mimo-tts`, which provides the same expressive text-to-speech capability, including voice cloning from a 10 to 30 second reference clip, inline style tags such as `(sigh)` and plain-language delivery instructions; the original VibeVoice weights are available at https://github.com/microsoft/VibeVoice if you want to self-host. The client also exposes `elevenlabs/tts-v3` for emotionally aware multilingual narration.

**Official project:** https://github.com/microsoft/VibeVoice

## Use cases

- **Podcast narration** — call `run()` with the script as `text` and a built-in `voice` to render a segment, then concatenate segments per speaker.
- **Voice cloning from a sample** — pass a 10 to 30 second clean `reference` clip and the model speaks your text in that voice.
- **Invent a character voice** — supply a `description` such as "woman in her sixties, warm, slightly hoarse" to get a new voice without any reference audio.
- **Audiobook batches** — submit one job per chapter without blocking and collect the files through a webhook.
- **Emotion-tagged dialogue** — prefix lines with a style tag like `(happy)` or add `instructions="slow down, sound tired"` to direct delivery per line.
- **Multilingual product voiceovers** — switch to the `elevenlabs/tts-v3` endpoint with a `language_code` for narration in dozens of languages.

## FAQ

**Is there a VibeVoice API?**

Microsoft publishes VibeVoice as open weights and a research repository, not as a hosted API. This package wraps a Synexa endpoint that provides the same expressive text-to-speech and voice cloning capability, so you can call it over HTTPS without running the model yourself.

**How much does the VibeVoice API cost?**

The default endpoint, `xiaomi/mimo-tts`, is $0.02 per run. The `elevenlabs/tts-v3` endpoint is $0.05 per run. Billing is per completed run.

**Can I run VibeVoice without a GPU?**

The 1.5B model can be coaxed onto CPU but generation is far slower than real time, and the 7B model needs a 24 GB-class GPU. With this client the synthesis happens on the hosted side, so any machine that can make an HTTPS request is enough.

**Does this client work with the original microsoft/VibeVoice repo or ComfyUI?**

No. It does not load local checkpoints or talk to the ComfyUI VibeVoice nodes. It is an HTTP client for the hosted endpoints only.

**What input formats does it accept?**

Only `text` is required. You may then choose one of `voice` (a built-in voice), `reference` (a .wav or .mp3 clip of 10 to 30 seconds to clone) or `description` (a sentence describing a new voice); they are mutually exclusive. `instructions` adds a delivery note and cannot be combined with `description`. `audio_format` selects the output container.

**Is this the official VibeVoice SDK?**

No. This is an independent client and is not affiliated with Microsoft. The official project is at https://github.com/microsoft/VibeVoice.

## Related

- [VibeVoice (official repository)](https://github.com/microsoft/VibeVoice)
- [Synexa Python client](https://github.com/synexa-ai/synexa-python)
- [xiaomi/mimo-tts on Synexa](https://synexa.ai/explore/xiaomi/mimo-tts)
- [elevenlabs/tts-v3 on Synexa](https://synexa.ai/explore/elevenlabs/tts-v3)

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of VibeVoice. Model weights and trademarks belong to their respective owners.

_Last reviewed: 2026-09-22_
