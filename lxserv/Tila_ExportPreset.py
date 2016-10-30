#!/usr/bin/env python

import lx
import lxu
import lxifc
import lxu.command
import lxu.service
import modo

from collections import OrderedDict

import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper
from Tila_BatchExportModule import dialog


def tilaBExpUserValues():
    '''Returns all user values where the name begins with 'tilaBExp.' '''

    svc = lx.service.ScriptSys()
    tilaBExpUserValues = []

    for i in xrange(svc.UserValueCount()):
        u = svc.UserValueByIndex(i)
        if u.Name().startswith(t.kit_prefix):
            tilaBExpUserValues.append(u)

    return tilaBExpUserValues

def readUserValue(uvname='exportType'):
    '''Utility method to return a uservalue's value'''

    userValueObject = lx.service.ScriptSys().UserValueLookup(uvname)

    utype = userValueObject.Type()
    uvalue = None
    if utype == lx.symbol.i_TYPE_INTEGER:
        uvalue = userValueObject.GetInt()
    elif utype == lx.symbol.i_TYPE_STRING:
        uvalue = userValueObject.GetString()
    elif utype == lx.symbol.i_TYPE_FLOAT:
        uvalue = userValueObject.GetFlt()

    return uvalue


def prefixTilaBExpUserValueName(baseName):
    '''Small method that prepends the common prefix 'sceneio.fbx.save.' to a string'''
    return t.kit_prefix+baseName



def findAndFormatMsg(tableName, keyName=None, index=None, *args):
    '''Substitution for Modo Messages

    example:

        msg = findAndFormatMsg ('gameExport', 'uvMapNotFound', None, "A", "B", "C")
        print lx.service.Message().MessageText (msg)
        # Result: "UV map 'A' referenced by Texture ''B' was not found for mesh 'C'"
    '''

    index = 0 if index is None else index
    keyName = '' if keyName is None else keyName

    msg = lx.object.Message(lx.service.Message().Allocate())
    msg.SetMessage(tableName, keyName, index)

    indices = range(1, len(args) + 1)
    for i, value in zip(indices, args):
        msg.SetArgumentString(i, str(value))

    return msg


def getMsgText (tableName, keyName=None, index=None, *args):
    '''Get message text from a table and optionally substitutes words'''
    service = lx.service.Message()
    msg = findAndFormatMsg (tableName, keyName, index, *args)
    return service.MessageText (msg)


class Listeners(lxifc.SelectionListener, lxifc.UserValueListener, lxifc.SessionListener):
    # We need the undo service, to check if it is safe to execute commands
    undoService = lx.service.Undo()
    numTilaBExpUserValues = len(tilaBExpUserValues())
    changedUserValues = set()

    def __init__(self):
        # Fetch the listener service and ask it to create a new listener server for us
        self.listenerService = lx.service.Listener()
        self.COM_object = lx.object.Unknown(self)
        self.listenerService.AddListener(self.COM_object)

        self.cls = self.__class__

        # This is used to detect
        self._previousModifiedState = False

    def __del__(self):
        self.listenerService.RemoveListener(self.COM_object)

    def selevent_Add(self, type, subtType):
        if lxu.decodeID4(type) == 'CINE':
            self.update()

    def selevent_Remove(self, type, subtType):
        if lxu.decodeID4(type) == 'CINE':
            self.update()

    def update(self):
        if not Listeners.undoService.State() == lx.symbol.iUNDO_ACTIVE:
            return

        sceneChanged = True

    def uvl_ValueChanged(self, userValue):
        if lx.object.UserValue(userValue).Name().startswith(t.kit_prefix):

            # This block exist to ensure the UI form is only refreshed once
            # when the state of the preset changes from modified to unmodified.
            modified = exportPresets.isModified

            if modified != self._previousModifiedState:
                UpdateAsteriskNotifier.reset()

            self._previousModifiedState = modified

            # Notify
            UpdateAsteriskNotifier().NotifyPresetChanged()


listener = Listeners()


class PersistenceWrapper(object):
    """
    "Work in progress"-version of a generic wrapper around the persistence interface.
    Once initialized, the container-stype bracket access can be used to set and get values.

    TODO: Add support for creating hierarchies and lists
    """

    def __init__(self, name="ExportPresets", hashtype="ExportPresetValues", fields=None):

        self.config = None
        self.name = name
        self.hashtype = hashtype
        self._hashes = []

        if not fields:
            self.fields = OrderedDict()
        else:
            self.fields = fields
            self.register()

        for i in xrange(self.config.hash_main.Count()):
            self.config.hash_main.Select(i)
            # TODO: search for uses of self._hashes.append and factor them out
            self._hashes.append(self.config.hash_main.Hash())

        self.activeHash = None

    class PersistDataVisitor(lxifc.Visitor):

        def __init__(self, name, fields):
            self.name = name
            self.fields = fields
            self.atoms = {}
            self.svc = lx.service.Persistence()

        def addAtom(self, name, valueType=lx.symbol.sTYPE_STRING):
            self.svc.Start(name, lx.symbol.i_PERSIST_ATOM)
            self.svc.AddValue(valueType)
            atom = self.svc.End()
            self.atoms[name] = atom

        def vis_Evaluate(self):
            self.addAtom('selection', lx.symbol.sTYPE_STRING)

            self.svc.Start(self.name, lx.symbol.i_PERSIST_HASH)

            for fieldName, fieldType in self.fields.items():
                self.addAtom(fieldName, fieldType)

            self.hash_main = self.svc.End()

    def register(self):
        """
        Note that this method can only be called once and will throw an exception when called again.
        """
        self.config = self.PersistDataVisitor(self.hashtype, self.fields)
        lx.service.Persistence().Configure(self.name, self.config)

    def setValue(self, hashKey, key, value):

        previousHash = self.config.hash_main.Hash()
        try:
            self.config.hash_main.Lookup(hashKey)
        except LookupError:
            self.config.hash_main.Insert(hashKey)
            count = self.config.hash_main.Count()
            self.config.hash_main.Select(count - 1)

        atom = self.config.atoms[key]

        atom.Append()
        lxu.object.Attributes(atom).Set(0, value)

        self.config.hash_main.Lookup(previousHash)

    def getValue(self, hashKey, key):

        try:
            self.config.hash_main.Lookup(hashKey)
        except LookupError:
            raise LookupError('Key "%s" not found' % str(key))

        atom = self.config.atoms[key]

        try:
            return lxu.object.Attributes(atom).Get(0)
        except RuntimeError:
            return None

    def __setitem__(self, key, value):

        if not self.activeHash:
            raise LookupError('No active key')

        self.setValue(self.activeHash, key, value)

    def __getitem__(self, key):

        if self.activeHash is None:
            raise LookupError('No active key')

        return self.getValue(self.activeHash, key)

    def __iter__(self):
        for key in self.keys():
            yield self[key]

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.keys()

    def insertHash(self, key):
        # Note that inserting an existing key wipes the contents
        self.config.hash_main.Insert(key)
        count = self.config.hash_main.Count()
        self.config.hash_main.Lookup(key)
        self.activeHash = key
        self._hashes.append(key)

    def removeHash(self, key):
        h = self.config.hash_main
        try:
            h.Lookup(key)
            h.Delete()
            self._hashes.pop(self._hashes.index(key))
        except LookupError:
            raise LookupError('Could not find key "%s"' % key)

    def keys(self):
        return self.fields.keys()

    def hashes(self):
        return self._hashes


class ExportPresets(PersistenceWrapper):
    _instance = None

    def __init__(self, *args, **kwargs):
        super(ExportPresets, self).__init__(*args, **kwargs)
        self.userValues = tilaBExpUserValues()

        atom = self.config.atoms['selection']
        atom.Append()

        if 'default' not in self.hashes():
            self.insertHash('default', 'default')
            self.pullUserValues()
            self.activeHash = 'default'

            # Write selection to config
            lxu.object.Attributes(atom).SetString(0, self.activeHash)

        else:
            # Read selection from config
            self.activeHash = lxu.object.Attributes(atom).Get(0)

    @staticmethod
    def _userValueGet(userValueObject):
        qualifier = userValueObject.Name().split(t.kit_prefix)[1]

        utype = userValueObject.Type()
        uvalue = None
        if utype == lx.symbol.i_TYPE_INTEGER:
            uvalue = userValueObject.GetInt()
        elif utype == lx.symbol.i_TYPE_STRING:
            uvalue = userValueObject.GetString()
        elif utype == lx.symbol.i_TYPE_FLOAT:
            uvalue = userValueObject.GetFlt()

        return uvalue

    @staticmethod
    def exportUserValueFields():
        result = {t.TILA_PRESET_NAME: lx.symbol.sTYPE_STRING}
        for uservalue in tilaBExpUserValues():
            qualifier = uservalue.Name().split(t.kit_prefix)[1]
            result[qualifier] = uservalue.TypeName()
        return result

    def pullUserValues(self):
        # Pull fbx settings
        for uservalue in tilaBExpUserValues():
            qualifier = uservalue.Name().split(t.kit_prefix)[1]
            self[qualifier] = ExportPresets._userValueGet(uservalue)

    def pushUserValues(self):

        # Push from config to the user values
        for uservalue in tilaBExpUserValues():
            qualifier = uservalue.Name().split(t.kit_prefix)[1]
            configValue = self[qualifier]
            if configValue is not None:
                lx.eval('user.value tilaBExp.{0} {1}'.format(qualifier, configValue))

    def selectPreset(self, presetName):
        if presetName in self.hashes():
            self.activeHash = presetName
            self.config.hash_main.Lookup(presetName)
        else:
            raise LookupError('Preset "%s" not found' % presetName)

        # Store selection in config
        atom = exportPresets.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, presetName)

    def getSelectedPreset(self):
        return self.activeHash

    def insertHash(self, key, userName):
        super(self.__class__, self).insertHash(key)
        self[t.TILA_PRESET_NAME] = userName
        # self.hashUserNames[key] = userName

    def hashUserName(self, key):
        return self.getValue(key, t.TILA_PRESET_NAME)

    def addPreset(self, userName):

        # Remove spaces and make lower case
        internalName = userName.translate(None, ' ').lower()
        self.insertHash(internalName, userName)

        self[t.TILA_PRESET_NAME] = userName
        self.activeHash = internalName

        # needs to copy the values of the previous preset over
        self.pullUserValues()

        # Write selection to config
        atom = self.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, self.activeHash)

    def removeCurrentPreset(self):

        self.removeHash(self.activeHash)
        self.activeHash = 'default'
        self.pushUserValues()

        # Write selection to config
        atom = self.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, self.activeHash)

    def pushToConfig(self):

        # workaround some odd behavior
        username = self[t.TILA_PRESET_NAME]

        for u in self.userValues:
            key = u.Name()
            basename = key.split('.')[-1]
            self[basename] = self._userValueGet(u)

        self[t.TILA_PRESET_NAME] = username

        # Write selection to config
        atom = self.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, self.activeHash)

    @property
    def isModified(self):
        '''Returns true if any value from the buffer differs from the persistent (config) data.'''

        for argName in self.keys():

            if argName in (t.TILA_PRESET_NAME,):
                continue

            # Is value stored in both, the buffer and the config?
            isInBuffer = self.fields.keys()
            isInConfig = argName in self

            if isInBuffer and isInConfig:

                a = readUserValue(prefixTilaBExpUserValueName(argName))
                b = self[argName]

                if a != b:
                    return True

        return False

exportPresets = ExportPresets(name="ExportPresets", hashtype="ExportPresetValues", fields=ExportPresets.exportUserValueFields())


#exportPresets = ExportPresets()


class CmdExportPresets(lxu.command.BasicCommand):

    def __init__(self):

        lxu.command.BasicCommand.__init__(self)
        self.dyna_Add('preset', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_QUERY)

        # Setup notifier
        self.not_svc = lx.service.NotifySys()
        self.notifier = lx.object.Notifier()

    def cmd_Flags(self):
        return lx.symbol.fCMD_UI

    def basic_Enable(self, msg):
        return True

    def cmd_Interact(self):
        pass

    def basic_Execute(self, msg, flags):

        if not self.dyna_IsSet(0):
            return

        presetName = self.dyna_String(0, None)

        if presetName == 'new':
            newname = dialog.textInputDialog('Preset Name')
            if newname:
                exportPresets.addPreset(newname)

        elif presetName == 'store':
            if exportPresets.activeHash in ['default']:
                textCannotDeleteBuiltins = getMsgText('gameExport', 'cannotDeleteBuiltin')
                modo.dialogs.alert('Info', textCannotDeleteBuiltins)
                return
            exportPresets.pushToConfig()

        elif presetName == 'remove':

            if exportPresets.activeHash in ['default']:
                textCannotDeleteBuiltins = getMsgText('gameExport', 'cannotDeleteBuiltin')
                modo.dialogs.alert('Info', textCannotDeleteBuiltins)
                return

            # Pop up a dialog to confirm deleting the preset
            textConfirmTitle = getMsgText('gameExport', 'removePresetTitle')
            textConfirm = getMsgText('gameExport', 'removePresetConfirm', None, exportPresets[t.TILA_PRESET_NAME])

            if modo.dialogs.okCancel(textConfirmTitle, textConfirm) != 'ok':
                return

            # Removes current preset and selects 'default'
            exportPresets.removeCurrentPreset()

        else:
            if presetName in exportPresets._hashes:

                # When the user changes from 'default' to another preset, store the 'default' values first.
                if exportPresets.activeHash == 'default' and presetName != 'default':
                    exportPresets.pullUserValues()

                exportPresets.selectPreset(presetName)
                exportPresets.pushUserValues()

        # Notify UI elements
        UpdateAsteriskNotifier.reset()
        UpdateAsteriskNotifier().Notify(lx.symbol.fCMDNOTIFY_DATATYPE)

    def arg_UIValueHints(self, index):
        if index == 0:

            keys = exportPresets.hashes()
            values = [exportPresets.hashUserName(key) for key in keys]
            noneName = 'Default'
            # If the preset has been modified, display a star in front of the name
            if exportPresets.isModified:
                index = keys.index(exportPresets.activeHash)
                values[index] = values[index] + '*'
                noneName = 'Default*'

            # Removing the 'none' entry to insert it at the beginning again below,
            # just to make it always appear first in the popup list.

            notInList = lambda a: a not in ('default', 'Default', 'default*', 'Default*')

            keys = filter(notInList, keys)
            values = filter(notInList, values)


            # Generate list of two tuples where the first one contains lower case keys and the
            # second one contains the "nicer" user names.
            keys = tuple(['default'] + keys + ['new', 'store', 'remove'])
            userNames = tuple([noneName] + values + ['(New Preset)', '(Store Preset)', '(Remove Preset)'])
            return PopUp([keys, userNames])

    def cmd_Query(self, index, vaQuery):
        va = lx.object.ValueArray()
        va.set(vaQuery)
        if index == 0:
            va.AddString(exportPresets.getSelectedPreset())

    def cmd_NotifyAddClient(self, argument, object):
        self.notifier = self.not_svc.Spawn(t.REFRESH_ASTERISK_NOTIFIER, "")
        self.notifier.AddClient(object)

    def cmd_NotifyRemoveClient(self, object):
        self.notifier.RemoveClient(object)


# bless() the command to register it as a plugin
lx.bless(CmdExportPresets, t.TILA_EXPORT_PRESET)


class PopUp(lxifc.UIValueHints):
    def __init__(self, items):
        self._items = items

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_POPUPS

    def uiv_PopCount(self):
        return len(self._items[0])

    def uiv_PopUserName(self,index):
        return self._items[1][index]

    def uiv_PopInternalName(self,index):
        return self._items[0][index]


class UpdateAsteriskNotifier(lxifc.Notifier):
    masterList = {}
    _presetValuesChanged = False

    @classmethod
    def reset(cls):
        '''
        This method is called every time the user selects/creates/deletes a preset.
        It causes the next preset change to redraw the UI and update the Asterisk once.
        This is to reduce the flicker cause by the absense of double buffering in the form.
        '''
        cls._presetValuesChanged = False

    def noti_Name(self):
        return t.REFRESH_ASTERISK_NOTIFIER

    def noti_AddClient(self, event):
        self.masterList[event.__peekobj__()] = event

    def noti_RemoveClient(self, event):
        del self.masterList[event.__peekobj__()]

    def Notify(self, flags):
        for event in self.masterList:
            evt = lx.object.CommandEvent(self.masterList[event])
            evt.Event(flags)

    def NotifyPresetChanged(self):
        '''To avoid re-building the entire form too often which causes flickering, we only do it once'''

        cls = self.__class__
        if not cls._presetValuesChanged:
            self.Notify(lx.symbol.fCMDNOTIFY_DATATYPE)

        cls._presetValuesChanged = True


lx.bless(UpdateAsteriskNotifier, t.REFRESH_ASTERISK_NOTIFIER)


fields = helper.construct_dict_from_arr(t.userValues, 1)

_previousModificationState = False

'''
def createGenericAttributeCommand(argName, argType):
    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add(argName, argType)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_QUERY)

        self.argName = argName
        self.argType = argType

    def cmd_Flags(self):
        return lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def attrSetterFunc(self, argType):
        if self.argType == lx.symbol.sTYPE_STRING:
            return self.attr_SetString

        elif self.argType in (lx.symbol.sTYPE_INTEGER, lx.symbol.sTYPE_BOOLEAN):
            return self.attr_SetInt

        elif self.argType == lx.symbol.sTYPE_FLOAT:
            return self.attr_SetFlt
        return None

    def attrGetterFunc(self, argType):
        if self.argType == lx.symbol.sTYPE_STRING:
            return self.dyna_String

        elif self.argType in (lx.symbol.sTYPE_INTEGER, lx.symbol.sTYPE_BOOLEAN):
            return self.dyna_Int

        elif self.argType == lx.symbol.sTYPE_FLOAT:
            return self.dyna_Float
        return None

    def basic_Execute(self, msg, flags):
        if self.dyna_IsSet(0):

            getter = self.attrGetterFunc(self.argType)
            value = getter(0)

            exportPresets[self.argName] = value

            # This block exist to ensure the UI form is only refreshed once
            # when the state of the preset changes from modified to unmodified.
            global _previousModificationState
            modified = exportPresets.isModified
            if modified != _previousModificationState:
                UpdateAsteriskNotifier.reset()
            _previousModificationState = modified

            UpdateAsteriskNotifier().NotifyPresetChanged()

    def cmd_Query(self, index, vaQuery):

        va = lx.object.ValueArray()
        va.set(vaQuery)

        if index == 0:

            value = exportPresets[self.argName]

            if self.argType == lx.symbol.sTYPE_STRING:
                va.AddString(value)

            elif self.argType in (lx.symbol.sTYPE_INTEGER, lx.symbol.sTYPE_BOOLEAN):
                va.AddInt(value)

            elif self.argType == lx.symbol.sTYPE_FLOAT:
                va.AddFloat(value)

    def arg_UIValueHints(self, index):

        if index != 0:
            return

    cls_dict = {
        '__init__': __init__,
        'cmd_Flags': cmd_Flags,
        'basic_Execute': basic_Execute,
        'cmd_Query': cmd_Query,
        'attrSetterFunc': attrSetterFunc,
        'attrGetterFunc': attrGetterFunc,
        'arg_UIValueHints': arg_UIValueHints,
    }

    cls = classobj('CmdPreset%s' % argName, (lxu.command.BasicCommand,), cls_dict)

    lx.bless(cls, "%s%s" % (t.kit_prefix, argName))
'''
'''
for argName, argType in fields.iteritems():
    createGenericAttributeCommand(argName, argType)
'''