#!/usr/bin/env python

import lx
import lxu
import lxifc
import lxu.command
import lxu.service
import os
import modo
import shutil
from os.path import join as pjoin
from os.path import normpath
import re

from collections import namedtuple, OrderedDict, Iterable

from new import classobj

from os.path import isfile
import Tila_BatchExportModule as t
from Tila_BatchExportModule import helper
from Tila_BatchExportModule import dialog
from Tila_BatchExportModule import file


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


class PersistenceWrapper(object):
    """
    "Work in progress"-version of a generic wrapper around the persistence interface.
    Once initialized, the container-stype bracket access can be used to set and get values.

    TODO: Add support for creating hierarchies and lists
    """

    def __init__(self, name="FbxPresets", hashtype="FbxPresetValues", fields=None):

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
            if key == OPT_GAME_EXPORT_PATH:
                return ''
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
        # h = self.config.hash_main
        # result = []
        # for i in xrange(h.Count()):
        # h.Select(i)
        # result.append(h.Hash())
        return self._hashes


class ExportPresets(PersistenceWrapper):
    '''
    This class manages the contents of the presets. When values are changed, they are stored in a buffer until "pushToConfig" is called
    The data of the currently selected preset is accessed by using the angular brackets (i.e. __getitem__ and __setitem__ methods).
    '''

    fields = helper.construct_dict_from_arr(t.userValues, 1)

    defaults = helper.construct_dict_from_arr(t.userValues, 3)

    def __init__(self):

        super(self.__class__, self).__init__(name="GamePresets", hashtype="GamePreset", fields=self.__class__.fields)

        # Buffer that is populated when user changes settings.
        # needed to test if the preset state is changed from the original stored in the config.
        # Changed are only written to the config by invoking pushToConfig().
        self._buffer = {}

        atom = self.config.atoms['selection']
        atom.Append()

        if 'none' not in self._hashes:
            self.addPreset('none')

            # Apply initial default values
            for key, value in ExportPresets.defaults.items():
                self[key] = value

            self.pushToConfig()

            self.activeHash = 'none'

            # Write selection to config
            lxu.object.Attributes(atom).SetString(0, self.activeHash)

        else:
            # Read selection from config
            self.activeHash = lxu.object.Attributes(atom).Get(0)

        # Needs to populate the intermediate preset data (_buffer) from config first
        self.pullFromConfig()

    @property
    def selected(self):
        return self.activeHash

    @selected.setter
    def selected(self, key):

        if key not in self.hashes():
            raise LookupError('Key "%s" not found' % key)

        self.activeHash = key

        # Store selection in config
        atom = exportPresets.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, key)

    def addPreset(self, userName, doCopyValuesFromPrevious=False):

        # Need to remember the previous preset to copy the values
        sourcePresetName = self.selected

        # Remove spaces and make lower case
        internalName = userName.translate(None, ' ').lower()

        self.insertHash(internalName)

        # needs to copy the values of the previous preset over
        if doCopyValuesFromPrevious:

            for key in self.fields.keys():
                value = self.getValue(sourcePresetName, key)
                self[key] = value

        self[OPT_GAME_USERNAME] = userName

        self.pushToConfig()

    def removeCurrentPreset(self):

        if len(self.hashes()) < 2:
            raise Exception("Cannot delete last preset")

        preset = self.selected
        self.removeHash(preset)
        self.selected = self.hashes()[0]
        self.pullFromConfig()

        # Write selection to config
        atom = self.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, self.activeHash)

    def getUserNames(self):
        result = {}

        h = self.config.hash_main
        for i in xrange(h.Count()):
            h.Select(i)

            key = h.Hash()
            username = lxu.object.Attributes(self.config.atoms[OPT_GAME_USERNAME]).Get(0)
            result[key] = username

        return result

    @property
    def userName(self):
        h = self.config.hash_main
        return lxu.object.Attributes(self.config.atoms[OPT_GAME_USERNAME]).Get(0)

    @property
    def attributeFields(self):
        '''Returns a dictionary without the keys that are not meant to be exposed as command attribute.'''
        ignore = ('key', OPT_GAME_USERNAME)
        return {key: value for key, value in self.fields.iteritems() if key not in ignore}

    def __setitem__(self, key, value):
        self._buffer[key] = value

    def __getitem__(self, key):
        if key in self._buffer:
            return self._buffer[key]

        return super(self.__class__, self).__getitem__(key)

    def pushToConfig(self):
        for key, value in self._buffer.iteritems():
            super(self.__class__, self).__setitem__(key, value)

        # Write selection to config
        atom = self.config.atoms['selection']
        atom.Append()
        lxu.object.Attributes(atom).SetString(0, self.activeHash)

        self._buffer = {}

    def pullFromConfig(self):
        for key in self.keys():

            value = super(self.__class__, self).__getitem__(key)

            # Options not found in the config are set to their default value during load
            if value is None:
                value = ExportPresets.defaults[key]
            self._buffer[key] = value

    @property
    def isModified(self):
        '''Returns true if any value from the buffer differs from the persistent (config) data.'''

        parentInstance = super(self.__class__, self)

        for argName in self.keys():

            # Is value stored in both, the buffer and the config?
            isInBuffer = argName in self._buffer
            isInConfig = parentInstance.__contains__(argName)

            if isInBuffer and isInConfig:

                a = self._buffer[argName]
                b = parentInstance.__getitem__(argName)
                if a != b:
                    return True

        return False

    def contains(self, presetName):
        return presetName in self.hashes()


class CmdExportPresets(lxu.command.BasicCommand):
    # Class level attributes
    _previousModifiedState = False

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)

        self.dyna_Add('selected', lx.symbol.sTYPE_STRING)
        self.basic_SetFlags(0, lx.symbol.fCMDARG_QUERY | lx.symbol.fCMDARG_OPTIONAL)

        # notifier
        self.not_svc = lx.service.NotifySys()
        self.notifier = lx.object.Notifier()

        self.cls = self.__class__

    def cmd_Query(self, index, vaQuery):

        va = lx.object.ValueArray()
        va.set(vaQuery)

        if index == 0:
            va.AddString(exportPresets.selected)

    def basic_Execute(self, msg, flags):

        doNotify = False

        # If first argument, "selected" is set ...
        if self.dyna_IsSet(0):
            presetName = self.dyna_String(0, None)
            if presetName == None:
                raise ValueError("Something is wrong here")

            if presetName == 'new':
                textRenamePresetTitle = getMsgText('gameExport', 'renamePresetTitle')
                newname = dialog.textInputDialog(textRenamePresetTitle)
                if newname:
                    exportPresets.addPreset(newname, doCopyValuesFromPrevious=True)
                    fbxPresets.addPreset(newname)

                    # Ensure the newly selected fbx preset is stored
                    # Remove spaces and make lower case
                    internalName = newname.translate(None, ' ').lower()
                    exportPresets[OPT_GAME_FBX_PRESET] = internalName
                    exportPresets.pushToConfig()

            elif presetName == 'store':
                exportPresets.pushToConfig()
                fbxPresets.pushToConfig()

            elif presetName == 'remove':

                if exportPresets.selected in ['unity', 'ue4']:
                    textCannotDelete = getMsgText('gameExport', 'cannotDeleteBuiltin')
                    modo.dialogs.alert('Info', textCannotDelete)
                    return

                # Pop up a dialog to confirm deleting the preset
                textConfirmTitle = getMsgText('gameExport', 'removePresetTitle')
                textConfirm = getMsgText('gameExport', 'removePresetConfirm', None, exportPresets.selected)

                if modo.dialogs.okCancel(textConfirmTitle, textConfirm) != 'ok':
                    return

                exportPresets.removeCurrentPreset()

                # Set scene to "next best" preset preset
                if exportPresets.hashes():
                    exportPresets.selected = exportPresets.hashes()[0]
                else:
                    raise LookupError('No preset left')

            else:
                if presetName in exportPresets._hashes:
                    exportPresets.selected = presetName
                    exportPresets.pullFromConfig()

                    try:
                        fbxPresets.selectPreset(exportPresets[OPT_GAME_FBX_PRESET])
                        fbxPresets.pushUserValues()
                    except LookupError:
                        pass

            doNotify = True

        # Notify UI elements
        if doNotify:
            UpdateAsteriskNotifier.reset()
            UpdateAsteriskNotifier().Notify(lx.symbol.fCMDNOTIFY_DATATYPE)

    def arg_UIValueHints(self, index):
        if index == 0:

            userNamesDict = exportPresets.getUserNames()
            keys = userNamesDict.keys()
            values = userNamesDict.values()

            noneName = 'None'

            # If the preset has been modified, display a star in front of the name
            if exportPresets.isModified or fbxPresets.isModified:
                index = keys.index(exportPresets.selected)
                values[index] = values[index] + '*'
                noneName = 'None*'

            notInList = lambda a: a not in ('none', 'none', 'None', 'off*', 'Off*', 'None*')

            keys = filter(notInList, keys)
            values = filter(notInList, values)

            # Generate list of two tuples where the first one contains lower case keys and the
            # second one contains the "nicer" user names.
            keys = tuple(['none'] + keys + ['new', 'store', 'remove'])
            userNames = tuple([noneName] + values + ['(New Preset)', '(Store Preset)', '(Remove Preset)'])

            return PopUp([keys, userNames])

    def cmd_NotifyAddClient(self, argument, object):
        self.notifier = self.not_svc.Spawn(FOLDERBROWSE_NOTIFIER, "")
        self.notifier.AddClient(object)

        self.fbxnotifier = self.not_svc.Spawn(t.REFRESH_ASTERISK_NOTIFIER, "")
        self.fbxnotifier.AddClient(object)

    def cmd_NotifyRemoveClient(self, object):
        self.notifier.RemoveClient(object)
        self.fbxnotifier.RemoveClient(object)

exportPresets = ExportPresets()


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

# bless() the command to register it as a plugin
lx.bless(CmdExportPresets, t.TILA_EXPORT_PRESET)

