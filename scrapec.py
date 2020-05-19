#!/usr/bin/env python3

import argparse
import zipfile
import json
import sys
import os

parser = argparse.ArgumentParser(description='Compile .sb3 files for Scrape to consume.')
parser.add_argument('file_name', help='Name of the .sb3 file.')
parser.add_argument('--sprite', help='Name of the sprite containing code to be executed.', default="Sprite1")
parser.add_argument('--json', help='Use this flag when the input file is a project.json file, not a .sb3 file.', action="store_true")

args = parser.parse_args()

if args.json:
    with open(args.file_name, 'r') as sb3json:
        projectjson = sb3json.read()
else:
    with zipfile.ZipFile(args.file_name, 'r') as sb3zip:
        projectjson = sb3zip.read("project.json").decode("utf-8")

project = json.loads(projectjson)

if args.sprite not in [target["name"] for target in project["targets"]]:
    print("Please put all code in Sprite1, or specify the sprite name using the --sprite flag.")
    sys.exit(1)

for target in project["targets"]:
    if target["isStage"]:
        stage = target
    elif target["name"] == args.sprite:
        sprite = target

output = dict()

output["container"] = dict()

output["container"]["variables"] = dict()
output["container"]["lists"] = dict()
for variable in stage["variables"]:
    output["container"]["variables"][variable] = stage["variables"][variable][1]
for array in stage["lists"]:
    output["container"]["lists"][array] = stage["lists"][array][1]

output_file_name = os.path.splitext(os.path.basename(args.file_name))[0] + ".scrape"
with open(output_file_name, "w") as scrapefile:
    json.dump(output, scrapefile)
