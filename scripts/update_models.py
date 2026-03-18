import json
import math
import os
import re
import sys
import time
from pathlib import Path

import requests

MODELS_FILE = Path("src/lib/data/models.json")
HF_API = "https://huggingface.co/api/models"

TARGET_QUANTS = ["Q4_K_M", "Q8_0", "Q6_K", "fp16"]
MIN_DOWNLOADS = 10_000


def auth():
    token = os.environ.get("HF_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def hf_get(url, **kwargs):
    r = requests.get(url, headers=auth(), timeout=30, **kwargs)
    r.raise_for_status()
    return r


def fetch_top_models(limit=100):
    return hf_get(
        HF_API,
        params={"filter": "gguf", "sort": "downloads", "direction": "-1", "limit": limit, "full": "true"},
    ).json()


def fetch_config(repo_id):
    url = f"https://huggingface.co/{repo_id}/resolve/main/config.json"
    try:
        r = requests.get(url, headers=auth(), timeout=30)
        return r.json() if r.ok else None
    except Exception:
        return None


def fetch_file_sizes(repo_id):
    try:
        data = hf_get(f"{HF_API}/{repo_id}", params={"blobs": "true"}).json()
    except Exception:
        return {}
    return {
        f["rfilename"]: f["size"] / 1024**3
        for f in data.get("siblings", [])
        if f.get("rfilename", "").endswith(".gguf") and f.get("size")
    }


def kv_cost(config):
    layers = config.get("num_hidden_layers")
    kv_heads = config.get("num_key_value_heads")
    head_dim = config.get("head_dim")
    if head_dim is None:
        h = config.get("hidden_size")
        n = config.get("num_attention_heads")
        if h and n:
            head_dim = h // n
    if not all([layers, kv_heads, head_dim]):
        return None
    # 2 (K+V) * layers * kv_heads * head_dim * fp16 (2 bytes) * 1000 tokens -> GB
    return round(2 * layers * kv_heads * head_dim * 2 * 1000 / 1024**3, 4)


def find_weight_gb(sizes, quant):
    q = quant.lower().replace("_", "-")
    for fname, gb in sizes.items():
        if q in fname.lower() or quant.lower() in fname.lower():
            return round(gb, 2)
    return None


def make_id(base, quant):
    b = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return f"{b}-{quant.lower().replace('_', '-')}"


def main():
    print("Pulling top GGUF models from HuggingFace...")
    raw = fetch_top_models()

    db = json.loads(MODELS_FILE.read_text(encoding="utf-8"))
    known = {m["id"] for m in db}
    added = 0

    for model in raw:
        repo_id = model.get("id", "")
        if model.get("downloads", 0) < MIN_DOWNLOADS:
            continue

        print(f"  {repo_id}")
        config = fetch_config(repo_id)
        time.sleep(0.5)
        if not config:
            continue

        kv = kv_cost(config)
        if not kv:
            continue

        max_ctx_k = round(config.get("max_position_embeddings", 4096) / 1000)
        base_name = repo_id.split("/")[-1].lower()

        # Try bartowski's quantized mirrors first, they have complete file lists
        sizes = fetch_file_sizes(f"bartowski/{base_name}-GGUF") or fetch_file_sizes(repo_id)
        time.sleep(0.5)

        for quant in TARGET_QUANTS:
            entry_id = make_id(base_name, quant)
            if entry_id in known:
                continue
            weight_gb = find_weight_gb(sizes, quant)
            if not weight_gb:
                continue

            name = (
                model.get("cardData", {}).get("model_name")
                or base_name.replace("-", " ").title()
            )
            db.append({
                "id": entry_id,
                "name": name,
                "quantization": quant,
                "weight_gb": weight_gb,
                "kv_per_1k_gb": kv,
                "max_context_k": max_ctx_k,
            })
            known.add(entry_id)
            added += 1

    MODELS_FILE.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. Total models: {len(db)}  (+{added} new)")


if __name__ == "__main__":
    main()
