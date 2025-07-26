import yaml

def load_settings(key_name, yaml_path="app_setting.yml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)
    return settings[key_name]["endpoint"], settings[key_name]["key"]
