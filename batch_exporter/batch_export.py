#!/usr/bin/env python

import lx
import os
import sys

# Arguments
triple = '0'
resetPos = '0'
rotAngle = '0'
scaleAmount = '1'
smoothAngle = '1'
exportEach = '1'
exportHierarchy = '0'
scanFiles = '0'
upAxis = lx.eval('pref.value units.upAxis ?')
iUpAxis = upAxis

# Get the current FBX Export setting.
fbx_export_setting = lx.eval1('user.value sceneio.fbx.save.exportType ?')

sceneIndex = lx.eval('query sceneservice scene.index ? current')
userSelection = lx.evalN('query layerservice layer.id ? fg')
userSelectionCount = len(userSelection)
currentPath = lx.eval("query sceneservice scene.file ? current")


def init_dialog(dialog_type, text):
    if dialog_type == "input":
        # Get the directory to export to.
        lx.eval('dialog.setup fileOpenMulti')
        lx.eval('dialog.fileType scene')
        lx.eval('dialog.title "Mesh Path"')
        lx.eval('dialog.msg "Select the meshes you want to process."')
        lx.eval('dialog.result "%s"' % currentPath)

    elif dialog_type == "output":
        # Get the directory to export to.
        lx.eval('dialog.setup dir')
        lx.eval('dialog.title "Export Path"')
        lx.eval('dialog.msg "Select path to export to."')
        lx.eval('dialog.result "%s"' % currentPath)

    elif dialog_type == "file_save":
        lx.eval('dialog.setup fileSave')
        lx.eval('dialog.title "Save File"')
        lx.eval('dialog.msg "Select path to save teh file."')
        lx.eval('dialog.result "%s"' % currentPath)

    elif dialog_type == "bad_formatting":
        lx.eval('dialog.setup error')
        lx.eval('dialog.title "Bad Formatting."')
        lx.eval('dialog.msg " Please check the synthax of the command : %s"' % text)


def init_message(type, title, message):
    lx.eval('dialog.setup {%s}' % type)
    lx.eval('dialog.title {%s}' % title)
    lx.eval('dialog.msg {%s}' % message)
    lx.eval('dialog.open')


def init_arg():
    global triple
    global resetPos
    global rotAngle
    global scaleAmount
    global smoothAngle
    global exportEach
    global exportHierarchy
    global scanFiles
    global upAxis

    args = lx.args()
    argCount = len(args)

    error_message = "Bad Formatting !"

    for a in xrange(0, argCount - 1):
        if a % 2 == 0:
            if args[a] == 'triple':
                if args[a + 1] != '0' and args[a + 1] != '1':
                    init_dialog(error_message, "triple")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    triple = args[a + 1]

            if args[a] == 'resetPos':
                if args[a + 1] != '0' and args[a + 1] != '1':
                    init_dialog(error_message, "resetPos")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    resetPos = args[a + 1]

            if args[a] == 'rotAngle':
                rotAngle = args[a + 1]

            if args[a] == 'scaleAmount':
                scaleAmount = args[a + 1]

            if args[a] == 'smoothAngle':
                smoothAngle = args[a + 1]

            if args[a] == 'exportEach':
                if args[a + 1] != '0' and args[a + 1] != '1':
                    init_dialog(error_message, "exportEach")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    exportEach = args[a + 1]

            if args[a] == 'exportHierarchy':
                if args[a + 1] != '0' and args[a + 1] != '1':
                    init_dialog(error_message, "exportHierarchy")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    exportHierarchy = args[a + 1]

            if args[a] == 'scanFiles':
                if args[a + 1] != '0' and args[a + 1] != '1':
                    init_dialog(error_message, "scanFiles")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    scanFiles = args[a + 1]

            if args[a] == 'upAxis':
                if args[a + 1] != 'X' and args[a + 1] != 'Y' and args[a + 1] != 'Z':
                    init_dialog(error_message, "upAxis")
                    try:
                        lx.eval('dialog.open')
                    except:
                        pass
                else:
                    upAxis = args[a + 1]


def flow():
    init_arg()

    if scanFiles == '0':  # export selected mesh in the scene
        if userSelectionCount == 0:
            init_message('error','No item selected', 'Select at least one item')
            sys.exit()

        init_dialog("output", "")

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            pass
        else:
            output_dir = lx.eval1('dialog.result ?')
            batch_export(output_dir)
    else:  # browse file to process

        init_dialog("input", "")
        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            pass
        else:
            files = lx.evalN('dialog.result ?')
            init_dialog("output", "")
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                pass
            else:
                output_dir = lx.eval1('dialog.result ?')

                for f in files:
                    print "processing " + os.path.basename(f)
                    name = os.path.basename(f)
                    ext = os.path.splitext(name)[1]
                    name = os.path.splitext(name)[0]

                    lx.eval('loaderOptions.wf_OBJ false false Meters')
                    # lx.eval('loaderOptions.fbx false true true true true true true true false false true true true true 0')
                    lx.eval('!scene.open "%s" normal' % f)

                    # if ext == 'fbx'
                    lx.eval('select.itemType mesh')

                    lx.eval('item.name %s mesh' % name)
                    batch_export(output_dir)
                    lx.eval('!scene.close')

    init_message('info','Done', 'Operation completed !')


def batch_export(output_dir):
    init_arg()

    if upAxis != lx.eval('pref.value units.upAxis ?'):
        lx.eval('pref.value units.upAxis %s' % upAxis)

    if exportHierarchy == '1':
        lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelectionWithHierarchy')
    else:
        lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelection')

    # Grab the IDs of each foreground layer.
    layers = userSelection

    if exportEach == '1':  # Export each layer separately.

        for layer in layers:
            export_loop(output_dir, layer)
            clean_scene()

    else:  # Export all selected layers in one file.
        export_loop(output_dir, layers)
        clean_scene()


def duplicate_rename(layer_name):
    if exportEach == '1':
        lx.eval('item.duplicate false all:true')
        lx.eval('item.name %s mesh' % (layer_name + '_1'))
    else:
        for l in xrange(0, userSelectionCount):
            layer_name = lx.eval1('query layerservice layer.name ? %s' % userSelection[l])
            lx.eval('select.subItem %s set mesh' % userSelection[l])
            lx.eval('item.duplicate false all:true')
            lx.eval('item.name %s mesh' % (layer_name + '_' + str(l)))
        select_duplicate(layer_name)


def get_name(layer):
    if exportEach == '1':
        return lx.eval1('query layerservice layer.name ? %s' % layer)
    else:
        return os.path.splitext(lx.eval1('query sceneservice scene.name ? current'))[0]


def set_name(layer_name):
    if exportEach == '1':
        lx.eval('item.name %s mesh' % layer_name)
    else:

        lx.eval('select.itemType mesh')
        duplicate = lx.evalN('query layerservice layer.id ? fg')
        for l in duplicate:
            lx.eval('select.subItem %s set mesh' % l)
            current_name = lx.eval1('query layerservice layer.name ? current')
            current_name = current_name[:-2]
            lx.eval('item.name %s mesh' % current_name)
        lx.eval('select.itemType mesh')


def select_duplicate(layer_name):
    if exportEach == '1':
        lx.eval('select.item {%s} set' % (layer_name + '_1'))
    else:
        get_user_selection()
        for l in xrange(0, userSelectionCount):
            new_layer_name = lx.eval('query layerservice layer.name ? %s' % userSelection[l])
            if l == 0:
                lx.eval('select.item {%s} set' % (new_layer_name + '_' + str(l)))
            else:
                lx.eval('select.item {%s} add' % (new_layer_name + '_' + str(l)))
    if exportHierarchy == '1':
        lx.eval('select.itemHierarchy')


def get_user_selection():
    for l in xrange(0, userSelectionCount):
        if l == 0:
            lx.eval('select.subItem {%s} set mesh' % userSelection[l])
        else:
            lx.eval('select.subItem {%s} add mesh' % userSelection[l])


def export_selection(output_path, layer_name):
    processing_log(layer_name)

    lx.eval('scene.new')
    newScene = lx.eval('query sceneservice scene.index ? current')
    lx.eval('select.itemType mesh')
    lx.eval('!!item.delete')
    lx.eval('scene.set %s' % sceneIndex)
    select_duplicate(layer_name)
    lx.eval('!layer.import %s {} true true false position:0' % newScene)
    lx.eval('scene.set %s' % newScene)
    set_name(layer_name)

    # Export to FBX.
    lx.eval('!scene.saveAs "%s" fbx false' % output_path)

    lx.eval('scene.close')

    lx.eval('scene.set %s' % sceneIndex)
    select_duplicate(layer_name)

    lx.eval('!!item.delete')


def export_loop(output_dir, layer):
    # Get the layer name.
    layer_name = get_name(layer)
    # Work out the export path from the name.
    output_path = os.path.join(output_dir, layer_name + '.fbx')

    if exportEach == '1':
        # Select only the mesh item.
        lx.eval('select.subItem %s set mesh' % layer)
    else:
        get_user_selection()

    if exportHierarchy == '1':
        lx.eval('select.itemHierarchy')

    duplicate_rename(layer_name)

    # Set Vertex normal
    lx.eval('vertMap.normals vert_normals false {%s}' % smoothAngle)

    if triple == '1':
        lx.eval('poly.triple')

    if resetPos == '1':
        lx.eval('transform.reset translation')

    if scaleAmount != '1':
        lx.eval('transform.freeze scale')
        lx.eval('transform.channel scl.X %s' % scaleAmount)
        lx.eval('transform.channel scl.Y %s' % scaleAmount)
        lx.eval('transform.channel scl.Z %s' % scaleAmount)
        lx.eval('transform.freeze scale')

    if rotAngle != '0':
        lx.eval('transform.channel rot.X "%s"' % rotAngle)
        lx.eval('transform.freeze rotation')
        lx.eval('edgesmooth.update')

    # Export to FBX.
    export_selection(output_path, layer_name)


def clean_scene():
    # get_user_selection()

    # Put the user's original FBX Export setting back.
    lx.eval('user.value sceneio.fbx.save.exportType %s' % fbx_export_setting)

    if upAxis != iUpAxis:
        lx.eval('pref.value units.upAxis %s' % iUpAxis)


def print_log(message):
    lx.out("BATCH_EXPORT : " + message)


def processing_log(message):
    print_log("Processing_File : " + message)


flow()
