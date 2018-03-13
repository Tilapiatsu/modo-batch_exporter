import lx
import os
import sys
import subprocess
from Tila_BatchExportModule import helper

dialogFormatType = {'LXO':[('LXO',), 'Modo scene LXO file', ('*.LXO',), 'lxo'],
                    'LWO':[('LWO',), 'Lightwave scene LWO file', ('*.LWO',), 'lwo'],
                    'FBX':[('FBX',), 'FBX file', ('*.FBX',), 'fbx'],
                    'OBJ':[('OBJ',), 'Wavefront OBJ file', ('*.OBJ',), 'obj'],
                    'STL':[('STL',), 'Stereolithography STL file', ('*.STL',), 'stl'],
                    'ABC':[('ABC',), 'Alembic file', ('*.ABC',), 'acb'],
                    'ABC-HDF':[('ABC',), 'Alembic(HDF) file', ('*.ABC',), 'acb'],
                    'DAE':[('DAE',), 'Collada file', ('*.DAE',), 'dae'],
                    'DXF':[('DXF',), 'DXF file', ('*.DXF',), 'dxf'],
                    '3DM':[('3DM',), 'Rhino 3DM file', ('*.3DM',), '3dm'],
                    'GEO':[('GEO',), 'VideoScape GEO file', ('*.GEO',), 'geo'],
                    'X3D':[('X3D',), 'Web3D Standard X3D file', ('*.X3D',), 'x3d'],
                    'SVG':[('SVG',), 'Scalable Vector Graphics file', ('*.SVG',), 'svg'],
                    'PLT':[('PTL',), 'HPGL Plotter file', ('*.PTL',), 'ptl']}

if sys.platform == 'darwin':
    def open_folder(path):
        subprocess.check_call(['open', '--', path])

elif sys.platform == 'linux2':
    def open_folder(path):
        subprocess.check_call(['xdg-open', '--', path])

elif sys.platform == 'win32':
    def open_folder(path):
        os.startfile(path)
        print_log('Opening path : ' + path)


def parentPath(path):
    return os.path.abspath(os.path.join(path, os.pardir))

# Print Method


def print_log(message):
    lx.out("TILA_BATCH_EXPORT : " + message)


def transform_log(message):
    print_log("Transform_Item : " + message)


def processing_log(message):
    print_log("Processing_Item : " + message)


def export_log(message):
    print_log("Exporting_File : " + message)


def begining_log(self):
    print_log('')
    print_log('----------------------------------------------------------------------------------------------------')
    text = " "
    if not self.exportFile_sw:
        text += 'TRANSFORM '
    else:
        text += 'EXPORT '
    text += 'SELECTION'
    print_log('--------------------------------------- ' + text + ' STARTED------------------------------------------')
    print_log('----------------------------------------------------------------------------------------------------')


def ending_log(self):
    print_log('----------------------------------------------------------------------------------------------------')
    text = " "
    if not self.exportFile_sw:
        text += 'TRANSFORM '
    else:
        text += 'EXPORT '
    text += 'SELECTION'
    print_log('---------------------------------------- ' + text + ' FINISHED-------------------------------------------')
    print_log('----------------------------------------------------------------------------------------------------')
    print_log('')


# http://modo.sdk.thefoundry.co.uk/wiki/Dialog_Commands
def init_custom_dialog(type, title, format, uname, ext, save_ext=None, path=None, init_dialog=False):
    ''' Custom file dialog wrapper function

        type  :   Type of dialog, string value, options are 'fileOpen' or 'fileSave'
        title :   Dialog title, string value.
        format:   file format, tuple of string values
        uname :   internal name
        ext   :   tuple of file extension filter strings
        save_ext: output file extension for fileSave dialog
        path  :   optional default loacation to open dialog

    '''
    lx.eval("dialog.setup %s" % type)
    lx.eval("dialog.title {%s}" % title)
    lx.eval("dialog.fileTypeCustom {%s} {%s} {%s} {%s}" % (format, uname, ext, save_ext))
    if type == 'fileSave' and save_ext != None:
        lx.eval("dialog.fileSaveFormat %s extension" % save_ext)
    if path is not None:
        lx.eval('dialog.result {%s}' % path)

    if init_dialog:
        try:
            lx.eval("dialog.open")
            return lx.eval("dialog.result ?")
        except:
            return None


def init_message(type, title, message):
    return_result = type == 'okCancel' \
                    or type == 'yesNo' \
                    or type == 'yesNoCancel' \
                    or type == 'yesNoAll' \
                    or type == 'yesNoToAll' \
                    or type == 'saveOK' \
                    or type == 'fileOpen' \
                    or type == 'fileOpenMulti' \
                    or type == 'fileSave' \
                    or type == 'dir'
    try:
        lx.eval('dialog.setup {%s}' % type)
        lx.eval('dialog.title {%s}' % title)
        lx.eval('dialog.msg {%s}' % message)
        lx.eval('dialog.open')

        if return_result:
            return lx.eval('dialog.result ?')

    except:
        if return_result:
            return lx.eval('dialog.result ?')

# Dialog initialisation

def init_dialog(dialog_type, currPath, format=None):
    if dialog_type == "input":
        # Get the directory to export to.
        lx.eval('dialog.setup fileOpenMulti')
        lx.eval('dialog.fileType scene')
        lx.eval('dialog.title "Mesh Path"')
        lx.eval('dialog.msg "Select the meshes you want to process."')
        lx.eval('dialog.result "%s"' % currPath)

    if dialog_type == "input_path":
        # Get the directory to Open.
        lx.eval('dialog.setup dir')
        lx.eval('dialog.title "Open Path"')
        lx.eval('dialog.msg "Select path to process."')
        lx.eval('dialog.result "%s"' % currPath)

    if dialog_type == "output":
        # Get the directory to export to.
        lx.eval('dialog.setup dir')
        lx.eval('dialog.title "Export Path"')
        lx.eval('dialog.msg "Select path to export to."')
        lx.eval('dialog.result "%s"' % currPath)

    if dialog_type == 'filesave':
        if format is None:
            print 'Unspecified format'
            sys.exit()
        else:
            init_custom_dialog('fileSave', 'SaveFile', format[0], format[1], format[2], format[3], currPath)

    if dialog_type == "cancel":
        #init_message('error', 'Canceled', 'Operation aborded')
        sys.exit()


def ask_before_override(filename):
    return init_message('yesNoAll', 'File already exist', 'Do you want to override %s ?' % filename)


def init_progress_bar(itemCount, message):
    dialog_svc = lx.service.StdDialog()
    mymonitor = lx.object.Monitor(dialog_svc.MonitorAllocate(message))
    mymonitor.Initialize(itemCount)
    return mymonitor, dialog_svc


def increment_progress_bar(self, monitor, progression, transform=False):
    try:
        monitor.Increment(1)
        progression[0] += 1
        return True
    except:
        if transform:
            helper.safe_select(self.proceededMesh)
            lx.eval('!!item.delete')

        lx.service.StdDialog().MonitorRelease()
        return False


def update_progression_message(message, progression):
    monitor = init_progress_bar(progression[1], str(progression[0]) + ' / ' + str(progression[1]) + ' || ' + message)
    return monitor


def deallocate_dialog_svc(dialog_svc):
    dialog_svc.MonitorRelease()

def textInputDialog(title):
    """Opens a text input dialog and returns it. When None is returned it means the user cancelled the dialog."""

    # Create a random name for the transient user value
    import tempfile
    randname = tempfile._RandomNameSequence().next()

    # Create a lambda shortcut for executing commands to save some typing
    cmdSvc = lx.service.Command()
    execCmd = lambda text : cmdSvc.ExecuteArgString(-1, lx.symbol.iCTAG_NULL, text)

    # Create a transient user value to use as text input dialog
    execCmd( 'user.defNew %s string' % randname )
    execCmd( 'user.def %s transient true' % randname )
    execCmd( 'user.def %s username "%s"' % (randname, title) )

    # Show the modal input dialog
    try:
        execCmd( 'user.value %s' % randname )
    except RuntimeError:

        # User cancelled
        return None

    # Fetch and return the user value's string content
    uservalue = lx.service.ScriptSys().UserValueLookup(randname)
    result = uservalue.GetString()

    return result