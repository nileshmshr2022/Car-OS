#
# Created on Fri Feb 09 2024 6:54:34 PM
#
# The MIT License (MIT)
# Copyright (c) 2024 Aananth C N
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

import ajson.core.lib as ajson
import gui.port.port_view as port_view



def save_port_configs(jdata, gui_obj):
    m_key = "Port"

    if port_view.PortView:
        jdata[m_key] = port_view.PortView

    return



def read_port_configs():
    m_key = "Port"
    jdata = {}

    if ajson.AJSON_Dump:
        if m_key in ajson.AJSON_Dump:
            jdata = ajson.AJSON_Dump[m_key]

    return jdata
