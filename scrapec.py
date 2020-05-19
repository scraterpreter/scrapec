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
parser.add_argument('--indent', help='Character used to indent the json outputted.')
parser.add_argument('-o', '--output', help='Name for the file being outputted.')

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

with open("opcodes.json", "r") as opcodesfile:
    opcodejson = json.load(opcodesfile)

opcodes = opcodejson["opcodes"]

ids = set()
ids.update(set(stage["variables"].keys()))
ids.update(set(stage["lists"].keys()))
ids.update(set(sprite["blocks"].keys()))
ids.difference_update({i for i in sprite["blocks"] if sprite["blocks"][i]["opcode"] == "event_whenflagclicked"})
ids = list(ids)
ids.sort()

def parseInput(input_data):
    if input_data[0] == 1:
        return [2, input_data[1][1]]
    else:
        return [1, parseId(input_data[1])]

def parseField(field_data):
    if field_data[1] == None:
        return [2, field_data[0]]
    else:
        return [1, parseId(field_data[1])]

def parseId(id_string):
    if id_string in ids:
        return str(ids.index(id_string))
    else:
        return None

output = dict()

output["container"] = dict()

output["container"]["variables"] = dict()
output["container"]["lists"] = dict()
for variable in stage["variables"]:
    output["container"]["variables"][parseId(variable)] = stage["variables"][variable][1]
for array in stage["lists"]:
    output["container"]["lists"][parseId(array)] = stage["lists"][array][1]

output["blocks"] = dict()
start = ""
event_whenflagclicked_count = 0
for block in sprite["blocks"]:
    if sprite["blocks"][block]["opcode"] == "event_whenflagclicked":
        start = sprite["blocks"][block]["next"]
        event_whenflagclicked_count += 1
    elif sprite["blocks"][block]["opcode"] not in opcodes:
        print("{0} is not a supported block yet.".format(sprite["blocks"][block]["opcode"]))
        sys.exit(1)
    else:
        block_id = parseId(block)
        output["blocks"][block_id] = dict()
        output["blocks"][block_id]["opcode"] = sprite["blocks"][block]["opcode"]
        output["blocks"][block_id]["next"] = parseId(sprite["blocks"][block]["next"])
        output["blocks"][block_id]["parent"] = parseId(sprite["blocks"][block]["parent"])
        output["blocks"][block_id]["inputs"] = {i: parseInput(sprite["blocks"][block]["inputs"][i]) for i in sprite["blocks"][block]["inputs"]}
        output["blocks"][block_id]["fields"] = {i: parseField(sprite["blocks"][block]["fields"][i]) for i in sprite["blocks"][block]["fields"]}

if event_whenflagclicked_count != 1:
    print("Your project must have one event_whenflagclicked block.")
    sys.exit(1)

output["start"] = parseId(start)

output["ids"] = len(ids)

if args.output == None:
    output_file_name = os.path.splitext(os.path.basename(args.file_name))[0] + ".scrape"
else:
    output_file_name = args.output
with open(output_file_name, "w") as scrapefile:
    json.dump(output, scrapefile, indent=args.indent)
