import ctypes
import os
import time
import psutil
import win32gui
import win32process
from ctypes import wintypes
from PIL import Image

user32 = ctypes.windll.user32

cursor_types = [
    32512,  # arrow
    32513,  # ibeam
    32514,  # wait
    32515,  # cross
    32516,  # arrow facing upwards
    32642,  # resize northwest-southeast
    32643,  # resize northeast-southwest
    32644,  # resize west-east
    32645,  # resize north-south
    32646,  # resize
    32648,  # no
    32649,  # hand
    32650,  # wait
    32651   # help
]

load_cursor_from_file = 0x0010
cursor_image = 2
restore_cursors = 0x0057


class CursorInfo(ctypes.Structure):
    _fields_ = [
        ("is_icon", wintypes.BOOL),
        ("hotspot_x", wintypes.DWORD),
        ("hotspot_y", wintypes.DWORD),
        ("mask", wintypes.HANDLE),
        ("color", wintypes.HANDLE),
    ]


folder = os.path.dirname(os.path.abspath(__file__))

cursor_file = os.path.join(folder, "cursor.cur")
png_file = os.path.join(folder, "cursor.png")


def convert_png_to_cursor():
    image = Image.open(png_file).convert("RGBA")

    # Windows cursors are usually 32x32 or 64x64
    image.save(
        cursor_file,
        format="CUR",
        sizes=[(image.width, image.height)]
    )

    print("converted cursor.png into cursor.cur")


if not os.path.exists(cursor_file):
    if os.path.exists(png_file):
        convert_png_to_cursor()
    else:
        raise FileNotFoundError(
            "could not find cursor.cur or cursor.png"
        )


def load_cursor():
    loaded_cursor = user32.LoadImageW(
        None,
        cursor_file,
        cursor_image,
        0,
        0,
        load_cursor_from_file
    )

    if not loaded_cursor:
        return None

    cursor_info = CursorInfo()

    if not user32.GetIconInfo(
        loaded_cursor,
        ctypes.byref(cursor_info)
    ):
        return None

    # make click point top-left
    cursor_info.hotspot_x = 0
    cursor_info.hotspot_y = 0

    return user32.CreateIconIndirect(
        ctypes.byref(cursor_info)
    )


def change_cursor():
    for cursor_type in cursor_types:
        cursor = load_cursor()

        if cursor:
            user32.SetSystemCursor(
                cursor,
                cursor_type
            )


def reset_cursor():
    user32.SystemParametersInfoW(
        restore_cursors,
        0,
        None,
        0
    )


def vortex_is_open():
    window = win32gui.GetForegroundWindow()

    if not window:
        return False

    try:
        _, process_id = win32process.GetWindowThreadProcessId(window)
        process = psutil.Process(process_id)

        return process.name().lower() == "vortex.exe"

    except:
        return False


cursor_active = False

print("cursor changer running...")
print("press ctrl+c to stop.")

try:
    while True:
        if vortex_is_open():
            if not cursor_active:
                change_cursor()
                cursor_active = True
                print("vortex cursor enabled")

        else:
            if cursor_active:
                reset_cursor()
                cursor_active = False
                print("restored original cursor")

        time.sleep(0.1)

except KeyboardInterrupt:
    reset_cursor()
    print("exiting")