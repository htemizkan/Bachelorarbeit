#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import gui_support
import os.path

from TkinterDnD2 import *

DEBUG = False

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    global prog_location
    prog_call = sys.argv[0]
    prog_location = os.path.split(prog_call)[0]

    root = TkinterDnD.Tk()
    gui_support.set_Tk_var()
    top = Toplevel1 (root)
    gui_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    global prog_location
    prog_call = sys.argv[0]
    prog_location = os.path.split(prog_call)[0]
    rt = root
    w = tk.Toplevel (root)
    gui_support.set_Tk_var()
    top = Toplevel1 (w)
    gui_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("818x841+484+136")
        top.title("Search for Labels")
        top.configure(highlightcolor="black")

        self.searchProgressbar = ttk.Progressbar(top)
        self.searchProgressbar.place(relx=0.049, rely=0.238, relwidth=0.513
                , relheight=0.0, height=19)
        self.searchProgressbar.configure(variable=gui_support.searchProgress)

        self.inFrame = tk.LabelFrame(top)
        self.inFrame.place(relx=0.037, rely=0.273, relheight=0.244
                , relwidth=0.538)
        self.inFrame.configure(relief='groove')
        self.inFrame.configure(text='''File input''')
        self.inFrame.configure(width=440)

        self.inImageButton = tk.Button(self.inFrame)
        self.inImageButton.place(relx=0.864, rely=0.244, height=21, width=40
                , bordermode='ignore')
        self.inImageButton.configure(activebackground="#f9f9f9")
        self.inImageButton.configure(command=gui_support.browseImageClick)
        self.inImageButton.configure(text='''...''')

        self.inDirectoryButton = tk.Button(self.inFrame)
        self.inDirectoryButton.place(relx=0.864, rely=0.488, height=21, width=40
                , bordermode='ignore')
        self.inDirectoryButton.configure(activebackground="#f9f9f9")
        self.inDirectoryButton.configure(command=gui_support.browseDirectoryClick)
        self.inDirectoryButton.configure(text='''...''')

        self.searchImageButton = tk.Button(self.inFrame)
        self.searchImageButton.place(relx=0.068, rely=0.683, height=51, width=181
                , bordermode='ignore')
        self.searchImageButton.configure(activebackground="#f9f9f9")
        self.searchImageButton.configure(command=gui_support.searchWithImageClick)
        self.searchImageButton.configure(text='''Search with Image''')

        self.searchImagesButton = tk.Button(self.inFrame)
        self.searchImagesButton.place(relx=0.545, rely=0.683, height=51
                , width=181, bordermode='ignore')
        self.searchImagesButton.configure(activebackground="#f9f9f9")
        self.searchImagesButton.configure(command=gui_support.searchWithDirectoryClick)
        self.searchImagesButton.configure(text='''Search with Directory''')

        self.imgPathEntry = tk.Entry(self.inFrame)
        self.imgPathEntry.place(relx=0.068, rely=0.244, height=23, relwidth=0.764
                , bordermode='ignore')
        self.imgPathEntry.configure(background="white")
        self.imgPathEntry.configure(font="TkFixedFont")
        self.imgPathEntry.configure(selectbackground="#c4c4c4")
        self.imgPathEntry.configure(textvariable=gui_support.imgPath)

        self.dirPathEntry = tk.Entry(self.inFrame)
        self.dirPathEntry.place(relx=0.068, rely=0.488, height=23, relwidth=0.764
                , bordermode='ignore')
        self.dirPathEntry.configure(background="white")
        self.dirPathEntry.configure(font="TkFixedFont")
        self.dirPathEntry.configure(selectbackground="#c4c4c4")
        self.dirPathEntry.configure(textvariable=gui_support.dirPath)

        self.imgInLabel = tk.Label(self.inFrame)
        self.imgInLabel.place(relx=0.068, rely=0.122, height=21, width=150
                , bordermode='ignore')
        self.imgInLabel.configure(activebackground="#f9f9f9")
        self.imgInLabel.configure(text='''Choose an image file :''')

        self.dirInLabel = tk.Label(self.inFrame)
        self.dirInLabel.place(relx=0.068, rely=0.366, height=21, width=130
                , bordermode='ignore')
        self.dirInLabel.configure(activebackground="#f9f9f9")
        self.dirInLabel.configure(text='''Choose a directory:''')

        self.resultsFrame = tk.LabelFrame(top)
        self.resultsFrame.place(relx=0.587, rely=0.012, relheight=0.505
                , relwidth=0.391)
        self.resultsFrame.configure(relief='groove')
        self.resultsFrame.configure(text='''Results''')
        self.resultsFrame.configure(width=320)

        self.style.configure('Treeview.Heading',  font="TkDefaultFont")
        self.resultsScrolledtreeview = ScrolledTreeView(self.resultsFrame)
        self.resultsScrolledtreeview.place(relx=0.031, rely=0.047
                , relheight=0.826, relwidth=0.938, bordermode='ignore')
        # build_treeview_support starting.
        self.resultsScrolledtreeview.heading("#0",text="Files")
        self.resultsScrolledtreeview.heading("#0",anchor="center")
        self.resultsScrolledtreeview.column("#0",width="286")
        self.resultsScrolledtreeview.column("#0",minwidth="20")
        self.resultsScrolledtreeview.column("#0",stretch="1")
        self.resultsScrolledtreeview.column("#0",anchor="w")
        if DEBUG == True:
            # creating an example tree for debug purposses:
            node = self.resultsScrolledtreeview.insert("", "end", text="pictures1", values = [ 'dir_path', 'directory'])
            # Level 1
            folder = self.resultsScrolledtreeview.insert(node, "end", text="pictures2", values = [ 'dir_path', 'directory'])
            # Level 2
            #image = self.resultsScrolledtreeview.insert(folder, "end", text="picture1", values = [ 'dir_path', 'image'])
            self.resultsScrolledtreeview.insert(folder, "end", text="picture2", values = [ 'dir_path', 'image'])
            self.resultsScrolledtreeview.insert(folder, "end", text="picture3", values = [ 'dir_path', 'image'])
            self.resultsScrolledtreeview.insert(folder, "end", text="picture4", values = [ 'dir_path', 'image'])
            # Level 3
            self.resultsScrolledtreeview.insert(image, "end", text="result1", values = [ 'dir_path', 'result'])
            self.resultsScrolledtreeview.insert(image, "end", text="result2", values = [ 'dir_path', 'result'])
            self.resultsScrolledtreeview.insert(image, "end", text="result3", values = [ 'dir_path', 'result'])
            self.resultsScrolledtreeview.insert(image, "end", text="result4", values = [ 'dir_path', 'result'])
            self.resultsScrolledtreeview.insert(image, "end", text="result5", values = [ 'dir_path', 'result'])
            self.resultsScrolledtreeview.get_children()

        self.exportTreeButton = tk.Button(self.resultsFrame)
        self.exportTreeButton.place(relx=0.031, rely=0.894, height=31, width=141
                , bordermode='ignore')
        self.exportTreeButton.configure(command=gui_support.exportTreeClick)
        self.exportTreeButton.configure(text='''Export as tree''')
        self.exportTreeButton.configure(width=141)

        self.exportJsonButton = tk.Button(self.resultsFrame)
        self.exportJsonButton.place(relx=0.531, rely=0.894, height=31, width=141
                , bordermode = 'ignore')
        self.exportJsonButton.configure(command=gui_support.exportJsonClick)
        self.exportJsonButton.configure(text='''Export as json''')
        self.exportJsonButton.configure(width=141)

        self.progressLabel = tk.Label(top)
        self.progressLabel.place(relx=0.049, rely=0.202, height=21, width=64)
        self.progressLabel.configure(activebackground="#f9f9f9")
        self.progressLabel.configure(text='''Progress:''')

        self.selectedImageFrame = tk.LabelFrame(top)
        self.selectedImageFrame.place(relx=0.477, rely=0.535, relheight=0.422
                , relwidth=0.501)
        self.selectedImageFrame.configure(relief='groove')
        self.selectedImageFrame.configure(text='''Selected Image''')
        self.selectedImageFrame.configure(width=410)

        self.selectedImageLabel = tk.Label(self.selectedImageFrame)
        self.selectedImageLabel.place(relx=0.049, rely=0.085, height=311
                , width=379, bordermode='ignore')
        self.selectedImageLabel.configure(activebackground="#f9f9f9")
        self.selectedImageLabel.pack(side="bottom", fill="both", expand="yes")
        self.selectedImageLabel.configure(image= gui_support.imageFile)


        self.dragAndDropFrame = tk.LabelFrame(top)
        self.dragAndDropFrame.place(relx=0.037, rely=0.535, relheight=0.422
                , relwidth=0.428)
        self.dragAndDropFrame.configure(relief='groove')
        self.dragAndDropFrame.configure(text='''Drag & Drop''')
        self.dragAndDropFrame.configure(width=350)

        self.dragAndDropImageLabel = tk.Label(top)
        self.dragAndDropImageLabel.place(relx=0.049, rely=0.559, height=321, width=329)
        self.dragAndDropImageLabel.configure(activebackground="#f9f9f9")
        photo_location = os.path.join(prog_location,"Drag.png")
        global _img0
        _img0 = tk.PhotoImage(file=photo_location)
        self.dragAndDropImageLabel.configure(image=_img0)
        self.dragAndDropImageLabel.drop_target_register(DND_FILES)
        self.dragAndDropImageLabel.dnd_bind('<<Drop>>', gui_support.drop)

        self.searchImgLabel = tk.Label(top)
        self.searchImgLabel.place(relx=0.037, rely=0.036, height=141, width=429)
        self.searchImgLabel.configure(activebackground="#f9f9f9")
        photo_location = os.path.join(prog_location,"search_objects.gif")
        global _img1
        _img1 = tk.PhotoImage(file=photo_location)
        self.searchImgLabel.configure(image=_img1)

        self.Message1 = tk.Message(top)
        self.Message1.place(relx=0.171, rely=0.963, relheight=0.03
                , relwidth=0.663)
        self.Message1.configure(text='''Console''')
        self.Message1.configure(textvariable=gui_support.consoleText)
        self.Message1.configure(width=542)

# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        else:
            methods = tk.Pack.__dict__.keys() + tk.Grid.__dict__.keys() \
                  + tk.Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledTreeView(AutoScroll, ttk.Treeview):
    '''A standard ttk Treeview widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')

if __name__ == '__main__':
    vp_start_gui()





