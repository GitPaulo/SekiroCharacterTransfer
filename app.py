import hashlib
import tkinter as gui
from tkinter import filedialog as fd

# == Vars

LARGE_FONT = ("Verdana", 16)
NORM_FONT  = ("Helvetica", 10)
SMALL_FONT = ("Helvetica", 8)

save_overwrite = 0
steamid_copy   = 0

source_save = False
target_save = False

save_regions = {
    "Checksum": [0x300, 0x30F],
    "Checksum_Area": [0x310, 0x10030F],
    "SteamID": [0x34164, 0x3416B],
    "Character": [0x16140, 0xA0F5F]
}

# == Functions

def getRegion(id, char_size=2):
    temp = save_regions.get(id)
    return (temp[0]*char_size, temp[1]*char_size + 2)

def center(win):
    win.update_idletasks()

    width     = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height    = win.winfo_height()
    
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height      = height + titlebar_height + frm_width
    
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def popup(msg, title='Error'):
    popup = gui.Tk()
    popup.wm_title(title)
    
    label = gui.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", pady=15, padx=15)
    
    button = gui.Button(popup, text="Okay", command = popup.destroy)
    button.pack(pady=15)
    
    center(popup)
    popup.mainloop()

def loadSave(file_name):
    with open(file_name, 'rb') as f:
        return f.read().hex()

def openSave():
    file = fd.askopenfilename(
        initialdir =  "./", 
        title = "Select Sekiro Save File", 
        filetype = (("Sekiro Save", "*.sl2"), ("All Files", "*.*")) 
    )

    return file

def requestSourceSave():
    global source_save 
    source_save = openSave()
    source_text.delete(1.0, gui.END)
    source_text.insert(gui.END, source_save or '<no file opened>')

def requestTargetSave():
    global target_save 
    target_save = openSave()
    target_text.delete(1.0, gui.END)
    target_text.insert(gui.END, target_save or '<no file opened>')

def transferSave():
    if not source_save:
        return popup('Character save has not been loaded.')

    if not target_save:
        return popup('Destination save has not been loaded')

    if source_save == target_save:
        return popup('Saves must not be the same.')

    source_data = loadSave(source_save)
    target_data = loadSave(target_save)

    # Useful
    original_length = len(target_data)

    # Copy steam id
    if steamid_copy == 1:
        sid_region  = getRegion('SteamID')
        new_sid     = source_data[sid_region[0]:sid_region[1]]
        target_data = target_data[:sid_region[0]] + new_sid + target_data[sid_region[1]:]
    
    # Character copy
    char_region = getRegion('Character')
    new_char    = source_data[char_region[0]:char_region[1]]
    target_data = target_data[:char_region[0]] + new_char + target_data[char_region[1]:]

    # MD5
    ca_region = getRegion('Checksum_Area')
    area_data = target_data[ca_region[0]:ca_region[1]]
    checksum  = hashlib.md5(area_data.encode()).hexdigest()

    # Place checksum
    cs_region   = getRegion('Checksum')
    target_data = target_data[:cs_region[0]] + checksum + target_data[cs_region[1]:]

    # Length Check
    if original_length != len(target_data):
        return popup('Something went wrong?\n' + original_length + ' and ' + len(target_data))

    # New Save
    new_save_file = open("new_save.sl2", "wb")
    new_save_file.write(bytes.fromhex(target_data))
    new_save_file.close()

    if save_overwrite == 1:
        return popup('Not working rn.')
    
    popup(
        "Completed character transfer from: \n'" + source_save + "' => '" + target_save + "'\n"
        + "Sekiro save file overwritten!" if save_overwrite == 1 else "Save can be found at: " + save_file,
        'Transfer Completed!'
    )


# == Main Logic

window = gui.Tk()
window.title("SCT") 

label = gui.Label(window, text="\n  Sekiro Character Transfer  \n", font=LARGE_FONT)
label.pack() 

source_button = gui.Button(window, text="Character Save", fg="blue", command=requestSourceSave)
source_button.pack()

source_text = gui.Text(window, height=1, width=30)
source_text.insert(gui.END, '<no file selected>')
source_text.pack(pady=15)

target_button = gui.Button(window, text="Destination Save", fg="blue", command=requestTargetSave)
target_button.pack()

target_text = gui.Text(window, height=1, width=30)
target_text.insert(gui.END, '<no file selected>')
target_text.pack(pady=15) 

save_overwrite  = gui.IntVar()
overwrite_check = gui.Checkbutton(window, text="Overwrite current sekiro save?", variable=save_overwrite, onvalue=1, offvalue=0)
overwrite_check.pack(pady=5)

steamid_copy  = gui.IntVar(value=1)
steamid_check = gui.Checkbutton(window, text="Transfer steam id?", variable=steamid_copy, onvalue=1, offvalue=0)
steamid_check.pack()

transfer_button = gui.Button(window, text="Transfer", fg="green", command=transferSave)
transfer_button.pack(pady=15)

center(window)
window.tk.call('wm', 'iconphoto', window._w, gui.PhotoImage(file='./assets/sicon.png'))
window.mainloop()