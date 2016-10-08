import lx
import os
import sys
import subprocess

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
    try:
        lx.eval('dialog.setup {%s}' % type)
        lx.eval('dialog.title {%s}' % title)
        lx.eval('dialog.msg {%s}' % message)
        lx.eval('dialog.open')

        if type == 'okCancel' \
                or type == 'yesNo' \
                or type == 'yesNoCancel' \
                or type == 'yesNoAll' \
                or type == 'yesNoToAll' \
                or type == 'saveOK' \
                or type == 'fileOpen' \
                or type == 'fileOpenMulti' \
                or type == 'fileSave' \
                or type == 'dir':
            return lx.eval('dialog.result ?')

    except:
        if type == 'okCancel' \
                or type == 'yesNo' \
                or type == 'yesNoCancel' \
                or type == 'yesNoAll' \
                or type == 'yesNoToAll' \
                or type == 'saveOK' \
                or type == 'fileOpen' \
                or type == 'fileOpenMulti' \
                or type == 'fileSave' \
                or type == 'dir':
            return lx.eval('dialog.result ?')

# Dialog initialisation

def init_dialog(dialog_type, currPath):
    if dialog_type == "input":
        # Get the directory to export to.
        lx.eval('dialog.setup fileOpenMulti')
        lx.eval('dialog.fileType scene')
        lx.eval('dialog.title "Mesh Path"')
        lx.eval('dialog.msg "Select the meshes you want to process."')
        lx.eval('dialog.result "%s"' % currPath)

    if dialog_type == "output":
        # Get the directory to export to.
        lx.eval('dialog.setup dir')
        lx.eval('dialog.title "Export Path"')
        lx.eval('dialog.msg "Select path to export to."')
        lx.eval('dialog.result "%s"' % currPath)

    if dialog_type == 'file_save':
        init_custom_dialog('fileSave', 'SaveFile', ('FBX',), 'FBX file', ('*.FBX',), 'fbx', currPath[:-4])

    if dialog_type == "cancel":
        init_message('error', 'Canceled', 'Operation aborded')
        sys.exit()


def ask_before_override(filename):
    return init_message('yesNoAll', 'File already exist', 'Do you want to override %s ?' % filename)
