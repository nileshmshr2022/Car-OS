#
# Created on Tue Oct 25 2022 10:23:58 PM
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

import os

# import arxml.spi.arxml_spi as arxml_spi
import utils.search as search

# Temporary work-around
import gui.mcu.uc_cgen as uc_cgen


SpiGeneralCfgType_str = "\n\ntypedef struct {\n\
    uint8 spi_level_delivered;\n\
    uint8 spi_chan_buff_allowed;\n\
    boolean spi_intr_seq_allowed;\n\
    boolean spi_hw_status_api;\n\
    boolean spi_cancel_api;\n\
    boolean spi_version_info_api;\n\
    boolean spi_dev_error_detect;\n\
    boolean spi_supp_conc_sync_tx;\n\
    uint32 spi_main_func_period_ms;\n\
} SpiGeneralCfgType;\n\
\n"


def define_ext_dev_enum_type(hf, ext_devs):
    hf.write("\ntypedef enum {\n")
    for dev in ext_devs:
        hf.write("\tSPI_EXT_DEV_"+dev.datavar['SpiHwUnit']+",\n")
    hf.write("\tSPI_EXT_DEV_MAX\n")
    hf.write("} SpiExtDevID_Type;\n\n")


SpiDataShiftEdge_str = "\ntypedef enum {\n\
    SPI_EDGE_LEADING,\n\
    SPI_EDGE_TRAILING\n\
} SpiDataShiftEdgeType;\n\
\n"

SpiLevel_str = "\ntypedef enum {\n\
    SPI_LEVEL_LOW,\n\
    SPI_LEVEL_HIGH\n\
} SpiLevelType;\n\
\n"

SpiCsSelection_str = "\ntypedef enum {\n\
    CS_VIA_PERIPHERAL_ENGINE,\n\
    CS_VIA_GPIO\n\
} SpiCsSelectionType;\n\
\n"

SpiExternalDevice_str = "\ntypedef struct {\n\
    SpiExtDevID_Type spi_hw_unit;\n\
    uint32 spi_baudrate;\n\
    SpiDataShiftEdgeType spi_data_shift_edge;\n\
    SpiLevelType spi_shftclk_idle_level;\n\
    boolean spi_enable_cs;\n\
    char spi_cs_id[128];\n\
    SpiCsSelectionType spi_cs_selection;\n\
    SpiLevelType spi_cs_polarity;\n\
    uint32 spi_usec_clk_2_cs;\n\
    uint32 spi_usec_cs_2_clk;\n\
    uint32 spi_usec_cs_2_cs;\n\
} SpiExternalDeviceType;\n\
\n"


SpiTransferStart_str = "\ntypedef enum {\n\
    SPI_TX_START_MSB,\n\
    SPI_TX_START_LSB\n\
} SpiTransferStartType;\n\
\n"

SpiChannel_str = "\ntypedef struct {\n\
    uint16 spi_chan_id;\n\
    uint8 spi_chan_type;\n\
    uint16 spi_data_width;\n\
    uint8* spi_default_data;\n\
    uint16 spi_eb_max_len;\n\
    uint16 spi_ib_num_buf;\n\
    SpiTransferStartType spi_tx_start;\n\
} SpiChannelCfgType;\n\
\n"

SpiJob_str = "\ntypedef struct {\n\
    uint16 spi_job_id;\n\
    uint16 spi_job_priority;\n\
    void (*job_end_notification_fn)(void);\n\
    SpiExtDevID_Type spi_dev_assignment;\n\
    uint16 spi_chan_list_size;\n\
    uint16* spi_chan_list;\n\
} SpiJobCfgType;\n\
\n"


SpiSequence_str = "\ntypedef struct {\n\
    uint16 spi_seq_id;\n\
    boolean spi_seq_interruptible;\n\
    void (*seq_end_notification_fn)(void);\n\
    uint16 spi_job_list_size;\n\
    uint16* spi_job_list;\n\
} SpiSequenceCfgType;\n\
\n\n"



def generate_headerfile(spi_src_path, spi_info):
    hf = open(spi_src_path+"/cfg/Spi_cfg.h", "w")
    hf.write("#ifndef NAMMA_AUTOSAR_SPI_CFG_H\n")
    hf.write("#define NAMMA_AUTOSAR_SPI_CFG_H\n\n")
    hf.write("// This file is autogenerated, any hand modifications will be lost!\n\n")
    hf.write("#include <Platform_Types.h>\n\n")

    hf.write("\n#define SPI_CHAN_TYPE_IB        1")
    hf.write("\n#define SPI_CHAN_TYPE_EB        2")
    hf.write("\n#define SPI_CHAN_TYPE_IB_EB     3\n")
    
    hf.write(SpiGeneralCfgType_str)
    define_ext_dev_enum_type(hf, spi_info["SpiExternalDevice"])
    hf.write(SpiDataShiftEdge_str)
    hf.write(SpiLevel_str)
    hf.write(SpiCsSelection_str)
    hf.write(SpiExternalDevice_str)
    hf.write(SpiTransferStart_str)
    hf.write(SpiChannel_str)
    hf.write(SpiJob_str)
    hf.write(SpiSequence_str)
    
    hf.write("#define SPI_DRIVER_MAX_CHANNEL   ("+str(spi_info["SpiDriver"][0].datavar["SpiMaxChannel"])+")\n")
    hf.write("#define SPI_DRIVER_MAX_JOB       ("+str(spi_info["SpiDriver"][0].datavar["SpiMaxJob"])+")\n")
    hf.write("#define SPI_DRIVER_MAX_SEQUENCE  ("+str(spi_info["SpiDriver"][0].datavar["SpiMaxSequence"])+")\n")
    hf.write("#define SPI_DRIVER_MAX_HW_UNIT   ("+str(spi_info["SpiDriver"][0].datavar["SpiMaxHwUnit"])+")\n")
    
    hf.write("\n\n#endif\n")
    hf.close()


# Delete this after development for Spi code generation is complete
def print_spi_configs(spi_configs):
    for key in spi_configs:
        print("#################### ", key, " ############################")
        print("## datavar")
        for item in spi_configs[key]:
            print("\t", item.datavar)
        print("## dispvar")
        for item in spi_configs[key]:
            print("\t", item.get())



def gen_spi_general_configs(cf, gen_cfg):
    cf.write("\nSpiGeneralCfgType SpiGeneralCfg = {\n")
    cf.write("\t.spi_level_delivered     = "+str(gen_cfg["SpiLevelDelivered"])+",\n")

    spi_chan_type = ""
    if "IB" in gen_cfg["SpiChannelBuffersAllowed"] and "EB" in gen_cfg["SpiChannelBuffersAllowed"]:
        spi_chan_type = "SPI_CHAN_TYPE_IB_EB"
    elif "IB" in gen_cfg["SpiChannelBuffersAllowed"]:
        spi_chan_type = "SPI_CHAN_TYPE_IB"
    elif "EB" in gen_cfg["SpiChannelBuffersAllowed"]:
        spi_chan_type = "SPI_CHAN_TYPE_EB"
    else:
        spi_chan_type = "ERROR_CHAN_TYPE"
    cf.write("\t.spi_chan_buff_allowed   = "+spi_chan_type+",\n")
    cf.write("\t.spi_intr_seq_allowed    = "+str(gen_cfg["SpiInterruptibleSeqAllowed"])+",\n")
    cf.write("\t.spi_hw_status_api       = "+str(gen_cfg["SpiHwStatusApi"])+",\n")
    cf.write("\t.spi_cancel_api          = "+str(gen_cfg["SpiCancelApi"])+",\n")
    cf.write("\t.spi_version_info_api    = "+str(gen_cfg["SpiVersionInfoApi"])+",\n")
    cf.write("\t.spi_dev_error_detect    = "+str(gen_cfg["SpiDevErrorDetect"])+",\n")
    cf.write("\t.spi_supp_conc_sync_tx   = "+str(gen_cfg["SpiSupportConcurrentSyncTransmit"])+",\n")
    cf.write("\t.spi_main_func_period_ms = "+str(int(1000*float(gen_cfg["SpiMainFunctionPeriod"])))+"\n")
    cf.write("};\n\n")



def generate_sourcefile(spi_src_path, spi_info):
    cf = open(spi_src_path+"/cfg/Spi_cfg.c", "w")
    cf.write("#include <Spi_cfg.h>\n\n\n")
    cf.write("// This file is autogenerated, any hand modifications will be lost!\n\n")
    
    print_spi_configs(spi_info)
    gen_spi_general_configs(cf, spi_info["SpiGeneral"][0].datavar)

    cf.close()



def generate_code(gui, spi_configs):
    cwd = os.getcwd()
    spi_src_path = search.find_dir("Spi", cwd+"/submodules/MCAL/")
    generate_headerfile(spi_src_path, spi_configs)
    generate_sourcefile(spi_src_path, spi_configs)
    uc_cgen.create_source(gui)
    
