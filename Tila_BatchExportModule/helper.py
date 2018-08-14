import lx
import modo
import os
from os.path import isfile
import sys
import math
import Tila_BatchExportModule as t
from Tila_BatchExportModule import renamer
from Tila_BatchExportModule import configFile
from Tila_BatchExportModule import modoItem


class ModoHelper(object):
    mm = t.dialog.MessageManagement('ModoHelper')
    renamer = renamer.Renamer()
    file = configFile.ConfigFile()

    scn = None
    cmd_svc = None

    currentlyProcessing = []

    def __init__(self, userValues=None):
        reload(renamer)
        reload(configFile)
        reload(modoItem)
        self.scn = modo.Scene()

        self.cmd_svc = lx.service.Command()
        self.scnName = modo.scene.current().name

        self.userSelection = self.scn.selected
        self.userSelectionCount = len(self.userSelection)

        self.currPath = modo.scene.current().filename
        if self.currPath is None:
            self.currPath = ''

        self.scnIndex = lx.eval('query sceneservice scene.index ? current')
        self.tempScnID = None

        registered = self.registerUserValues(userValues)

        if registered:

            if self.exportEach_sw:
                self.proceededMesh = []
            else:
                self.proceededMesh = self.init_ctype_dict_arr()

            self.itemToProceed = self.init_ctype_dict_arr()

            self.replicatorSrcIgnoreList = ()
            self.replicator_dict = {}
            self.replicator_group_source = {}
            self.replicator_multiple_source = {}
            self.replicator_non_group_source = {}
            self.deformer_item_dict = {}
            self.UDIMMaterials = set([])
            self.proceededMeshIndex = 0
            self.progress = None
            self.progression = [0, 0]
            self.filename = None
            self.firstIndex = self.init_ctype_dict_arr()

            self.overrideFiles = ''

            self.sortedItemToProceed = []

            self.defaultExportSettings = t.defaultExportSettings
            self.defaultImportSettings = t.defaultImportSettings

    def registerUserValues(self, userValues=None):
        if userValues is not None:
            index = 0
            self.exportVisible_sw = bool(userValues[index])
            if self.exportVisible_sw:
                self.userSelection = self.select_visible_items()
            index += 1
            self.exportFile_sw = bool(userValues[index])
            index += 1
            self.scanFiles_sw = bool(userValues[index])
            index += 1
            self.scanFolder_sw = bool(userValues[index])
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

            self.assignMaterialPerUDIMTile_sw = bool(userValues[index])
            index += 1
            self.UDIMTextureName = userValues[index]
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
            self.freezeMeshOp_sw = bool(userValues[index])
            index += 1
            self.freezeReplicator_sw = bool(userValues[index])
            index += 1

            self.pos_sw = bool(userValues[index])
            index += 1
            self.posX = userValues[index]
            index += 1
            self.posY = userValues[index]
            index += 1
            self.posZ = userValues[index]
            index += 1

            self.rot_sw = bool(userValues[index])
            index += 1
            self.rotX = userValues[index]
            index += 1
            self.rotY = userValues[index]
            index += 1
            self.rotZ = userValues[index]
            index += 1

            self.sca_sw = bool(userValues[index])
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

            self.exportMorphMap_sw = bool(userValues[index])
            index += 1
            self.applyMorphMap_sw = bool(userValues[index])
            index += 1
            self.morphMapName = userValues[index]
            index += 1

            self.openDestFolder_sw = bool(userValues[index])
            index += 1

            self.createFormatSubfolder_sw = bool(userValues[index])
            index += 1
            self.processSubfolder_sw = bool(userValues[index])
            index += 1
            self.subfolderDepth = userValues[index]
            index += 1
            self.formatFilter = userValues[index]
            index += 1

            self.filenamePattern = userValues[index]
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

            return True
        else:
            return False

    @staticmethod
    def init_ctype_dict_arr():
        arr = {}
        for type in list(t.compatibleItemType.viewkeys()):
            arr[type] = []

        return arr

    # Path Constructor

    def construct_file_path(self, output_dir, layer_name, ext, increment):
        # sceneName = os.path.splitext(modo.Scene().name)[0]

        if self.createFormatSubfolder_sw:
            output_dir = os.path.join(output_dir, ext)
            self.create_folder_if_necessary(output_dir)

        layer_name = self.renamer.construct_filename(layer_name, self.filenamePattern, self.filename, ext, increment)

        layer_name = os.path.splitext(layer_name)[0]

        return [os.path.join(output_dir, layer_name + '.' + ext),
                os.path.join(output_dir, layer_name + '_cage.' + ext)]

    # Helpers, setter/getter, Selector

    def items_to_proceed_constructor(self):
        for item in self.userSelection:
            mItem = modoItem.convert_to_modoItem(item)
            self.itemToProceed[mItem.typeKey].append(mItem)

        self.sortedItemToProceed = self.sort_items_dict_arr(self.itemToProceed)

    # sort Item per compatible types
    @staticmethod
    def sort_items_dict_arr(dict):
        result_arr = []

        for type in t.compatibleItemType.keys():
            result_arr += dict[type]

        return result_arr

    def construct_proceededMesh(self, arr, ctype):
        for o in arr:
            self.proceededMesh[ctype].append(o)

        return len(self.proceededMesh) - len(arr)

    @staticmethod
    def get_name_arr(arr):
        name_arr = []
        for o in arr:
            name_arr.append(o.name)

        return name_arr

    @staticmethod
    def get_generic_name_dict(arr):
        dict = {}
        for o in arr:
            for k in t.genericNameDict.keys():
                if k in o.name:
                    dict[o.name] = [k, t.genericNameDict[k], o.name.lower()]

        return dict

    def copy_arr_to_temporary_scene(self, arr, ctype=None):
        def replace_generic_name_dict(item, genericName_arr, gen):
            genericName_arr.append([item.name])
            item.name = item.name.replace(gen, t.genericNameDict[gen])
            genericName_arr[-1].append(item.name)

        def replace_generic_deformer_name_dict(item, genericName_arr, gen):
            if len(genericName_arr) == 0:
                genericName_arr.append([])
                genericName_arr.append([])

            genericName_arr[0].append(item.name)
            item.name = item.name.replace(gen, t.genericNameDict[gen])
            genericName_arr[1].append(item.name)

        try:
            srcscene = lx.eval('query sceneservice scene.index ? current')

            if self.exportEach_sw:
                reference_item = ''
                for name in t.genericName:
                    # hack to enable replicator item to be layer.import to the temporary scene
                    if name in arr[0].name:
                        reference_item = arr[0].name.lower()
                else:
                    reference_item = arr[0].name

            original_selection_name_arr = []
            modified_selection_name_arr = []
            genericName_arr = []
            genericDeformerName_dict = {}

            for item in arr:
                # Gather selection Original Names
                original_selection_name_arr.append(item.name)

                # construct deformer_item_dict
                if item.type == t.itemType['MESH_OPERATOR']:
                    self.mm.info('item "{}" have deformers'.format(item.name))
                    self.deformer_item_dict[item.name] = [modoItem.ModoDeformerItem(item)]
                    self.deformer_item_dict[item.name].append(
                        self.deformer_item_dict[item.name][0].deformer_names)

            if self.tempScnID is None:  # Create a new Scene and Store tmpScnID
                self.cmd_svc.ExecuteArgString(-1,
                                              lx.symbol.iCTAG_NULL, 'scene.new')
                self.tempScnID = lx.eval('query sceneservice scene.index ? current')

                for o in arr:
                    if o.type == t.compatibleItemType['REPLICATOR']:
                        if o.name in self.replicator_group_source.keys():
                            if len(modo.Scene().groups) == 0:
                                lx.eval('!group.create "{}" mode:empty'.format(self.replicator_group_source[o.name][0]))
                            elif self.replicator_group_source[o.name][0] not in [grp.name for grp in modo.Scene().groups]:
                                lx.eval('!group.create "{}" mode:empty'.format(self.replicator_group_source[o.name][0]))

                self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.set %s' % srcscene)

            self.scn.select(arr)

            for item in arr:  # Select all item related to the user selection
                # Select Replicator Soucres and Particles
                if item.type == t.compatibleItemType['REPLICATOR']:
                    for o in self.replicator_dict[item.name].source:
                        # add the source to the selection
                        lx.eval('select.item "{}" mode:add'.format(o.name))

                    lx.eval('select.item "{}" mode:add'.format(self.replicator_dict[item.name].particle.name))  # add the particle to the selection

            for item in self.scn.selected:  # Dealing with generic Names
                itemType = item.type
                original_name = item.name

                # Rename Item Generic Name
                for gen in t.genericName:
                    if gen in item.name:
                        if itemType == t.compatibleItemType['REPLICATOR']:
                            replicator = self.replicator_dict[original_name]

                            replace_generic_name_dict(item, genericName_arr, gen)

                            self.replicator_dict.pop(original_name, None)
                            self.replicator_dict[item.name] = replicator
                        elif item.type == t.itemType['MESH_OPERATOR']:
                            deformer = self.deformer_item_dict[original_name][0]

                            replace_generic_name_dict(item, genericName_arr, gen)

                            self.deformer_item_dict.pop(original_name, None)
                            self.deformer_item_dict[item.name] = []
                            self.deformer_item_dict[item.name].append(deformer)
                            self.deformer_item_dict[item.name][0].item_name = item.name
                            self.deformer_item_dict[item.name].append(self.deformer_item_dict[item.name][0].deformer_names)
                        else:
                            replace_generic_name_dict(item, genericName_arr, gen)

                # Rename Deformers Generic Name
                if item.type == t.itemType['MESH_OPERATOR']:
                    genericDeformerName = []
                    for gen in t.genericName:
                        for d in self.deformer_item_dict[item.name][0].deformers:
                            if gen in d.name:
                                replace_generic_deformer_name_dict(d, genericDeformerName, gen)

                    genericDeformerName_dict[item.name] = genericDeformerName

                modified_selection_name_arr.append(item.name)

            # Move all selected items to temporary scene
            self.cmd_svc.ExecuteArgString(
                -1, lx.symbol.iCTAG_NULL,
                '!layer.import {}'.format(self.tempScnID) + ' {} ' + 'childs:{} shaders:true move:false position:0'.format(self.exportHierarchy_sw))

            self.scn = modo.Scene()

            for i in xrange(len(modified_selection_name_arr)):
                curr_item = modified_selection_name_arr[i]
                # Investigate Why the name modo.Item(curr_item) is sometime not found on the new scene ?
                # revert Generic Deformer Name
                if item.type == t.itemType['MESH_OPERATOR']:
                    generic_deformer_name_arr = genericDeformerName_dict[curr_item]
                    for deformer_name in generic_deformer_name_arr[1]:
                        for val in t.genericNameDict.values():
                            if val in deformer_name:
                                old_name = generic_deformer_name_arr[0][generic_deformer_name_arr[1].index(
                                    deformer_name)]
                                deformer_obj = self.deformer_item_dict[curr_item][0]

                                deformer_obj.rename_deformer_by_name(
                                    deformer_name, old_name)

                                # switch to original Scene to revert name
                                lx.eval('scene.set {}'.format(self.scnIndex))

                                deformer_obj = self.deformer_item_dict[curr_item][0]

                                deformer_obj.rename_deformer_by_name(
                                    deformer_name, old_name)

                                lx.eval('scene.set {}'.format(self.tempScnID))

                    curr_name = modified_selection_name_arr[i]
                    self.deformer_item_dict[curr_name][0].reorder_deformers(
                        self.deformer_item_dict[curr_name][1])

                for val in t.genericNameDict.values():  # revert Generic Name
                    if val in modified_selection_name_arr[i]:
                        old_name = modified_selection_name_arr[i]
                        item = modo.Item(old_name)
                        itemType = item.type
                        initial_name = t.get_key_from_value(t.genericNameDict, val)
                        if initial_name is None:
                            continue
                        modified_selection_name_arr[i] = old_name.replace(
                            val, initial_name)
                        item.name = modified_selection_name_arr[i]

                        # switch to original Scene to revert name
                        lx.eval('scene.set {}'.format(self.scnIndex))
                        self.scn = modo.Scene()

                        if itemType == t.compatibleItemType['REPLICATOR']:
                            replicator = self.replicator_dict[old_name]
                            replicator.item_name = old_name
                            replicator.replicator_item.name = modified_selection_name_arr[i]
                            self.replicator_dict.pop(old_name, None)
                            self.replicator_dict[item.name] = replicator
                        elif item.type == t.itemType['MESH_OPERATOR']:
                            deformer_obj = self.deformer_item_dict[old_name]
                            deformer_obj[0].item_name = modified_selection_name_arr[i]
                            deformer_obj[0]._item.name = modified_selection_name_arr[i]
                            self.deformer_item_dict.pop(old_name, None)
                            self.deformer_item_dict[item.name] = deformer_obj
                        else:
                            self.scn.select(item.name.replace(
                                t.get_key_from_value(t.genericNameDict, val), val))
                            lx.eval('!item.name "{}" "{}"'.format(
                                    item.name, itemType))

                        lx.eval('scene.set {}'.format(self.tempScnID))
                        self.scn = modo.Scene()

            replicator_group_source_ignored = {}
            for o in arr:  # Assign Replicator source item to their proper group if needed
                if o.type == t.compatibleItemType['REPLICATOR']:
                    if o.name in self.replicator_group_source.keys():
                        group_name = self.replicator_group_source[o.name][0]
                        self.scn.deselect()
                        lx.eval('select.item "{}" set'.format(self.replicator_group_source[o.name][0]))
                        for source in self.replicator_group_source[o.name][1]:
                            if group_name not in replicator_group_source_ignored.keys():
                                self.scn.select(source.name, add=True)
                                replicator_group_source_ignored[group_name] = [source]
                            else:
                                if source not in replicator_group_source_ignored[group_name]:
                                    self.scn.select(source.name, add=True)
                                    replicator_group_source_ignored[group_name].append(source)

                        if len(self.scn.selected) > 1:
                            lx.eval('!group.edit add item')

                        self.scn.select(o.name)
                        lx.eval('replicator.source {}'.format(self.replicator_group_source[o.name][0]))
            self.scn.deselect()

            # Select items that were imported to the temporary scene
            for i in xrange(len(original_selection_name_arr)):
                if i == 0:
                    lx.eval('select.item {}'.format(
                            original_selection_name_arr[i]))
                else:
                    lx.eval('select.item {} mode:add'.format(
                            original_selection_name_arr[i]))

            if self.exportEach_sw:
                self.proceededMesh.append(modoItem.convert_to_modoItem(self.scn.item(reference_item)))
            else:
                for o in self.scn.selected:
                    self.proceededMesh[ctype].append(modoItem.convert_to_modoItem(o))

            return len(self.proceededMesh) - len(original_selection_name_arr)

        except:
            t.return_exception()

    def duplicate_rename(self, arr, suffix):
        duplicate_arr = []
        for item in arr:
            layer_name = item.name
            if item.type == t.itemType['MESH_FUSION']:
                self.select_hierarchy(force=True)
            if self.exportHierarchy_sw:
                self.scn.select(item)
                lx.eval('item.duplicate false all:true')
                duplicate = self.scn.selected[0]
            else:
                duplicate = self.scn.duplicateItem(item)
            duplicate.name = '%s%s' % (layer_name, suffix)
            duplicate_arr.append(duplicate)
            self.proceededMesh.append(duplicate)

        self.scn.select(duplicate_arr)
        return len(self.proceededMesh) - len(duplicate_arr)

    def get_name(self, layer):
        if self.exportEach_sw:
            return layer.name
        else:
            return self.scn.name

    @staticmethod
    def set_name(arr, shrink=0, suffix=''):
        for item in arr:
            currName = item.name

            if shrink:
                currName = currName[:-shrink]
            currName = '%s%s' % (currName, suffix)

            item.name = currName

    def open_destination_folder(self, output_dir):
        if self.exportFile_sw:
            if self.openDestFolder_sw:
                self.mm.open_folder(output_dir)

    def check_selection_count(self):
        if self.userSelectionCount == 0:  # No file Selected
            if self.exportVisible_sw:
                self.mm.init_message('error', 'No item visible', 'At least one item has to be visible')
            else:
                self.mm.init_message('error', 'No item selected', 'Select at least one item')
            sys.exit()

    @staticmethod
    def getIteratorTemplate(i):
        i = str(i)
        iterator = ''

        if lx.eval('pref.value application.indexStyle ?') == t.indexStyle[0]:
            iterator = ' (' + i + ')'

        elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[1]:
            iterator = '(' + i + ')'

        elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[2]:
            iterator = ' ' + i

        elif lx.eval('pref.value application.indexStyle ?') == t.indexStyle[3]:
            iterator = '_' + i

        return iterator

    def getLatestItemCreated(self, name):
        i = 1
        item = None
        while True:
            try:
                if i == 1:
                    item = modo.Item(name)
                else:
                    item = modo.Item('%s%s' % (name, self.getIteratorTemplate(i)))
                i += 1
            except:
                break

        return item

    def get_transformation_count(self):
        count = 0
        if self.triple_sw:
            count += 1
        if self.resetPos_sw:
            count += 1
        if self.resetRot_sw:
            count += 1
        if self.resetSca_sw:
            count += 1
        if self.resetShe_sw:
            count += 1
        if self.freezePos_sw:
            count += 1
        if self.freezeRot_sw:
            count += 1
        if self.freezeSca_sw:
            count += 1
        if self.freezeShe_sw:
            count += 1
        if self.freezeGeo_sw:
            count += 1
        if (self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw))):
            count += 1
        if self.freezeReplicator_sw:
            count += 1
        if (self.posX != 0 or self.posY != 0 or self.posZ != 0) and self.pos_sw:
            count += 1
        if (self.rotX != 0 or self.rotY != 0 or self.rotZ != 0) and self.rot_sw:
            count += 1
        if (self.scaX != 1 or self.scaY != 1 or self.scaZ != 1) and self.sca_sw:
            count += 1
        if self.smoothAngle_sw:
            count += 1
        if self.hardenUvBorder_sw:
            count += 1
        if self.applyMorphMap_sw:
            count += 1

        return count

    def get_progression_message(self, message):
        return 'Item %s / %s || %s' % (self.progression[0], self.progression[1], message)

    @staticmethod
    def select_arr(arr, replace=False):
        first = True
        for o in arr:
            if replace and first:
                first = False
                modo.item.Item.select(o, True)
            else:
                modo.item.Item.select(o)

    @staticmethod
    def construct_dict_from_arr(arr, keySubIndex):
        d = {}

        for i in arr:
            d[i[0]] = i[keySubIndex]

        return d

    def select_hierarchy(self, force=False):
        if self.exportHierarchy_sw or force:
            lx.eval('select.itemHierarchy')

    def get_replicator_source(self, replicator_arr):
        result_dict = {}
        selection = self.scn.selected

        for i in replicator_arr:
            replicator = modoItem.ModoReplicatorItem(i)
            result_dict[i.name] = replicator

        self.scn.select(selection)

        return result_dict

    @staticmethod
    def concatetate_string_arr(arr, separator):
        string = ''
        for i in xrange(len(arr)):
            if i == 0:
                string += arr[i]
            else:
                string += separator + arr[i]

        return string

    def get_recursive_subdir(self, path, depth):
        if depth == 0:
            return path

        else:
            subdir = set([])

            for p in path:
                if os.path.isdir(p):
                    subdir.add(p)
                    sub = self.get_immediate_subdir(p)

                    for s in sub:
                        subdir.add(s)

                    rec = self.get_recursive_subdir(sub, depth - 1)

                    for r in rec:
                        subdir.add(r)

            return list(subdir)

    @staticmethod
    def get_immediate_subdir(path):
        return [os.path.join(path, subdir) for subdir in os.listdir(path)
                if os.path.isdir(os.path.join(path, subdir))]

    @staticmethod
    def get_files_of_type(path, type):
        files = [os.path.join(path, f) for f in os.listdir(
            path) if isfile(os.path.join(path, f))]
        return [f for f in files if os.path.splitext(f)[1][1:] in type]

    @staticmethod
    def filter_string(string, filter):
        format_arr = string.split(',')
        return [f.lower() for f in format_arr if f.lower() in filter]

    @staticmethod
    def create_folder_if_necessary(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def select_compatible_item_type():
        for type in list(t.compatibleItemType.viewvalues()):
            lx.eval('select.itemType %s mode:add' % type)

    def get_compatible_item_type(self):
        compatible = []
        for type in list(t.compatibleItemType.viewvalues()):
            compatible += self.scn.items(type)
        return compatible

    def get_first_export_type(self):
        if self.exportFormatLxo_sw:
            return 'LXO'
        if self.exportFormatLwo_sw:
            return 'LWO'
        if self.exportFormatFbx_sw:
            return 'FBX'
        if self.exportFormatObj_sw:
            return 'OBJ'
        if self.exportFormatStl_sw:
            return 'STL'
        if self.exportFormatAbc_sw:
            return 'ABC'
        if self.exportFormatAbchdf_sw:
            return 'ABC-HDF'
        if self.exportFormatDae_sw:
            return 'DAE'
        if self.exportFormatDxf_sw:
            return 'DXF'
        if self.exportFormat3dm_sw:
            return '3DM'
        if self.exportFormatGeo_sw:
            return 'GEO'
        if self.exportFormatX3d_sw:
            return 'X3D'
        if self.exportFormatSvg_sw:
            return 'SVG'
        if self.exportFormatPlt_sw:
            return 'PLT'

    def select_item_materials(self, items):
        sel = []
        for item in items:
            for matname in self.get_material_list_from_item(item):
                mat = modo.Item(matname + ' (Material)')
                sel.append(mat)

        self.scn.select(sel + items)

    def get_material_list_from_item(self, item):
        tag = set([])

        for i in xrange(len(item.geometry.polygons)):
            tag.add(item.geometry.polygons[i].materialTag)

        return list(tag)

    def get_udim_value(self, uv):
        x = math.ceil(uv[0])
        y = math.ceil(uv[1])

        if x > 10 or x < 1 or y < 1:
            raise ValueError('invalid uv value')

        udim_value = x + 10 * (y - 1)
        return int(udim_value), int(1000 + udim_value)

    def get_udim_tile(self, item, uvmap):
        udim = set([])
        for i in xrange(len(item.geometry.polygons)):
            vert = item.geometry.polygons[i].vertices
            for v in vert:
                uv = item.geometry.polygons[i].getUV(v, uvmap)
                udim.add(self.get_udim_value(uv)[1])

        return udim

    def offset_uv(self, uv):
        lx.eval('tool.viewType uv')
        lx.eval('tool.set xfrm.transform on')
        lx.eval('tool.reset')
        lx.eval('tool.setAttr xfrm.transform U %s' % uv[0])
        lx.eval('tool.setAttr xfrm.transform V %s' % uv[1])
        lx.eval('tool.doApply')
        lx.eval('tool.set xfrm.transform off')

    def get_normalize_uv_offset(self, uv):
        x = uv[0]
        y = uv[1]
        return [- math.floor(x), - math.floor(y)]

    def assign_material_and_move_udim(self, item, uvmap, udim, destination, color):
        main_layer = lx.eval1('query layerservice layer.index ? main')

        udim_dict = {}
        uv_offset_dict = {}

        for u in udim:
            udim_dict[u] = set([])
            uv_offset_dict[u] = []

        for i in xrange(len(item.geometry.polygons)):
            vert = item.geometry.polygons[i].vertices

            for v in vert:
                uv = item.geometry.polygons[i].getUV(v, uvmap)

                current_udim = self.get_udim_value(uv)[1]

                uv_offset_dict[current_udim] = self.get_normalize_uv_offset(uv)

                if current_udim in udim:
                    udim_dict[current_udim].add(v.index)

        lx.eval('vertMap.list txuv %s' % uvmap)

        for u in udim_dict:
            lx.eval('select.type vertex')
            for v in udim_dict[u]:
                lx.eval('select.element %s vertex add index:%s' % (main_layer, v))

            lx.eval('select.convert polygon')
            self.offset_uv(uv_offset_dict[u])

            lx.eval('poly.setMaterial %s {%s %s %s} 0.8 0.04 true false' % (
                    str(u), color[0], color[1], color[2]))

            lx.eval('select.drop vertex')
            lx.eval('select.drop polygon')
            lx.eval('select.drop item')
            lx.eval('select.drop item mask')
            lx.eval('select.drop item advancedMaterial')

            self.UDIMMaterials.add(modo.Item(str(u) + ' (Material)'))

        lx.eval('vertMap.list txuv _____n_o_n_e_____')

        lx.eval('select.type item')

    def construct_replicator_dict(self):
        if len(self.itemToProceed['REPLICATOR']) > 0:
            self.replicator_dict = self.get_replicator_source(self.itemToProceed['REPLICATOR'])
            for o in self.replicator_dict.keys():  # Generate self.replicator_group_source
                if self.replicator_dict[o].source_is_group:
                    self.replicator_group_source[o] = [
                        self.replicator_dict[o].source_group_name, self.replicator_dict[o].source]
                elif len(self.replicator_dict[o].source) > 1:
                    self.replicator_multiple_source[o] = self.replicator_dict[o].source
                else:
                    self.replicator_non_group_source[o] = self.replicator_dict[o].source

    @staticmethod
    def file_conflict(path):
        return os.path.isfile(path)

    def select_visible_items(self):
        compatible = self.get_compatible_item_type()

        visible = []

        for item in compatible:
            visible_channel = item.channel('visible').get()
            if visible_channel == 'default' or visible_channel == 'on':
                visible.append(item)

        self.scn.select(visible)
        return visible
    # Cleaning

    def revert_scene_preferences(self):
        # lx.eval('scene.set {}'.format(self.currScn))
        self.scn.select(self.userSelection)

        # Put the user's original Export setting back.
        if self.exportFormatFbx_sw:
            lx.eval('user.value sceneio.fbx.save.exportType {}'.format(self.defaultExportSettings['FBX_EXPORT_TYPE']))
            lx.eval('user.value sceneio.fbx.save.surfaceRefining {}'.format(self.defaultExportSettings['FBX_SURFACE_REFINING']))
            lx.eval('user.value sceneio.fbx.save.format {}'.format(self.defaultExportSettings['FBX_FORMAT']))

    def clean_duplicates(self, closeScene=False):
        if closeScene:
            lx.eval('scene.set %s' % self.tempScnID)
            lx.eval('!scene.close')
        self.revert_scene_preferences()
        sys.exit()

    def revert_initial_parameter(self):
        self.itemToProceed = self.init_ctype_dict_arr()
        self.sortedItemToProceed = []
        if self.exportEach_sw:
            self.proceededMesh = []
        else:
            self.proceededMesh = self.init_ctype_dict_arr()
        self.replicator_dict = {}
        self.proceededMeshIndex = 0
        self.progress = None
        self.progression = [0, 0]
        self.tempScnID = None
        self.replicatorSrcIgnoreList = ()
        self.firstIndex = self.init_ctype_dict_arr()

    def reset_import_settings(self):
        # Put the user's original Import setting back.
        lx.eval('user.value sceneio.obj.import.static {}'.format(self.defaultImportSettings['OBJ_STATIC']))
        lx.eval('user.value sceneio.obj.import.separate.meshes {}'.format(self.defaultImportSettings['OBJ_SEPARATE_MESH']))
        lx.eval('user.value sceneio.obj.import.suppress.dialog %{s}'.format(self.defaultImportSettings['OBJ_SUPRESS_DIALOG']))
        lx.eval('user.value sceneio.obj.import.units %{s}'.format(self.defaultImportSettings['OBJ_UNIT']))
