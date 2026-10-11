"""
Model Loader with RAM Safety Guardrails
Designed for 8GB RAM devices. Enforces strict memory caps and lazy loading.
"""
import gc
import logging
from typing import Dict, Optional, Tuple
import psutil

from ..config import DEFAULT_MODEL_ID, MAX_RAM_ALLOWANCE_MB

logger = logging.getLogger("walkbacker.model_loader")


def get_system_memory_status() -> Dict:
    """
    Returns live physical RAM metrics and process memory consumption in MB.
    """
    vm = psutil.virtual_memory()
    proc = psutil.Process()
    proc_info = proc.memory_info()

    return {
        "total_system_ram_mb": round(vm.total / (1024 * 1024), 1),
        "available_system_ram_mb": round(vm.available / (1024 * 1024), 1),
        "percent_system_ram_used": vm.percent,
        "process_ram_mb": round(proc_info.rss / (1024 * 1024), 1),
        "max_allowance_mb": MAX_RAM_ALLOWANCE_MB,
        "memory_safe": vm.percent < 88.0
    }


class LocalModelEngine:
    """
    Manages lightweight open-weight models with automatic memory safety.
    """
    def __init__(self, model_id: str = DEFAULT_MODEL_ID):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        self.load_error = None

    def load_model(self) -> Tuple[bool, str]:
        """
        Loads the open-weight model into CPU memory only if memory permits.
        """
        mem = get_system_memory_status()
        if not mem["memory_safe"]:
            msg = f"System RAM usage is high ({mem['percent_system_ram_used']}%). Avoiding neural weights to safeguard 8GB RAM limits."
            logger.warning(msg)
            self.load_error = msg
            return False, msg

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            logger.info(f"Loading open-weight model '{self.model_id}' onto CPU...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                local_files_only=False
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                device_map="cpu"
            )
            self.is_loaded = True
            logger.info("Open-weight model loaded successfully.")
            return True, "Model loaded successfully into CPU memory."
        except Exception as e:
            self.load_error = str(e)
            logger.error(f"Failed to load model '{self.model_id}': {e}")
            return False, f"Model load error: {e}"

    def unload_model(self):
        """
        Explicitly free neural model weights from memory.
        """
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        gc.collect()
        logger.info("Model unloaded. Memory freed.")

    def generate(self, prompt: str, max_new_tokens: int = 150) -> Optional[str]:
        """
        Run local CPU inference with torch.no_grad().
        """
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            return None

        try:
            import torch
            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return decoded
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None


# Global Model Engine instance
local_engine = LocalModelEngine()
