#!/usr/bin/env python3
"""Compose local Devicon brand SVGs into light and dark technology cards."""

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ICONS = [
    ("typescript", "TypeScript"), ("python", "Python"), ("rust", "Rust"),
    ("react", "React"), ("electron", "Electron"), ("cloudflare", "Cloudflare"),
]


def element(parent, tag, **attributes):
    return ET.SubElement(parent, f"{{{NS}}}{tag}", attributes)


for theme in ("light", "dark"):
    dark = theme == "dark"
    foreground = "#f0f6fc" if dark else "#17213b"
    root = ET.Element(f"{{{NS}}}svg", {
        "width": "640", "height": "78", "viewBox": "0 0 640 78", "role": "img",
    })
    element(root, "title").text = ", ".join(label for _, label in ICONS)
    element(root, "desc").text = "Brand icons from Devicon. License and attribution in assets/brand-icons."
    for index, (name, label) in enumerate(ICONS):
        group = element(root, "g", transform=f"translate({index * 108},0)")
        element(group, "rect", x=".5", y=".5", width="99", height="76", rx="12",
                fill="#131b2b" if dark else "#ffffff",
                stroke="#29344b" if dark else "#dce3f2")
        icon = deepcopy(ET.parse(ROOT / "assets" / "brand-icons" / f"{name}.svg").getroot())
        icon.attrib.update({"x": "32", "y": "9", "width": "36", "height": "36"})
        if name == "rust":
            icon.set("fill", foreground)
        group.append(icon)
        text = element(group, "text", x="50", y="63", fill=foreground)
        text.attrib.update({
            "text-anchor": "middle", "font-size": "11",
            "font-family": "-apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif",
        })
        text.text = label
    ET.indent(root)
    ET.ElementTree(root).write(ROOT / "assets" / f"stack-{theme}.svg", encoding="utf-8")
    print(f"Generated stack-{theme}.svg")
