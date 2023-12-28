import sys
import json
from datetime import datetime


def format_story(storydata):
    # Per-story information (title, etc)
    title = storydata.get("name", "Untitled")
    created = storydata.get("createdOn")
    if created is not None:
        created = datetime.fromisoformat(created)
    lastmod = storydata.get("lastModified")
    if lastmod is not None:
        lastmod = datetime.fromisoformat(lastmod)
    description = storydata.get("description")
    character_map = storydata.get("configuration", {}).get("characterMap", {})

    # Chapter and scene information
    chapters = sorted(storydata.get("chapters", []),
                      key=lambda c: c.get("order", 0))
    chapter_scenes = []
    for chapter in chapters:
        chapter_title = chapter.get("title", "")
        if chapter_title:
            chapter_title = ": " + chapter_title
        chapter_description = chapter.get("description", "")
        scenes = sorted(chapter.get("contents", {}).get("scenes", {}).values(),
                        key=lambda s: s.get("order", 0))
        scene_components = []
        for scene in scenes:
            scene_title = scene.get("title", "Untitled")
            component_text = []
            for comp in scene.get("components", []):
                if comp["type"] == "dialogComponent":
                    character_key = comp.get("characterAssetId")
                    character_name = character_map.get(character_key, {}).get("characterName", "")
                    if character_name:
                        character_name += ": "
                    component_text.append("{}{}".format(character_name, comp["dialog"]))
                elif comp["type"] == "textComponent":
                    component_text.append(comp["text"])
            scene_components.append((scene_title, component_text))
        chapter_scenes.append((chapter_title, chapter_description, scene_components))

    # Now write it all out
    output = f"""# {title} #

Created {created.strftime("%Y/%m/%d")}

Last modified {lastmod.strftime("%Y/%m/%d")}

### Description ###

{description}
"""
    for ichapter, (chapter_title, chapter_desc, scenelist) in enumerate(chapter_scenes):
        chapter_output = f"""
## Chapter {ichapter + 1}{chapter_title} ##

---

{chapter_desc}

---

"""
        for scene_title, component_text in scenelist:
            scene_output = f"""### Scene: {scene_title} ###

"""
            for comp in component_text:
                scene_output += f"""
{comp}

"""
            chapter_output += scene_output
        output += chapter_output

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        storydata = json.load(f)

    print(format_story(storydata))

