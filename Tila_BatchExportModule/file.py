import modo
import os
import Tila_BatchExportModule as t
from os.path import isfile
import xml.etree.cElementTree as ET
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def initConfigFile(config):
    return ET.Element(config)

def updateExportPath(export_path, browse_path):
    if isFileExist(t.config_file_path):

        tree = ET.parse(t.config_file_path)
        root = tree.getroot()

        configuration = ET.Element(t.configRoot)
        attribute = ET.SubElement(configuration, t.configSubElement, type="LastDirectory")

        ET.SubElement(attribute,t.configSubElement, type="ExportPath").text = export_path
        ET.SubElement(attribute,t.configSubElement, type="BrowsePath").text = browse_path


    else:
        configuration = ET.Element(t.configRoot)
        attribute = ET.SubElement(configuration, t.configSubElement, type="LastDirectory")
        ET.SubElement(attribute, t.configSubElement, type="ExportPath").text = export_path
        ET.SubElement(attribute, t.configSubElement, type="BrowsePath").text = browse_path

        writeConfigFile(configuration)


def isFileExist(filepath):
    if isfile(filepath):
        return True
    else:
        return False


def writeConfigFile(root):
    tree = ET.ElementTree(root)
    tree.write(t.config_file_path, method='xml', encoding='utf-8', xml_declaration=True)