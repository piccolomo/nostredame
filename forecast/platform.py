import os, sys


platform = 'windows' if  sys.platform in ['win32', 'cygwin'] else 'unix'


# Plot Utilities
def get_screen_size():
    try:
        if platform == "unix":
            process = os.popen("xrandr -q -d :0")
            screen = process.readlines()[0]
            process.close()
            width = screen.split()[7]
            height = screen.split()[9][:-1]
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
        width, height = 2560, 1440
        print("screen size failed in " + platform + ": defaulting to", width, "x", height)
    return width, height
