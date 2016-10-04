import modo
import lx
import os
import sys
import subprocess
import dialog
import item_processing
import helper

def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)


class TilaBacthExport:
    def __init__(self,
                 userSelection,
                 userSelectionCount,
                 scn,
                 currScn,
                 currPath,
                 scnIndex,
                 upAxis,
                 iUpAxis,
                 fbxExportType,
                 fbxTriangulate,
                 exportFile_sw,
                 scanFiles_sw,
                 exportEach_sw,
                 exportHierarchy_sw,
                 triple_sw,
                 resetPos_sw,
                 resetRot_sw,
                 resetSca_sw,
                 resetShe_sw,
                 freezePos_sw,
                 freezeRot_sw,
                 freezeSca_sw,
                 freezeShe_sw,
                 freezeGeo_sw,
                 freezeInstance_sw,
                 posX,
                 posY,
                 posZ,
                 rotX,
                 rotY,
                 rotZ,
                 scaX,
                 scaY,
                 scaZ,
                 smoothAngle_sw,
                 smoothAngle,
                 hardenUvBorder_sw,
                 uvMapName,
                 exportFormatFbx_sw,
                 exportFormatObj_sw,
                 exportFormatLxo_sw,
                 exportFormatLwo_sw,
                 exportFormatAbc_sw,
                 exportFormatAbchdf_sw,
                 exportFormatDae_sw,
                 exportFormatDxf_sw,
                 exportFormat3dm_sw,
                 exportFormatGeo_sw,
                 exportCageMorph_sw,
                 cageMorphMapName,
                 applyMorphMap_sw,
                 morphMapName,
                 openDestFolder_sw):

        self.userSelection = userSelection
        self.userSelectionCount = userSelectionCount
        self.scn = scn
        self.currScn = currScn
        self.currPath = currPath
        self.scnIndex = scnIndex
        self.upAxis = upAxis
        self.iUpAxis = iUpAxis
        self.fbxExportType = fbxExportType
        self.fbxTriangulate = fbxTriangulate

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

        self.applyMorphMap_sw = applyMorphMap_sw
        self.morphMapName = morphMapName

        self.meshItemToProceed = []
        self.meshInstToProceed = []
        self.sortedOriginalItems = []
        self.proceededMesh = []
        self.processingItemType = enum('MESHITEM', 'MESHINST')

    # Loops methods

    def batch_export(self):
        if self.userSelectionCount == 0:  # No file Selected
            dialog.init_message('error', 'No item selected', 'Select at least one item')
            sys.exit()

        dialog.begining_log(self)

        if self.exportEach_sw:
            dialog.init_dialog("output", self.currPath)
        else:
            dialog.init_dialog("file_save", self.currPath)

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            dialog.init_dialog('cancel', self.currPath)
        else:
            output_dir = lx.eval1('dialog.result ?')
            self.batch_process(output_dir)

        helper.open_destination_folder(self, output_dir)

    def batch_folder(self):
        dialog.init_dialog("input", self.currPath)

        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            dialog.init_dialog('cancel', self.currPath)
        else:
            files = lx.evalN('dialog.result ?')
            dialog.init_dialog("output", self.currPath)
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPath)
            else:
                output_dir = lx.eval1('dialog.result ?')

                for f in files:
                    dialog.processing_log('.....................................   ' + os.path.basename(
                        f) + '   .....................................')

                    lx.eval('!scene.open "%s" normal' % f)

                    # if ext == 'fbx'
                    lx.eval('select.itemType mesh')

                    scnIndex = lx.eval('query sceneservice scene.index ? current')
                    self.userSelection = self.scn.selected
                    self.userSelectionCount = len(self.userSelection)

                    dialog.print_log('.....................................   ' + str(
                        self.userSelectionCount) + ' mesh item founded   .....................................')

                    self.batch_process(output_dir)
                    lx.eval('!scene.close')

                    dialog.init_message('info', 'Done', 'Operation completed successfully !')

        helper.open_destination_folder(self, output_dir)


    def process_items(self):
        dialog.begining_log(self)

        if not self.exportFile_sw:  # Transform Selected
            if self.userSelectionCount == 0:  # No file Selected
                dialog.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            self.transform_loop()
            self.scn.select(self.userSelection)

        elif not self.scanFiles_sw:  # export selected mesh
            if self.userSelectionCount == 0:  # No file Selected
                dialog.init_message('error', 'No item selected', 'Select at least one item')
                sys.exit()

            if self.exportEach_sw:
                dialog.init_dialog("output", self.currPath)
            else:
                dialog.init_dialog("file_save", self.currPath)

            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPath)
            else:
                output_dir = lx.eval1('dialog.result ?')
                self.batch_export(output_dir)

        else:  # browse file to process
            dialog.init_dialog("input", self.currPath)
            try:  # mesh to process dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPath)
            else:
                files = lx.evalN('dialog.result ?')
                dialog.init_dialog("output", self.currPath)
                try:  # output folder dialog
                    lx.eval('dialog.open')
                except:
                    dialog.init_dialog('cancel', self.currPath)
                else:
                    output_dir = lx.eval1('dialog.result ?')

                    for f in files:
                        dialog.processing_log('.....................................   ' + os.path.basename(f) + '   .....................................')

                        lx.eval('!scene.open "%s" normal' % f)

                        # if ext == 'fbx'
                        lx.eval('select.itemType mesh')

                        scnIndex = lx.eval('query sceneservice scene.index ? current')
                        self.userSelection = self.scn.selected
                        self.userSelectionCount = len(self.userSelection)

                        dialog.print_log('.....................................   ' + str(self.userSelectionCount) + ' mesh item founded   .....................................')

                        self.batch_process(output_dir)
                        lx.eval('!scene.close')

                        dialog.init_message('info', 'Done', 'Operation completed successfully !')

        helper.open_destination_folder(self, output_dir)

    def batch_process(self, output_dir):
        if self.upAxis != lx.eval('pref.value units.upAxis ?'):
            lx.eval('pref.value units.upAxis %s' % self.upAxis)

        if self.exportFormatFbx_sw:
            #lx.eval('user.value sceneio.fbx.save.triangulate false')
            if self.exportHierarchy_sw:
                lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelectionWithHierarchy')
            else:
                lx.eval('user.value sceneio.fbx.save.exportType FBXExportSelection')

        self.transform_loop()

        if self.exportEach_sw:
            for i in xrange(0, len(self.proceededMesh)):
                item_arr = []
                item_arr.append(self.proceededMesh[i])
                self.export_all_format(output_dir, item_arr, self.proceededMesh[i].name[:-2], i)
        else:
            self.export_all_format(output_dir, self.proceededMesh, self.scn.name)

        self.clean_scene()

    def transform_loop(self):
        helper.items_to_proceed_constructor(self)

        if len(self.meshInstToProceed) > 0:
            self.scn.select(self.meshInstToProceed)
            self.transform_selected(type=self.processingItemType.MESHINST)

        if len(self.meshItemToProceed) > 0:
            self.scn.select(self.meshItemToProceed)
            self.transform_selected(type=self.processingItemType.MESHITEM)

    def transform_selected(self, type):
        self.export_hierarchy()

        if self.exportFile_sw:
            if type == self.processingItemType.MESHITEM:
                helper.duplicate_rename(self, self.meshItemToProceed, '1')
            if type == self.processingItemType.MESHINST:
                helper.duplicate_rename(self, self.meshInstToProceed, '1')

        item_processing.freeze_instance(self, type=type)

        item_processing.smooth_angle(self)
        item_processing.harden_uv_border(self)

        item_processing.freeze_geo(self)
        item_processing.triple(self)

        item_processing.apply_morph(self, self.applyMorphMap_sw, self.morphMapName)

        item_processing.reset_pos(self)
        item_processing.reset_rot(self)
        item_processing.reset_sca(self)
        item_processing.reset_she(self)

        item_processing.position_offset(self)
        item_processing.scale_amount(self)
        item_processing.rot_angle(self)

        item_processing.freeze_rot(self)
        item_processing.freeze_sca(self)
        item_processing.freeze_pos(self)
        item_processing.freeze_she(self)

    def export_all_format(self, output_dir, duplicate, layer_name, index=0):

        originalItem = []
        if self.exportEach_sw:
            originalItem.append(self.sortedOriginalItems[index])
        else:
            originalItem = self.sortedOriginalItems

        helper.set_name(self, originalItem, shrink=False, add=True, layer_name='_0')
        self.scn.select(duplicate)
        helper.set_name(self, duplicate, shrink=True, add=True)

        if self.exportFormatFbx_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'fbx')
            self.export_selection(output_path, 'fbx')

        if self.exportFormatLxo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'lxo')
            self.export_selection(output_path, '$LXOB')

        if self.exportFormatLwo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'lwo')
            self.export_selection(output_path, '$NLWO2')

        if self.exportFormatObj_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'obj')
            self.export_selection(output_path, 'wf_OBJ')

        if self.exportFormatDxf_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'dxf')
            self.export_selection(output_path, 'DXF')

        if self.exportFormatDae_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'dae')
            self.export_selection(output_path, 'COLLADA_141')

        if self.exportFormat3dm_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, '3dm')
            self.export_selection(output_path, 'THREEDM')

        if self.exportFormatAbc_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'abc')
            self.export_selection(output_path, 'Alembic')

        if self.exportFormatAbchdf_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'abc')
            self.export_selection(output_path, 'AlembicHDF')

        if self.exportFormatGeo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, 'geo')
            self.export_selection(output_path, 'vs_GEO')

        self.scn.select(duplicate)

        lx.eval('!!item.delete')

        helper.set_name(self, originalItem, shrink=True, add=True)

    def export_selection(self, output_path, export_format):
        lx.eval('!scene.saveAs "%s" "%s" true' % (output_path[0], export_format))

        dialog.export_log(os.path.basename(output_path[0]))

        if self.exportCageMorph_sw:
            self.export_cage(output_path[1], export_format)

    def export_cage(self, output_path, export_format):
        # Smooth the mesh entirely
        lx.eval('vertMap.softenNormals connected:true')

        # Apply Cage Morph map
        item_processing.apply_morph(self, True, self.cageMorphMapName)

        lx.eval('!scene.saveAs "%s" "%s" true' % (output_path, export_format))
        dialog.export_log(os.path.basename(output_path))

    def export_hierarchy(self):
        if self.exportHierarchy_sw:
            lx.eval('select.itemHierarchy')


    # Cleaning

    def clean_scene(self):
        self.scn.select(self.userSelection)

        # Put the user's original FBX Export setting back.

        if self.exportFormatFbx_sw:
            lx.eval('user.value sceneio.fbx.save.exportType %s' % self.fbxExportType)
            #lx.eval('user.value sceneio.fbx.save.triangulate %s' % self.fbxTriangulate)

        if self.upAxis != self.iUpAxis:
            lx.eval('pref.value units.upAxis %s' % self.iUpAxis)

