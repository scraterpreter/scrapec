import argparse
import zipfile
import json
import sys
import os
import copy

def main():
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

    # with open("opcodes.json", "r") as opcodesfile:
        # opcodejson = json.load(opcodesfile)

    opcodejson = {
        "opcodes": [
            "control_repeat",
            "control_repeat_until",
            "control_forever",
            "control_wait",
            "control_wait_until",
            "control_if",
            "control_if_else",
            "control_stop",
            "data_variable",
            "data_setvariableto",
            "data_changevariableby",
            "data_listcontents",
            "data_addtolist",
            "data_deleteoflist",
            "data_deletealloflist",
            "data_insertatlist",
            "data_replaceitemoflist",
            "data_itemoflist",
            "data_itemnumoflist",
            "data_lengthoflist",
            "data_listcontainsitem",
            "event_whenflagclicked",
            "looks_say",
            "looks_think",
            "operator_add",
            "operator_subtract",
            "operator_multiply",
            "operator_divide",
            "operator_lt",
            "operator_equals",
            "operator_gt",
            "operator_and",
            "operator_or",
            "operator_not",
            "operator_random",
            "operator_join",
            "operator_letter_of",
            "operator_length",
            "operator_contains",
            "operator_mod",
            "operator_round",
            "operator_mathop",
            "sensing_timer",
            "sensing_resettimer",
            "sensing_current",
            "sensing_dayssince2000",
            "sensing_askandwait",
            "sensing_answer",
            "sensing_username"
        ],
        "inputs_requirements": {
            "control_repeat": ["TIMES", "SUBSTACK"],
            "control_repeat_until": ["CONDITION", "SUBSTACK"],
            "control_forever": ["SUBSTACK"],
            "control_wait": ["DURATION"],
            "control_wait_until": ["CONDITION"],
            "control_if": ["CONDITION", "SUBSTACK"],
            "control_if_else": ["CONDITION", "SUBSTACK", "SUBSTACK2"],
            "data_setvariableto": ["VALUE"],
            "data_changevariableby": ["VALUE"],
            "data_addtolist": ["ITEM"],
            "data_deleteoflist": ["INDEX"],
            "data_insertatlist": ["ITEM", "INDEX"],
            "data_replaceitemoflist": ["ITEM", "INDEX"],
            "data_itemoflist": ["INDEX"],
            "data_itemnumoflist": ["ITEM"],
            "data_listcontainsitem": ["ITEM"],
            "looks_say": ["MESSAGE"],
            "looks_think": ["MESSAGE"],
            "operator_add": ["NUM1", "NUM2"],
            "operator_subtract": ["NUM1", "NUM2"],
            "operator_multiply": ["NUM1", "NUM2"],
            "operator_divide": ["NUM1", "NUM2"],
            "operator_lt": ["OPERAND1", "OPERAND2"],
            "operator_equals": ["OPERAND1", "OPERAND2"],
            "operator_gt": ["OPERAND1", "OPERAND2"],
            "operator_and": ["OPERAND1", "OPERAND2"],
            "operator_or": ["OPERAND1", "OPERAND2"],
            "operator_not": ["OPERAND"],
            "operator_random": ["FROM", "TO"],
            "operator_join": ["STRING1", "STRING2"],
            "operator_letter_of": ["LETTER", "STRING"],
            "operator_length": ["STRING"],
            "operator_contains": ["STRING1", "STRING2"],
            "operator_mod": ["NUM1", "NUM2"],
            "operator_round": ["NUM"],
            "operator_mathop": ["NUM"],
            "sensing_askandwait": ["QUESTION"]
        }
    }

    opcodes = opcodejson["opcodes"]
    inputs_requirements = opcodejson["inputs_requirements"]

    ids = set()
    ids.update(set(stage["variables"].keys()))
    ids.update(set(stage["lists"].keys()))
    ids.update(set(sprite["blocks"].keys()))
    ids.difference_update({i for i in sprite["blocks"] if type(sprite["blocks"][i]) == type(dict()) and sprite["blocks"][i]["opcode"] == "event_whenflagclicked"})
    ids = list(ids)
    ids.sort()

    def parseInput(input_data):
        if input_data[0] == 1:
            if input_data[1] == None:
                print("A block contains a null value in one of its inputs.")
                sys.exit(1)
            return [2, input_data[1][1]]
        else:
            return [1, parseId(input_data[1])]

    def parseField(field_data):
        if field_data[1] == None:
            return [2, field_data[0]]
        else:
            return [1, parseId(field_data[1])]

    def parseId(id_string):
        if type(id_string) == type(list()):
            return parseId(id_string[2])
        if id_string in ids:
            return str(ids.index(id_string))
        else:
            return None

    output = dict()

    output["container"] = dict()

    output["container"]["variables"] = dict()
    output["container"]["lists"] = dict()
    for variable in stage["variables"]:
        output["container"]["variables"][parseId(variable)] = str(stage["variables"][variable][1])
    for array in stage["lists"]:
        output["container"]["lists"][parseId(array)] = stage["lists"][array][1]

    output["blocks"] = dict()
    start = ""
    event_whenflagclicked_count = 0
    for block in sprite["blocks"]:
        if type(sprite["blocks"][block]) != type(dict()):
            continue
        if sprite["blocks"][block]["opcode"] == "event_whenflagclicked":
            start = sprite["blocks"][block]["next"]
            event_whenflagclicked_count += 1
        elif sprite["blocks"][block]["opcode"] not in opcodes:
            print("{0} is not a supported block yet.".format(sprite["blocks"][block]["opcode"]))
            sys.exit(1)
        elif sprite["blocks"][block]["opcode"] in inputs_requirements and not set(sprite["blocks"][block]["inputs"].keys()).issuperset(set(inputs_requirements[sprite["blocks"][block]["opcode"]])):
            print("One of the {0} block has some input(s) missing.".format(sprite["blocks"][block]["opcode"]))
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

    def available_nodes(graph, visited):
        available = set()
        for i in graph:
            if graph[i].issubset(visited) and i not in visited:
                available.add(i)
        return available

    def bfs(graph, visited_order=list()):
        visited_set = set(visited_order)
        while True:
            queue = list(available_nodes(graph, visited_set))
            if len(queue) == 0:
                break
            queue.sort()
            node = queue[0]
            visited_order.append(node)
            visited_set.add(node)
        return visited_order

    graph = dict()
    for block in output["blocks"]:
        graph[int(block)] = set()
        for parameter in output["blocks"][block]["inputs"]:
            if output["blocks"][block]["inputs"][parameter][0] == 1:
                graph[int(block)].add(int(output["blocks"][block]["inputs"][parameter][1]))
        for field in output["blocks"][block]["fields"]:
            if output["blocks"][block]["fields"][field][0] == 1:
                graph[int(block)].add(int(output["blocks"][block]["fields"][field][1]))
        if output["blocks"][block]["next"] != None:
            graph[int(block)].add(int(output["blocks"][block]["next"]))

    container_ids = [int(i) for i in list(output["container"]["variables"].keys()) + list(output["container"]["lists"].keys())]
    container_ids.sort()

    result = bfs(graph, copy.copy(container_ids))
    if len(result) < len(graph):
        print("There is something wrong with the provided project file.")
        sys.exit(1)
    else:
        output["build_order"] = [str(i) for i in result[len(container_ids):]]

    if args.output == None:
        output_file_name = os.path.splitext(os.path.basename(args.file_name))[0] + ".scrape"
    else:
        output_file_name = args.output
    with open(output_file_name, "w") as scrapefile:
        json.dump(output, scrapefile, indent=args.indent)

if __name__ == "__main__":
    main()
