# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import os
import numpy as np
import re
from .JZ_utils import conf


def autolist(ini_file, raw_dir, lst_dir,
             sel_obj=None, sel_band=None,
             extra_config=None,
             # withbands=True, spchar="_"
             ):
    """
    create list for files in datadir, by their names
    21a: use [re] but not [parse], [parse] does not work good at 85 filenames
    :param ini_file:
    :param raw_dir: dir of data files
    :param lst_dir: dir of lists
    :param sel_obj: object to handle
    :param sel_band: band to handle
    :param withbands: if true, all filename as obj_band_sn, else obj_sn
    :param spchar: split char between object, band, and sn
    :return:
    """
    # 20201111, use parse.parse to parse filenames
    ini = conf(ini_file, extra_config)
    tm = ini["filename_temp"]
    # print(tm)
    def fn_split(fn):
        # pget = lambda r, f, d: r[f] if f in r.groupdict() else d  # result, field, default
        # parse filename
        x = re.search(tm, fn)
        obj = x.groupdict().get("obj", "UNKNOWN")  # pget(x, "obj", "UNKNOWN")
        band = x.groupdict().get("band", "X")  # pget(x, "band", "X")
        sn = int(x.groupdict().get("sn", "0"))  # int(pget(x, "sn", "0"))
        return obj, band, sn

    # get files
    files = [f for f in os.listdir(raw_dir) if f.endswith(".fits") or f.endswith(".fit")]
    files.sort()
    print("{:3d} fits files found in {}".format(len(files), raw_dir))
    fileinfo = [fn_split(f) for f in files]
    # extract objects, handle bias and flat
    # for bias, band="", others use real bands, if no bands, use X (for multi-channels)
    # 20201111
    # obj = [f.split(spchar)[0] for f in files]
    # obj = ["bias" if o.lower() == "bias" else "flat" if o.lower() == "flat" else o for o in obj]
    # if withbands:
    #     band = [f.split(spchar)[1] for f in files]
    #     band = [b if o != "bias" else "" for b, o in zip(band, obj)]
    # else:
    #     band = ["X" if o != "bias" else "" for o in obj]
    obj = ["bias" if "bias" in f[0].lower() else "flat" if "flat" in f[0].lower() else f[0] for f in fileinfo]
    band = ["" if "bias" in f[0].lower() else f[1] for f in fileinfo]

    # dispatch files
    file_all = {}
    list_all = {}
    for f, o, b in zip(files, obj, band):
        # skip files not as specified
        if ((sel_obj is not None and o not in (sel_obj, 'bias', 'flat')) or
            (sel_band is not None and b not in (sel_band, ''))):
            continue
        # for a new band, create a sub dict
        if b not in file_all:
            file_all[b] = {}
            list_all[b] = []
        if o not in file_all[b]:
            file_all[b][o] = []
            list_all[b].append(o)
        file_all[b][o].append(f)

    # remove bands with only flat but no objects
    bad_band = []
    for b in file_all:
        if len(file_all[b]) == 1 and "flat" in file_all[b]:
            bad_band.append(b)
    for b in bad_band:
        del(file_all[b])
        del(list_all[b])

    # output lists
    for b in file_all:
        for o in file_all[b]:
            ob = o + "_" + b if b else o
            with open(lst_dir + ob + ".lst", "w") as ff:
                for f in file_all[b][o]:
                    ff.write(f + "\n")
                print("    {:3d} ==> {}".format(len(file_all[b][o]), lst_dir + ob))

    return list_all
