#!/usr/bin/env python

import lx
import os
import sys
import subprocess
import modo

scn = modo.Scene()
currScn = modo.scene.current()


############## TODO ###################
'''
 - find a way to keep last output folder in memory
 - ReWrite with Modo TDSDK
 - Refactoring everything ?
 - Create a class ?
 - extract some methods to other files ( Freeze Transform, Position Offset etc... )
 - Find a way to avoid using Farfarer's edgesmooth methods
 - Create a progress bar https://gist.github.com/tcrowson/e3d401055739d1a72863
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )

'''


############## Arguments ##############
triple_sw = False
resetPos_sw = False
resetRot_sw = False
resetSca_sw = False
resetShe_sw = False

freezePos_sw = False
freezeRot_sw = False
freezeSca_sw = False
freezeShe_sw = False

freezeGeo_sw = False

rotX = 0
rotY = 0
rotZ = 0

scaX = 1
scaY = 1
scaZ = 1

smoothAngle_sw = False
smoothAngle = 180

hardenUvBorder_sw = False
uvMapName = 'Texture'

exportFormatFbx_sw = True
exportFormatObj_sw = False
exportFormatLxo_sw = False
exportFormatLwo_sw = False
exportFormatAbc_sw = False
exportFormatAbchdf_sw = False
exportFormatDae_sw = False
exportFormatDxf_sw = False
exportFormat3dm_sw = False
exportFormatGeo_sw = False


exportCageMorph_sw = False
cageMorphMapName = 'cage'

exportFile_sw = True
exportEach_sw = True
exportHierarchy_sw = False
scanFiles_sw = False

openDestFolder_sw = True

upAxis = lx.eval('pref.value units.upAxis ?')
iUpAxis = upAxis

debug_log = True

debug_mode = False


# Get the current FBX Export setting.
fbx_export_setting = lx.eval1('user.value sceneio.fbx.save.exportType ?')

sceneIndex = lx.eval('query sceneservice scene.index ? current')
userSelection = lx.evalN('query layerservice layer.id ? fg')
userSelectionCount = len(userSelection)

currentPath = lx.eval("query sceneservice scene.file ? current")

if currentPath is None:
    currentPath = ""


if sys.platform == 'darwin':
    def open_folder(path):
        subprocess.check_call(['open', '--', path])
elif sys.platform == 'linux2':
    def open_folder(path):
        subprocess.check_call(['xdg-open', '--', path])
elif sys.platform == 'win32':
    def open_folder(path):
        os.startfile(path)


def init_dialog(dialog_type):
    if dialog_type == "input":
        # Get the directory to export to.
        lx.eval('dialog.setup fileOpenMulti')
        lx.eval('dialog.fileType scene')
        lx.eval('dialog.title "Mesh Path"')
        lx.eval('dialog.msg "Select the meshes you want to process."')
        lx.eval('dialog.result "%s"' % currentPath)

    if dialog_type == "output":
        # Get the directory to export to.
        lx.eval('dialog.setup dir')
        lx.eval('dialog.title "Export Path"')
        lx.eval('dialog.msg "Select path to export to."')
        lx.eval('dialog.result "%s"' % currentPath)

    if dialog_type == 'file_save':
        init_custom_dialog('fileSave', 'SaveFile', ('FBX',), 'FBX file', ('*.FBX',), 'fbx', currentPath[:-4])


    if dialog_type == "cancel":
        init_message('error', 'Canceled', 'Operation aborded')
        sys.exit()


# http://modo.sdk.thefoundry.co.uk/wiki/Dialog_Commands
def init_custom_dialog(type, title, format, uname, ext, save_ext=None, path=None, init_dialog = False):
    ''' Custom file dialog wrapper function

        type  :   Type of dialog, string value, options are 'fileOpen' or 'fileSave'
        title :   Dialog title, string value.
        format:   file format, tuple of string values
        uname :   internal name
        ext   :   tuple of file extension filter strings
        save_ext: output file extension for fileSave dialog
        path  :   optional default loacation to open dialog

    '''
    lx.eval("dialog.setup %s" % type)
    lx.eval("dialog.title {%s}" % (title))
    lx.eval("dialog.fileTypeCustom {%s} {%s} {%s} {%s}" % (format, uname, ext, save_ext))
    if type == 'fileSave' and save_ext != None:
        lx.eval("dialog.fileSaveFormat %s extension" % save_ext)
    if path is not None:
        lx.eval('dialog.result {%s}' % path)

    if init_dialog:
        try:
            lx.eval("dialog.open")
            return lx.eval("dialog.result ?")
        except:
            return None


def init_message(type, title, message):
    lx.eval('dialog.setup {%s}' % type)
    lx.eval('dialog.title {%s}' % title)
    lx.eval('dialog.msg {%s}' % message)
    lx.eval('dialog.open')


def set_bool_arg(arg_arr, index, arg_name, init_value):
    if arg_arr[index] == arg_name:
        if arg_arr[index + 1] != '0' and arg_arr[index + 1] != '1':
            init_message('error', arg_name, 'Illegal ' + arg_name + ' = ' + arg_arr[index + 1] + ' argument value')
            sys.exit()
        else:
            if arg_arr[index + 1] == '0':
                return False
            if arg_arr[index + 1] == '1':
                return True
    else:
        return init_value


def set_float_arg(arg_arr, index, arg_name, init_value):
    if arg_arr[index] == arg_name:
        return arg_arr[index + 1]
    else:
        return init_value


def set_axis_arg(arg_arr, index, arg_name, init_value):
    if arg_arr[index] == arg_name:
        if arg_arr[index + 1] != 'X' and arg_arr[index + 1] != 'Y' and arg_arr[index + 1] != 'Z':
            init_message('error', arg_name, 'Illegal ' + arg_name + ' = ' + arg_arr[index + 1] + ' argument value')
            sys.exit()
        else:
            return arg_arr[index + 1]
    else:
        return init_value


def get_user_value(value_name, default_value):
    if not lx.eval("query scriptsysservice userValue.isDefined ? {%s}" % ('tilaBExp.' + value_name)):
        return default_value
    else:
        return lx.eval("user.value {%s} ?" % ('tilaBExp.' + str(value_name)))


def init_arg():
    global triple_sw
    global resetPos_sw
    global resetRot_sw
    global resetSca_sw
    global resetShe_sw

    global freezePos_sw
    global freezeRot_sw
    global freezeSca_sw
    global freezeShe_sw

    global freezeGeo_sw

    global posX
    global posY
    global posZ

    global rotX
    global rotY
    global rotZ

    global scaX
    global scaY
    global scaZ

    global smoothAngle_sw
    global smoothAngle

    global hardenUvBorder_sw
    global uvMapName

    global exportCageMorph_sw
    global cageMorphMapName

    global exportFormatFbx_sw
    global exportFormatObj_sw
    global exportFormatLxo_sw
    global exportFormatLwo_sw
    global exportFormatAbc_sw
    global exportFormatAbchdf_sw
    global exportFormatDae_sw
    global exportFormatDxf_sw
    global exportFormat3dm_sw
    global exportFormatGeo_sw

    global exportFile_sw
    global exportEach_sw
    global exportHierarchy_sw
    global scanFiles_sw

    global openDestFolder_sw

    global upAxis

    triple_sw = get_user_value('triple_sw', False)

    resetPos_sw = get_user_value('resetPos_sw', False)
    resetRot_sw = get_user_value('resetRot_sw', False)
    resetSca_sw = get_user_value('resetSca_sw', False)
    resetShe_sw = get_user_value('resetShe_sw', False)

    freezePos_sw = get_user_value('freezePos_sw', False)
    freezeRot_sw = get_user_value('freezeRot_sw', False)
    freezeSca_sw = get_user_value('freezeSca_sw', False)
    freezeShe_sw = get_user_value('freezeShe_sw', False)

    freezeGeo_sw = get_user_value('freezeGeo_sw', False)

    posX = get_user_value('posX', 0)
    posY = get_user_value('posY', 0)
    posZ = get_user_value('posZ', 0)

    rotX = get_user_value('rotX', 0)
    rotY = get_user_value('rotY', 0)
    rotZ = get_user_value('rotZ', 0)

    scaX = get_user_value('scaX', 1)
    scaY = get_user_value('scaY', 1)
    scaZ = get_user_value('scaZ', 1)

    smoothAngle_sw = get_user_value('smoothAngle_sw', False)
    smoothAngle = get_user_value('smoothAngle', 180)

    hardenUvBorder_sw = get_user_value('hardenUvBorder_sw', False)
    uvMapName = get_user_value('uvMapName', 'Texture')

    exportCageMorph_sw = get_user_value('exportCageMorph_sw', False)
    cageMorphMapName = get_user_value('cageMorphMapName', 'cage')

    exportFormat3dm_sw = get_user_value('exportFormat3dm_sw', False)
    exportFormatGeo_sw = get_user_value('exportFormatGeo_sw', False)
    exportFormatAbc_sw = get_user_value('exportFormatAbc_sw', False)
    exportFormatAbchdf_sw = get_user_value('exportFormatAbchdf_sw', False)
    exportFormatDae_sw = get_user_value('exportFormatDae_sw', False)
    exportFormatDxf_sw = get_user_value('exportFormatDxf_sw', False)
    exportFormatObj_sw = get_user_value('exportFormatObj_sw', False)
    exportFormatLwo_sw = get_user_value('exportFormatLwo_sw', False)
    exportFormatLxo_sw = get_user_value('exportFormatLxo_sw', False)
    exportFormatFbx_sw = get_user_value('exportFormatFbx_sw', True)

    exportEach_sw = get_user_value('exportEach_sw', True)

    openDestFolder_sw = get_user_value('openDestFolder_sw', True)

    args = lx.args()
    argCount = len(args)

    for a in xrange(0, argCount - 1):
        if a % 2 == 0:
            exportFile_sw = set_bool_arg(args, a, 'exportFile_sw', exportFile_sw)
            exportHierarchy_sw = set_bool_arg(args, a, 'exportHierarchy_sw', exportHierarchy_sw)
            scanFiles_sw = set_bool_arg(args, a, 'scanFiles_sw', scanFiles_sw)


def flow():

    global sceneIndex
    global userSelection
    global userSelectionCount

    init_arg()

    if not exportFile_sw:
        if userSelectionCount == 0:
            init_message('error', 'No item selected', 'Select at least one item')
            sys.exit()

        for item in userSelection:
            transform_selected(item)

    elif not scanFiles_sw:  # export selected mesh in the scene
        if userSelectionCount == 0:
            init_message('error', 'No item selected', 'Select at least one item')
            sys.exit()

        if exportEach_sw:
            init_dialog("output")
        else:
            init_dialog("file_save")

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            init_dialog('cancel')
        else:
            output_dir = lx.eval1('dialog.result ?')
            batch_export(output_dir)

    else:  # browse file to process
        init_dialog("input")
        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            init_dialog('cancel')
        else:
            files = lx.evalN('dialog.result ?')
            init_dialog("output")
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                init_dialog('cancel')
            else:
                output_dir = lx.eval1('dialog.result ?')

                for f in files:
                    processing_log('.....................................   '
                     + os.path.basename(f) + '   .....................................')

                    name = os.path.basename(f)
                    # ext = os.path.splitext(name)[1]
                    # name = os.path.splitext(name)[0]

                    # lx.eval('loaderOptions.wf_OBJ false false Meters')
                    lx.eval('!scene.open "%s" normal' % f)

                    # if ext == 'fbx'
                    lx.eval('select.itemType mesh')

                    sceneIndex = lx.eval('query sceneservice scene.index ? current')
                    userSelection = lx.evalN('query layerservice layer.id ? fg')
                    userSelectionCount = len(userSelection)

                    print_log('.....................................   ' + str(userSelectionCount) + ' mesh item founded   .....................................'
                                    )

                    batch_export(output_dir)
                    lx.eval('!scene.close')

    init_message('info', 'Done', 'Operation completed successfully !')

    if exportFile_sw:
        if openDestFolder_sw:
            if scanFiles_sw:
                open_folder(output_dir)
            if exportEach_sw:
                open_folder(output_dir)
            else:
                open_folder(os.path.split(output_dir)[0])


def batch_export(output_dir):
    init_arg()

    if upAxis != lx.eval('pref.value units.upAxis ?'):
        lx.eval('pref.value units.upAxis %s' % upAxis)

    if exportHierarchy_sw:
        lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelectionWithHierarchy')
    else:
        lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelection')

    # Grab the IDs of each foreground layer.
    layers = userSelection

    if exportEach_sw:  # Export each layer separately.

        for layer in layers:
            export_loop(output_dir, layer)
            clean_scene()

    else:  # Export all selected layers in one file.
        export_loop(output_dir, layers)
        clean_scene()


def duplicate_rename(layer_name):
    if exportEach_sw:
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
    if exportEach_sw:
        return lx.eval1('query layerservice layer.name ? %s' % layer)
    else:
        return os.path.splitext(lx.eval1('query sceneservice scene.name ? current'))[0]


def set_name(layer_name):
    if exportEach_sw:
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
    if exportEach_sw:
        lx.eval('select.item {%s} set' % (layer_name + '_1'))
    else:
        get_user_selection()
        for l in xrange(0, userSelectionCount):
            new_layer_name = lx.eval('query layerservice layer.name ? %s' % userSelection[l])
            if l == 0:
                lx.eval('select.item {%s} set' % (new_layer_name + '_' + str(l)))
            else:
                lx.eval('select.item {%s} add' % (new_layer_name + '_' + str(l)))
    if exportHierarchy_sw == '1':
        lx.eval('select.itemHierarchy')


def get_user_selection():
    for l in xrange(0, userSelectionCount):
        if l == 0:
            lx.eval('select.subItem {%s} set mesh' % userSelection[l])
        else:
            lx.eval('select.subItem {%s} add mesh' % userSelection[l])


def export_selection(output_path, layer_name, export_format):
    processing_log('.....................................   '
                   +
                   layer_name + '   .....................................')

    lx.eval('scene.new')
    newScene = lx.eval('query sceneservice scene.index ? current')
    lx.eval('select.itemType mesh')
    lx.eval('!!item.delete')
    lx.eval('scene.set %s' % sceneIndex)
    select_duplicate(layer_name)
    lx.eval('!layer.import %s {} true true false position:0' % newScene)
    lx.eval('scene.set %s' % newScene)
    set_name(layer_name)

    lx.eval('!scene.saveAs "%s" "%s" false' % (output_path[0], export_format))

    Export_log(os.path.basename(output_path[0]))

    if exportCageMorph_sw:
        export_cage(output_path[1], export_format)

    lx.eval('scene.close')


def export_cage(output_path, export_format):
    # Smooth the mesh entirely
    lx.eval('edgesmooth.soften connected:true')
    # Apply Cage Morph map
    lx.eval('vertMap.applyMorph %s 1.0' % cageMorphMapName)
    lx.eval('!scene.saveAs "%s" "%s" false' % (output_path, export_format))
    Export_log(os.path.basename(output_path))


def construct_file_path(output_dir, layer_name, ext):
    if scanFiles_sw:
        if exportEach_sw:
            sceneName = os.path.splitext(lx.eval1('query sceneservice scene.name ? current'))[0]
            return [os.path.join(output_dir, sceneName + '_-_' + layer_name + '.' + ext),
                    os.path.join(output_dir, sceneName + '_-_' + layer_name
                                 + '_cage.' + ext)]
        else:
            return [os.path.join(output_dir, layer_name + '.' + ext),
                    os.path.join(output_dir, layer_name + '_cage.' + ext)]
    else:
        if exportEach_sw:
            return [os.path.join(output_dir, layer_name + '.' + ext), os.path.join(output_dir, layer_name + '_cage.' + ext)]
        else:
            splited_path = os.path.splitext(output_dir)
            return [output_dir, splited_path[0] + '_cage' + splited_path[1]]


def export_loop(output_dir, layer):
    # Get the layer name.
    layer_name = get_name(layer)

    if exportEach_sw:
        # Select only the mesh item.
        lx.eval('select.subItem %s set mesh' % layer)
    else:
        get_user_selection()

    transform_selected(layer_name)

    export_all_format(output_dir, layer_name)


def export_all_format(output_dir, layer_name):
    if exportFormatFbx_sw:
        output_path = construct_file_path(output_dir, layer_name, 'fbx')
        export_selection(output_path, layer_name, 'fbx')

    if exportFormatLxo_sw:
        output_path = construct_file_path(output_dir, layer_name, 'lxo')
        export_selection(output_path, layer_name, '$LXOB')

    if exportFormatLwo_sw:
        output_path = construct_file_path(output_dir, layer_name, 'lwo')
        export_selection(output_path, layer_name, '$NLWO2')

    if exportFormatObj_sw:
        output_path = construct_file_path(output_dir, layer_name, 'obj')
        export_selection(output_path, layer_name, 'wf_OBJ')

    if exportFormatDxf_sw:
        output_path = construct_file_path(output_dir, layer_name, 'dxf')
        export_selection(output_path, layer_name, 'DXF')

    if exportFormatDae_sw:
        output_path = construct_file_path(output_dir, layer_name, 'dae')
        export_selection(output_path, layer_name, 'COLLADA_141')

    if exportFormat3dm_sw:
        output_path = construct_file_path(output_dir, layer_name, '3dm')
        export_selection(output_path, layer_name, 'THREEDM')

    if exportFormatAbc_sw:
        output_path = construct_file_path(output_dir, layer_name, 'abc')
        export_selection(output_path, layer_name, 'Alembic')

    if exportFormatAbchdf_sw:
        output_path = construct_file_path(output_dir, layer_name, 'abc')
        export_selection(output_path, layer_name, 'AlembicHDF')

    if exportFormatGeo_sw:
        output_path = construct_file_path(output_dir, layer_name, 'geo')
        export_selection(output_path, layer_name, 'vs_GEO')

    lx.eval('scene.set %s' % sceneIndex)
    select_duplicate(layer_name)

    lx.eval('!!item.delete')


def export_hierarchy():
    if exportHierarchy_sw:
        lx.eval('select.itemHierarchy')


def transform_selected(layer_name):
    export_hierarchy()

    if exportFile_sw:
        duplicate_rename(layer_name)

    smooth_angle(smoothAngle)
    harden_uv_border(uvMapName)
    freeze_geo()
    triple()
    reset_pos()
    position_offset(posX, posY, posZ)

    scale_amount(scaX, scaY, scaZ)

    rot_angle(rotX, rotY, rotZ)
    freeze_rot()
    freeze_sca()
    freeze_pos()

    freeze_she()


def smooth_angle(smoothAngle):
    if smoothAngle_sw:
        processing_log("CalculateNormal with %s degrees smoothing" % smoothAngle)
        lx.eval('edgesmooth.harden {%s}' % smoothAngle)
        lx.eval('edgesmooth.update')


def harden_uv_border(uvMapName):
    if hardenUvBorder_sw:
        processing_log("HardenUvBorder = " + uvMapName)
        lx.eval('select.vertexMap {%s} txuv replace' % uvMapName)
        lx.eval('uv.selectBorder')
        lx.eval('edgesmooth.harden uv')
        lx.eval('edgesmooth.update')
        lx.eval('select.type item')


def triple():
    if triple_sw:
        processing_log("Triangulate")
        lx.eval('poly.triple')


def reset_pos():
    if resetPos_sw:
        transform_log("Reset Position")
        lx.eval('transform.reset translation')


def reset_rot():
    if resetRot_sw:
        transform_log("Reset Rotation")
        lx.eval('transform.reset rotation')


def reset_sca():
    if resetSca_sw:
        transform_log("Reset Scale")
        lx.eval('transform.reset scale')


def reset_she():
    if resetShe_sw:
        transform_log("Reset Shear")
        lx.eval('transform.reset shear')


def freeze_pos():
    if freezePos_sw:
        transform_log("Freeze Position")
        lx.eval('transform.freeze translation')


def freeze_rot():
    if freezeRot_sw:
        transform_log("Freeze Rotation")
        lx.eval('transform.freeze rotation')


def freeze_sca():
    if freezeSca_sw:
        transform_log("Freeze Scale")
        lx.eval('transform.freeze scale')


def freeze_she():
    if freezeShe_sw:
        transform_log("Freeze Shear")
        lx.eval('transform.freeze shear')


def freeze_geo():
    if freezeGeo_sw:
        transform_log("Freeze Geometry")
        lx.eval('poly.freeze twoPoints false 2 true true true true 5.0 false Morph')


def position_offset(posX, posY, posZ):
    if posX != 0.0 or posY != 0.0 or posZ != 0.0:
        transform_log("Position offset = (%s, %s, %s)" % (posX, posY, posZ))

        currPosition = currScn.selected[0].position

        lx.eval('transform.channel pos.X %s' % str(float(posX) + currPosition.x.get()))
        lx.eval('transform.channel pos.Y %s' % str(float(posY) + currPosition.y.get()))
        lx.eval('transform.channel pos.Z %s' % str(float(posZ) + currPosition.z.get()))


def scale_amount(scaX, scaY, scaZ):
    if scaX != 1.0 or scaY != 1.0 or scaZ != 1.0:
        transform_log("Scale amount = (%s, %s, %s)" % (scaX, scaY, scaZ))

        currScale = currScn.selected[0].scale

        freeze_sca()
        lx.eval('transform.channel scl.X %s' % str(float(scaX) * currScale.x.get()))
        lx.eval('transform.channel scl.Y %s' % str(float(scaY) * currScale.y.get()))
        lx.eval('transform.channel scl.Z %s' % str(float(scaZ) * currScale.z.get()))


def rot_angle(rotX, rotY, rotZ):
    if rotX != 0.0 or rotY != 0.0 or rotZ != 0.0:
        transform_log("Rotation Angle = (%s, %s, %s)" % (rotX, rotY, rotZ))

        currRotation = currScn.selected[0].rotation
        lx.eval('transform.freeze rotation')
        lx.eval('transform.channel rot.X "%s"' % str(float(rotX) + currRotation.x.get()))
        lx.eval('transform.channel rot.Y "%s"' % str(float(rotY) + currRotation.y.get()))
        lx.eval('transform.channel rot.Z "%s"' % str(float(rotZ) + currRotation.z.get()))
        freeze_rot()
        #lx.eval('edgesmooth.update')


def clean_scene():
    get_user_selection()

    # Put the user's original FBX Export setting back.
    lx.eval('user.value sceneio.fbx.save.exportType %s' % fbx_export_setting)

    if upAxis != iUpAxis:
        lx.eval('pref.value units.upAxis %s' % iUpAxis)


def print_log(message):
    lx.out("TILA_BATCH_EXPORT : " + message)


def print_debug_log(message):
    if debug_log:
        print_log('Debug : ' + message)


def transform_log(message):
    print_log("Transform_Item : " + message)


def processing_log(message):
    print_log("Processing_Item : " + message)


def debug(message):
    if debug_mode:
        print_debug_log(message)


def Export_log(message):
    print_log("Exporting_File : " + message)


flow()
