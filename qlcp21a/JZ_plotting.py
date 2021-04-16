# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np
import matplotlib
#matplotlib.use('Agg')
from matplotlib import pyplot as plt
from .JZ_utils import meanclip


def plot_im_star(ini, img, x, y, mag, err, title, filename):
    """
    Plot observed image and overplot stars
    :param ini:
    :param img:
    :param x:
    :param y:
    :param mag:
    :param err:
    :param title:
    :param filename: file to save
    :return:
    """

    ny, nx = img.shape
    fig = plt.figure(figsize=(nx/50.0, ny/50.0))
    ax = fig.add_subplot(111)

    d_m, d_s = meanclip(img)
    ax.imshow(img, cmap="gray",
              vmin=d_m - d_s * ini["plot_img_lowsigma"],
              vmax=d_m + d_s * ini["plot_img_highsigma"])
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)

    ix_g = np.where(err < 0.1)
    ix_b = np.where(err >= 0.1)
    ms = (25.0 - mag) * 5
    ms[mag > 25] = 1.0
    # ms[mag < 10] = 15.0
    ax.scatter(x[ix_g], y[ix_g], marker="o", s=ms[ix_g], c="", edgecolors="r")
    ax.scatter(x[ix_b], y[ix_b], marker="o", s=ms[ix_b], c="", edgecolors="c")

    ax.set_title(title)

    fig.savefig(filename, bbox_inches='tight')
    plt.close()


def plot_magerr(ini, mag, err, title, filename):
    """
    Plot mag-err figure
    :param ini:
    :param mag:
    :param err:
    :param title:
    :param filename: file to save
    :return:
    """

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    ax.plot(mag, err, '.')
    ax.set_xlim(10, 25)
    ax.set_ylim(-0.001, 1.0)
    ax.set_xlabel("Mag (Inst)")
    ax.set_ylabel("Error")

    ax.set_title(title)

    fig.savefig(filename)
    plt.close()


def plot_im_target(ini, img,
                   target_x, target_y,
                   ref_x, ref_y,
                   chk_x, chk_y,
                   title, filename,
                   target_marker=("s", "r"),
                   ref_marker=("s", "y"),
                   chk_marker=("o", "y"),
                   noplot=False,
                   ):
    """
    Plot image and mark target, referenece, and check stars
    :param ini:
    :param img:
    :param target_x:
    :param target_y:
    :param ref_x:
    :param ref_y:
    :param chk_x:
    :param chk_y:
    :param title:
    :param filename:
    :param target_marker: 2-tuple for marker, marker type and border color
    :param ref_marker:
    :param chk_marker:
    :param noplot:
    :return:
    """

    ny, nx = img.shape
    fig = plt.figure(figsize=(nx / 100.0, ny / 100.0))
    ax = fig.add_subplot(111)
    fsize = nx / 100  # font size
    msize = fsize * 5   # marker size

    d_m, d_s = meanclip(img)
    ax.imshow(img, cmap="gray",
              vmin=d_m - d_s * ini["plot_img_lowsigma"],
              vmax=d_m + d_s * ini["plot_img_highsigma"])
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)

    if target_x is not None:
        ax.scatter(target_x, target_y, marker=target_marker[0], s=msize, c="", edgecolors=target_marker[1])
        if np.isscalar(target_x): target_x = (target_x, )
        if np.isscalar(target_y): target_y = (target_y, )
        for i in range(len(target_x)):
            ax.text(target_x[i]+fsize/2, target_y[i]+fsize/2, "T-{}".format(i),
                    color=target_marker[1], fontsize=fsize)

    if ref_x is not None:
        ax.scatter(ref_x, ref_y, marker=ref_marker[0], s=msize, c="", edgecolors=ref_marker[1])
        if np.isscalar(ref_x): ref_x = (ref_x, )
        if np.isscalar(ref_y): ref_y = (ref_y, )
        for i in range(len(ref_x)):
            ax.text(ref_x[i]+fsize/2, ref_y[i]+fsize/2, "R-{}".format(i),
                    color=ref_marker[1], fontsize=fsize)

    if chk_x is not None:
        ax.scatter(chk_x, chk_y, marker=chk_marker[0], s=msize, c="", edgecolors=chk_marker[1])
        if np.isscalar(chk_x): chk_x = (chk_x, )
        if np.isscalar(chk_y): chk_y = (chk_y, )
        for i in range(len(chk_x)):
            ax.text(chk_x[i]+fsize/2, chk_y[i]+fsize/2, "C-{}".format(i),
                    color=chk_marker[1], fontsize=fsize)

    ax.set_title(title)

    fig.savefig(filename, bbox_inches='tight')
    if noplot:
        plt.close(fig)


def plot_im_obj(ini, img,
                obj_x, obj_y,
                title, filename,
                target_marker=("s", "r"),
                noplot=False,
                ):
    """
    Plot only objects, without using ref or check
    :param ini:
    :param img:
    :param obj_x:
    :param obj_y:
    :param title:
    :param filename:
    :param target_marker:
    :param noplot:
    :return:
    """
    plot_im_target(ini, img, obj_x, obj_y,
                   None, None, None, None,
                   title, filename,
                   target_marker,
                   noplot=noplot,
    )
