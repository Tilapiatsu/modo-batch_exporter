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

def getLatestPath(attribName):
    if isFileExist(t.config_file_path):
        configuration = getFileRoot(t.config_file_path)

        last_dir = configuration.find(t.config_last_directory)
        return getSubElement(last_dir, 'type', attribName).text
    else:
        return ''

def updateExportPath(export_path, browse_src_path, browse_dest_path):
    if isFileExist(t.config_file_path):
        configuration = getFileRoot(t.config_file_path)

        last_dir = configuration.find(t.config_last_directory)
        updateElementIfNeeded(last_dir, 'type', t.config_export_path, export_path)
        updateElementIfNeeded(last_dir, 'type', t.config_browse_src_path, browse_src_path)
        updateElementIfNeeded(last_dir, 'type', t.config_browse_dest_path, browse_dest_path)

    else:
        configuration = ET.Element(t.config_root)
        last_dir = ET.SubElement(configuration, t.config_last_directory)
        ET.SubElement(last_dir, t.config_sub_element, type=t.config_export_path).text = export_path
        ET.SubElement(last_dir, t.config_sub_element, type=t.config_browse_src_path).text = browse_src_path
        ET.SubElement(last_dir, t.config_sub_element, type=t.config_browse_dest_path).text = browse_dest_path

    writeConfigFile(configuration)


def updateElementIfNeeded(element, attrib, sub, currValue):
    for e in element.iter(t.config_sub_element):
        if e.get(attrib) == sub:
            path = e.text
            if path != currValue and currValue != '':
                e.text = currValue

def getFileRoot(file):
    tree = ET.parse(file)
    return tree.getroot()

def getSubElement(element, attrib, sub):
    for e in element.iter(t.config_sub_element):
        if e.get(attrib) == sub:
            return e


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
