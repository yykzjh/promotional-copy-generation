"""
Model deployment - vLLM and diffusers based serving.

Models:
  - main: Qwen3-30B-A3B (text-to-text, Agent 主模型)
  - vl: Qwen3-VL-8B (image+text-to-text)
  - image_gen: Qwen-Image-2512 (text-to-image, diffusion)

Config loading: model_deployment.config
"""

from . import config

__all__ = ["config"]
