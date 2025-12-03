import json, os
from typing import Any

def ensure_dir_for_file(path: str):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

def readFile(path: str) -> Any:
    try:
        if not os.path.exists(path):
            return []
        with open(path,"r",encoding="utf-8") as f:
            content=f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except:
        return []

def saveFile(path: str, data: Any) -> bool:
    try:
        ensure_dir_for_file(path)
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
        return True
    except:
        return False
