import modo
import os
import Tila_BatchExportModule as t
from os.path import isfile
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def initConfigFile(config):
    return ET.Element(config)

def updateExportPath(export_path, browse_path):
    if isFileExist(t.config_file_path):

        tree = ET.parse(t.config_file_path)
        configuration = tree.getroot()

        for atom in configuration.iter(t.config_last_directory):
            updateElementIfNeeded(atom, 'ExportPath', export_path)
            updateElementIfNeeded(atom, 'BrowsPath', browse_path)

    else:
        configuration = ET.Element(t.config_root)
        attribute = ET.SubElement(configuration, t.config_last_directory)
        ET.SubElement(attribute, t.config_sub_element, type="ExportPath").text = export_path
        ET.SubElement(attribute, t.config_sub_element, type="BrowsePath").text = browse_path

    writeConfigFile(configuration)

def updateElementIfNeeded(element, name, currValue):
    if element.get(name) != currValue:
        element.set(name, currValue)

def isFileExist(filepath):
    if isfile(filepath):
        return True
    else:
        return False


def writeConfigFile(root):
    indent(root)
    tree = ET.ElementTree(root)

    if not os.path.exists(t.config_path):
        os.makedirs(t.config_path)

    tree.write(t.config_file_path, method='xml', encoding='utf-8', xml_declaration=True)
