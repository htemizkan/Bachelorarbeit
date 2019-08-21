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

#adding other imports
from tkFileDialog import *
from PIL import ImageTk, Image
import search_labels
import os
import imghdr
import math
import json

FILE_TYPES = [("jpeg",".jpeg"),("gif",".gif"),("png",".png"),("jpg",".jpg")]

def set_Tk_var():
    global searchProgress
    searchProgress = tk.IntVar()
    global imgPath
    imgPath = tk.StringVar()
    #adding
    global dirPath
    dirPath = tk.StringVar()
    global imageFile
    imageFile = None
    global consoleText
    consoleText = tk.StringVar()
    consoleText.set('')
    global folderIcon
    folderIcon = tk.PhotoImage(file='folder.gif')
    global imageIcon
    imageIcon = tk.PhotoImage(file = 'img_icon.gif')
    global start_node
    start_node = ""
    global text
    text = []
    global data
    data = {}


def browseDirectoryClick():
    print('gui_support.browseDirectoryClick')

    directoryPath = askdirectory(initialdir='.', parent=w.inFrame, title='select a directory')

    if (directoryPath):
        if os.path.isdir(directoryPath):
            print("yes this is a directory")
            dirPath.set(directoryPath)
            show_image("folder_big.gif")

    sys.stdout.flush()

def browseImageClick():
    print('gui_support.browseImageClick')

    filePath = askopenfilename(defaultextension='*',
                                initialdir='.', initialfile='', parent=w.inFrame, title='select an image', filetypes=FILE_TYPES)

    if(filePath):
        if os.path.isfile(filePath):
            print("Yes this is a file")
            for t in FILE_TYPES:
                for e in t:
                    if e is imghdr.what(filePath):
                        print("yes this is an image file!")
                        imgPath.set(filePath)
                        show_image(filePath)
    sys.stdout.flush()

def show_image(filePath):
    global imageFile
    #imageFile = tk.PhotoImage(file=filePath)

    image = Image.open(filePath)
    image = image.resize((300, 300), Image.ANTIALIAS)  ## The (300, 300) is (height, width)

    imageFile = ImageTk.PhotoImage(image)

    w.selectedImageLabel.configure(image = imageFile)

def exportTreeClick():
    print('gui_support.exportTreeClick')

    f = asksaveasfile(defaultextension='*',
                                initialdir='.', initialfile='', parent=w.resultsFrame, title='select the file path', confirmoverwrite=True, filetypes=[("text",".txt")], typevariable='')

    if f is None:
        return

    tree_to_string(start_node, w.resultsScrolledtreeview)

    f.write(''.join(text))
    f.close()

    sys.stdout.flush()

def exportJsonClick():
    print('gui_support.exportJsonClick')

    f = asksaveasfile(defaultextension='*',
                                initialdir='.', initialfile='', parent=w.resultsFrame, title='select the file path', confirmoverwrite=True, filetypes=[("json",".json")], typevariable='')

    if f is None:
        return

    tree_to_dict(start_node, w.resultsScrolledtreeview, data)


    json.dump(data, f, indent=8)
    f.close()
    data.clear()

    sys.stdout.flush()

def tree_to_dict(parent, tree, node):
    nd = tree.item(parent)
    n_text = nd['text']

    #if bool(nd['value'])
    #    n_type = nd['value'][1]

    if parent != "" :
        n_type = nd['values'][1]
        if n_type == 'directory':
            node[n_text] = {}
        elif n_type == 'image' and isinstance(node, dict):
            node[n_text] = []
        elif n_type == 'result' and isinstance(node, list):
            node.append(n_text)

    for child in tree.get_children(parent):
        if(bool(node)):
            tree_to_dict(child, tree, node[n_text])
        else:
            tree_to_dict(child, tree, node)

def tree_to_string(parent, tree, indent=''):

    nd = tree.item(parent)
    n_text = nd['text']

    if parent != "" :
        print("+" + n_text)
        text.append("+" + n_text + "\n")

    shift = math.ceil(math.log10(len(n_text))) \
            if len(n_text) >= 2 else 1
    indent += ' ' * int(shift)

    for child in tree.get_children(parent)[:-1]:
        nd = tree.item(child)
        n_text = nd['text']
        print(indent + '|' + '-' * 4),
        text.append(indent + '|' + '-' * 4)
        tree_to_string(child, tree, indent + '|' + ' ' * 4)

    if(tree.get_children(parent)):
        child = tree.get_children(parent)[-1]
        print(indent + '`' + '-' * 4),
        text.append(indent + '`' + '-' * 4)
        tree_to_string(child, tree, indent + ' ' * 4)

def searchWithDirectoryClick():
    print('gui_support.searchWithDirectoryClick')

    if(dirPath.get()):
        w.searchProgressbar['value'] = 0
        node = ""
        searchWithDirectory(dirPath.get(),node)

    sys.stdout.flush()

def searchWithDirectory(path,node):

    fPaths = []
    imCount = 0
    results = []

    fList = os.listdir(path)
    fList.sort()

    for f in fList:
        str_var = path + '/' + f
        fPaths.append(os.path.join(path,f))

    for f in fPaths:
        if isImage(f):
         imCount += 1


    for f in fPaths:
        if isImage(f):
            results.append(se.run(path=f))
            w.searchProgressbar['value'] = (w.searchProgressbar['value'] + int(100 / imCount))
        else:
            print("No image found")

    node = insert_results(results, path, node = node)

    for f in fPaths:
        if os.path.isdir(f):
            searchWithDirectory(f,node)

    return node

def isImage(file):
    if os.path.isfile(file):
        print("Yes this is a file")
        for t in FILE_TYPES:
            for e in t:
                if e is imghdr.what(file):
                    return True
    else:
        print("This one is a problem : " + file)
        print("This is not a valid image file!")
        return False

def searchWithImageClick():
    searchProgress.set(0)
    print('gui_support.searchWithImageClick')

    if (os.path.isfile(imgPath.get())):
        result = search_labels.Result()
        result = se.run(path = imgPath.get(), progress=searchProgress, top = root)
        insert_result(result)

    sys.stdout.flush()

def drop(event):

    #White space are couising path to be recognized as list of paths.
    #To solve this replacing curly bracets with ""
    path = replace_cbracets(event.data)
    print("new path:" + path)

    if os.path.isdir(path):
        print("yes this is a directory")
        dirPath.set(path)
        show_image("folder_big.gif")
    elif os.path.isfile(path):
        print("Yes this is a file")
        for t in FILE_TYPES:
            for e in t:
                if e is imghdr.what(path):
                    print("yes this is an image file!")
                    imgPath.set(path)
                    show_image(path)
    else:
        print("This is not an image or directory!")

    #w.dragAndDropImageLabel.configure(image=imageFile)
    #print('Data:', event.data)
    #print_event_info(event)

def replace_cbracets(data):
    return data.replace("{", "").replace("}", "")

def escape_whitespace(path):
    list = []
    for x in split(path):
        if x.isspace():
            print " yes it is a space"
            list.append("\\" + x)

        else:
            list.append(x)
    print("result path : " + ''.join(list))
    return ''.join(list)

def split(word):
    return [char for char in word]

def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

    #added initialize main program
    global se
    se = search_labels.SearchEngine()

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

def insert_results(results, dir_name, **kwargs):
    # result has the filename as first element
    # and a list of labels named labels

    if('node' in kwargs):
        node = kwargs['node']
    else:
        node = ""

    # Level 1
    folder_node = w.resultsScrolledtreeview.insert(node, "end", text=os.path.basename(dir_name), values = [ dir_name, 'directory'], image=folderIcon)
    # Level 2
    for result in results:
        if(isinstance(result, list)):
            #insert_results(result, dir_name, node = folder_node)
            pass
        else:
            insert_result(result, node = folder_node)

    print("folder node : " + folder_node)
    return folder_node


def insert_result(result, **kwargs):

    if('node' in kwargs):
        node = kwargs['node']
    else:
        node = ""

    # Level 1
    image = w.resultsScrolledtreeview.insert(node, "end", text=result.fileName, values = [ result.fileName, 'image'], image=imageIcon)
    # Level 2
    for label in result.labels:
        w.resultsScrolledtreeview.insert(image, "end", text=label, values = [ label, 'result'])


if __name__ == '__main__':
    import gui
    gui.vp_start_gui()




