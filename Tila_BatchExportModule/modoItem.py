import lx
import modo
import Tila_BatchExportModule as t
from Tila_BatchExportModule import dialog


class ModoItem(modo.item.Item):
    mm = dialog.MessageManagement('ModoItem')
    _key = None

    def __init__(self, item):
        modo.item.Item.__init__(self, item)
        self.scn = modo.Scene()
        self.name = item.name
        self.cmd_svc = lx.service.Command()

        # store scene source scene ID
        self.srcScnID = lx.eval('query sceneservice scene.index ? current')
        self.dstScnID = None
        self.dstItem = None

    @staticmethod
    def get_name_arr(arr):
        name_arr = []
        for o in arr:
            name_arr.append(o.name)

        return name_arr

    @property
    def type(self):
        if self._key is None:
            return self._item.type
        else:
            return t.itemType[self._key]

    @property
    def typeKey(self):
        return t.get_key_from_value(t.compatibleItemType, self.type)

    @property
    def position(self):
        return modo.item.LocatorSuperType(self._item).position

    @property
    def rotation(self):
        return modo.item.LocatorSuperType(self._item).rotation

    @property
    def scale(self):
        return modo.item.LocatorSuperType(self._item).scale

    def have_deformers(self):
        if len(self._item.deformers):
            return True
        else:
            return False

    def apply_morph(self, morph_map_name):
        morph_maps = morph_map_name.split(',')
        for maps in morph_maps:
            lx.eval('vertMap.applyMorph %s 1.0' % maps)

    def clearitems(self):
        try:
            lx.eval('select.itemType mesh')
            lx.eval('select.itemType camera mode:add')
            lx.eval('select.itemType light super:true mode:add')
            lx.eval('select.itemType renderOutput mode:add')
            lx.eval('select.itemType defaultShader mode:add')
            lx.eval('!!item.delete')
        except:
            t.return_exception()

    def copy_to_scene(self, dstScnID=None):
        # store the original name of the item
        originalName = self._item.name

        # create a new temporary scene if no one scene is specified
        if dstScnID is None:
            self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.new')
            self.dstScnID = lx.eval('query sceneservice scene.index ? current')

            self.clearitems()

            self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, 'scene.set %s' % self.srcScnID)
        else:
            self.dstScnID = dstScnID

        # rename item if it is contains a generic name
        modifiedName = self.rename_generic_name()

        self.scn.select(modifiedName)

        # Move all selected items to temporary scene
        self.cmd_svc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, '!layer.import {}'.format(self.dstScnID) + ' {} ' + 'childs:{} shaders:true move:false position:0'.format(False))

        self.scn = modo.Scene()

        if modifiedName is not None:
            self.revert_generic_name(originalName, modifiedName)

        self.store_dstItem(originalName)

    def rename_generic_name(self):
        for gen in t.genericName:
            if gen in self._item.name:
                self._item.name = self._item.name.replace(gen, t.genericNameDict[gen])
                return self._item.name
        else:
            return None

    def revert_generic_name(self, originalName, modifiedName):
        if self.srcScnID is None or self.dstScnID is None:
            self.mm.error('Temporary scene not found. \n can\'t revert name', dialog=True)
            return False

        # rename item in destination scene
        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        item = modo.Item(modifiedName)

        item.name = originalName

        # switch to source Scene to revert name
        lx.eval('scene.set {}'.format(self.srcScnID))
        self.scn = modo.Scene()

        item = modo.Item(modifiedName)

        item.name = originalName

        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        return True

    def store_dstItem(self, name):
        curr_scnID = lx.eval('query sceneservice scene.index ? current')

        lx.eval('scene.set {}'.format(self.dstScnID))
        self.scn = modo.Scene()

        self.dstItem = convert_to_modoItem(modo.Item(name))

        lx.eval('scene.set {}'.format(curr_scnID))
        self.scn = modo.Scene()


class ModoMeshItem(ModoItem):

    def __init__(self, item):
        ModoItem.__init__(self, item)


class ModoMeshInstance(ModoItem):

    def __init__(self, item):
        ModoItem.__init__(self, item)


class ModoGroupLocatorItem(ModoItem):

    def __init__(self, item):
        ModoItem.__init__(self, item)


class ModoLocatorItem(ModoItem):

    def __init__(self, item):
        ModoItem.__init__(self, item)


class ModoMeshFusionItem(ModoItem):
    _key = 'MESH_FUSION'

    def __init__(self, item):
        ModoItem.__init__(self, item)


class ModoReplicatorItem(ModoItem):
    _key = 'REPLICATOR'

    def __init__(self, item):
        ModoItem.__init__(self, item)
        self._replicator = None
        self._source_group_name = self.source_group_name

    @property
    def replicator_item(self):
        self._item = modo.Item(self.name)
        return self._item

    @property
    def replicator_src_arr(self):
        self.scn = modo.Scene()
        selection = self.scn.selected

        lx.eval('select.item {}'.format(self._item.name))
        source = lx.eval('replicator.source ?')
        particle = lx.eval('replicator.particle ?')

        if 'group' in source:
            lx.eval('select.item {}'.format(source))
            lx.eval('group.scan sel item')
            source = self.scn.selected
            replicator = [source, self.scn.item(particle)]
            self.scn.select(selection)
            self._replicator = replicator
            return replicator
        elif isinstance(source, tuple) or isinstance(source, list):
            source_arr = []
            for o in source:
                source_arr.append(modo.Item(o))
            replicator = [source_arr, self.scn.item(particle)]
            self._replicator = replicator
            self.scn.select(selection)
            return replicator
        elif modo.Item(source).type in [t.itemType['MESH'], t.itemType['MESH_INSTANCE'], t.itemType['GROUP_LOCATOR'], t.itemType['LOCATOR']]:
            replicator = [[self.scn.item(source)], self.scn.item(particle)]
            self._replicator = replicator
            self.scn.select(selection)
            return replicator

        self.scn.select(selection)

    @property
    def source(self):
        return self.replicator_src_arr[0]

    @property
    def source_name(self):
        return self.get_name_arr(self.replicator_src_arr[0])

    @property
    def particle(self):
        return self.replicator_src_arr[1]

    def select_src_arr(self):
        self.scn = modo.Scene()
        self.scn.deselect()
        for o in self.replicator_src_arr[0]:
            self.scn.select(o, add=True)

        self.scn.select(self.replicator_src_arr[1], add=True)

    @property
    def source_is_group(self):
        if self._item.type == t.compatibleItemType['REPLICATOR']:
            self.scn = modo.Scene()
            selection = self.scn.selected

            lx.eval('select.item {}'.format(self._item.name))
            source = lx.eval('replicator.source ?')

            result = 'group' in source

            self.scn.select(selection)

            return result
        else:
            return False

    @property
    def source_group_name(self):
        if self.source_is_group:
            self.scn = modo.Scene()
            selection = self.scn.selected

            lx.eval('select.item {}'.format(self._item.name))
            source = lx.eval('replicator.source ?')

            group = modo.Item(source)

            self.scn.select(selection)

            return group.name

        else:
            return None

    @property
    def source_group(self):
        name = self.source_group_name
        if name is not None:
            for grp in self.scn.groups:
                if grp.name == name:
                    return grp
        else:
            return None

    def set_source(self, source_arr):
        if self.replicator_item is not None:
            selection = self.scn.selected

            self.scn.select(self.replicator_item)

            if self.source_is_group:
                lx.eval('replicator.source "{}"'.format(
                        self._source_group_name))
                group = modo.item.Group(self._source_group_name)
                for o in source_arr:
                    if not group.hasItem(o):
                        group.addItems(o)
            elif len(source_arr) == 1:
                lx.eval('replicator.source "{}"'.format(source_arr[0].name))
            else:
                for o in source_arr:
                    # Need to link with multiple item
                    lx.eval('item.link particle.proto {} {} replace:false'.format(o, self.replicator_item.name))
                    # lx.eval('replicator.source "{}"'.format(o.name))

            self.scn.select(selection)


class ModoDeformerItem(ModoItem):
    _key = 'MESH_OPERATOR'

    # is Used by MOP Item
    def __init__(self, item):
        ModoItem.__init__(self, item)
        self.deformer_group = None
        self._deformer_item = None
        self._deformers = None
        if not self.is_deformer_item:
            self.mm.warning('The item {} has no deformer'.format(self.name))

    @property
    def deformer_item(self):
        self._deformer_item = modo.Item(self.name)
        return self._deformer_item

    @deformer_item.setter
    def deformer_item(self, item):
        self._deformer_item = item
        self.item_name = item.name

    @property
    def is_deformer_item(self):
        if len(self.deformer_item.deformers):
            return True
        else:
            return False

    @property
    def deformers(self):
        if self.is_deformer_item:
            self._deformers = self.deformer_item.deformers
            return self._deformers
        else:
            self.mm.warning('The item {} has no deformer'.format(self.name))
            return None

    def get_deformer_by_name(self, name, absolute=True):
        for d in self.deformers:
            if absolute:
                if name == d.name:
                    return d
            else:
                if name in d.name:
                    return d
        else:
            return None

    def rename_deformer_by_name(self, old_name, new_name):
        deformer = self.get_deformer_by_name(old_name)

        if deformer:
            deformer.name = new_name
            return True
        else:
            return False

    @property
    def deformer_names(self):
        return self.get_name_arr(self.deformers)

    def select_deformers(self):
        i = 0
        for o in self.deformers:
            if i == 0:
                lx.eval('select.deformer "{}" set'.format(o))
            else:
                lx.eval('select.deformer "{}" add'.format(o))
            i = i + 1

    def group_deformers(self):
        # Create a Deform Group
        if self.deformer_group is None:
            lx.eval('deformer.create deformFolder')
            self.deformer_group = self.scn.selected[0]
            self.deformer_group.name = self.name + '_DF'

        i = 0
        for d in self.deformers:
            lx.eval('deformer.setGroup "{}" "{}" {}'.format(d.name, self.deformer_group.name, i))

    def ungroup_deformers(self):  # It break The OoO ! Don't use tt as it is
        deformers_count = len(self.deformers)

        for d in self.deformers:
            lx.eval('deformer.setGroup "{}" seq:{}'.format(d.name, str(deformers_count - 1)))

        self.scn.removeItems(self.deformer_group, False)

    def reorder_deformers(self, new_order):
        for d in new_order:
            if d in self.deformer_names:
                index = self.deformer_names.index(d)
                lx.eval('deformer.setGroup "{}" seq:0'.format(self.deformers[index].name))


modoItemTypes = {'MESH': ModoMeshItem,
                 'MESH_INSTANCE': ModoMeshInstance,
                 'REPLICATOR': ModoReplicatorItem,
                 'GROUP_LOCATOR': ModoGroupLocatorItem,
                 'LOCATOR': ModoLocatorItem,
                 'MESH_FUSION': ModoMeshFusionItem,
                 'DEFORMER': ModoDeformerItem}


def convert_to_modoItem(item):
    if item.type in t.compatibleItemType.values():
        key = t.get_key_from_value(t.compatibleItemType, item.type)
        mItem = modoItemTypes[key](item)
        if mItem.have_deformers():
            mItem = modoItemTypes['DEFORMER'](item)

        return mItem
    else:
        mm = dialog.MessageManagement('ModoItem')
        mm.info('The item {} can\'t be converted to modo Item'.format(item.name))
        return item
