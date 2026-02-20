"""Load model deployment config from config/model_deployment/."""

from pathlib import Path
from typing import Any

import yaml

_config_dir = Path(__file__).resolve().parent.parent / "config" / "model_deployment"

# Cache for loaded configs
_config_cache: dict[str, dict[str, Any]] = {}


def _load_config(name: str) -> dict[str, Any]:
    """Load config for a model (main, vl, image_gen). Cached."""
    if name in _config_cache:
        return _config_cache[name]
    path = _config_dir / f"{name}.yaml"
    if not path.exists():
        _config_cache[name] = {}
        return {}
    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    _config_cache[name] = cfg
    return cfg


def load_config(name: str) -> dict[str, Any]:
    """Load config for a model (main, vl, image_gen)."""
    return _load_config(name).copy()


# --- vLLM ---


def get_vllm_config(name: str) -> dict[str, Any]:
    """Get vLLM config dict from config file."""
    cfg = _load_config(name)
    if cfg.get("backend") != "vllm":
        return {}
    vllm = dict(cfg.get("vllm", {}))
    vllm.setdefault("model_id", cfg.get("model_id", ""))
    return vllm


def get_vllm_args(name: str) -> list[str]:
    """Build vllm serve command args from config (model_id + vllm params). CLI pass-through overrides when provided."""
    vllm = get_vllm_config(name)
    if not vllm:
        return []
    model_id = vllm.get("model_id", "")
    if not model_id:
        return []
    args = [model_id]
    if host := vllm.get("host"):
        args.extend(["--host", str(host)])
    if port := vllm.get("port"):
        args.extend(["--port", str(port)])
    tp = vllm.get("tensor_parallel_size", 1)
    if tp > 1:
        args.extend(["--tensor-parallel-size", str(tp)])
    if gpu := vllm.get("gpu_memory_utilization"):
        args.extend(["--gpu-memory-utilization", str(gpu)])
    if max_len := vllm.get("max_model_len"):
        args.extend(["--max-model-len", str(max_len)])
    return args


# --- diffusers ---


def get_diffusers_config() -> dict[str, Any]:
    """Get full diffusers config from image_gen.yaml."""
    cfg = _load_config("image_gen")
    return dict(cfg.get("diffusers", {}))


def get_diffusers_server_params(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Get diffusers server params (host, port) for uvicorn. CLI overrides take precedence."""
    diff = get_diffusers_config()
    params = {
        "host": diff.get("host", "0.0.0.0"),
        "port": diff.get("port", 8002),
    }
    if overrides:
        for k in ("host", "port"):
            if k in overrides and overrides[k] is not None:
                params[k] = overrides[k]
    return params


def get_diffusers_pipeline_params() -> dict[str, Any]:
    """Get diffusers pipeline load params (model_id, device, torch_dtype)."""
    cfg = _load_config("image_gen")
    model_id = cfg.get("model_id", "Qwen/Qwen-Image-2512")
    diff = cfg.get("diffusers", {})
    dtype_map = {"bfloat16": "bfloat16", "float16": "float16", "float32": "float32"}
    return {
        "model_id": model_id,
        "device": diff.get("device", "cuda"),
        "torch_dtype": diff.get("torch_dtype", "bfloat16"),
    }


def get_diffusers_inference_defaults() -> dict[str, Any]:
    """Get diffusers inference default params (for API requests)."""
    diff = get_diffusers_config()
    return {
        "default_width": diff.get("default_width", 1024),
        "default_height": diff.get("default_height", 1024),
        "num_inference_steps": diff.get("num_inference_steps", 50),
        "true_cfg_scale": diff.get("true_cfg_scale", 4.0),
        "default_negative_prompt": diff.get(
            "default_negative_prompt",
            "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感。",
        ),
    }


# --- agent (promotional_copy_generation 使用) ---


def get_agent_image_config() -> dict[str, Any]:
    """Get agent image gen config (default_size for API request)."""
    cfg = _load_config("image_gen")
    return dict(cfg.get("agent", {}))
