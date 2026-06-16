# agnes-ai

Agnes AI 全能创作 Skill — 文生图、图生图、图像识别、文生视频、图生视频

## 能力概览

| 能力 | 模型 | 说明 |
|---|---|---|
| 文生图 | `agnes-image-2.0-flash` | 从文字描述生成图片 |
| 图生图 | `agnes-image-2.0-flash` | 基于参考图修改/重绘 |
| 图像识别 | `agnes-2.0-flash` | 图像描述、OCR、截图分析 |
| 文生视频 | `agnes-video-v2.0` | 从文字描述生成视频 |
| 图生视频 | `agnes-video-v2.0` | 动画化单图或多图 |

## 文件结构

```
agnes-ai/
├── SKILL.md              # Skill 主文件（触发 + 使用说明）
├── references/
│   └── api-reference.md  # 完整 API 文档
├── scripts/
│   ├── gen_image.py      # 图像生成辅助脚本
│   └── gen_video.py      # 视频生成辅助脚本
├── evals/
│   └── evals.json        # 测试用例
└── workspace/            # 测试输出
```

## 快速开始

### 环境变量

```bash
export AGNES_API_KEY="sk-FvetkuZyrc3103s707K9KIEzeROVj7ftdv7gfzPlPxl010Fb"
```

### 文生图

```bash
python3 scripts/gen_image.py --prompt "a cyberpunk city at night" --style anime --size 1024x1024
```

### 图像识别

发送图片 URL 给 `agnes-2.0-flash` 模型进行描述、OCR 或分析。

### 文生视频

```bash
python3 scripts/gen_video.py --prompt "A cinematic shot of a cat walking on the beach at sunset"
```

## API 端点

- **图像生成:** `POST https://apihub.agnes-ai.com/v1/images/generations`
- **图像识别/聊天:** `POST https://apihub.agnes-ai.com/v1/chat/completions`
- **视频生成:** `POST https://apihub.agnes-ai.com/v1/videos`（异步）

详见 [references/api-reference.md](references/api-reference.md)。

## License

MIT
