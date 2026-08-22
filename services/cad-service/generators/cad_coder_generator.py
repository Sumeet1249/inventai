"""
CAD-Coder Generator
───────────────────
Wraps the gudo7208/CAD-Coder HuggingFace model (Qwen2.5-7B fine-tuned with
GRPO geometric reward) to convert natural-language descriptions into executable
CadQuery Python code, then executes that code safely to produce a cq.Workplane.

Hardware notes (RTX 3050 6 GB):
  - Full BF16 model  ≈ 14 GB VRAM  → does NOT fit
  - 4-bit NF4 (bitsandbytes) ≈ 4.5 GB VRAM → fits with headroom
  - CPU fallback is available but slow (~3-5 min per generation)

Model is downloaded once into HF_HOME (/models/hf_cache inside the container)
and reused across restarts via a Docker volume.
"""

from __future__ import annotations

import ast
import logging
import os
import re
import textwrap
import threading
from typing import Optional

import cadquery as cq

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

MODEL_ID       = "gudo7208/CAD-Coder"
HF_CACHE_DIR   = os.environ.get("HF_HOME", "/models/hf_cache")
# Also check the host-mounted cache from download_cad_model.py
HF_HOST_CACHE  = "/models/hf_host_cache"
MAX_NEW_TOKENS = 2048
TEMPERATURE    = 0.1   # low = more deterministic CadQuery code

# Sandbox: only these top-level names are allowed in generated code
_ALLOWED_IMPORTS = {"cadquery", "cq", "math", "numpy", "np"}

# Fallback geometry — NO import statements (cq is injected into namespace)
_FALLBACK_SHAPE_CODE = textwrap.dedent("""
    result = (
        cq.Workplane("XY")
        .box(80, 80, 10)
        .faces(">Z")
        .workplane()
        .rect(60, 60, forConstruction=True)
        .vertices()
        .cboreHole(5, 8, 4)
    )
""")


# ── Singleton model loader ────────────────────────────────────────────────────

class _ModelSingleton:
    """Thread-safe lazy loader — the model is loaded once on first use."""

    _instance: Optional["_ModelSingleton"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._model     = None
        self._tokenizer = None
        self._loaded    = False
        self._load_lock = threading.Lock()

    @classmethod
    def get(cls) -> "_ModelSingleton":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load(self):
        """Download (if needed) and load the model with 4-bit quantization."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        logger.info("Loading CAD-Coder model from HuggingFace (%s) …", MODEL_ID)

        # Prefer host-mounted pre-downloaded cache, fall back to Docker volume cache
        cache_dir = HF_CACHE_DIR
        if os.path.isdir(HF_HOST_CACHE) and any(
            "CAD-Coder" in d for d in os.listdir(HF_HOST_CACHE)
            if os.path.isdir(os.path.join(HF_HOST_CACHE, d))
        ):
            cache_dir = HF_HOST_CACHE
            logger.info("Using host-mounted model cache: %s", cache_dir)
        else:
            logger.info("Using Docker volume cache: %s", cache_dir)

        os.makedirs(cache_dir, exist_ok=True)

        # 4-bit NF4 quantization — fits in 6 GB VRAM
        use_gpu = torch.cuda.is_available()
        if use_gpu:
            logger.info("GPU detected: %s (%d MB VRAM)",
                        torch.cuda.get_device_name(0),
                        torch.cuda.get_device_properties(0).total_memory // 1_048_576)
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            device_map = "auto"
        else:
            logger.warning("No GPU detected — loading model in 8-bit on CPU (slow).")
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)
            device_map = "cpu"

        self._tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            cache_dir=cache_dir,
            trust_remote_code=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            cache_dir=cache_dir,
            quantization_config=bnb_config,
            device_map=device_map,
            trust_remote_code=True,
        )
        self._model.eval()
        self._loaded = True
        logger.info("CAD-Coder model loaded successfully.")

    def ensure_loaded(self):
        if not self._loaded:
            with self._load_lock:
                if not self._loaded:
                    self._load()

    @property
    def model(self):
        self.ensure_loaded()
        return self._model

    @property
    def tokenizer(self):
        self.ensure_loaded()
        return self._tokenizer


# ── Code generation ───────────────────────────────────────────────────────────

def _build_prompt(description: str, params: dict) -> str:
    """
    Build the instruction prompt for CAD-Coder.
    The model was trained on chat-template format (Qwen2.5-Instruct style).
    """
    param_lines = "\n".join(
        f"  - {k}: {v}" for k, v in params.items() if v is not None
    )
    instruction = textwrap.dedent(f"""
        You are an expert CAD engineer. Generate executable CadQuery Python code
        for the following mechanical component.

        Description: {description}

        Design parameters:
        {param_lines}

        Requirements:
        - Use CadQuery (import cadquery as cq) only.
        - The final result MUST be assigned to a variable named `result`.
        - result must be a cq.Workplane object.
        - Do NOT include any print statements, file I/O, or plt.show() calls.
        - Do NOT include any import statements other than cadquery and math.
        - Output only the Python code block, no explanations.
    """).strip()
    return instruction


def _extract_code(raw_output: str) -> str:
    """
    Extract the Python code block from the model's raw text output.
    Handles ```python ... ``` fences and bare code.
    """
    # Try fenced code block first
    fence = re.search(r"```(?:python)?\s*(.*?)```", raw_output, re.DOTALL)
    if fence:
        return fence.group(1).strip()

    # Fallback: return everything after the last occurrence of "import cadquery"
    idx = raw_output.rfind("import cadquery")
    if idx != -1:
        return raw_output[idx:].strip()

    return raw_output.strip()


def _generate_cadquery_code(description: str, params: dict) -> str:
    """Call CAD-Coder and return raw CadQuery code string."""
    import torch

    singleton = _ModelSingleton.get()
    tokenizer = singleton.tokenizer
    model     = singleton.model

    prompt = _build_prompt(description, params)

    # Apply the model's chat template (Qwen2.5-Instruct style)
    text = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer([text], return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=TEMPERATURE > 0,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the newly generated tokens
    new_tokens = outputs[0][inputs.input_ids.shape[1]:]
    raw = tokenizer.decode(new_tokens, skip_special_tokens=True)
    logger.debug("CAD-Coder raw output:\n%s", raw)

    code = _extract_code(raw)
    logger.info("Extracted CadQuery code (%d chars).", len(code))
    return code


# ── Safe code execution ───────────────────────────────────────────────────────

def _validate_ast(code: str) -> None:
    """
    Lightweight static check: reject code that imports unexpected modules
    or uses obviously dangerous builtins (open, exec, eval, __import__).
    Raises ValueError if the code looks unsafe.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Generated code has syntax error: {e}") from e

    dangerous = {"open", "exec", "eval", "__import__", "subprocess",
                 "os", "sys", "shutil", "socket", "compile"}

    for node in ast.walk(tree):
        # Check import statements
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ""
            if isinstance(node, ast.Import):
                module = node.names[0].name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split(".")[0]
            if module and module not in _ALLOWED_IMPORTS:
                raise ValueError(f"Disallowed import in generated code: {module!r}")

        # Check function calls for dangerous names
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in dangerous:
                raise ValueError(
                    f"Disallowed function call in generated code: {node.func.id!r}"
                )


def _execute_code(code: str) -> cq.Workplane:
    """
    Execute generated CadQuery code in an isolated namespace.
    The code MUST assign its final result to a variable called `result`.
    Returns the cq.Workplane object.
    """
    import math
    import numpy as np

    namespace: dict = {
        "cq":   cq,
        "math": math,
        "np":   np,
        "__builtins__": {
            # Allow only safe builtins
            "range": range, "len": len, "int": int, "float": float,
            "str": str, "list": list, "dict": dict, "tuple": tuple,
            "enumerate": enumerate, "zip": zip, "min": min, "max": max,
            "abs": abs, "round": round, "print": lambda *a, **k: None,
            "True": True, "False": False, "None": None,
        },
    }

    exec(compile(code, "<cad_coder_generated>", "exec"), namespace)  # noqa: S102

    result = namespace.get("result")
    if result is None:
        raise ValueError(
            "Generated code did not assign to `result`. "
            "Check CAD-Coder output."
        )
    if not isinstance(result, cq.Workplane):
        raise TypeError(
            f"Generated `result` is {type(result).__name__}, expected cq.Workplane."
        )
    return result


# ── Fallback geometry ─────────────────────────────────────────────────────────

def _fallback_geometry(params: dict) -> cq.Workplane:
    """
    Returns a simple parametric shape when CAD-Coder fails.
    Built directly with CadQuery — no exec() involved.
    """
    logger.warning("Using fallback geometry (CAD-Coder unavailable or failed).")
    span = params.get("span_mm", 200)
    motor_count = int(params.get("motor_count", 4))
    wall = max(2, params.get("wall_thickness_mm", params.get("height_mm", 10)))

    try:
        # Build a parametric cross-frame drone base
        arm_len = span * 0.4
        arm_w   = max(15, span * 0.05)
        chassis = cq.Workplane("XY").box(span * 0.2, span * 0.2, wall)

        angle_step = 360.0 / max(motor_count, 1)
        for i in range(motor_count):
            import math
            angle = math.radians(i * angle_step)
            arm = (
                cq.Workplane("XY")
                .transformed(rotate=(0, 0, i * angle_step))
                .center(0, span * 0.2)
                .rect(arm_w, arm_len)
                .extrude(wall * 0.8)
            )
            chassis = chassis.union(arm)
            mount = (
                cq.Workplane("XY")
                .transformed(rotate=(0, 0, i * angle_step))
                .center(0, span * 0.4)
                .circle(arm_w * 0.8)
                .extrude(wall * 1.2)
            )
            chassis = chassis.union(mount)

        return chassis
    except Exception as exc:
        logger.error("Fallback geometry also failed: %s", exc)
        # Absolute last resort — plain box
        return cq.Workplane("XY").box(100, 100, 10)


# ── Public API ────────────────────────────────────────────────────────────────

def generate_with_cad_coder(description: str, params: dict) -> tuple[cq.Workplane, str]:
    """
    Main entry point called by cad_service.py.

    Parameters
    ----------
    description : str
        Natural-language description of the part (e.g. "foldable quadcopter frame").
    params : dict
        Structured parameters from the CAD planner (span_mm, motor_count, etc.).

    Returns
    -------
    workplane : cq.Workplane
        Executable CadQuery geometry ready for STEP/STL/GLTF export.
    generated_code : str
        The raw CadQuery Python code that was generated and executed
        (useful for logging / debug display in the frontend).
    """
    generated_code = ""
    try:
        # 1. Generate code with CAD-Coder
        generated_code = _generate_cadquery_code(description, params)

        # 2. Static safety check
        _validate_ast(generated_code)

        # 3. Execute in sandbox
        workplane = _execute_code(generated_code)

        logger.info("CAD-Coder generation + execution successful.")
        return workplane, generated_code

    except Exception as exc:
        logger.error("CAD-Coder pipeline failed: %s", exc, exc_info=True)
        # Surface the error code so it shows in SSE status
        return _fallback_geometry(params), generated_code or f"# ERROR: {exc}"


def warmup():
    """
    Pre-load the model at service startup so the first real request
    doesn't pay the 30-60 second download/load penalty.
    Call this from FastAPI's @app.on_event("startup").
    """
    try:
        logger.info("CAD-Coder warmup: loading model …")
        _ModelSingleton.get().ensure_loaded()
        logger.info("CAD-Coder warmup complete.")
    except Exception as exc:
        logger.warning("CAD-Coder warmup failed (will retry on first request): %s", exc)
