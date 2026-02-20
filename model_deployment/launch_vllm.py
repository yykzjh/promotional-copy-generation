#!/usr/bin/env python3
"""
Launch vLLM server for LLM models.

Usage:
  uv run python -m model_deployment.launch_vllm main
  uv run python -m model_deployment.launch_vllm main --port 8001
  uv run python -m model_deployment.launch_vllm vl --tensor-parallel-size 2

Config file provides model_id and default vllm args. CLI args override config args with same name.
"""

import subprocess
import sys

from model_deployment.config import get_vllm_args


def _parse_kv_args(args: list[str]) -> tuple[list[str], dict[str, str | bool]]:
    """Parse args: (positional_prefix, {key: value}). -key/--key value or -key/--key (flag)."""
    positional: list[str] = []
    kv: dict[str, str | bool] = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("-") and len(a) > 1:  # -key or --key
            raw = a.lstrip("-")
            key = raw.replace("-", "_")  # tensor-parallel-size -> tensor_parallel_size
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                kv[key] = args[i + 1]
                i += 2
            else:
                kv[key] = True  # boolean flag
                i += 1
        else:
            positional.append(a)
            i += 1
    return positional, kv


def _kv_to_args(kv: dict[str, str | bool]) -> list[str]:
    """Convert kv dict to --key value args. Key order: stable sort."""
    result: list[str] = []
    for k in sorted(kv.keys()):
        v = kv[k]
        result.append("--" + k.replace("_", "-"))
        if v is not True:
            result.append(str(v))
    return result


def _merge_vllm_args(config_args: list[str], remainder: list[str]) -> list[str]:
    """Merge: remainder overrides config for same keys."""
    cfg_pos, cfg_kv = _parse_kv_args(config_args)
    _, rem_kv = _parse_kv_args(remainder)
    # remainder values override config
    merged = {**cfg_kv, **rem_kv}
    return cfg_pos + _kv_to_args(merged)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m model_deployment.launch_vllm <main|vl> [vllm args...]")
        sys.exit(1)

    name = sys.argv[1].lower()
    if name not in ("main", "vl"):
        print("Unknown model. Use: main, vl")
        sys.exit(1)

    config_args = get_vllm_args(name)
    if not config_args:
        print(f"No vLLM config for {name}")
        sys.exit(1)

    remainder = sys.argv[2:]
    merged = _merge_vllm_args(config_args, remainder)

    cmd = ["vllm", "serve"] + merged
    print("Running:", " ".join(cmd))
    sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
