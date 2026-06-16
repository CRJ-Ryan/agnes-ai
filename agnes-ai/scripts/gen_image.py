#!/usr/bin/env python3
"""Generate images via Agnes AI Image API."""
import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://apihub.agnes-ai.com/v1/images/generations"


def generate_image(api_key: str, prompt: str, **kwargs) -> dict:
    """Call the Agnes image generation API."""
    payload = {
        "model": kwargs.get("model", "agnes-image-2.0-flash"),
        "prompt": prompt,
    }
    if kwargs.get("image_url"):
        payload["image_url"] = kwargs["image_url"]
    if kwargs.get("n"):
        payload["n"] = kwargs["n"]
    if kwargs.get("size"):
        payload["size"] = kwargs["size"]
    if kwargs.get("style"):
        payload["style"] = kwargs["style"]
    if kwargs.get("negative_prompt"):
        payload["negative_prompt"] = kwargs["negative_prompt"]
    if kwargs.get("seed") is not None:
        payload["seed"] = kwargs["seed"]

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


def main():
    parser = argparse.ArgumentParser(description="Agnes AI Image Generator")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--key", "-k", default=None, help="API key (default: from env)")
    parser.add_argument("--model", default="agnes-image-2.0-flash")
    parser.add_argument("--n", type=int, default=1, help="Number of images (1-4)")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--style", choices=["realistic", "anime", "cartoon"])
    parser.add_argument("--negative-prompt", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--image-url", default=None, help="Input image URL for img2img")
    parser.add_argument("--output", "-o", default=None, help="Save JSON response to file")

    args = parser.parse_args()

    api_key = args.key or os.environ.get("AGNES_API_KEY", "")
    if not api_key:
        print("Error: API key required. Use --key or AGNES_API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    result = generate_image(
        api_key,
        args.prompt,
        model=args.model,
        n=args.n,
        size=args.size,
        style=args.style,
        negative_prompt=args.negative_prompt,
        seed=args.seed,
        image_url=args.image_url,
    )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Response saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))

    # Print image URLs
    for i, img in enumerate(result.get("data", [])):
        url = img.get("url")
        if url:
            print(f"\nImage {i+1}: {url}")


if __name__ == "__main__":
    import os
    main()
