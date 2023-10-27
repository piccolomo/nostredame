import os, sys

platform = 'windows' if 'win' in sys.platform else 'unix'

def set_screen_default_size(width = 2560, height = 1440):
    global width_default, height_default
    width_default = width
    height_default = height
    #get_screen_size()

# Plot Utilities
def get_screen_size():
    global width
    global height
    try:
        if platform == "unix":
            process = os.popen("xrandr -q -d :0")
            screen = process.readlines()[0]
            process.close()
            width = screen.split()[7]
            height = screen.splixt()[9][:-1]
        elif platform == "windows":
            #process = os.popen("wmic desktopmonitor get screenheight, screenwidth")
            process = os.popen("wmic PATH Win32_VideoController GET CurrentVerticalResolution,CurrentHorizontalResolution")
            lines = process.readlines()
            process.close()
            #height, width = lines[4].split()
            width, height = lines[4].split()
        else:
            height, width = None, None
        width, height = int(width), int(height)
    except:
        width, height = width_default, height_default
        print("screen size failed in " + platform + ": defaulting to", width_default, "x", height_default)
    return width, height

#set_screen_default_size()
#get_screen_size()
