# Agnes AI 完整 API 文档

## 概述

Agnes AI 提供四种核心能力：
1. **图像生成** — 文生图、图生图
2. **图像识别** — 图像描述、OCR、截图分析
3. **视频生成** — 文生视频、图生视频、多图视频、关键帧动画
4. **聊天对话** — 多轮对话、工具调用、流式输出

**API Key:** `sk-FvetkuZyrc3103s707K9KIEzeROVj7ftdv7gfzPlPxl010Fb`

---

## 1. 图像生成 (Image Generation)

**Base URL:** `https://apihub.agnes-ai.com/v1/images/generations`
**Method:** `POST`
**Auth:** `Authorization: Bearer <API_KEY>`

### Models

| Model | Type |
|---|---|
| `agnes-image-2.0-flash` | Primary image model |
| `agnes-image-2.1-flash` | Newer version |

### Parameters

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | - | Model ID |
| `prompt` | string | Yes | - | Text description |
| `image_url` | string | No | - | Input image URL for img2img |
| `n` | integer | No | 1 | Number of images (1-4) |
| `size` | string | No | - | `1024x1024`, `768x768`, `1024x1536`, `1536x1024` |
| `style` | string | No | - | `realistic`, `anime`, `cartoon` |
| `negative_prompt` | string | No | - | Exclude unwanted elements |
| `seed` | integer | No | - | Reproducible results |

### Response

```json
{
  "created": 1781592455,
  "data": [
    {
      "url": "https://platform-outputs.agnes-ai.space/images/.../image.png"
    }
  ]
}
```

---

## 2. 图像识别 (Image Recognition)

**Base URL:** `https://apihub.agnes-ai.com/v1/chat/completions`
**Method:** `POST`
**Model:** `agnes-2.0-flash`

### Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | string | Yes | Use `agnes-2.0-flash` |
| `messages` | array | Yes | Conversation messages |
| `messages[].content` | string/array | Yes | Text or array of text+image blocks |
| `temperature` | number | No | Randomness control |
| `max_tokens` | number | No | Max output tokens |
| `stream` | boolean | No | Enable streaming |
| `tools` | array | No | Tool/function definitions |
| `thinking` | object | No | Enable thinking mode |

### Image Input Format

```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "Describe this image."
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/image.jpg"
      }
    }
  ]
}
```

### Thinking Mode

For coding/reasoning tasks:
```json
{
  "model": "agnes-2.0-flash",
  "messages": [...],
  "chat_template_kwargs": {
    "enable_thinking": true
  }
}
```

### Model Limits

- Context: 256K
- Max Output: 65.5K
- Pricing: Currently free

---

## 3. 视频生成 (Video Generation)

### 3.1 Create Task

**Endpoint:** `POST https://apihub.agnes-ai.com/v1/videos`
**Model:** `agnes-video-v2.0`

#### Parameters

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `model` | string | Yes | - | Use `agnes-video-v2.0` |
| `prompt` | string | Yes | - | Video description |
| `image` | string/array | No | - | Image URL(s) for img2video |
| `height` | integer | No | 768 | Video height |
| `width` | integer | No | 1152 | Video width |
| `num_frames` | integer | No | - | Must be ≤441, rule 8n+1 |
| `frame_rate` | number | No | - | FPS, range 1-60 |
| `negative_prompt` | string | No | - | Avoid unwanted content |
| `seed` | integer | No | - | Reproducible results |
| `extra_body.image` | array | No | - | Multiple images |
| `extra_body.mode` | string | No | - | Set to `"keyframes"` |

#### Video Modes

| Mode | How | Description |
|---|---|---|
| Text-to-Video | `prompt` only | Generate from text |
| Image-to-Video | `prompt` + `image` | Animate single image |
| Multi-Image | `prompt` + `extra_body.image` (array) | Transition between images |
| Keyframe | `prompt` + `extra_body.mode: "keyframes"` | Smooth keyframe transitions |

#### Duration Control

```
seconds = num_frames / frame_rate
```

| Duration | num_frames | frame_rate |
|---|---|---|
| ~3s | 81 | 24 |
| ~5s | 121 | 24 |
| ~10s | 241 | 24 |
| ~18s | 441 | 24 |

#### Create Response

```json
{
  "id": "task_xxx",
  "task_id": "task_xxx",
  "video_id": "video_xxx",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "queued",
  "progress": 0,
  "created_at": 1780457477,
  "seconds": "10.0",
  "size": "1280x768"
}
```

### 3.2 Query Result

**Endpoint:** `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`
**Auth:** Bearer Token

**Completed Response:**
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

### Task States

| State | Description |
|---|---|
| `queued` | Waiting in queue |
| `in_progress` | Generating |
| `completed` | Done — video URL available |
| `failed` | Error |

### Error Codes

| Code | Meaning |
|---|---|
| 400 | Invalid request |
| 401 | Unauthorized (bad API key) |
| 404 | Task/video not found |
| 500 | Server error |
| 503 | Service busy |

---

## 4. 聊天对话 (Chat Completion)

**Endpoint:** `POST https://apihub.agnes-ai.com/v1/chat/completions`
**Model:** `agnes-2.0-flash`

Same as Section 2 but without image input — pure text chat.

### Streaming

Add `"stream": true` to enable SSE streaming.

### Tool Calls

Define `tools` array for function calling and agent workflows.

### JSON Output

Set response format to JSON for structured outputs.
