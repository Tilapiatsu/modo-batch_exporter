import lx
import os
import sys
import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper
from Tila_BatchExportModule import item_processing
from Tila_BatchExportModule import modoItem

############## TODO ###################
'''
 - Sometime the XML Tila_Config\tila_batchexport.cfg is corrupded and the file wont export
 - add a checkbox to vertMap.updateNormals at export
 - freezeing meshop isn't correct if more than one item is selected
 - check with witch export format force_freeze_meshop and force_freeze_replicator need to be enabled
 - Expose some settings ( Freeze Geometry, Export/Import settings )
 - Add Mesh Cleanup
 - check export for procedural geometry and fusion item
 - polycount limit to avoid crash : select the first 1 M polys and transform them then select the next 1 M Poly etc ...
 - Implement a log windows to see exactly what's happening behind ( That file is exporting to this location 9 / 26 )
'''

'''
Help doc:
- popup : http://sdk.luxology.com/wiki/Pop-up_List_Choice
- treeview exemple : http://sdk.luxology.com/wiki/Python_Treeview_Example
- Remote Debugging : http://sdk.luxology.com/wiki/Remote_Debugging
	https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#remote-interpreter

	https://code.visualstudio.com/docs/python/debugging#_remote-debugging
faut voir si tu peux installer pip install ptvsd==3.0.0 dans le python de MODO

'''


class TilaBacthExport(helper.ModoHelper):
    exportedFileCount = 0

    def __init__(self, userValues):
        reload(helper)
        reload(item_processing)
        super(TilaBacthExport, self).__init__(userValues)
        self.itemProcessing = item_processing.ItemProcessing(userValues)

    @property
    def transform_condition(self):
        return {"freeze_instance": self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw)),
                "freeze_deformers": self.freezeMeshOp_sw,
                "freeze_replicator": self.freezeReplicator_sw,
                "position_offset": (self.posX != 0.0 or self.posY != 0.0 or self.posZ != 0.0) and self.pos_sw,
                "scale_amount": (self.scaX != 1.0 or self.scaY != 1.0 or self.scaZ != 1.0) and self.sca_sw,
                "rot_angle": (self.rotX != 0.0 or self.rotY != 0.0 or self.rotZ != 0.0) and self.rot_sw,
                "export_morph": not self.exportMorphMap_sw,
                "apply_morph": self.applyMorphMap_sw,
                "smooth_angle": self.smoothAngle_sw,
                "harden_uv_border": self.hardenUvBorder_sw,
                "assign_material_per_udim": self.assignMaterialPerUDIMTile_sw,
                "triple": self.triple_sw,
                "reset_pos": self.resetPos_sw,
                "reset_rot": self.resetRot_sw,
                "reset_sca": self.resetSca_sw,
                "reset_she": self.resetShe_sw,
                "freeze_pos": self.freezePos_sw,
                "freeze_rot": self.freezePos_sw,
                "freeze_sca": self.freezeRot_sw,
                "freeze_she": self.freezeSca_sw,
                "freeze_geo": self.freezeGeo_sw,
                "preFreeze_pos": self.preFreezePos_sw,
                "preFreeze_rot": self.preFreezeRot_sw,
                "preFreeze_sca": self.preFreezeSca_sw,
                "preFreeze_she": self.preFreezeShe_sw}

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
            self.mm.init_message('info', 'No export format selected', 'Select at least one export fromat in the form')
            sys.exit()

    def at_least_one_compatible_item_selected(self, exit=True):
        self.items_to_proceed_constructor()

        totalLength = 0
        for arr in self.itemToProceed.keys():
            totalLength += len(arr)
        if totalLength == 0:
            if exit:
                message = ''
                separator = ' or '
                for i in xrange(len(t.compatibleItemType)):
                    if i < len(t.compatibleItemType) - 1:
                        message += t.compatibleItemType.keys()[i] + separator
                    else:
                        message += t.compatibleItemType.keys()[i]
                self.mm.init_message('info', 'No compatible item selected', 'Select at least one item of this type : \n \n {} '.format(message))
                sys.exit()
            else:
                return True

    # Loops methods

    def batch_export(self):
        # check if at least one item is selected
        self.check_selection_count()
        # check if within this selection, at least one item is compatible with by this script referenced by t.compatibleItemType
        # Construct the queue of item to proceed self.itemToProceed_dict, filtered them and exclude all incompatible types
        self.at_least_one_compatible_item_selected()

        self.mm.begining_log(self.exportFile_sw)

        self.currPath = self.file.getLatestPath(t.config_export_path)

        path = os.path.join(self.currPath, os.path.splitext(self.scn.name)[0])
        self.mm.init_dialog("filesave", path, self.mm.dialogFormatType[self.get_first_export_type()])

        try:  # output folder dialog
            lx.eval('dialog.open')
        except:
            self.mm.init_dialog('cancel', self.currPath)
        else:
            output_dir = lx.eval1('dialog.result ?')

            self.filename = os.path.splitext(os.path.split(output_dir)[1])[0]
            output_dir = os.path.split(output_dir)[0]

            self.file.updateExportPath(output_dir, '', '')

            self.batch_process(output_dir, self.filename)

            self.revert_initial_parameter()

        self.open_destination_folder(output_dir)
        self.mm.ending_log(self.exportFile_sw)

    def batch_files(self):
        self.currPath = self.file.getLatestPath(t.config_browse_src_path)
        self.mm.init_dialog("input", self.currPath)

        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            self.mm.init_dialog('cancel', self.currPath)
        else:
            files = lx.evalN('dialog.result ?')
            self.file.updateExportPath('', os.path.split(files[0])[0], '')
            self.currPath = self.file.getLatestPath(t.config_browse_dest_path)
            self.mm.init_dialog("output", self.currPath)
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                self.mm.init_dialog('cancel', self.currPath)
            else:
                output_dir = lx.eval1('dialog.result ?')
                self.file.updateExportPath('', '', output_dir)

                file_count = len(files)

                self.progress = self.mm.init_progress_bar(file_count, 'Exporting files...')

                self.progression[1] = file_count
                self.progression[0] = 0

                t.set_import_setting()

                for f in files:
                    self.mm.processing_log('.....................................   ' + os.path.basename(f) + '   .....................................')

                    lx.eval('!scene.open "%s" normal' % f)

                    self.scnIndex = lx.eval('query sceneservice scene.index ? current')

                    self.mm.select_compatible_item_type()

                    self.userSelection = self.scn.selected
                    self.userSelectionCount = len(self.userSelection)

                    self.mm.print_log('.....................................   ' + str(self.userSelectionCount) + ' mesh item founded   .....................................')

                    if self.at_least_one_compatible_item_selected(exit=False):
                        lx.eval('!scene.close')
                        continue

                    self.filename = os.path.splitext(os.path.basename(f))[0]

                    self.batch_process(output_dir, self.filename)

                    self.mm.increment_progress_bar(self.progress[0], self.progression)

                    self.revert_initial_parameter()

                    lx.eval('!scene.close')

                self.reset_import_settings()

        self.mm.init_message('info', 'Done', 'Operation completed successfully ! %s file(s) exported' % self.exportedFileCount)

        self.open_destination_folder(output_dir)

        self.mm.ending_log(self.exportFile_sw)

    def batch_folder(self):
        self.currPath = self.file.getLatestPath(t.config_browse_src_path)
        self.mm.init_dialog("input_path", self.currPath)

        try:  # mesh to process dialog
            lx.eval('dialog.open')
        except:
            self.mm.init_dialog('cancel', self.currPath)
        else:
            input_dir = lx.eval1('dialog.result ?')
            self.file.updateExportPath('', input_dir, '')
            self.currPath = self.file.getLatestPath(t.config_browse_dest_path)
            self.mm.init_dialog("output", self.currPath)
            try:  # output folder dialog
                lx.eval('dialog.open')
            except:
                self.mm.init_dialog('cancel', self.currPath)
            else:
                output_dir = lx.eval1('dialog.result ?')
                self.file.updateExportPath('', '', output_dir)

                if not self.processSubfolder_sw:
                    format = self.filter_string(self.formatFilter, t.compatibleImportFormat)
                    files = self.get_files_of_type(input_dir, format)
                    self.mm.info('{} files found'.format(len(files)))
                else:
                    input_subdir = self.get_recursive_subdir([input_dir], self.subfolderDepth)
                    files = []
                    format = self.filter_string(self.formatFilter, t.compatibleImportFormat)
                    for subdir in input_subdir:
                        subfiles = self.get_files_of_type(subdir, format)

                        for f in subfiles:
                            files.append(f)
                    self.mm.info('{} files found'.format(len(files)))

                file_count = len(files)

                self.progress = self.mm.init_progress_bar(file_count, 'Exporting files...')

                self.progression[1] = file_count
                self.progression[0] = 0

                t.set_import_setting()

                for f in files:
                    self.mm.processing_log('.....................................   ' + os.path.basename(
                        f) + '   .....................................')

                    lx.eval('!scene.open "%s" normal' % f)

                    self.scnIndex = lx.eval('query sceneservice scene.index ? current')

                    self.select_compatible_item_type()

                    self.userSelection = self.scn.selected
                    self.userSelectionCount = len(self.userSelection)

                    self.mm.print_log('.....................................   ' + str(
                        self.userSelectionCount) + ' mesh item founded   .....................................')

                    if self.at_least_one_compatible_item_selected(exit=False):
                        lx.eval('!scene.close')
                        continue

                    input_relative_dir_root = os.path.split(f)[0].split(input_dir)[1][1:]
                    output_subdir = os.path.join(output_dir, input_relative_dir_root)

                    self.create_folder_if_necessary(output_subdir)

                    self.filename = os.path.splitext(os.path.basename(f))[0]

                    self.batch_process(output_subdir, self.filename)

                    self.mm.increment_progress_bar(self.progress[0], self.progression)

                    self.revert_initial_parameter()

                    lx.eval('!scene.close')

                self.reset_import_settings()

                # dialog.deallocate_dialog_svc(self.progress[1])

        self.mm.init_message('info', 'Done', 'Operation completed successfully ! %s file(s) exported' % self.exportedFileCount)

        self.open_destination_folder(output_dir)

        self.mm.ending_log(self)

    def batch_transform(self):
        self.check_selection_count()
        self.at_least_one_compatible_item_selected()

        self.proceededMesh = self.itemToProceed
        self.mm.begining_log(self.exportFile_sw)

        self.construct_replicator_dict()

        self.transform_loop()

        self.mm.ending_log(self.exportFile_sw)

    # Loop Processes
    def batch_process(self, output_dir, filename):
        # helper.select_hierarchy(self)

        self.construct_replicator_dict()

        item_count = len(self.sortedItemToProceed)

        self.progress = self.mm.init_progress_bar(item_count, 'Exporting ...')
        self.progression[1] = item_count
        self.progression[0] = 0

        if self.exportEach_sw:
            for tcount in xrange(item_count):
                self.currentlyProcessing = self.sortedItemToProceed[tcount]

                self.tempScnID = self.currentlyProcessing.dstScnID

                self.currentlyProcessing.copy_to_scene(dstScnID=self.tempScnID)

                self.currentlyProcessing = self.currentlyProcessing.create_dstItem()

                self.transform_item()

                self.proceededMeshIndex = tcount
                self.mm.increment_progress_bar(self.proceededMesh, self.progress[0], self.progression)

                self.export_all_format(output_dir, self.currentlyProcessing.name, tcount)

                lx.eval('scene.set {}'.format(self.tempScnID))
                lx.eval('!!scene.close')

                self.scn.deselect()

                self.tempScnID = None
                self.currentlyProcessing = None

        else:  # export all in one file
            self.currentlyProcessing = []
            for item in self.sortedItemToProceed:
                self.set_current_scene(self.scnIndex)

                item.copy_to_scene(dstScnID=self.tempScnID)

                if self.tempScnID is None:
                    self.tempScnID = item.dstScnID

                self.currentlyProcessing.append(item.create_dstItem())

            self.transform_loop()

            self.export_all_format(output_dir, filename)
            self.mm.increment_progress_bar(self, self.progress[0], self.progression)

            lx.eval('scene.set {}'.format(self.tempScnID))
            lx.eval('!!scene.close')
            self.tempScnID = None
            self.currentlyProcessing = None

        # helper.set_name(self.sortedOriginalItems, shrink=len(t.TILA_BACKUP_SUFFIX))

        self.revert_scene_preferences()

    def transform_loop(self):

        transformed = []

        currentlyProcessing_bak = self.currentlyProcessing

        for item in self.currentlyProcessing:
            self.currentlyProcessing = item
            transformed += [self.transform_item()]
            self.currentlyProcessing = currentlyProcessing_bak

        if self.mergeMesh_sw:
            self.mm.breakPoint('Before Merging')
            self.proceededMesh = [self.itemProcessing.merge_meshes(True, transformed)]
            self.currentlyProcessing = self.proceededMesh[0]

            layer_name = self.renamer.construct_filename('', self.filenamePattern, self.filename, '', 0)
            layer_name = os.path.splitext(layer_name)[0]
            self.mm.breakPoint()
            self.proceededMesh[0].name = layer_name

    # Transform Processes

    def transform_item(self):
        self.progression = [1, self.get_transformation_count()]
        self.progress = self.mm.init_progress_bar(self.progression[1], 'Processing item(s) ...')

        self.select_hierarchy()

        self.currentlyProcessing = self.itemProcessing.freeze_instance(self.transform_condition['freeze_instance'], self.currentlyProcessing)
        self.itemProcessing.freeze_replicator(self.transform_condition['freeze_replicator'], self.currentlyProcessing)
        self.itemProcessing.freeze_deformers(self.transform_condition['freeze_deformers'], self.currentlyProcessing)

        self.itemProcessing.smooth_angle(self.transform_condition['smooth_angle'], self.currentlyProcessing, angle=self.smoothAngle)
        self.itemProcessing.harden_uv_border(self.transform_condition['harden_uv_border'], self.currentlyProcessing)

        self.itemProcessing.freeze_geo(self.transform_condition['freeze_geo'], self.currentlyProcessing)
        self.itemProcessing.triple(self.transform_condition['triple'], self.currentlyProcessing)

        self.itemProcessing.assign_material_per_udim(self.transform_condition['assign_material_per_udim'], self.currentlyProcessing)
        self.itemProcessing.apply_morph(self.transform_condition['apply_morph'], self.currentlyProcessing, name=self.morphMapName)
        self.itemProcessing.export_morph(self.transform_condition['export_morph'], self.currentlyProcessing)

        self.itemProcessing.reset_pos(self.transform_condition['reset_pos'], self.currentlyProcessing)
        self.itemProcessing.reset_rot(self.transform_condition['reset_rot'], self.currentlyProcessing)
        self.itemProcessing.reset_sca(self.transform_condition['reset_sca'], self.currentlyProcessing)
        self.itemProcessing.reset_she(self.transform_condition['reset_she'], self.currentlyProcessing)

        self.itemProcessing.freeze_rot(self.transform_condition['preFreeze_rot'], self.currentlyProcessing)
        self.itemProcessing.freeze_sca(self.transform_condition['preFreeze_sca'], self.currentlyProcessing)
        self.itemProcessing.freeze_pos(self.transform_condition['preFreeze_pos'], self.currentlyProcessing)
        self.itemProcessing.freeze_she(self.transform_condition['preFreeze_she'], self.currentlyProcessing)

        self.itemProcessing.position_offset(self.transform_condition['position_offset'], self.currentlyProcessing, offset=(self.posX, self.posY, self.posZ))
        self.itemProcessing.scale_amount(self.transform_condition['scale_amount'], self.currentlyProcessing, amount=(self.scaX, self.scaY, self.scaZ))
        self.itemProcessing.rot_angle(self.transform_condition['rot_angle'], self.currentlyProcessing, angle=(self.rotX, self.rotY, self.rotZ))

        self.itemProcessing.freeze_rot(self.transform_condition['freeze_rot'], self.currentlyProcessing)
        self.itemProcessing.freeze_sca(self.transform_condition['freeze_sca'], self.currentlyProcessing)
        self.itemProcessing.freeze_pos(self.transform_condition['freeze_pos'], self.currentlyProcessing)
        self.itemProcessing.freeze_she(self.transform_condition['freeze_she'], self.currentlyProcessing)

        self.mm.deallocate_dialog_svc(self.progress[1])

        return self.currentlyProcessing

    # Export Processes
    def export_all_format(self, output_dir, layer_name, increment=0):

        if self.exportFormatLxo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[0][0], increment)
            self.export_selection(output_path, t.exportTypes[0][1])

        if self.exportFormatLwo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[1][0], increment)
            self.export_selection(output_path, t.exportTypes[1][1])

        if self.exportFormatFbx_sw:
            # self.itemProcessing.force_freeze_deformers(self.currentlyProcessing)
            # self.itemProcessing.force_freeze_replicator(self.currentlyProcessing)
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[2][0], increment)
            lx.eval('user.value sceneio.fbx.save.exportType FBXExportAll')
            lx.eval('user.value sceneio.fbx.save.surfaceRefining subDivs')
            lx.eval('user.value sceneio.fbx.save.format FBXLATEST')
            self.export_selection(output_path, t.exportTypes[2][1])

        if self.exportFormatObj_sw:
            # self.itemProcessing.force_freeze_replicator(self.currentlyProcessing)
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[3][0], increment)
            self.export_selection(output_path, t.exportTypes[3][1])

        if self.exportFormatAbc_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[4][0], increment)
            self.export_selection(output_path, t.exportTypes[4][1])

        if self.exportFormatAbchdf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[5][0], increment)
            self.export_selection(output_path, t.exportTypes[5][1])

        if self.exportFormatDae_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[6][0], increment)
            self.export_selection(output_path, t.exportTypes[6][1])

        if self.exportFormatDxf_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[7][0], increment)
            self.export_selection(output_path, t.exportTypes[7][1])

        if self.exportFormat3dm_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[8][0], increment)
            self.export_selection(output_path, t.exportTypes[8][1])

        if self.exportFormatGeo_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[9][0], increment)
            self.export_selection(output_path, t.exportTypes[9][1])

        if self.exportFormatStl_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[10][0], increment)
            self.export_selection(output_path, t.exportTypes[10][1])

        if self.exportFormatX3d_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[11][0], increment)
            self.export_selection(output_path, t.exportTypes[11][1])

        if self.exportFormatSvg_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[12][0], increment)
            self.export_selection(output_path, t.exportTypes[12][1])

        if self.exportFormatPlt_sw:
            output_path = self.construct_file_path(output_dir, layer_name, t.exportTypes[13][0], increment)
            self.export_selection(output_path, t.exportTypes[13][1])

        self.select_arr(self.UDIMMaterials)
        # lx.eval('!!item.delete')

    def export_selection(self, output_path, export_format):

        self.save_file(output_path[0], export_format)

        if self.exportCageMorph_sw:
            self.export_cage(output_path[1], export_format)

    def export_cage(self, output_path, export_format):
        # Smooth the mesh entirely
        lx.eval('vertMap.softenNormals connected:true')

        # Apply Cage Morph map
        self.select_compatible_item_type()
        self.itemProcessing.apply_morph(self, True, self.cageMorphMapName)

        self.save_file(output_path, export_format)

    # Saving Methods

    def save_file(self, output_path, export_format):
        if self.file_conflict(output_path) and self.askBeforeOverride_sw:
            if self.overrideFiles != 'yesToAll' and self.overrideFiles != 'noToAll':
                self.overrideFiles = self.mm.ask_before_override(os.path.split(output_path)[1])
                if self.overrideFiles == 'cancel':
                    self.clean_duplicates(self)

            if self.overrideFiles == 'ok' or self.overrideFiles == 'yesToAll':
                self.save_command(output_path, export_format)
        else:
            self.save_command(output_path, export_format)

    def save_command(self, output_path, export_format):
        try:
            # lx.eval('!!tila.exportselected {} {} "{}"'.format(export_format, 'false', output_path))
            lx.eval('!scene.saveAs {%s} %s true' % (output_path, export_format))
            message = self.get_progression_message(os.path.basename(output_path))
            self.mm.export_log(message)
            self.exportedFileCount += 1

        except RuntimeError:
            self.mm.error('Failed to export {}'.format(output_path))
