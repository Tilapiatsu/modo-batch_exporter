#!/usr/bin/env python

import modo
import sys
import os
import subprocess
import lx
import lxifc
import lxu.command
import lxu.select
import traceback


############## TODO ###################
'''
 - find a way to keep last output folder in memory
 - ReWrite with Modo TDSDK
 - Refactoring everything ?
 - Create a class ?
 - extract some methods to other files ( Freeze Transform, Position Offset etc... )
 - Create a progress bar https://gist.github.com/tcrowson/e3d401055739d1a72863
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )
 - Add export Visible Feature

'''
'''
scn = modo.Scene()
currScn = modo.scene.current()

currentPath = modo.Scene.filename
if currentPath is None:
    currentPath = ""

fbx_export_setting = lx.eval1('user.value sceneio.fbx.save.exportType ?')

sceneIndex = lx.eval('query sceneservice scene.index ? current')

userSelection = scn.selected
userSelectionCount = len(userSelection)

upAxis = lx.eval('pref.value units.upAxis ?')
iUpAxis = upAxis
'''


class TilaBacthExport:
    currentPath = modo.Scene.filename

    def __init__(self, userSelection, userSelectionCount, scn, currScn, currPath, scnIndex, upAxis, iUpAxis, fbxExportSetting, exportFile_sw, scanFiles_sw, exportEach_sw, exportHierarchy_sw, triple_sw, resetPos_sw, resetRot_sw, resetSca_sw, resetShe_sw, freezePos_sw, freezeRot_sw, freezeSca_sw, freezeShe_sw, freezeGeo_sw, freezeInstance_sw, posX, posY, posZ, rotX, rotY, rotZ, scaX, scaY, scaZ, smoothAngle_sw, smoothAngle, hardenUvBorder_sw, uvMapName, exportFormatFbx_sw, exportFormatObj_sw, exportFormatLxo_sw, exportFormatLwo_sw, exportFormatAbc_sw, exportFormatAbchdf_sw, exportFormatDae_sw, exportFormatDxf_sw, exportFormat3dm_sw, exportFormatGeo_sw, exportCageMorph_sw, cageMorphMapName, openDestFolder_sw):

        self.userSelection = userSelection
        self.userSelectionCount = userSelectionCount
        self.scn = scn
        self.currScn = currScn
        self.currPath = currPath
        self.scnIndex = scnIndex
        self.upAxis = upAxis
        self.iUpAxis = iUpAxis
        self.fbxExportSetting = fbxExportSetting

        self.exportFile_sw = exportFile_sw
        self.scanFiles_sw = scanFiles_sw
        self.exportEach_sw = exportEach_sw
        self.exportHierarchy_sw = exportHierarchy_sw

        self.triple_sw = triple_sw

        self.resetPos_sw = resetPos_sw
        self.resetRot_sw = resetRot_sw
        self.resetSca_sw = resetSca_sw
        self.resetShe_sw = resetShe_sw

        self.freezePos_sw = freezePos_sw
        self.freezeRot_sw = freezeRot_sw
        self.freezeSca_sw = freezeSca_sw
        self.freezeShe_sw = freezeShe_sw

        self.freezeGeo_sw = freezeGeo_sw
        self.freezeInstance_sw = freezeInstance_sw

        self.posX = posX
        self.posY = posY
        self.posZ = posZ

        self.rotX = rotX
        self.rotY = rotY
        self.rotZ = rotZ

        self.scaX = scaX
        self.scaY = scaY
        self.scaZ = scaZ

        self.smoothAngle_sw = smoothAngle_sw
        self.smoothAngle = smoothAngle

        self.hardenUvBorder_sw = hardenUvBorder_sw
        self.uvMapName = uvMapName

        self.exportFormatFbx_sw = exportFormatFbx_sw
        self.exportFormatObj_sw = exportFormatObj_sw
        self.exportFormatLxo_sw = exportFormatLxo_sw
        self.exportFormatLwo_sw = exportFormatLwo_sw
        self.exportFormatAbc_sw = exportFormatAbc_sw
        self.exportFormatAbchdf_sw = exportFormatAbchdf_sw
        self.exportFormatDae_sw = exportFormatDae_sw
        self.exportFormatDxf_sw = exportFormatDxf_sw
        self.exportFormat3dm_sw = exportFormat3dm_sw
        self.exportFormatGeo_sw = exportFormatGeo_sw

        self.exportCageMorph_sw = exportCageMorph_sw
        self.cageMorphMapName = cageMorphMapName

        self.openDestFolder_sw = openDestFolder_sw

    if sys.platform == 'darwin':
        @staticmethod
        def open_folder(path):
            subprocess.check_call(['open', '--', path])

    elif sys.platform == 'linux2':
        @staticmethod
        def open_folder(path):
            subprocess.check_call(['xdg-open', '--', path])

    elif sys.platform == 'win32':
        @staticmethod
        def open_folder(path):
            os.startfile(path)

    @staticmethod
    def print_log(message):
        lx.out("TILA_BATCH_EXPORT : " + message)

    @staticmethod
    def transform_log(message):
        TilaBacthExport.print_log("Transform_Item : " + message)

    @staticmethod
    def processing_log(message):
        TilaBacthExport.print_log("Processing_Item : " + message)

    @staticmethod
    def export_log(message):
        TilaBacthExport.print_log("Exporting_File : " + message)

    def init_dialog(self, dialog_type):
        if dialog_type == "input":
            # Get the directory to export to.
            lx.eval('dialog.setup fileOpenMulti')
            lx.eval('dialog.fileType scene')
            lx.eval('dialog.title "Mesh Path"')
            lx.eval('dialog.msg "Select the meshes you want to process."')
            lx.eval('dialog.result "%s"' % self.currPath)

        if dialog_type == "output":
            # Get the directory to export to.
            lx.eval('dialog.setup dir')
            lx.eval('dialog.title "Export Path"')
            lx.eval('dialog.msg "Select path to export to."')
            lx.eval('dialog.result "%s"' % self.currPath)

        if dialog_type == 'file_save':
            self.init_custom_dialog('fileSave', 'SaveFile', ('FBX',), 'FBX file', ('*.FBX',), 'fbx', self.currPath[:-4])

        if dialog_type == "cancel":
            self.init_message('error', 'Canceled', 'Operation aborded')
            sys.exit()

    # http://modo.sdk.thefoundry.co.uk/wiki/Dialog_Commands
    @staticmethod
    def init_custom_dialog(type, title, format, uname, ext, save_ext=None, path=None, init_dialog=False):
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

    @staticmethod
    def init_message(type, title, message):
        lx.eval('dialog.setup {%s}' % type)
        lx.eval('dialog.title {%s}' % title)
        lx.eval('dialog.msg {%s}' % message)
        lx.eval('dialog.open')

    def process_item(self):
        if not self.exportFile_sw:  # Transform Selected
            if self.userSelectionCount == 0:  # No file Selected
                self.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            for item in self.userSelection:
                self.scn.select(item)
                self.transform_selected()
            self.get_user_selection()

        elif not self.scanFiles_sw:  # export selected mesh
            if self.userSelectionCount == 0:  # No file Selected
                self.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            if self.exportEach_sw:
                self.init_dialog("output")
            else:
                self.init_dialog("file_save")

            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                self.init_dialog('cancel')
            else:
                output_dir = lx.eval1('dialog.result ?')
                self.batch_export(output_dir)

        else:  # browse file to process
            self.init_dialog("input")
            try:  # mesh to process dialog
                lx.eval('dialog.open')
            except:
                self.init_dialog('cancel')
            else:
                files = lx.evalN('dialog.result ?')
                self.init_dialog("output")
                try:  # output folder dialog
                    lx.eval('dialog.open')
                except:
                    self.init_dialog('cancel')
                else:
                    output_dir = lx.eval1('dialog.result ?')

                    for f in files:
                        self.processing_log('.....................................   ' + os.path.basename(f) + '   .....................................')

                        lx.eval('!scene.open "%s" normal' % f)

                        # if ext == 'fbx'
                        lx.eval('select.itemType mesh')

                        scnIndex = lx.eval('query sceneservice scene.index ? current')
                        self.userSelection = self.scn.selected
                        self.userSelectionCount = len(self.userSelection)

                        self.print_log('.....................................   ' + str(self.userSelectionCount) + ' mesh item founded   .....................................')

                        self.batch_export(output_dir)
                        lx.eval('!scene.close')

                self.init_message('info', 'Done', 'Operation completed successfully !')

        if self.exportFile_sw:
            if self.openDestFolder_sw:
                if self.scanFiles_sw:
                    self.open_folder(output_dir)
                if self.exportEach_sw:
                    self.open_folder(output_dir)
                else:
                    self.open_folder(os.path.split(output_dir)[0])

    def batch_export(self, output_dir):
        if self.upAxis != lx.eval('pref.value units.upAxis ?'):
            lx.eval('pref.value units.upAxis %s' % self.upAxis)

        if self.exportHierarchy_sw:
            lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelectionWithHierarchy')
        else:
            lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelection')

        if self.exportEach_sw:  # Export each layer separately.

            for layer in self.userSelection:
                self.export_loop(output_dir, layer)
                self.clean_scene()

        else:  # Export all selected layers in one file.
            self.export_loop(output_dir, self.userSelection)
            self.clean_scene()

    def duplicate_rename(self):
        if self.exportEach_sw:
            duplicate = self.scn.duplicateItem(self.scn.selected)
            duplicate.name = '%s_1' % self.scn.selected[0].name
        else:
            for item in self.userSelection:
                layer_name = item.name
                duplicate = self.scn.duplicateItem(item)
                duplicate.name = '%s_1' % layer_name
            self.select_duplicate(layer_name)

    def select_duplicate(self, layer_name):
        if self.exportEach_sw:
            self.scn.select(layer_name + '_1')
        else:
            self.get_user_selection()
            for i in xrange(0, self.userSelectionCount):
                new_layer_name = self.userSelection[i].name
                if i == 0:
                    self.scn.select(new_layer_name + '_1')
                else:
                    self.scn.select(new_layer_name + '_1', add=True)

        if self.exportHierarchy_sw:
            lx.eval('select.itemHierarchy')

    def get_user_selection(self):
        for i in xrange(0, self.userSelectionCount):
            if i == 0:
                self.scn.select(self.userSelection[i])
            else:
                self.scn.select(self.userSelection[i], add=True)

    def get_name(self):
        if self.exportEach_sw:
            return self.scn.selected[0].name
        else:
            return self.scn.name

    def set_name(self, layer_name):
        if self.exportEach_sw:
            self.scn.selected.name = layer_name

        else:
            lx.eval('select.itemType mesh')
            duplicate = self.scn.selected
            for l in duplicate:
                self.scn.select(l)
                current_name = l.name
                current_name = current_name[:-2]
                l.name = current_name
            lx.eval('select.itemType mesh')

    def export_selection(self, output_path, layer_name, export_format):
        self.processing_log('.....................................   '
                       +
                       layer_name + '   .....................................')

        lx.eval('scene.new')
        newScene = lx.eval('query sceneservice scene.index ? current')
        lx.eval('select.itemType mesh')
        self.scn.removeItems(self.scn.selected)
        lx.eval('scene.set %s' % self.scnIndex)
        self.select_duplicate(layer_name)
        lx.eval('!layer.import %s {} true true false position:0' % newScene)
        lx.eval('scene.set %s' % newScene)
        self.set_name(layer_name)

        lx.eval('!scene.saveAs "%s" "%s" false' % (output_path[0], export_format))

        self.export_log(os.path.basename(output_path[0]))

        if self.exportCageMorph_sw:
            self.export_cage(output_path[1], export_format)

        lx.eval('scene.close')

    def export_cage(self, output_path, export_format):
        # Smooth the mesh entirely
        lx.eval('vertMap.softenNormals connected:true')
        # Apply Cage Morph map
        lx.eval('vertMap.applyMorph %s 1.0' % self.cageMorphMapName)
        lx.eval('!scene.saveAs "%s" "%s" false' % (output_path, export_format))
        self.export_log(os.path.basename(output_path))

    def construct_file_path(self, output_dir, layer_name, ext):


        if self.scanFiles_sw:
            if self.exportEach_sw:
                sceneName = self.scn.name
                return [os.path.join(output_dir, sceneName + '_-_' + layer_name + '.' + ext),
                        os.path.join(output_dir, sceneName + '_-_' + layer_name
                                     + '_cage.' + ext)]
            else:
                return [os.path.join(output_dir, layer_name + '.' + ext),
                        os.path.join(output_dir, layer_name + '_cage.' + ext)]
        else:
            if self.exportEach_sw:
                return [os.path.join(output_dir, layer_name + '.' + ext),
                        os.path.join(output_dir, layer_name + '_cage.' + ext)]
            else:
                splited_path = os.path.splitext(output_dir)
                return [output_dir, splited_path[0] + '_cage' + splited_path[1]]

    def export_loop(self, output_dir, layer):
        # Get the layer name.
        layer_name = self.get_name()

        if self.exportEach_sw:
            # Select only the mesh item.
            lx.eval('select.subItem %s set mesh' % layer)
        else:
            self.get_user_selection()

        self.transform_selected()

        self.export_all_format(output_dir, layer_name)

    def export_all_format(self, output_dir, layer_name):
        if self.exportFormatFbx_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'fbx')
            self.export_selection(output_path, layer_name, 'fbx')

        if self.exportFormatLxo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'lxo')
            self.export_selection(output_path, layer_name, '$LXOB')

        if self.exportFormatLwo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'lwo')
            self.export_selection(output_path, layer_name, '$NLWO2')

        if self.exportFormatObj_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'obj')
            self.export_selection(output_path, layer_name, 'wf_OBJ')

        if self.exportFormatDxf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'dxf')
            self.export_selection(output_path, layer_name, 'DXF')

        if self.exportFormatDae_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'dae')
            self.export_selection(output_path, layer_name, 'COLLADA_141')

        if self.exportFormat3dm_sw:
            output_path = self.construct_file_path(output_dir, layer_name, '3dm')
            self.export_selection(output_path, layer_name, 'THREEDM')

        if self.exportFormatAbc_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'abc')
            self.export_selection(output_path, layer_name, 'Alembic')

        if self.exportFormatAbchdf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'abc')
            self.export_selection(output_path, layer_name, 'AlembicHDF')

        if self.exportFormatGeo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, 'geo')
            self.export_selection(output_path, layer_name, 'vs_GEO')

        lx.eval('scene.set %s' % self.scnIndex)
        self.select_duplicate(layer_name)

        lx.eval('!!item.delete')

    def export_hierarchy(self):
        if self.exportHierarchy_sw:
            lx.eval('select.itemHierarchy')

    def transform_selected(self):
        self.export_hierarchy()

        if self.exportFile_sw:
            self.duplicate_rename()

        self.freeze_instance()
        self.smooth_angle()
        self.harden_uv_border()
        self.freeze_geo()
        self.triple()
        self.reset_pos()
        self.reset_rot()
        self.reset_sca()
        self.reset_she()
        self.position_offset()

        self.scale_amount()

        self.rot_angle()
        self.freeze_rot()
        self.freeze_sca()
        self.freeze_pos()

        self.freeze_she()

    def smooth_angle(self):
        if self.smoothAngle_sw:
            self.processing_log("CalculateNormal with %s degrees smoothing" % self.smoothAngle)
            lx.eval('vertMap.hardenNormals {%s}' % self.smoothAngle)
            lx.eval('vertMap.updateNormals')

    def harden_uv_border(self):
        if self.hardenUvBorder_sw:
            self.processing_log("HardenUvBorder = " + self.uvMapName)
            lx.eval('select.vertexMap {%s} txuv replace' % self.uvMapName)
            lx.eval('uv.selectBorder')
            lx.eval('vertMap.hardenNormals uv')
            lx.eval('vertMap.updateNormals')
            lx.eval('select.type item')

    def triple(self):
        if self.triple_sw:
            self.processing_log("Triangulate")
            lx.eval('poly.triple')

    def reset_pos(self):
        if self.resetPos_sw:
            self.transform_log("Reset Position")
            lx.eval('transform.reset translation')

    def reset_rot(self):
        if self.resetRot_sw:
            self.transform_log("Reset Rotation")
            lx.eval('transform.reset rotation')

    def reset_sca(self):
        if self.resetSca_sw:
            self.transform_log("Reset Scale")
            lx.eval('transform.reset scale')

    def reset_she(self):
        if self.resetShe_sw:
            self.transform_log("Reset Shear")
            lx.eval('transform.reset shear')

    def freeze_pos(self):
        if self.freezePos_sw:
            self.transform_log("Freeze Position")
            lx.eval('transform.freeze translation')

    def freeze_rot(self):
        if self.freezeRot_sw:
            self.transform_log("Freeze Rotation")
            lx.eval('transform.freeze rotation')

    def freeze_sca(self):
        if self.freezeSca_sw:
            self.transform_log("Freeze Scale")
            lx.eval('transform.freeze scale')

    def freeze_she(self):
        if self.freezeShe_sw:
            self.transform_log("Freeze Shear")
            lx.eval('transform.freeze shear')

    def freeze_geo(self):
        if self.freezeGeo_sw:
            self.transform_log("Freeze Geometry")
            lx.eval('poly.freeze twoPoints false 2 true true true true 5.0 false Morph')

    def freeze_instance(self):
        if self.freezeInstance_sw:
            if self.scn.selected[0].type == 'meshInst':
                self.transform_log("Freeze Instance")
                lx.eval('item.setType Mesh')

    def position_offset(self):
        if self.posX != 0.0 or self.posY != 0.0 or self.posZ != 0.0:
            self.transform_log("Position offset = (%s, %s, %s)" % (self.posX, self.posY, self.posZ))

            currPosition = self.scn.selected[0].position

            lx.eval('transform.channel pos.X %s' % str(float(self.posX) + currPosition.x.get()))
            lx.eval('transform.channel pos.Y %s' % str(float(self.posY) + currPosition.y.get()))
            lx.eval('transform.channel pos.Z %s' % str(float(self.posZ) + currPosition.z.get()))

    def scale_amount(self):
        if self.scaX != 1.0 or self.scaY != 1.0 or self.scaZ != 1.0:
            self.transform_log("Scale amount = (%s, %s, %s)" % (self.scaX, self.scaY, self.scaZ))

            currScale = self.scn.selected[0].scale

            self.freeze_sca()
            lx.eval('transform.channel scl.X %s' % str(float(self.scaX) * currScale.x.get()))
            lx.eval('transform.channel scl.Y %s' % str(float(self.scaY) * currScale.y.get()))
            lx.eval('transform.channel scl.Z %s' % str(float(self.scaZ) * currScale.z.get()))

    def rot_angle(self):
        if self.rotX != 0.0 or self.rotY != 0.0 or self.rotZ != 0.0:
            self.transform_log("Rotation Angle = (%s, %s, %s)" % (self.rotX, self.rotY, self.rotZ))

            currRotation = self.scn.selected[0].rotation
            lx.eval('transform.freeze rotation')
            lx.eval('transform.channel rot.X "%s"' % str(float(self.rotX) + currRotation.x.get()))
            lx.eval('transform.channel rot.Y "%s"' % str(float(self.rotY) + currRotation.y.get()))
            lx.eval('transform.channel rot.Z "%s"' % str(float(self.rotZ) + currRotation.z.get()))
            self.freeze_rot()

    def clean_scene(self):
        self.get_user_selection()

        # Put the user's original FBX Export setting back.
        lx.eval('user.value sceneio.fbx.save.exportType %s' % self.fbxExportSetting)

        if self.upAxis != self.iUpAxis:
            lx.eval('pref.value units.upAxis %s' % self.iUpAxis)


class CmdBatchExport(lxu.command.BasicCommand):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('exportFile_sw', lx.symbol.sTYPE_BOOLEAN)
        self.dyna_Add('scanFiles_sw', lx.symbol.sTYPE_BOOLEAN)

        self.dyna_Add('exportEach_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(2, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportHierarchy_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(3, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('triple_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(4, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetPos_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(5, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetRot_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(6, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetSca_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(7, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('resetShe_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(8, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezePos_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(9, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeRot_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(10, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeSca_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(11, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeShe_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(12, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeGeo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(13, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('freezeInstance_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(14, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(15, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(16, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('posZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(17, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(18, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(19, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('rotZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(20, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaX', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(21, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaY', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(22, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('scaZ', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(23, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('smoothAngle_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(24, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('smoothAngle', lx.symbol.sTYPE_FLOAT)
        self.basic_SetFlags(25, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('hardenUvBorder_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(26, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('uvMapName', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(27, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatFbx_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(28, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatObj_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(29, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatLxo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(30, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatLwo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(31, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatAbc_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(32, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatAbchdf_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(33, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatDae_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(34, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatDxf_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(35, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormat3dm_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(36, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportFormatGeo_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(37, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('exportCageMorph_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(38, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('cageMorphMapName', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(39, lx.symbol.fCMDARG_OPTIONAL)

        self.dyna_Add('openDestFolder_sw', lx.symbol.sTYPE_BOOLEAN)
        self.basic_SetFlags(40, lx.symbol.fCMDARG_OPTIONAL)

    def query_User_Value(self, index, name):
        if not self.dyna_IsSet(index):
            return lx.eval('user.value tilaBExp.%s ?' % name)

    def query_User_Values(self):
        userValues = []

        for i in xrange(0, self.attr_Count()):
            userValues.append(self.query_User_Value(i, self.attr_Name(i)))

        return userValues

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):
        try:
            scn = modo.Scene()
            currScn = modo.scene.current()

            userSelection = scn.selected
            userSelectionCount = len(userSelection)

            currPath = currScn.filename

            if currPath is None:
                currPath = ""

            fbxExportSetting = lx.eval1('user.value sceneio.fbx.save.exportType ?')

            scnIndex = lx.eval('query sceneservice scene.index ? current')

            upAxis = lx.eval('pref.value units.upAxis ?')
            iUpAxis = upAxis

            userValues = self.query_User_Values()

            tbe = TilaBacthExport

            tbe.process_item(tbe(userSelection, userSelectionCount, scn, currScn, currPath, scnIndex, upAxis, iUpAxis, fbxExportSetting, self.dyna_Bool(0), self.dyna_Bool(1), bool(userValues[2]), bool(userValues[3]), bool(userValues[4]), bool(userValues[5]), bool(userValues[6]), bool(userValues[7]), bool(userValues[8]), bool(userValues[9]), bool(userValues[10]), bool(userValues[11]), bool(userValues[12]), bool(userValues[13]), bool(userValues[14]), userValues[15], userValues[16], userValues[17], userValues[18], userValues[19], userValues[20], userValues[21], userValues[22], userValues[23], bool(userValues[24]), userValues[25], bool(userValues[26]), userValues[27], bool(userValues[28]), bool(userValues[29]), bool(userValues[30]), bool(userValues[31]), bool(userValues[32]), bool(userValues[33]), bool(userValues[34]), bool(userValues[35]), bool(userValues[36]), bool(userValues[37]), bool(userValues[38]), userValues[39], bool(userValues[40])))
        except:
            lx.out(traceback.format_exc())

    def cmd_Query(self, index, vaQuery):
        lx.notimpl()


lx.bless(CmdBatchExport, "tila.batchexport")