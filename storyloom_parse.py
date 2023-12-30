import sys
import json
from datetime import datetime


def _print_text_component(comp):
    print(comp["text"])
    print()


def _print_dialog_component(comp, config):
    character_key = comp.get("characterAssetId")
    character_name = config.get("characterMap", {}).get(character_key, {}).get("characterName")
    dialog = comp["dialog"]

    # Format the dialog nice
    dialog = "> " + dialog.replace("\n", "\n> ")

    if character_name is not None:
        print(f"{character_name}:")
        print()
    print(dialog)
    print()


def _print_switch_component(comp, variables, config):
    var_id = comp["variableId"]
    var_name = [v["name"] for v in variables if v["id"] == var_id][0]
    print(f"VARIABLE CHECK. DEPENDING ON `{var_name}`, TAKE ONE BRANCH:")
    print()
    for ibranch, branch in enumerate(comp["branches"], start=1):
        print(f"BRANCH {ibranch}")
        print()
        for branch_comp in branch["components"]:
            _print_component(branch_comp, variables, config)
    print("END VARIABLE CHECK")
    print()


def _print_choice_component(comp, variables, config):
    print("BEGIN CHOICE BLOCK")
    print()
    prompt = comp.get("promptComponent")
    if prompt is not None:
        _print_component(prompt, variables, config)
    for iopt, option in enumerate(comp.get("options", []), start=1):
        choice_text = option.get("displayText")
        if choice_text is not None:
            print(f"OPTION {iopt}: {choice_text}")
            print()
        for opt_comp in option.get("components", []):
            _print_component(opt_comp, variables, config)
    print("END CHOICE BLOCK")
    print()


def _print_component(comp, variables, config):
    component_type = comp.get("type")
    if component_type == "textComponent":
        _print_text_component(comp)
    elif component_type == "dialogComponent":
        _print_dialog_component(comp, config)
    elif component_type == "choiceV2Component":
        _print_choice_component(comp, variables, config)
    elif component_type == "switchComponent":
        _print_switch_component(comp, variables, config)


def format_story(storydata):
    # Get the story configuration data
    variables = storydata.get("variables", {})
    config = storydata.get("configuration", {})

    # Story title
    title = storydata.get("name", "Untitled")
    print(f"# {title} #")
    print()

    # Dates of creation and last modification
    created = storydata.get("createdOn")
    if created is not None:
        created = datetime.fromisoformat(created).strftime("%Y/%m/%d")
    lastmod = storydata.get("lastModified")
    if lastmod is not None:
        lastmod = datetime.fromisoformat(lastmod).strftime("%Y/%m/%d")
    print(f"Created {created}")
    print()
    print(f"Last modified {lastmod}")
    print()

    # Story description
    description = storydata.get("description")
    print("### Description ###")
    print()
    print(description)
    print()

    # Chapter and scene information
    chapters = sorted(storydata.get("chapters", []),
                      key=lambda c: c.get("order", 0))
    for ichapter, chapter in enumerate(chapters, start=1):
        # Chapter title
        chapter_title = chapter.get("title")
        print(f"## Chapter {ichapter}", end="")
        print("" if chapter_title is None else f": {chapter_title}")
        print()

        # Chapter description
        chapter_description = chapter.get("description")
        if chapter_description is not None:
            print("---")
            print()
            print(chapter_description)
            print()
            print("---")
            print()

        scenes = sorted(chapter.get("contents", {}).get("scenes", {}).values(),
                        key=lambda s: s.get("order", 0))
        for scene in scenes:
            # Scene title
            scene_title = scene.get("title", "Untitled")
            print(f"### Scene: {scene_title}")
            print()

            # Print the scene components
            for comp in scene.get("components", []):
                _print_component(comp, variables, config)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        storydata = json.load(f)

    format_story(storydata)
