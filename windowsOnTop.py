import ctypes
import sys
from ctypes import wintypes

# 检查管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行脚本"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

if not is_admin():
    print("请以管理员权限运行此脚本。")
    run_as_admin()

# 加载 user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 常量定义
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_FRAMECHANGED = 0x0020

# 函数参数设置
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowLongW.argtypes = (wintypes.HWND, ctypes.c_int)
user32.SetWindowLongW.argtypes = (wintypes.HWND, ctypes.c_int, wintypes.LONG)
user32.SetWindowPos.argtypes = (wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint)

def is_valid_window(hwnd):
    """检查窗口句柄是否有效"""
    return user32.IsWindow(hwnd) != 0

def get_window_text(hwnd):
    """获取窗口标题"""
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buffer, 256)
    return buffer.value

def get_class_name(hwnd):
    """获取窗口类名"""
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value

def is_special_window(hwnd):
    """检查窗口是否是特殊窗口（桌面、状态栏或开始菜单）"""
    class_name = get_class_name(hwnd)
    title = get_window_text(hwnd)
    return class_name in ["WorkerW", "Shell_TrayWnd", "Progman"] or title in ["", "开始", "Start"]

def toggle_topmost():
    """切换窗口置顶状态"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd or hwnd == user32.GetDesktopWindow():
        print("无法操作桌面窗口。")
        return

    if is_special_window(hwnd):
        print("无法操作特殊窗口（桌面、状态栏或开始菜单）。")
        return

    if not is_valid_window(hwnd):
        print("无效的窗口句柄。")
        return

    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if ex_style & 0x00000008:  # WS_EX_TOPMOST
        print("取消置顶")
        result = user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    else:
        print("设置置顶")
        result = user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

    if not result:
        print(f"SetWindowPos 调用失败，错误代码: {ctypes.get_last_error()}")
    else:
        print("操作成功")

def toggle_titlebar():
    """切换标题栏显示状态"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd or hwnd == user32.GetDesktopWindow():
        print("无法操作桌面窗口。")
        return

    if is_special_window(hwnd):
        print("无法操作特殊窗口（桌面、状态栏或开始菜单）。")
        return

    if not is_valid_window(hwnd):
        print("无效的窗口句柄。")
        return

    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    if style & WS_CAPTION:
        print("隐藏标题栏和边框")
        new_style = style & ~WS_CAPTION & ~WS_THICKFRAME
    else:
        print("恢复标题栏和边框")
        new_style = style | WS_CAPTION | WS_THICKFRAME

    user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED)

def toggle_click_block():
    """切换点击阻止状态"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd or hwnd == user32.GetDesktopWindow():
        print("无法操作桌面窗口。")
        return

    if is_special_window(hwnd):
        print("无法操作特殊窗口（桌面、状态栏或开始菜单）。")
        return

    if not is_valid_window(hwnd):
        print("无效的窗口句柄。")
        return

    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if ex_style & WS_EX_TRANSPARENT:
        print("恢复点击功能")
        new_style = ex_style & ~WS_EX_TRANSPARENT
    else:
        print("阻止点击功能")
        new_style = ex_style | WS_EX_TRANSPARENT | WS_EX_LAYERED

    result = user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
    if result == 0:
        print(f"SetWindowLongW 调用失败，错误代码: {ctypes.get_last_error()}")
    else:
        print("样式设置成功")

    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED)

def register_hotkeys():
    """注册全局快捷键"""
    try:
        import keyboard
        keyboard.add_hotkey('ctrl+alt+1', toggle_topmost)
        keyboard.add_hotkey('ctrl+alt+2', toggle_titlebar)
        keyboard.add_hotkey('ctrl+alt+3', toggle_click_block)
        print("快捷键已启用：")
        print("Ctrl+Alt+1 - 窗口置顶/取消")
        print("Ctrl+Alt+2 - 隐藏/显示标题栏")
        print("Ctrl+Alt+3 - 切换点击阻止")
        keyboard.wait()
    except ImportError:
        print("未安装 keyboard 模块，请运行 'pip install keyboard'")
        sys.exit()
    except Exception as e:
        print(f"发生异常：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    register_hotkeys()