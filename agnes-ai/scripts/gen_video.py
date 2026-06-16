#!/usr/bin/env python3
"""Generate videos via Agnes AI Video API (async task + polling)."""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "https://apihub.agnes-ai.com/v1/videos"
QUERY_URL = "https://apihub.agnes-ai.com/agnesapi"


def create_video_task(api_key: str, prompt: str, **kwargs) -> dict:
    """Create a video generation task."""
    payload = {
        "model": kwargs.get("model", "agnes-video-v2.0"),
        "prompt": prompt,
    }
    if kwargs.get("image"):
        payload["image"] = kwargs["image"]
    if kwargs.get("height"):
        payload["height"] = kwargs["height"]
    if kwargs.get("width"):
        payload["width"] = kwargs["width"]
    if kwargs.get("num_frames"):
        payload["num_frames"] = kwargs["num_frames"]
    if kwargs.get("frame_rate"):
        payload["frame_rate"] = kwargs["frame_rate"]
    if kwargs.get("negative_prompt"):
        payload["negative_prompt"] = kwargs["negative_prompt"]
    if kwargs.get("seed") is not None:
        payload["seed"] = kwargs["seed"]
    if kwargs.get("num_inference_steps"):
        payload["num_inference_steps"] = kwargs["num_inference_steps"]
    if kwargs.get("extra_body"):
        payload["extra_body"] = kwargs["extra_body"]

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def poll_result(api_key: str, video_id: str, poll_interval: int = 5, timeout: int = 600) -> dict:
    """Poll for video result until completed or failed."""
    start = time.time()
    while True:
        url = f"{QUERY_URL}?video_id={video_id}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())

                status = result.get("status", "")
                progress = result.get("progress", 0)
                print(f"  Status: {status}, Progress: {progress}%")

                if status == "completed":
                    return result
                elif status == "failed":
                    print(f"Failed: {result.get('error', 'unknown error')}", file=sys.stderr)
                    return result
                elif status in ("queued", "in_progress"):
                    if time.time() - start > timeout:
                        print(f"Timeout after {timeout}s", file=sys.stderr)
                        return result
                    time.sleep(poll_interval)
                else:
                    return result
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"HTTP {e.code}: {body}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Agnes AI Video Generator")
    parser.add_argument("--prompt", "-p", required=True, help="Video prompt")
    parser.add_argument("--key", "-k", default=None, help="API key")
    parser.add_argument("--model", default="agnes-video-v2.0")
    parser.add_argument("--image", "-i", default=None, help="Image URL for img2video")
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--width", type=int, default=1152)
    parser.add_argument("--num-frames", type=int, default=121,
                        help="8n+1 rule, max 441 (e.g., 81, 121, 161, 241, 441)")
    parser.add_argument("--frame-rate", type=int, default=24)
    parser.add_argument("--negative-prompt", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--mode", choices=["ti2vid", "keyframes"], default=None,
                        help="Generation mode")
    parser.add_argument("--multi-image", nargs="+", default=None,
                        help="Multiple image URLs for multi-image video")
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--output", "-o", default=None)

    args = parser.parse_args()

    api_key = args.key or os.environ.get("AGNES_API_KEY", "")
    if not api_key:
        print("Error: API key required. Use --key or AGNES_API_KEY.", file=sys.stderr)
        sys.exit(1)

    # Build extra_body for special modes
    extra_body = {}
    if args.mode:
        extra_body["mode"] = args.mode
    if args.multi_image:
        extra_body["image"] = args.multi_image

    # Create task
    print("Creating video task...")
    task_result = create_video_task(
        api_key,
        args.prompt,
        model=args.model,
        image=args.image,
        height=args.height,
        width=args.width,
        num_frames=args.num_frames,
        frame_rate=args.frame_rate,
        negative_prompt=args.negative_prompt,
        seed=args.seed,
        extra_body=extra_body if extra_body else None,
    )

    video_id = task_result.get("video_id")
    task_id = task_result.get("task_id")
    print(f"Task created: task_id={task_id}, video_id={video_id}")
    print(f"Status: {task_result.get('status')}")
    print("Polling for result...")

    # Poll
    result = poll_result(api_key, video_id, poll_interval=args.poll_interval)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))

    # Print video URL
    video_url = result.get("remixed_from_video_id") or result.get("video_url")
    if video_url:
        print(f"\nVideo URL: {video_url}")
    else:
        print("\nVideo not yet available (status may not be completed)")


if __name__ == "__main__":
    main()
