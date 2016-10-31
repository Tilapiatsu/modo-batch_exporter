import lx
import modo
import os
import dialog
import sys
import Tila_BatchExportModule as t


# Path Constructor

def construct_file_path(self, output_dir, layer_name, ext):
    sceneName = os.path.splitext(self.scn.name)[0]
    if self.scanFiles_sw:
        if self.exportEach_sw:
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
            return [os.path.join(output_dir, sceneName + '.' + ext),
                    os.path.join(output_dir, sceneName + '_cage.' + ext)]


# Helpers, setter/getter, Selector

def items_to_proceed_constructor(self):
    for item in self.userSelection:
        if item.type == t.itemType['MESH_INSTANCE']:
            self.meshInstToProceed.append(item)
        if item.type == t.itemType['MESH']:
            self.meshItemToProceed.append(item)
        if item.type == t.itemType['REPLICATOR']:
            self.meshReplToProceed.append(item)
        '''
        if item.type == t.compatibleItemType['MESH_FUSION']:
            self.meshFusionToProceed.append(item)
        '''
    sort_original_items(self)


def sort_original_items(self):
    self.sortedOriginalItems = self.meshInstToProceed +\
                               self.meshFusionToProceed +\
                               self.meshItemToProceed +\
                               self.meshReplToProceed


def duplicate_rename(self, arr, suffix):
    duplicate_arr = []
    for item in arr:
        layer_name = item.name
        if item.type == t.itemType['MESH_FUSION']:
            select_hierarchy(self, force=True)
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
            dialog.open_folder(output_dir)



def check_selection_count(self):
    if self.userSelectionCount == 0:  # No file Selected
        if self.exportVisible_sw:
            dialog.init_message('error', 'No item visible', 'At least one mesh item has to be visible')
        else:
            dialog.init_message('error', 'No item selected', 'Select at least one mesh item')
        sys.exit()


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


def getLatestItemCreated(name):
    i = 1
    item = None
    while True:
        try:
            if i == 1:
                item = modo.Item(name)
            else:
                item = modo.Item('%s%s' % (name, getIteratorTemplate(i)))
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
    if self.scn.selected[0].type == t.itemType['MESH_INSTANCE'] and (self.exportFile_sw or ((not self.exportFile_sw) and (self.freezeInstance_sw or self.freezePos_sw or self.freezeRot_sw or self.freezeSca_sw or self.freezeShe_sw))):
        count += 1
    if self.scn.selected[0].type == t.itemType['REPLICATOR']:
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


def safe_select(tuple):
    first = False
    for i in tuple:
        if isItemTypeCompatibile(i):
            if not first:
                first = True
                modo.item.Item.select(i, True)
            else:
                modo.item.Item.select(i)


def isItemTypeCompatibile(item):
    for type in t.itemType.values():
        try:
            if str(item.type) == type:
                return True
        except AttributeError:
            break
    return False

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
        self.scn.select(i)
        source_arr = lx.eval('replicator.source ?')

        result_dict[i.name] = source_arr

    self.scn.select(selection)

    return result_dict


def replace_replicator_source(self, item_arr):
    selection = self.scn.selected
    for i in item_arr:
        for k, v in self.replicatorSource.iteritems():
            if i.name[:-len(t.TILA_DUPLICATE_SUFFIX)] == k:
                self.scn.select(i)

                source_name = concatetate_string_arr([v], ';')
                print source_name
                lx.eval('replicator.source %s' % source_name)

    self.scn.select(selection)


def concatetate_string_arr(arr, separator):

    string = ''
    index = 0
    for i in xrange(len(arr)):
        if i == 0:
            string += arr[i]
        else:
            string += separator + arr[i]

    return string

# Cleaning


def revert_scene_preferences(self):
    self.scn.select(self.userSelection)

    # Put the user's original FBX Export setting back.

    if self.exportFormatFbx_sw:
        lx.eval('user.value sceneio.fbx.save.exportType %s' % self.fbxExportType)
        lx.eval('user.value sceneio.fbx.save.surfaceRefining %s' % self.fbxTriangulate)
        lx.eval('user.value sceneio.fbx.save.format %s' % self.fbxFormat)


def clean_duplicates(self, closeScene=False):
    if closeScene:
        if lx.eval('query sceneservice scene.index ? current') == self.tempScnID:
            lx.eval('!!scene.close')
            lx.eval('scene.set %s' % self.scnIndex)

    safe_select(self.proceededMesh)
    lx.eval('!!item.delete')
    set_name([self.sortedOriginalItems[self.proceededMeshIndex]], shrink=len(t.TILA_BACKUP_SUFFIX))
    revert_scene_preferences(self)
    sys.exit()
