---
name: agnes-ai
description: >
  Agnes AI 全能创作 — 文生图、图生图、图像识别、文生视频、图生视频。Use this skill whenever the user asks to generate, create, draw, paint, or design an image or video from a text description, or when they want to transform/modify an existing image or generate video from images (image-to-image, image-to-video). Also triggers when the user mentions AI art, AI illustration, concept art, character design, product mockup, video generation, animate a photo, analyze an image, read text from image, OCR, screenshot analysis, or needs any visual content created. Use proactively for any image/video/text-generation task — don't wait for the user to ask about API details.
---

# Agnes AI 全能创作

Use this skill to generate images, videos, analyze images, and chat — all via the Agnes AI API platform.

## API Keys

| Service | Key |
|---|---|
| Image / Chat (Image Recognition) | `sk-FvetkuZyrc3103s707K9KIEzeROVj7ftdv7gfzPlPxl010Fb` |

Set as env var `AGNES_API_KEY` or pass via `--key` in scripts.

## Capabilities

| Capability | Model | Endpoint | What it does |
|---|---|---|---|
| **Text-to-Image** | `agnes-image-2.0-flash` | `POST /v1/images/generations` | Generate images from text |
| **Image-to-Image** | `agnes-image-2.0-flash` | `POST /v1/images/generations` | Modify existing image (provide `image_url`) |
| **Image Recognition** | `agnes-2.0-flash` | `POST /v1/chat/completions` | Analyze, describe, OCR images (send `image_url` in messages) |
| **Text-to-Video** | `agnes-video-v2.0` | `POST /v1/videos` | Generate video from text prompt |
| **Image-to-Video** | `agnes-video-v2.0` | `POST /v1/videos` | Animate a single image |
| **Multi-Image Video** | `agnes-video-v2.0` | `POST /v1/videos` | Create video from multiple reference images |
| **Keyframe Animation** | `agnes-video-v2.0` | `POST /v1/videos` | Smooth transitions between keyframes |

---

## 1. 文生图 / 图生图 (Image Generation)

**Endpoint:** `POST https://apihub.agnes-ai.com/v1/images/generations`

### Workflow

**Clarify the request:** Ask about subject, style, mood, composition, and aspect ratio.

**Recommended sizes:**
- `1024x1024` — square, default
- `768x768` — smaller, faster
- `1024x1536` — portrait
- `1536x1024` — landscape

**Text-to-Image:**
```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "a serene lake at sunset with mountains",
    "size": "1024x1024",
    "style": "realistic",
    "n": 1
  }'
```

**Image-to-Image:** Add `image_url` to reference an input image:
```json
{
  "model": "agnes-image-2.0-flash",
  "prompt": "add cherry blossom petals falling",
  "image_url": "https://example.com/reference.png",
  "size": "1024x1024"
}
```

**Available parameters:** `model`, `prompt`, `image_url`, `n` (1-4), `size`, `style` (realistic/anime/cartoon), `negative_prompt`, `seed`

**Response:** Returns `data[].url` with the image URL (PNG). URLs are temporary — download locally.

Use `scripts/gen_image.py` for convenience.

---

## 2. 图像识别 (Image Recognition)

**Endpoint:** `POST https://apihub.agnes-ai.com/v1/chat/completions`

Agnes 2.0 Flash supports image input — send an image URL alongside text instructions in `messages[].content` array. The model can describe, analyze, extract text (OCR), or answer questions about images.

**Send image with instructions:**
```bash
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-2.0-flash",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Describe the content of this image."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/image.jpg"
            }
          }
        ]
      }
    ]
  }'
```

**Requirements:**
- Image URL must be publicly accessible (no login/auth)
- Supports JPG, PNG, WebP
- Use together with streaming, tool calls, and agent workflows

**Model specs:** 256K context, 65.5K max output, supports thinking mode for complex reasoning.

**For coding/debugging tasks:** Add `"chat_template_kwargs": {"enable_thinking": true}` to enable thinking mode.

---

## 3. 视频生成 (Video Generation)

**Endpoint:** `POST https://apihub.agnes-ai.com/v1/videos`

Video generation is **asynchronous** — create a task, then poll for results using `video_id`.

### Step 1: Create Video Task

**Text-to-Video:**
```bash
curl -X POST https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion",
    "height": 768,
    "width": 1152,
    "num_frames": 121,
    "frame_rate": 24
  }'
```

**Image-to-Video** (animate a single image):
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "The woman slowly turns around and looks back at the camera",
  "image": "https://example.com/image.png",
  "num_frames": 121,
  "frame_rate": 24
}
```

**Multi-Image Video** (transformation between multiple images):
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "Create a smooth transformation scene between the two reference images",
  "extra_body": {
    "image": ["https://example.com/image1.png", "https://example.com/image2.png"]
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

**Keyframe Animation:**
```json
{
  "model": "agnes-video-v2.0",
  "prompt": "Generate a smooth cinematic transition between the keyframes",
  "extra_body": {
    "image": ["https://example.com/kf1.png", "https://example.com/kf2.png"],
    "mode": "keyframes"
  },
  "num_frames": 121,
  "frame_rate": 24
}
```

**Create task response** returns both `task_id` and `video_id`. Use `video_id` for polling.

### Step 2: Poll for Result

```bash
curl --location --request GET 'https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>' \
  --header 'Authorization: Bearer $AGNES_API_KEY'
```

**Response when completed:**
```json
{
  "id": "task_xxx",
  "video_id": "video_xxx",
  "model": "agnes-video-v2.0",
  "status": "completed",
  "progress": 100,
  "seconds": "10.0",
  "size": "1280x768",
  "remixed_from_video_id": "https://storage.googleapis.com/.../video.mp4"
}
```

**Status values:** `queued` → `in_progress` → `completed` (or `failed`)

### Video Parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `model` | string | - | Use `agnes-video-v2.0` |
| `prompt` | string | - | Video description |
| `image` | string/array | - | URL(s) for img2video/multi-image |
| `height` | integer | 768 | Video height |
| `width` | integer | 1152 | Video width |
| `num_frames` | integer | - | Must be ≤441 and follow 8n+1 rule (81, 121, 161, 241, 441) |
| `frame_rate` | number | 24 | FPS range: 1-60 |
| `num_inference_steps` | integer | - | Inference steps |
| `seed` | integer | - | For reproducible results |
| `negative_prompt` | string | - | Content to avoid |
| `extra_body.image` | array | - | Multiple images or keyframes |
| `extra_body.mode` | string | - | Set to `"keyframes"` for keyframe mode |

### Duration Control

```
seconds = num_frames / frame_rate
```

**Recommended configs:**
| Duration | num_frames | frame_rate |
|---|---|---|
| ~3 seconds | 81 | 24 |
| ~5 seconds | 121 | 24 |
| ~10 seconds | 241 | 24 |
| ~18 seconds | 441 | 24 |

### Prompt Structure

**Text-to-Video:**
```
[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]
```

**Image-to-Video:** Describe what should move vs what should stay stable.

**Multi-Image:** Describe the relationship between images and how the scene should transition.

---

## Helper Scripts

- `scripts/gen_image.py` — Image generation helper
- `scripts/gen_video.py` — Video generation helper (async task + polling)

Run with: `python3 scripts/gen_*.py --help`

## Tips

### Images
- Be specific: describe subject, setting, lighting, mood, composition
- Use `negative_prompt`: `"blurry, low quality, distorted, watermark, text"`
- Download images locally — URLs are temporary

### Video
- Use `num_frames` in steps of 8n+1: 81, 121, 161, 241, 441
- Higher `frame_rate` = smoother but shorter video (same num_frames)
- Use fixed `seed` for reproducible results
- For longer videos: increase `num_frames` or reduce `frame_rate`

### Image Recognition
- Image URL must be publicly accessible
- For screenshots/UI: add text instructions about what to focus on
- Combine with tool calls, streaming, and agent workflows
