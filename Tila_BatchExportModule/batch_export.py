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

        index = 0
        self.exportVisible_sw = bool(userValues[index])
        index += 1
        self.exportFile_sw = bool(userValues[index])
        index += 1
        self.scanFiles_sw = bool(userValues[index])
        index += 1
        self.exportEach_sw = bool(userValues[index])
        index += 1
        self.exportHierarchy_sw = bool(userValues[index])
        index += 1

        self.triple_sw = bool(userValues[index])
        index += 1
        self.mergeMesh_sw = bool(userValues[index])
        index += 1
        self.askBeforeOverride_sw = bool(userValues[index])
        index += 1

        self.resetPos_sw = bool(userValues[index])
        index += 1
        self.resetRot_sw = bool(userValues[index])
        index += 1
        self.resetSca_sw = bool(userValues[index])
        index += 1
        self.resetShe_sw = bool(userValues[index])
        index += 1

        self.freezePos_sw = bool(userValues[index])
        index += 1
        self.freezeRot_sw = bool(userValues[index])
        index += 1
        self.freezeSca_sw = bool(userValues[index])
        index += 1
        self.freezeShe_sw = bool(userValues[index])
        index += 1

        self.freezeGeo_sw = bool(userValues[index])
        index += 1
        self.freezeInstance_sw = bool(userValues[index])
        index += 1

        self.pos_sw = userValues[index]
        index += 1
        self.posX = userValues[index]
        index += 1
        self.posY = userValues[index]
        index += 1
        self.posZ = userValues[index]
        index += 1

        self.rot_sw = userValues[index]
        index += 1
        self.rotX = userValues[index]
        index += 1
        self.rotY = userValues[index]
        index += 1
        self.rotZ = userValues[index]
        index += 1

        self.sca_sw = userValues[index]
        index += 1
        self.scaX = userValues[index]
        index += 1
        self.scaY = userValues[index]
        index += 1
        self.scaZ = userValues[index]
        index += 1

        self.smoothAngle_sw = bool(userValues[index])
        index += 1
        self.smoothAngle = userValues[index]
        index += 1

        self.hardenUvBorder_sw = bool(userValues[index])
        index += 1
        self.uvMapName = userValues[index]
        index += 1

        self.exportCageMorph_sw = bool(userValues[index])
        index += 1
        self.cageMorphMapName = userValues[index]
        index += 1

        self.applyMorphMap_sw = bool(userValues[index])
        index += 1
        self.morphMapName = userValues[index]
        index += 1

        self.openDestFolder_sw = bool(userValues[index])
        index += 1

        self.exportFormatLxo_sw = bool(userValues[index])
        index += 1
        self.exportFormatLwo_sw = bool(userValues[index])
        index += 1
        self.exportFormatFbx_sw = bool(userValues[index])
        index += 1
        self.exportFormatObj_sw = bool(userValues[index])
        index += 1
        self.exportFormatAbc_sw = bool(userValues[index])
        index += 1
        self.exportFormatAbchdf_sw = bool(userValues[index])
        index += 1
        self.exportFormatDae_sw = bool(userValues[index])
        index += 1
        self.exportFormatDxf_sw = bool(userValues[index])
        index += 1
        self.exportFormat3dm_sw = bool(userValues[index])
        index += 1
        self.exportFormatGeo_sw = bool(userValues[index])
        index += 1
        self.exportFormatStl_sw = bool(userValues[index])
        index += 1
        self.exportFormatX3d_sw = bool(userValues[index])
        index += 1
        self.exportFormatSvg_sw = bool(userValues[index])
        index += 1
        self.exportFormatPlt_sw = bool(userValues[index])

        self.meshItemToProceed = []
        self.meshInstToProceed = []
        self.meshFusionToProceed = []
        self.meshReplToProceed = []
        self.sortedOriginalItems = []
        self.proceededMesh = []
        self.proceededMeshIndex = 0
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

    def at_least_one_item_selected(self, exit=True):
        helper.items_to_proceed_constructor(self)
        if len(self.meshItemToProceed + self.meshInstToProceed + self.meshReplToProceed + self.meshFusionToProceed) == 0:
            if exit:
                dialog.init_message('info', 'No mesh item selected', 'Select at least one mesh item')
                sys.exit()
            else:
                return True

    # Loops methods

    def batch_export(self):
        helper.check_selection_count(self)
        self.at_least_one_item_selected()

        dialog.begining_log(self)

        self.currPath = file.getLatestPath(t.config_export_path)

        dialog.init_dialog("output", self.currPath)

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            dialog.init_dialog('cancel', self.currPath)
        else:
            output_dir = lx.eval1('dialog.result ?')
            file.updateExportPath(output_dir, '', '')
            self.batch_process(output_dir, os.path.splitext(self.scn.name))

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

                    lx.eval('select.itemType %s mode:add' % t.itemType['MESH'])
                    lx.eval('select.itemType %s mode:add' % t.itemType['MESH_INSTANCE'])
                    lx.eval('select.itemType %s mode:add' % t.itemType['REPLICATOR'])

                    self.userSelection = self.scn.selected
                    self.userSelectionCount = len(self.userSelection)

                    dialog.print_log('.....................................   ' + str(
                        self.userSelectionCount) + ' mesh item founded   .....................................')

                    if self.at_least_one_item_selected(exit=False):
                        lx.eval('!scene.close')
                        continue

                    self.batch_process(output_dir, os.path.splitext(os.path.basename(f))[0])

                    self.meshItemToProceed = []
                    self.meshInstToProceed = []
                    self.meshFusionToProceed = []
                    self.meshReplToProceed = []
                    self.sortedOriginalItems = []
                    self.proceededMesh = []
                    self.proceededMeshIndex = 0
                    self.overrideFiles = ''
                    self.progress = None
                    self.progression = [0, 0]
                    self.tempScnID = None

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

    def batch_process(self, output_dir, filename):
        helper.select_hierarchy(self)

        self.transform_loop()

        self.progress = dialog.init_progress_bar(len(self.proceededMesh), 'Exporting ...')
        self.progression[1] = len(self.proceededMesh)
        self.progression[0] = 0

        helper.set_name(self.sortedOriginalItems, suffix=t.TILA_BACKUP_SUFFIX)

        if self.exportEach_sw:
            for i in xrange(0, len(self.proceededMesh)):
                item_arr = []
                item_arr.append(self.proceededMesh[i])
                self.proceededMeshIndex = i

                dialog.increment_progress_bar(self, self.progress[0], self.progression)

                self.export_all_format(output_dir, item_arr, self.proceededMesh[i].name[:-len(t.TILA_DUPLICATE_SUFFIX)])
        else:
            self.export_all_format(output_dir, self.proceededMesh, filename)

        helper.set_name(self.sortedOriginalItems, shrink=len(t.TILA_BACKUP_SUFFIX))

        self.progress = None
        helper.revert_scene_preferences(self)

    def transform_loop(self):

        instances = self.transform_type(self.meshInstToProceed, t.itemType['MESH_INSTANCE'])

        fusion = self.transform_type(self.meshFusionToProceed, t.itemType['MESH_FUSION'])

        replicator = self.transform_type(self.meshReplToProceed, t.itemType['REPLICATOR'])

        meshes = self.transform_type(self.meshItemToProceed, t.itemType['MESH'])

        if self.mergeMesh_sw:
            transformed = meshes + instances + fusion + replicator

            item_processing.merge_meshes(self, transformed)
            self.proceededMesh = [self.scn.selected[0]]
            self.proceededMesh[0].name = os.path.splitext(self.scn.name)[0]

    def transform_type(self, type_item_arr, type):
        item_arr = []
        if len(type_item_arr) > 0:
            self.scn.select(type_item_arr)
            self.transform_selected(type=type)
            item_arr = self.scn.selected

        return item_arr

    def transform_selected(self, type):
        helper.select_hierarchy(self)

        self.progression = [1, helper.get_transformation_count(self)]

        self.progress = dialog.init_progress_bar(self.progression[1], 'Processing item(s) ...')

        first_index = 0

        if self.exportFile_sw:
            if type == t.itemType['MESH']:
                first_index = helper.duplicate_rename(self, self.meshItemToProceed, t.TILA_DUPLICATE_SUFFIX)
            if type == t.itemType['MESH_INSTANCE']:
                first_index = helper.duplicate_rename(self, self.meshInstToProceed, t.TILA_DUPLICATE_SUFFIX)
            if type == t.itemType['MESH_FUSION']:
                first_index = helper.duplicate_rename(self, self.meshFusionToProceed, t.TILA_DUPLICATE_SUFFIX)
            if type == t.itemType['REPLICATOR']:
                first_index = helper.duplicate_rename(self, self.meshReplToProceed, t.TILA_DUPLICATE_SUFFIX)

        item_processing.freeze_instance(self, type=type, first_index=first_index)
        item_processing.freeze_replicator(self, type=type, first_index=first_index)

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

    def export_all_format(self, output_dir, duplicate, layer_name):

        self.scn.select(duplicate)
        helper.set_name(duplicate, shrink=len(t.TILA_DUPLICATE_SUFFIX))

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
        mesh = self.scn.items(t.itemType['MESH'])
        meshInstance = self.scn.items(t.itemType['MESH_INSTANCE'])
        meshFusion = self.scn.items(t.itemType['MESH_FUSION'])
        meshReplicator = self.scn.items(t.itemType['REPLICATOR'])

        compatible = mesh + meshInstance + meshFusion + meshReplicator

        visible = []

        for item in compatible:
            visible_channel = item.channel('visible').get()
            if visible_channel == 'default' or visible_channel == 'on':
                visible.append(item)

        self.scn.select(visible)
        return visible

    @staticmethod
    def file_conflict(path):
        return os.path.isfile(path)
