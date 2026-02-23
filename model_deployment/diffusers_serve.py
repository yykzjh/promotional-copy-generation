#!/usr/bin/env python3
"""
Diffusers-based image generation server for Qwen-Image-2512.

Exposes OpenAI-compatible /v1/images/generations endpoint.

Usage:
  uv run python -m model_deployment.diffusers_serve
  uv run python -m model_deployment.diffusers_serve --port 8003

CLI args override config file defaults.
"""

import base64
import io
import logging
from typing import Any

from fastapi import FastAPI, HTTPException

from model_deployment.config import (
    get_diffusers_inference_defaults,
    get_diffusers_pipeline_params,
    get_diffusers_server_params,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qwen-Image-2512 Diffusers Server")

_pipe = None


def _load_pipeline():
    global _pipe
    if _pipe is not None:
        return _pipe

    params = get_diffusers_pipeline_params()
    model_id = params.get("model_id", "Qwen/Qwen-Image-2512")
    device = params.get("device", "cuda")
    dtype_str = params.get("torch_dtype", "bfloat16")
    device_map = params.get("device_map")

    import torch
    from diffusers import DiffusionPipeline

    dtype_map = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
    torch_dtype = dtype_map.get(dtype_str, torch.bfloat16)

    load_kwargs: dict[str, Any] = {"torch_dtype": torch_dtype}
    if device_map:
        load_kwargs["device_map"] = device_map
        logger.info("Loading pipeline %s with device_map=%s", model_id, device_map)
    else:
        logger.info("Loading pipeline %s on %s", model_id, device)

    _pipe = DiffusionPipeline.from_pretrained(model_id, **load_kwargs)
    if not device_map:
        _pipe = _pipe.to(device)
    return _pipe


@app.post("/v1/images/generations")
async def images_generations(req: dict[str, Any]):
    """OpenAI-compatible images/generations endpoint."""
    prompt = req.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt required")

    defaults = get_diffusers_inference_defaults()
    n = int(req.get("n", 1))
    size = req.get("size") or f"{defaults['default_width']}x{defaults['default_height']}"
    negative_prompt = req.get("negative_prompt") or defaults["default_negative_prompt"]
    num_inference_steps = int(req.get("num_inference_steps") or defaults["num_inference_steps"])
    true_cfg_scale = float(req.get("true_cfg_scale") or defaults["true_cfg_scale"])

    try:
        w = defaults["default_width"]
        h = defaults["default_height"]
        if size and "x" in str(size):
            parts = str(size).split("x")
            if len(parts) == 2:
                w, h = int(parts[0]), int(parts[1])

        pipe = _load_pipeline()
        import torch

        gen_device = getattr(pipe, "device", None) or "cuda"
        generator = torch.Generator(device=gen_device).manual_seed(42)

        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=w,
            height=h,
            num_inference_steps=num_inference_steps,
            true_cfg_scale=true_cfg_scale,
            num_images_per_prompt=n,
            generator=generator,
        )

        images = result.images
        data = []
        for img in images[:n]:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            data.append({"b64_json": base64.b64encode(buf.getvalue()).decode()})
        return {"data": data}
    except Exception as e:
        logger.exception("Image generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


def main():
    import os

    # 必须在 import torch 之前设置，才能限定可见 GPU
    params = get_diffusers_pipeline_params()
    if gpu_ids := params.get("gpu_ids"):
        gpu_str = ",".join(str(x) for x in gpu_ids)
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_str
        logger.info("Using GPUs: %s", gpu_str)

    import argparse

    parser = argparse.ArgumentParser(description="Diffusers image generation server")
    parser.add_argument("--host", help="Override host")
    parser.add_argument("--port", type=int, help="Override port")
    args = parser.parse_args()

    overrides = {}
    if args.host is not None:
        overrides["host"] = args.host
    if args.port is not None:
        overrides["port"] = args.port

    params = get_diffusers_server_params(overrides)
    import uvicorn

    # 启动时预加载权重，避免首次请求等待
    logger.info("Preloading pipeline at startup...")
    _load_pipeline()
    logger.info("Pipeline ready, starting server")

    uvicorn.run(app, host=params["host"], port=params["port"])


if __name__ == "__main__":
    main()
