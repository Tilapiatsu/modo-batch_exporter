import os
import dialog

# Path Constructor
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


# Helpers, setter/getter, Selector

def items_to_proceed_constructor(self):
    for item in self.userSelection:
        if item.type == 'meshInst':
            self.meshInstToProceed.append(item)
        if item.type == 'mesh':
            self.meshItemToProceed.append(item)
    self.sort_original_items()


def sort_original_items(self):
    for i in self.meshInstToProceed:
        self.sortedOriginalItems.append(i)
    for i in self.meshItemToProceed:
        self.sortedOriginalItems.append(i)


def duplicate_rename(self, arr, number):
    duplicate_arr = []
    for item in arr:
        layer_name = item.name
        duplicate = self.scn.duplicateItem(item)
        duplicate.name = '%s_%s' % (layer_name, number)
        duplicate_arr.append(duplicate)
        self.proceededMesh.append(duplicate)

    self.scn.select(duplicate_arr)


def get_name(self, layer):
    if self.exportEach_sw:
        return layer.name
    else:
        return self.scn.name


def set_name(self, arr, shrink, add, layer_name=''):
    for item in arr:
        currName = item.name

        if add:
            if shrink:
                currName = currName[:-2]
            currName += layer_name
        else:
            currName = layer_name

        item.name = currName

def open_destination_folder(self, output_dir):
    if self.exportFile_sw:
        if self.openDestFolder_sw:
            if self.scanFiles_sw:
                dialog.open_folder(output_dir)
            if self.exportEach_sw:
                dialog.open_folder(output_dir)
            else:
                dialog.open_folder(os.path.split(output_dir)[0])

    dialog.ending_log(self)