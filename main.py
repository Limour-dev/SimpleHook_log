# mamba create -n SimpleHook_log python=3.10 -c conda-forge
# conda activate SimpleHook_log
# pip install Pymem -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
from mods.m05_attachprocess import getAttachProcess
from pymem import Pymem
import tkinter as tk
from tkinter import ttk
import mods.m03_windows as windows


def str2ce(_s: str, _encode):
    _hex = _s.encode(_encode).hex(sep=' ')
    return _hex


class Galgame:
    def __init__(self, _game: Pymem, _address: str, _encoding: str, _len: int = 50):
        self._game = _game
        self._address = int(_address, 16)
        self._encoding = _encoding
        self._len = _len

    def __call__(self):
        tmp = self._game.read_bytes(self._address, self._len)
        tmp = tmp.decode(self._encoding, errors='ignore')
        try:
            _idx = tmp.index('\x00')
            tmp = tmp[:_idx]
        except ValueError as e:
            print(tmp)
        tmp = tmp.rstrip('\x00')
        return tmp


class Cfg:
    encoding_list = [
        'utf-16le',
        'utf-16be',
        'shift_jis',
        'gb2312',
        'utf-8',
        'big5',
    ]
    game: Pymem
    selectedp: tuple
    n: Galgame = None
    d: Galgame = None


class Windows:
    # ===== str2ce =====
    label_str2ce: tk.Label
    ddb_str2ce: ttk.Combobox
    entry_str2ce: tk.Entry
    button_str2ce: tk.Button
    # ===== 打开进程 =====
    label_AttachProcessPID: tk.Label
    button_AttachProcess: tk.Button
    # ===== 人物 =====
    ddb_char: ttk.Combobox
    entry_char: tk.Entry
    entry_char_max_len: tk.Entry
    button_char: tk.Button
    # ===== 内容 =====
    ddb_content: ttk.Combobox
    entry_content: tk.Entry
    entry_content_max_len: tk.Entry
    button_content: tk.Button
    # ===== 显示信息 =====
    label_cb_n: tk.Label
    label_cb_d: tk.Label

    root = tk.Tk()


def ddb_encoding_list():
    _ddb = ttk.Combobox(Windows.root)
    _ddb['value'] = Cfg.encoding_list
    _ddb.current(0)
    return _ddb


# ===== 初始化窗口 =====
Windows.root.title("SimpleHook_log v0.1 " + "管理员" if windows.IsUserAnAdmin() else "非管理员")  # 窗口名
Windows.root.geometry('540x180+10+10')  # 540x180为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
Windows.root.attributes("-topmost", True)  # 设置窗口在最上层
# ===== str2ce =====
Windows.label_str2ce = tk.Label(Windows.root, text='CE转义：')
Windows.label_str2ce.grid(row=0, column=0)

Windows.ddb_str2ce = ddb_encoding_list()
Windows.ddb_str2ce.grid(row=0, column=1)

Windows.entry_str2ce = tk.Entry(Windows.root)
Windows.entry_str2ce.grid(row=0, column=2)


def button_str2ce():
    Windows.root.clipboard_clear()
    Windows.root.clipboard_append(
        str2ce(
            _s=Windows.entry_str2ce.get(),
            _encode=Windows.ddb_str2ce.get()
        )
    )


Windows.button_str2ce = tk.Button(
    Windows.root,
    text='复制到剪贴板',
    command=button_str2ce
)
Windows.button_str2ce.grid(row=0, column=3)

# ===== 打开进程 =====
Windows.label_AttachProcessPID = tk.Label(Windows.root, text=f'等待注入进程')
Windows.label_AttachProcessPID.grid(row=1, column=2)


def button_AttachProcess():
    Cfg.selectedp = getAttachProcess(Windows.root)
    Cfg.game = Pymem(Cfg.selectedp[0][0])
    Windows.label_AttachProcessPID.config(text=f'进程号:  {Cfg.selectedp[0]}')
    print(Cfg.game)


Windows.button_AttachProcess = tk.Button(Windows.root, text='注入进程', command=button_AttachProcess)
Windows.button_AttachProcess.grid(row=1, column=3)

# ===== 人物 =====
Windows.ddb_char = ddb_encoding_list()
Windows.ddb_char.grid(row=2, column=1)

Windows.entry_char = tk.Entry(Windows.root)
Windows.entry_char.grid(row=2, column=0)


@Windows.root.register
def check_digit(content):
    if content.isdigit() or content == "":
        return True
    else:
        return False


Windows.entry_char_max_len = tk.Entry(Windows.root,
                                      validate='key',
                                      textvariable=tk.StringVar(value='10'),
                                      vcmd=(check_digit, '%P'))
Windows.entry_char_max_len.grid(row=2, column=2)


def button_char():
    Cfg.n = Galgame(
        Cfg.game,
        Windows.entry_char.get(),
        Windows.ddb_char.get(),
        int(Windows.entry_char_max_len.get())
    )


Windows.button_char = tk.Button(
    Windows.root,
    text='设置人名地址',
    command=button_char
)
Windows.button_char.grid(row=2, column=3)

# ===== 内容 =====
Windows.ddb_content = ddb_encoding_list()
Windows.ddb_content.grid(row=3, column=1)

Windows.entry_content = tk.Entry(Windows.root)
Windows.entry_content.grid(row=3, column=0)

Windows.entry_content_max_len = tk.Entry(Windows.root,
                                         validate='key',
                                         textvariable=tk.StringVar(value='60'),
                                         vcmd=(check_digit, '%P'))
Windows.entry_content_max_len.grid(row=3, column=2)


def button_content():
    Cfg.d = Galgame(
        Cfg.game,
        Windows.entry_content.get(),
        Windows.ddb_content.get(),
        int(Windows.entry_content_max_len.get())
    )


Windows.button_content = tk.Button(
    Windows.root,
    text='设置内容地址',
    command=button_content
)
Windows.button_content.grid(row=3, column=3)

# ===== 时钟循环 =====
Windows.label_cb_n = tk.Label(Windows.root, text=f'旁白')
Windows.label_cb_n.grid(row=98, columnspan=4, sticky=tk.W)
Windows.label_cb_d = tk.Label(Windows.root, text=f'内容')
Windows.label_cb_d.grid(row=99, columnspan=4, sticky=tk.W)


def clock_loop():
    try:
        if Cfg.n is not None:
            Windows.label_cb_n.config(text=Cfg.n())
        if Cfg.d is not None:
            Windows.label_cb_d.config(text=Cfg.d())
    finally:
        Windows.root.after(500, clock_loop)


Windows.root.after(500, clock_loop)
# ===== 进入消息循环 =====
Windows.root.mainloop()
