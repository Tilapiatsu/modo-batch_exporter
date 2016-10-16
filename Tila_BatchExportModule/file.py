import os
from os.path import isfile
import lx
import Tila_BatchExportModule as t
import dialog
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

    writeConfigFile(configuration, t.config_file_path)


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
    return isfile(filepath)


def constructPresetPath(filename):
    return os.path.join(t.preset_path, filename)


def writePreset(name, userValues):
    configuration = ET.Element(t.config_root)
    settings = ET.SubElement(configuration, t.config_export_settings)
    for i in xrange(len(t.userValues)):
        ET.SubElement(settings, t.config_sub_element, setting=t.userValues[i][0]).text = str(userValues[i])

    filepath = os.path.join(t.preset_path, name + '.cfg')

    if isFileExist(filepath):
        result = dialog.init_message('yesNo', 'Override preset ?', ' Preset already exist ! Do you want to override it ?')
        if result == 'ok':
            writeConfigFile(configuration, os.path.join(t.preset_path, name + '.cfg'))
            presets = [f for f in os.listdir(t.preset_path) if isfile(os.path.join(t.preset_path, f))]
            refreshPresetForm('70945661220', presets)
            return True
        else:
            return False
    else:
        writeConfigFile(configuration, os.path.join(t.preset_path, name + '.cfg'))
        presets = [f for f in os.listdir(t.preset_path) if isfile(os.path.join(t.preset_path, f))]
        refreshPresetForm('70945661220', presets)
        return True


def loadPreset(name):
    filepath = os.path.join(t.preset_path, name + '.cfg')

    if isFileExist(filepath):
        configuration = getFileRoot(filepath)
        settings = configuration.find(t.config_export_settings)
        settingList = list(settings.iter(t.config_sub_element))

        for i in xrange(len(settingList)):
            if settingList[i].get('setting') == t.userValues[i][0]:
                setUserValueFromPreset(settingList[i], i)
        return True
    else:
        return False


def setUserValueFromPreset(e, i):
    lx.eval('user.value %s%s %s' % (t.kit_prefix, t.userValues[i][0], e.text))


def refreshPresetForm(hashkey, presets):
    configuration = ET.Element(t.config_root)
    attribute = ET.SubElement(configuration, t.config_sub_element, type='Attributes')

    sheet = ET.SubElement(attribute, "hash", type='Sheet', key="%s:sheet" % hashkey)

    ET.SubElement(sheet, t.config_sub_element, type="Label").text = "Tila_Presets"
    ET.SubElement(sheet, t.config_sub_element, type="Desc").text = ""
    ET.SubElement(sheet, t.config_sub_element, type="Tooltip").text = ""
    ET.SubElement(sheet, t.config_sub_element, type="Help").text = ""
    ET.SubElement(sheet, t.config_sub_element, type="ShowLabel").text = "1"
    ET.SubElement(sheet, t.config_sub_element, type="PopupFace").text = "option"
    ET.SubElement(sheet, t.config_sub_element, type="Enable").text = "1"
    ET.SubElement(sheet, t.config_sub_element, type="Alignment").text = "default"
    ET.SubElement(sheet, t.config_sub_element, type="Style").text = "inline"
    ET.SubElement(sheet, t.config_sub_element, type="Export").text = "0"
    ET.SubElement(sheet, t.config_sub_element, type="Filter").text = ""
    ET.SubElement(sheet, t.config_sub_element, type="Layout").text = "vtoolbar"
    ET.SubElement(sheet, t.config_sub_element, type="Justification").text = "left"
    ET.SubElement(sheet, t.config_sub_element, type="Columns").text = "1"
    ET.SubElement(sheet, t.config_sub_element, type="StartCollapsed").text = "0"
    ET.SubElement(sheet, t.config_sub_element, type="EditorColor").text = "none"
    ET.SubElement(sheet, t.config_sub_element, type="Proficiency").text = "basic"
    ET.SubElement(sheet, t.config_sub_element, type="Group").text = "Tilapiatsu/Tila_BatchExporter"

    for m in range(len(presets)):
        list = ET.SubElement(sheet, "list", type="Control", val='cmd tila.exportpreset.load %s' % m)
        ET.SubElement(list, t.config_sub_element, type="ShowWhenDisabled").text = "1"
        ET.SubElement(list, t.config_sub_element, type="booleanStyle").text = "default"
        ET.SubElement(list, t.config_sub_element, type="Enable").text = "1"
        ET.SubElement(list, t.config_sub_element, type="Label").text = os.path.splitext(presets[m])[0]
        ET.SubElement(list, t.config_sub_element, type="Help").text = ""
        ET.SubElement(list, t.config_sub_element, type="Tooltip").text = ""
        ET.SubElement(list, t.config_sub_element, type="Desc").text = ""
        ET.SubElement(list, t.config_sub_element, type="ShowLabel").text = "1"
        ET.SubElement(list, t.config_sub_element, type="PopupFace").text = "option"
        ET.SubElement(list, t.config_sub_element, type="Alignment").text = "default"
        ET.SubElement(list, t.config_sub_element, type="Style").text = "default"
        ET.SubElement(list, t.config_sub_element, type="StartCollapsed").text = "0"
        ET.SubElement(list, t.config_sub_element, type="Proficiency").text = "basic"
        ET.SubElement(list, t.config_sub_element, type="ProficiencyOverride").text = "default"

    writeConfigFile(configuration, os.path.join(t.root_path, 'presetForm.cfg'))


def writeConfigFile(root, path):
    indent(root)
    tree = ET.ElementTree(root)

    if not os.path.exists(os.path.split(path)[0]):
        os.makedirs(os.path.split(path)[0])

    tree.write(path, method='xml', encoding='utf-8', xml_declaration=True)
