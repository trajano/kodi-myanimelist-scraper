from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from typing import Dict, Any
import time
import markdown
import bs4


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        metadata = self.metadata.core
        readme = bs4.BeautifulSoup(
            markdown.markdown(metadata.readme), "html.parser"
        ).get_text()
        addon = Element(
            "addon",
            {
                "id": metadata.name.replace("-", "."),
                "version": metadata.version,
                "name": metadata.description,
                "provider-name": metadata.authors_data.get("name", [""])[0]
                if metadata.authors_data
                else "",
            },
        )
        requires = SubElement(addon, "requires")
        SubElement(
            requires,
            "import",
            {
                "addon": "xbmc.python",
                "version": "3.0.0",
            },
        )
        SubElement(
            requires,
            "import",
            {
                "addon": "xbmc.metadata",
                "version": "2.1.0",
            },
        )
        SubElement(
            requires,
            "import",
            {
                "addon": "script.module.pil",
                "version": "5.1.0",
            },
        )

        SubElement(
            addon,
            "extension",
            {
                "point": "xbmc.metadata.scraper.tvshows",
                "library": "addon.py",
                "cachepersistence": "00:01",
            },
        )

        addon_metadata = SubElement(
            addon,
            "extension",
            {"point": "xbmc.addon.metadata"},
        )

        SubElement(addon_metadata, "summary").text = metadata.description
        SubElement(addon_metadata, "description").text = readme
        SubElement(addon_metadata, "platform").text = "all"
        SubElement(addon_metadata, "license").text = metadata.license_expression

        xml_str = minidom.parseString(tostring(addon)).toprettyxml(indent="  ")
        with open(os.path.join(self.root, "addon.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str)
        print(xml_str)

    def finalize(
        self, version: str, build_data: Dict[str, Any], artifact_path: str
    ) -> None:
        ts = str(int(time.time()))
        dirpath, fname = os.path.split(artifact_path)
        name, ext = os.path.splitext(fname)
        new_fname = f"{name}.{ts}{ext}"
        new_path = os.path.join(dirpath, new_fname)
        os.rename(artifact_path, new_path)
