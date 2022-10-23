#
# Created on Wed Oct 20 2022 9:51:55 PM
#
# The MIT License (MIT)
# Copyright (c) 2022 Aananth C N
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

import gui.lib.window as window
import gui.lib.asr_widget as dappa # dappa in Tamil means box




class SpiExternalDeviceTab:
    n_spi_extdev = 0
    max_spi_extdev = 255
    n_spi_extdev_str = None

    gui = None
    tab_struct = None # passed from *_view.py file
    scrollw = None
    configs = None # all UI configs (tkinter strings) are stored here.
    cfgkeys = ["SpiHwUnit", "SpiBaudrate", "SpiDataShiftEdge", "SpiShiftClockIdleLevel", "SpiEnableCs", "SpiCsIdentifier",
               "SpiCsSelection", "SpiCsPolarity", "SpiTimeClk2Cs", "SpiTimeCs2Clk", "SpiTimeCs2Cs"]
    
    n_header_objs = 0 #Objects / widgets that are part of the header and shouldn't be destroyed
    header_row = 3
    non_header_objs = []
    dappas_per_row = len(cfgkeys) + 1 # +1 for row labels
    init_view_done = False


    def __init__(self, gui, spidrvtab, spijobtab, ar_cfg):
        self.gui = gui
        self.configs = []
        self.n_spi_extdev = 0
        self.n_spi_extdev_str = tk.StringVar()
        self.spidrvtab = spidrvtab
        self.spijobtab = spijobtab

        if ar_cfg["SpiExternalDevice"] == None:
            return
        for dev in ar_cfg["SpiExternalDevice"]:
            self.configs.insert(len(self.configs), dappa.AsrCfgStr(self.cfgkeys, dev))
            self.n_spi_extdev += 1
        self.n_spi_extdev_str.set(self.n_spi_extdev)


    def __del__(self):
        del self.n_spi_extdev_str
        del self.non_header_objs[:]
        del self.configs[:]



    def create_empty_configs(self):
        spi_extdev = {}
        spi_extdev["SpiHwUnit"] = "CSIB"+str(self.n_spi_extdev-1)
        spi_extdev["SpiBaudrate"] = "1000000.0"
        spi_extdev["SpiDataShiftEdge"] = "LEADING"
        spi_extdev["SpiShiftClockIdleLevel"] = "LOW"
        spi_extdev["SpiEnableCs"] = "FALSE"
        spi_extdev["SpiCsIdentifier"] = "CS_"
        spi_extdev["SpiCsSelection"] = "CS_VIA_PERIPHERAL_ENGINE"
        spi_extdev["SpiCsPolarity"] = "LOW"
        spi_extdev["SpiTimeClk2Cs"] = "0.0"
        spi_extdev["SpiTimeCs2Clk"] = "0.000001" # 1usec
        spi_extdev["SpiTimeCs2Cs"]  = "0.000001" # 1usec
        return spi_extdev



    def draw_dappa_row(self, i):
        dappa.label(self, "Spi Dev. #", self.header_row+i, 0, "e")
        dappa.entry(self, "SpiHwUnit", i, self.header_row+i, 1, 10, "normal")
        dappa.entry(self, "SpiBaudrate", i, self.header_row+i, 2, 15, "normal")
        dappa.combo(self, "SpiDataShiftEdge", i, self.header_row+i, 3, 18, ("LEADING", "TRAILING"))
        dappa.combo(self, "SpiShiftClockIdleLevel", i, self.header_row+i, 4, 13, ("LOW", "HIGH"))
        dappa.combo(self, "SpiEnableCs", i, self.header_row+i, 5, 13, ("FALSE", "TRUE"))
        dappa.entry(self, "SpiCsIdentifier", i, self.header_row+i, 6, 23, "normal")
        dappa.combo(self, "SpiCsSelection", i, self.header_row+i, 7, 26, ("CS_VIA_PERIPHERAL_ENGINE", "CS_VIA_GPIO"))
        dappa.combo(self, "SpiCsPolarity", i, self.header_row+i, 8, 13, ("LOW", "HIGH"))
        dappa.entry(self, "SpiTimeClk2Cs", i, self.header_row+i, 9, 13, "normal")
        dappa.entry(self, "SpiTimeCs2Clk", i, self.header_row+i, 10, 15, "normal")
        dappa.entry(self, "SpiTimeCs2Cs", i, self.header_row+i, 11, 15, "normal")
        
        # Channel list changed hence ask SpiDriver to redraw
        self.spidrvtab.tab.spi_extdrv_list_changed(self.configs)
        self.spijobtab.tab.spi_extdrv_list_changed(self.configs)



    def update(self):
        # get dappas to be added or removed
        self.n_spi_extdev = int(self.n_spi_extdev_str.get())

        # Tune memory allocations based on number of rows or boxes
        n_dappa_rows = len(self.configs)
        if not self.init_view_done:
            for i in range(n_dappa_rows):
                self.draw_dappa_row(i)
            self.init_view_done = True
        elif self.n_spi_extdev > n_dappa_rows:
            for i in range(self.n_spi_extdev - n_dappa_rows):
                self.configs.insert(len(self.configs), dappa.AsrCfgStr(self.cfgkeys, self.create_empty_configs()))
                self.draw_dappa_row(n_dappa_rows+i)
        elif n_dappa_rows > self.n_spi_extdev:
            for i in range(n_dappa_rows - self.n_spi_extdev):
                dappa.delete_dappa_row(self, (n_dappa_rows-1)+i)
                del self.configs[-1]

        # Set the self.cv scrolling region
        self.scrollw.scroll()



    def draw(self, tab):
        self.tab_struct = tab
        self.scrollw = window.ScrollableWindow(tab.frame, tab.xsize, tab.ysize)
        
        #Number of modes - Label + Spinbox
        label = tk.Label(self.scrollw.mnf, text="No. of Spi Sequence:")
        label.grid(row=0, column=0, sticky="w")
        spinb = tk.Spinbox(self.scrollw.mnf, width=10, textvariable=self.n_spi_extdev_str, command=lambda : self.update(),
                    values=tuple(range(0,self.max_spi_extdev+1)))
        self.n_spi_extdev_str.set(self.n_spi_extdev)
        spinb.grid(row=0, column=1, sticky="w")

        # Save Button
        genm = tk.Button(self.scrollw.mnf, width=10, text="Save Configs", command=self.save_data, bg="#206020", fg='white')
        genm.grid(row=0, column=2)

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self.scrollw.update()

        # Table heading @2nd row, 1st column
        dappa.place_heading(self, 2, 1)

        self.update()



    def save_data(self):
        self.tab_struct.save_cb(self.gui)


    def frange(self, start, stop, step):
        return map(lambda x: x/100000000.0, range(start, stop, step))
