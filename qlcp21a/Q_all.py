# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np
import os
from .Q0_autolist import autolist
from .Q0_biascomb import biascomb
from .Q0_flatcomb import flatcomb
from .Q1_imgproc import imgproc
from .Q2_phot import phot
from .Q3_wcs import wcs
from .Q4_offset import offset
from .Q5_pick import pick
from .Q6_catalog import catalog
from .Q7_cali import cali
from .Q8_curve import curve
from .JZ_utils import conf


def do_all(ini_file, raw_dir, lst_dir, red_dir,
           obj=None, band=None, bandobj=None,
           base_img_id=0,
           base_cat_file=None,
           base_fits_file=None,
           starxy=None,
           obj_coord=None,
           tgt_id=0,
           ref_id=None,
           chk_id=None,
           fig_set=None,
           noplot=False,
           overwrite=False,
           steps="lbfipocdg",
           extra_config=None):
    """
    do from the first step to the last
    :param ini_file:
    :param raw_dir:
    :param lst_dir:
    :param red_dir:
    :param obj: object to handle
    :param band: band to handle
    :param bandobj: a dict, structure as autolist result if obj & band are none
        if autolist is executed, use its result as lists
        if obj and band are all given, use their cross as lists
        if obj or band is none, use bandobj as lists
        if one of obj and band is none, and bandobj is none, quit with error
    :param base_img_id:
    :param base_cat_file: template catalog file, if base < 0, use this
    :param base_fits_file: template image file, if base id < 0, this must be provided
    :param starxy: a list of [(x1, y1), (x2, y2), ...], if None, no this step
    :param obj_coord: 2-tuple, RA and Dec of the object, in HMS/DMS or deg,
        or a dict, the object name as key, 2-tuple of ra/dec as value
    :param tgt_id: parameters used in plotting light-curve
    :param ref_id:
    :param chk_id:
    :param fig_set:
    :param noplot: if true, only save as png but not displayed in screen
    :param overwrite:
    :param steps: steps called in this session
                l: auto List
                b: Bias combine
                f: Flat combine
                i: Image correction
                p: Photometry
                w: Wcs
                o: Offset
                k: picK reference stars
                c: Catalog
                d: Differential calibration
                g: Graph
    :param extra_config: extra config beside ini files
    :return:
    """
    # do all steps one by one, if the step char in the parameters

    if not red_dir.endswith("/"):
        red_dir = red_dir + "/"
    os.makedirs(red_dir, exist_ok=True)

    if lst_dir.endswith("/"):
        os.makedirs(lst_dir, exist_ok=True)

    ini = conf(ini_file, extra_config)

    def _filename_(filetype, **kwargs):
        """
        internal function to generate filenames
        :param filetype:
        :param kwargs:
        :return:
        """
        return ini["filename_" + filetype].format(**kwargs)
        # return filename_fmt[step].format(**kwargs)
    # endregion

    # in this step, lst must be filled, by autolist, or by cross of given obj and band, or by bandobj
    if "l" in steps:
        lst = autolist(
            ini_file=ini_file,
            raw_dir=raw_dir, lst_dir=lst_dir,
            sel_obj=obj, sel_band=band,
            extra_config=extra_config
        )
        if steps == "l":
            return lst
    else:
        # if no autolist, use given band and obj to generate a lst
        if obj and band:
            if type(obj) is str:
                obj = [obj]
            lst = {b:obj for b in band}
        elif bandobj:
            lst = bandobj
        else:
            lst = None
            return

    # make a clean band-obj zip
    bandobj = []
    for b in lst:
        for o in lst[b]:
            if o not in ["bias", "flat"]:
                bandobj.append((b, o))

    if "b" in steps:
        biascomb(
            ini_file=ini_file,
            file_lst=lst_dir + _filename_("bias_lst", obj="bias", band="X"),
            out_bias_fits=red_dir + _filename_("bias_fit", obj="bias", band="X"),
            raw_path=raw_dir,
            overwrite=overwrite,
            log=red_dir + _filename_("bias_log", obj="bias", band="X"),
            extra_config=extra_config,
        )

    if "f" in steps:
        for b in lst:
            if "flat" in lst[b]:
                flatcomb(
                    ini_file=ini_file,
                    file_lst=lst_dir + _filename_("flat_lst", obj="flat", band=b),
                    bias_fits=red_dir + _filename_("bias_fit", obj="bias", band="X"),
                    out_flat_fits=red_dir + _filename_("flat_fit", obj="flat", band=b),
                    raw_path=raw_dir,
                    overwrite=overwrite,
                    log=red_dir + _filename_("flat_log", obj="flat", band=b),
                    extra_config=extra_config,
                )

    for b, o in bandobj:
        # iteration all items
        if type(obj_coord) is dict:
            oc = obj_coord[o]
        else:
            oc = obj_coord

        imgproc(
            ini_file=ini_file,
            file_lst=lst_dir + _filename_("file_lst", obj=o, band=b),
            bias_fits=red_dir + _filename_("bias_fit", obj="bias", band="X"),
            flat_fits=red_dir + _filename_("flat_fit", obj="flat", band=b),
            obj_coord=oc,
            raw_path=raw_dir,
            red_path=red_dir,
            extra_hdr=None,
            overwrite=overwrite,
            log=red_dir + _filename_("imgproc_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "i" in steps else None

        phot(
            ini_file=ini_file,
            file_lst=lst_dir + _filename_("file_lst", obj=o, band=b),
            red_path=red_dir,
            overwrite=overwrite,
            log=red_dir + _filename_("phot_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "p" in steps else None

        wcs(
            ini_file = ini_file,
            file_lst = lst_dir + _filename_("file_lst", obj=o, band=b),
            out_wcs_file=red_dir + _filename_("wcs_txt", obj=o, band=b),
            ct_coord=obj_coord,
            # pixscl=pixscl, #fov=fov,
            # nrefgood=nrefgood,
            red_path = red_dir,
            overwrite = overwrite,
            log = red_dir + _filename_("wcs_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "w" in steps else None

        offset(
            ini_file=ini_file,
            file_lst=lst_dir + _filename_("file_lst", obj=o, band=b),
            out_offset_file=red_dir + _filename_("offset_txt", obj=o, band=b),
            base_img_id=base_img_id,
            base_cat_file=base_cat_file,
            red_path=red_dir,
            overwrite=overwrite,
            log=red_dir + _filename_("offset_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "o" in steps else None

        if "k" in steps or ("c" in steps and (not starxy or len(starxy) == 1)):
            xy_var, xy_ref = pick(
                ini_file=ini_file,
                file_lst=lst_dir + _filename_("file_lst", obj=o, band=b),
                offset_file=red_dir + _filename_("offset_txt", obj=o, band=b),
                out_pick_txt=red_dir + _filename_("pick_txt", obj=o, band=b),
                base_img_id=base_img_id,
                base_cat_file=base_cat_file,
                red_path=red_dir,
                overwrite=overwrite,
                log=red_dir + _filename_("pick_log", obj=o, band=b),
                extra_config=extra_config,
            )
            if not starxy:
                pick_starxy = [xy_var[:1]] + xy_ref
            else:
                pick_starxy = list(starxy) + xy_ref
        else:
            pick_starxy = starxy

        catalog(
            ini_file=ini_file,
            file_lst=lst_dir + _filename_("file_lst", obj=o, band=b),
            offset_file=red_dir + _filename_("offset_txt", obj=o, band=b),
            out_cat_fits=red_dir + _filename_("cat_fit", obj=o, band=b),
            out_cat_table_txt=red_dir + _filename_("cat_table_txt", obj=o, band=b),
            out_cat_list_txt=red_dir + _filename_("cat_list_txt", obj=o, band=b),
            out_finding_img=red_dir + _filename_("finding_img", obj=o, band=b),
            base_img_id=base_img_id,
            base_fits_file=base_fits_file,
            red_path=red_dir,
            starxy=pick_starxy,
            # obj_coord=oc,
            overwrite=overwrite,
            noplot=noplot,
            log=red_dir + _filename_("cat_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "c" in steps else None

        cali(
            ini_file=ini_file,
            cat_fits=red_dir + _filename_("cat_fit", obj=o, band=b),
            out_cali_fits=red_dir + _filename_("cali_fit", obj=o, band=b),
            out_cali_txt=red_dir + _filename_("cali_txt", obj=o, band=b),
            tgt_id=tgt_id,
            ref_id=ref_id,
            chk_id=chk_id,
            overwrite=overwrite,
            log=red_dir + _filename_("cali_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "d" in steps else None

        curve(
            ini_file=ini_file,
            cali_fits=red_dir + _filename_("cali_fit", obj=o, band=b),
            out_lc_png=red_dir + _filename_("lc_png", obj=o, band=b),
            fig_set=fig_set,
            noplot=noplot,
            overwrite=overwrite,
            log=red_dir + _filename_("lc_log", obj=o, band=b),
            extra_config=extra_config,
        ) if "g" in steps else None

    return