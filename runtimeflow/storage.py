"""Flow 持久化"""

import json
import os
from datetime import datetime

from runtimeflow.models import Flow


def save_skill(flow: Flow, directory: str = "skills") -> str:
    """保存 flow 为 JSON 文件，返回文件路径"""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{flow.name}_{timestamp}.json"
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(flow.to_dict(), f, ensure_ascii=False, indent=2)
    return filepath


def load_skill(name: str, directory: str = "skills") -> Flow:
    """按名称加载最新的 skill"""
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")

    candidates = [
        fname for fname in os.listdir(directory)
        if fname.startswith(name + "_") and fname.endswith(".json")
    ]
    if not candidates:
        raise FileNotFoundError(f"未找到名为 '{name}' 的 skill")

    candidates.sort()
    filepath = os.path.join(directory, candidates[-1])
    with open(filepath, "r", encoding="utf-8") as f:
        return Flow.from_dict(json.load(f))


def list_skills(directory: str = "skills") -> list[dict]:
    """列出所有 skill 的摘要信息"""
    if not os.path.isdir(directory):
        return []

    skills = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".json"):
            continue
        filepath = os.path.join(directory, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            skills.append({
                "name": data.get("name", ""),
                "file": fname,
                "created_at": data.get("created_at", ""),
                "event_count": data.get("event_count", 0),
                "duration_ms": data.get("duration_ms", 0),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return skills
