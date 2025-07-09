# Build Config
import os
import json
import time

basedir = os.path.dirname(__file__)
json_path = os.path.join(basedir, "config.json")
output_path = os.path.join(basedir, "config.py")

with open(json_path, "r", encoding="utf-8") as f:
    config = json.load(f)

config["date"] = time.strftime("%d_%m_%Y")
config["hour"] = time.strftime("_%H_%M_%S")

with open(output_path , "w", encoding="utf-8") as f:
    for key, value in config.items():
        f.write(f'{key} = {repr(value)}\n')

print("Config builded.")
