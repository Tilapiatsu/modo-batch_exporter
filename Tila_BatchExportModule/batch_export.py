import modo
import lx
import os
import sys
import Tila_BatchExportModule as t
import dialog
import item_processing
import helper
from Tila_BatchExportModule import file

############## TODO ###################
'''
 - Add a preset saver/loader : Save a .cfg file that contain all the settings of the kit for better reusability
 - Try to export more Item Types : camera, light, replicator, rig etc... ( cf compatibleItemType in __init__.py )
 - check export for procedural geometry and fusion item
 - polycount limit to avoid crash : select the first 1 M polys and transform them then select the next 1 M Poly etc ...
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )
 - Add a rename auto_rename Template when exporting multiple objects : <objectName>_<sceneName>_####_low.<ext>
'''

class TilaBacthExport:
    def __init__(self,
                 userSelection,
                 userSelectionCount,
                 scn,
                 currScn,
                 currPath,
                 scnIndex,
                 userValues):

        reload(dialog)
        reload(item_processing)
        reload(helper)
        reload(file)
        self.userSelection = userSelection
        self.userSelectionCount = userSelectionCount
        self.scn = scn
        self.currScn = currScn
        self.currPath = currPath
        self.scnIndex = scnIndex

        self.exportVisible_sw = bool(userValues[0])
        self.exportFile_sw = bool(userValues[1])
        self.scanFiles_sw = bool(userValues[2])
        self.exportEach_sw = bool(userValues[3])
        self.exportHierarchy_sw = bool(userValues[4])

        self.triple_sw = bool(userValues[5])
        self.mergeMesh_sw = bool(userValues[6])
        self.askBeforeOverride_sw = bool(userValues[7])
        self.udimPerMaterialSet_sw = bool(userValues[8])

        self.resetPos_sw = bool(userValues[9])
        self.resetRot_sw = bool(userValues[10])
        self.resetSca_sw = bool(userValues[11])
        self.resetShe_sw = bool(userValues[12])

        self.freezePos_sw = bool(userValues[13])
        self.freezeRot_sw = bool(userValues[14])
        self.freezeSca_sw = bool(userValues[15])
        self.freezeShe_sw = bool(userValues[16])

        self.freezeGeo_sw = bool(userValues[17])
        self.freezeInstance_sw = bool(userValues[18])

        self.pos_sw = userValues[19]
        self.posX = userValues[20]
        self.posY = userValues[21]
        self.posZ = userValues[22]

        self.rot_sw = userValues[23]
        self.rotX = userValues[24]
        self.rotY = userValues[25]
        self.rotZ = userValues[26]

        self.sca_sw = userValues[27]
        self.scaX = userValues[28]
        self.scaY = userValues[29]
        self.scaZ = userValues[30]

        self.smoothAngle_sw = bool(userValues[31])
        self.smoothAngle = userValues[32]

        self.hardenUvBorder_sw = bool(userValues[33])
        self.uvMapName = userValues[34]

        self.exportCageMorph_sw = bool(userValues[35])
        self.cageMorphMapName = userValues[36]

        self.applyMorphMap_sw = bool(userValues[37])
        self.morphMapName = userValues[38]

        self.openDestFolder_sw = bool(userValues[39])

        self.exportFormatLxo_sw = bool(userValues[40])
        self.exportFormatLwo_sw = bool(userValues[41])
        self.exportFormatFbx_sw = bool(userValues[42])
        self.exportFormatObj_sw = bool(userValues[43])
        self.exportFormatAbc_sw = bool(userValues[44])
        self.exportFormatAbchdf_sw = bool(userValues[45])
        self.exportFormatDae_sw = bool(userValues[46])
        self.exportFormatDxf_sw = bool(userValues[47])
        self.exportFormat3dm_sw = bool(userValues[48])
        self.exportFormatGeo_sw = bool(userValues[49])
        self.exportFormatStl_sw = bool(userValues[50])
        self.exportFormatX3d_sw = bool(userValues[51])
        self.exportFormatSvg_sw = bool(userValues[52])
        self.exportFormatPlt_sw = bool(userValues[53])

        self.meshItemToProceed = []
        self.meshInstToProceed = []
        self.sortedOriginalItems = []
        self.proceededMesh = []
        self.proceededMeshIndex = 0
        self.processingItemType = t.processingItemType
        self.overrideFiles = ''
        self.progress = None
        self.progression = [0, 0]
        self.tempScnID = None

        t.get_default_settings(self)

    def export_at_least_one_format(self):
        if not (self.exportFormatFbx_sw
                or self.exportFormatObj_sw
                or self.exportFormatLxo_sw
                or self.exportFormatLwo_sw
                or self.exportFormatAbc_sw
                or self.exportFormatAbchdf_sw
                or self.exportFormatDae_sw
                or self.exportFormatDxf_sw
                or self.exportFormat3dm_sw
                or self.exportFormatGeo_sw
                or self.exportFormatStl_sw
                or self.exportFormatX3d_sw
                or self.exportFormatSvg_sw
                or self.exportFormatPlt_sw):
            dialog.init_message('info', 'No export format selected', 'Select at least one export fromat in the form')
            sys.exit()

    def at_least_one_item_selected(self):
        helper.items_to_proceed_constructor(self)
        if len(self.meshItemToProceed) == 0 and len(self.meshInstToProceed) == 0:
            dialog.init_message('info', 'No mesh item selected', 'Select at least one mesh item')
            sys.exit()

    # Loops methods

    def batch_export(self):
        helper.check_selection_count(self)
        self.at_least_one_item_selected()

        dialog.begining_log(self)

        if self.exportEach_sw:
            self.currPath = file.getLatestPath(t.config_export_path)
            dialog.init_dialog("output", self.currPath)
        else:
            self.currPath = file.getLatestPath(t.config_export_path)
            dialog.init_dialog("file_save", self.currPath)

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            dialog.init_dialog('cancel', self.currPath)
        else:
            output_dir = lx.eval1('dialog.result ?')
            file.updateExportPath(output_dir, '', '')
            self.batch_process(output_dir)

        helper.open_destination_folder(self, output_dir)
        dialog.ending_log(self)

    def batch_folder(self):
        self.currPath = file.getLatestPath(t.config_browse_src_path)
        dialog.init_dialog("input", self.currPath)

        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            dialog.init_dialog('cancel', self.currPath)
        else:
            files = lx.evalN('dialog.result ?')
            file.updateExportPath('', os.path.split(files[0])[0], '')
            self.currPath = file.getLatestPath(t.config_browse_dest_path)
            dialog.init_dialog("output", self.currPath)
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                dialog.init_dialog('cancel', self.currPath)
            else:
                output_dir = lx.eval1('dialog.result ?')
                file.updateExportPath('', '', output_dir)

                for f in files:
                    dialog.processing_log('.....................................   ' + os.path.basename(
                        f) + '   .....................................')

                    lx.eval('!scene.open "%s" normal' % f)

                    # if ext == 'fbx'
                    lx.eval('select.itemType mesh')

                    self.userSelection = self.scn.selected
                    self.userSelectionCount = len(self.userSelection)

                    dialog.print_log('.....................................   ' + str(
                        self.userSelectionCount) + ' mesh item founded   .....................................')

                    self.batch_process(output_dir)
                    lx.eval('!scene.close')

        dialog.init_message('info', 'Done', 'Operation completed successfully !')

        helper.open_destination_folder(self, output_dir)

        dialog.ending_log(self)

    def batch_transform(self):
        helper.check_selection_count(self)
        self.at_least_one_item_selected()
        dialog.begining_log(self)

        self.transform_loop()
        self.scn.select(self.proceededMesh)
        dialog.ending_log(self)

    def batch_process(self, output_dir):
        self.select_hierarchy()

        self.transform_loop()

        self.progress = dialog.init_progress_bar(len(self.proceededMesh), 'Exporting ...')
        self.progression[1] = len(self.proceededMesh)
        self.progression[0] = 0

        if self.exportEach_sw:
            for i in xrange(0, len(self.proceededMesh)):
                item_arr = []
                item_arr.append(self.proceededMesh[i])
                self.proceededMeshIndex = i

                dialog.increment_progress_bar(self, self.progress[0], self.progression)

                self.export_all_format(output_dir, item_arr, self.proceededMesh[i].name[:-2], i)
        else:
            self.export_all_format(output_dir, self.proceededMesh, self.scn.name)

        self.progress = None
        helper.revert_scene_preferences(self)

    def transform_loop(self):

        instances = []
        if len(self.meshInstToProceed) > 0:
            self.scn.select(self.meshInstToProceed)
            self.transform_selected(type=self.processingItemType.MESHINST)
            instances = self.scn.selected

        meshes = []
        if len(self.meshItemToProceed) > 0:
            self.scn.select(self.meshItemToProceed)
            self.transform_selected(type=self.processingItemType.MESHITEM)
            meshes = self.scn.selected

        if self.mergeMesh_sw:
            for i in instances:
                meshes.append(i)

            item_processing.merge_meshes(self, meshes)
            self.proceededMesh = [self.scn.selected[0]]
            self.proceededMesh[0].name = os.path.split(self.currPath)[1][:-2]

    def transform_selected(self, type):
        self.select_hierarchy()

        self.progression = [1, helper.get_transformation_count(self)]

        self.progress = dialog.init_progress_bar(self.progression[1], 'Processing item(s) ...')

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

        dialog.deallocate_dialog_svc(self.progress[1])
        self.progress = None


    def export_all_format(self, output_dir, duplicate, layer_name, index=0):
        originalItem = []

        if self.exportEach_sw:
            originalItem.append(self.sortedOriginalItems[index])
        else:
            originalItem = self.sortedOriginalItems

        helper.set_name(self, originalItem, shrink=False, add=True, layer_name='_0')
        self.scn.select(duplicate)
        helper.set_name(self, duplicate, shrink=True, add=True)

        if self.exportFormatLxo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[0][0])
            self.export_selection(duplicate, output_path, t.exportTypes[0][1])

        if self.exportFormatLwo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[1][0])
            self.export_selection(duplicate, output_path, t.exportTypes[1][1])

        if self.exportFormatFbx_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[2][0])
            lx.eval('user.value sceneio.fbx.save.exportType FBXExportAll')
            lx.eval('user.value sceneio.fbx.save.surfaceRefining subDivs')
            lx.eval('user.value sceneio.fbx.save.format FBXLATEST')
            self.export_selection(duplicate, output_path, t.exportTypes[2][1])

        if self.exportFormatObj_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[3][0])
            self.export_selection(duplicate, output_path, t.exportTypes[3][1])

        if self.exportFormatAbc_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[4][0])
            self.export_selection(duplicate, output_path, t.exportTypes[4][1])

        if self.exportFormatAbchdf_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[5][0])
            self.export_selection(duplicate, output_path, t.exportTypes[5][1])

        if self.exportFormatDae_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[6][0])
            self.export_selection(duplicate, output_path, t.exportTypes[6][1])

        if self.exportFormatDxf_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[7][0])
            self.export_selection(duplicate, output_path, t.exportTypes[7][1])

        if self.exportFormat3dm_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[8][0])
            self.export_selection(duplicate, output_path, t.exportTypes[8][1])

        if self.exportFormatGeo_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[9][0])
            self.export_selection(duplicate, output_path, t.exportTypes[9][1])

        if self.exportFormatStl_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[10][0])
            self.export_selection(duplicate, output_path, t.exportTypes[10][1])

        if self.exportFormatX3d_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[11][0])
            self.export_selection(duplicate, output_path, t.exportTypes[11][1])

        if self.exportFormatSvg_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[12][0])
            self.export_selection(duplicate, output_path, t.exportTypes[12][1])

        if self.exportFormatPlt_sw:
            output_path = helper.construct_file_path(self, output_dir, layer_name, t.exportTypes[13][0])
            self.export_selection(duplicate, output_path, t.exportTypes[13][1])

        self.scn.select(duplicate)

        lx.eval('!!item.delete')

        helper.set_name(self, originalItem, shrink=True, add=True)

    def export_selection(self, item, output_path, export_format):
        lx.eval("scene.new")
        self.tempScnID = lx.eval('query sceneservice scene.index ? current')

        self.scn.select('Mesh')
        lx.eval('!!item.delete')

        lx.eval('scene.set %s' % self.scnIndex)
        self.scn.select(item)

        lx.eval('!!layer.import %s {} true true move:false position:0' % self.tempScnID)

        lx.eval('scene.set %s' % self.tempScnID)

        self.scn.select('Camera')
        lx.eval('!!item.delete')

        self.scn.select('Directional Light')
        lx.eval('!!item.delete')

        self.save_file(output_path[0], export_format)

        if self.exportCageMorph_sw:
            self.export_cage(output_path[1], export_format)

        lx.eval('!!scene.close')
        lx.eval('scene.set %s' % self.scnIndex)

    def export_cage(self, output_path, export_format):
        # Smooth the mesh entirely
        lx.eval('vertMap.softenNormals connected:true')

        # Apply Cage Morph map
        item_processing.apply_morph(self, True, self.cageMorphMapName)

        self.save_file(output_path, export_format)

    def select_hierarchy(self):
        if self.exportHierarchy_sw:
            lx.eval('select.itemHierarchy')

    def save_file(self, output_path, export_format):
        if self.file_conflict(output_path) and self.askBeforeOverride_sw:
            if self.overrideFiles != 'yesToAll' and self.overrideFiles != 'noToAll':
                self.overrideFiles = dialog.ask_before_override(os.path.split(output_path)[1])
                if self.overrideFiles == 'cancel':
                    helper.clean_duplicates(self, closeScene=True)

            if self.overrideFiles == 'ok' or self.overrideFiles == 'yesToAll':
                self.save_command(output_path, export_format)
        else:
            self.save_command(output_path, export_format)

    def save_command(self, output_path, export_format):
        try:
            lx.eval('!scene.saveAs "%s" %s true' % (output_path, export_format))
            message = helper.get_progression_message(self, os.path.basename(output_path))
            dialog.export_log(message)

        except RuntimeError:
            helper.clean_duplicates(self, closeScene=True)

    def select_visible_items(self):
        mesh = self.scn.items('mesh')
        meshInst = self.scn.items('meshInst')

        visible = []

        for item in meshInst:
            mesh.append(item)

        for item in mesh:
            visible_channel = item.channel('visible').get()
            if visible_channel == 'default' or visible_channel == 'on':
                visible.append(item)

        self.scn.select(visible)
        return visible

    @staticmethod
    def file_conflict(path):
        return os.path.isfile(path)
