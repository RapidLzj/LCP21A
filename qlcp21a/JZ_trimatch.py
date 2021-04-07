# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np
from .JZ_cata import match


def make_tri(x, y, goodix=None):
    """
    Generate C_n_3 triangles with given stars, return the triangle array
    :param x: x coordinates
    :param y: y coordinates
    :param goodix: indices of good stars
    :return: a rec-array of triangles
    """
    if goodix is None:
        goodix = np.arange(len(x))

    # 选出的优质星的个数
    ngood = len(goodix)
    # 能够组成的三角形的个数 C_ng_3
    ntri = ngood * (ngood - 1) * (ngood - 2) // 6
    # print("{} Stars ==> {} Triangles".format(ngood, ntri))

    # 三角形数组
    tr = np.empty(ntri, [
        ("len0", float),  # 最长边长度
        ("fac1", float),  # 次长边和最长边比值
        ("fac2", float),  # 最短边和最长边比值
        ("p0", int),  # 最长边相对节点编号
        ("p1", int),  # 次长边相对节点编号
        ("p2", int),  # 最短边相对节点编号
    ])

    # 计算两点之间距离的函数
    edgelen = lambda i1, i2: np.sqrt((x[pp[i1]] - x[pp[i2]]) ** 2 + (y[pp[i1]] - y[pp[i2]]) ** 2)

    k = 0
    for k1 in range(0, ngood - 2):
        for k2 in range(k1 + 1, ngood - 1):
            for k3 in range(k2 + 1, ngood):
                # 生成一个三角形，将其规范化后放入数组中

                # 先弄明白三个顶点的真实编号
                pp = goodix[[k1, k2, k3]]
                # 求三边长，边编号为对面的顶点编号，并整成列表
                ee = edgelen(1, 2), edgelen(2, 0), edgelen(0, 1)

                # 对三边长排序，得到下标序列
                ei = np.argsort(ee)
                # 计算参数并保存到三角形数组中
                tr[k]["len0"] = ee[ei[2]]
                tr[k]["fac1"] = ee[ei[1]] / ee[ei[2]]
                tr[k]["fac2"] = ee[ei[0]] / ee[ei[2]]
                tr[k]["p0"] = pp[ei[0]]
                tr[k]["p1"] = pp[ei[1]]
                tr[k]["p2"] = pp[ei[2]]

                k += 1

    return tr


def argunique_old(a):
    """
    找出序列中每个元素第一次出现的下标
    """
    au = np.unique(a)
    nau = len(au)
    ix = np.empty(nau, int)
    for i in range(nau):
        ix[i] = np.where(a == au[i])[0][0]
    return ix


def argunique(a, b):
    """
    找出a--b对应体中的唯一对应体，即保证最终输出的aa--bb没有重复元素，也没有多重对应
    :param a:
    :param b:
    :return: aaa, bbb 使得aaa-bbb是唯一对
    """
    # 先对a中元素进行逐个检查，如果第一次出现，那么添加到aa中，如果不是第一次，那么检查是否一致，不一致则设置成-1
    # 设置成-1，代表a中当前元素i有过一对多纪录，剔除。同时-1也不会被再匹配到
    seta = {}
    for i, j in zip(a, b):
        if i not in seta:
            seta[i] = j
        elif seta[i] != j:
            seta[i] = -1
    aa = [i for i in seta if seta[i] != -1]
    bb = [seta[i] for i in seta if seta[i] != -1]
    # 再反过来做一遍，以b为索引，剔除重复项
    setb = {}
    for i, j in zip(aa, bb):
        if j not in setb:
            setb[j] = i
        elif setb[j] != i:
            setb[j] = -1
    aaa = [setb[j] for j in setb if setb[j] != -1]
    bbb = [j for j in setb if setb[j] != -1]

    return aaa, bbb


def match_triangle(tr1, tr2, maxerr=2.5e-3):
    """
    Match two arrays of triangles
    :param tr1: triangle list 1
    :param tr2: triangle list 2
    :param maxerr: max error in matching
    :return: matched stars
    """
    # 开始匹配三角形
    mix1, mix2, dis = match(
        tr1["fac1"], tr1["fac2"], None,
        tr2["fac1"], tr2["fac2"], None,
        dis_limit=maxerr)
    print("{} Triangles matched".format(len(mix1)))

    # 根据匹配到的三角形，找出他们的三个顶点的序列，这是真正的匹配到的点
    pp1 = np.concatenate((tr1[mix1]["p0"], tr1[mix1]["p1"], tr1[mix1]["p2"]))
    pp2 = np.concatenate((tr2[mix2]["p0"], tr2[mix2]["p1"], tr2[mix2]["p2"]))

    # 去重。根据第一个序列找到每个重复点的第一次出现，纪录下标
    ppix = argunique(pp1)
    ppix = ppix[argunique(pp2[ppix])]
    pp1u = pp1[ppix]
    pp2u = pp2[ppix]

    # 返回匹配到的点的下标，具体怎么进行下一轮匹配和天测，交给主程序
    return pp1u, pp2u  #, tr1, tr1, mix1, mix2
