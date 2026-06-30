from pathlib import Path
import xml.etree.ElementTree as ET


class PremiereXML:

    def __init__(self, fps: int = 25):
        self.fps = fps

    def seconds_to_frames(self, seconds: float) -> int:
        return int(seconds * self.fps)

    def create_project(self, project_name: str = "VideoAI"):
        root = ET.Element("xmeml")
        root.set("version", "5")

        sequence = ET.SubElement(root, "sequence")
        sequence.set("id", "sequence-1")

        name = ET.SubElement(sequence, "name")
        name.text = project_name

        return root, sequence

    def save(self, root, output: Path):
        tree = ET.ElementTree(root)
        tree.write(output, encoding="utf-8", xml_declaration=True)