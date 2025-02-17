#
# Created on Sat Jan 14 2023 9:57:00 PM
#
# The MIT License (MIT)
# Copyright (c) 2023 Aananth C N
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import tkinter as tk
from tkinter import ttk

import gui.ethif.ethif_gen as ethif_gen
import gui.ethif.ethif_configset as ethif_cs

import ajson.ethif.ajson_ethif as ajson_ethif
import gui.ethif.ethif_code_gen as ethif_cgen


TabList = []
EthIfConfigViewActive = False
EthIfView = []


class EthIfTab:
    tab = None
    name = None
    xsize = None
    ysize = None
    frame = None
    save_cb = None
    
    def __init__(self, f, w, h):
        self.save_cb = ethif_save_callback
        self.frame = f
        self.xsize = w
        self.ysize = h



def ethif_config_close_event(gui, view):
    global EthIfConfigViewActive

    EthIfConfigViewActive = False
    view.destroy()



def ethif_save_callback(gui):
    global EthIfView

    EthIfView.clear()
    ethif_configs = {}

    # pull all configs from UI tabs
    for tab in TabList:
        ethif_configs[tab.name] = tab.tab.configs[0].get()

    # update config to View object and then to ajson file
    EthIfView.append(ethif_configs)
    gui.save()

    # generate code
    ethif_cgen.generate_code(gui, EthIfView)


    
def show_ethif_tabs(gui):
    global EthIfConfigViewActive, TabList, EthIfView
    
    if EthIfConfigViewActive:
        return

    # Create a child window (tabbed view)
    width = gui.main_view.xsize * 50 / 100
    height = gui.main_view.ysize * 60 / 100
    view = tk.Toplevel()
    gui.main_view.child_window = view
    xoff = (gui.main_view.xsize - width)/2
    yoff = (gui.main_view.ysize - height)/3
    view.geometry("%dx%d+%d+%d" % (width, height, xoff, yoff))
    view.title("AUTOSAR Ethernet Interface Configuration Tool")
    EthIfConfigViewActive = True
    view.protocol("WM_DELETE_WINDOW", lambda: ethif_config_close_event(gui, view))
    notebook = ttk.Notebook(view)

    # Create tabs to configure EthIf
    gen_frame = ttk.Frame(notebook)
    cfg_frame = ttk.Frame(notebook)
    
    # Add tabs to configure EthIf
    notebook.add(gen_frame, text ='EthIfGeneral')
    notebook.add(cfg_frame, text ='EthIfConfigSet')
    notebook.pack(expand = 1, fill ="both")

    # destroy old GUI objects
    del TabList[:]

    # read EthIf content from A-JSON file
    EthIfView = ajson_ethif.read_ethif_configs()
    
    # create the EthIfGeneral GUI tab
    ethif_gen_view = EthIfTab(gen_frame, width, height)
    ethif_gen_view.tab = ethif_gen.EthIfGeneralView(gui, EthIfView)
    ethif_gen_view.name = "EthIfGeneral"
    TabList.append(ethif_gen_view)

    # create the EthIfGeneral GUI tab
    ethif_configset_view = EthIfTab(cfg_frame, width, height)
    ethif_configset_view.tab = ethif_cs.EthIfConfigSetView(gui, EthIfView)
    ethif_configset_view.name = "EthIfConfigSet"
    TabList.append(ethif_configset_view)

    # Draw all tabs
    ethif_gen_view.tab.draw(ethif_gen_view)
    ethif_configset_view.tab.draw(ethif_configset_view)

    # gui.main_view.child_window.bind("<<NotebookTabChanged>>", show_os_tab_switch)



# Main Entry Point
def ethif_block_click_handler(gui):
    show_ethif_tabs(gui)