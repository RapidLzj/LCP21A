# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np


def findneighbor(u1, v1, u2=None, v2=None, dis_limit=0.0005):
    """Distance match, find match between two list
    Originally part of match algorithm, also used in find isolated stars
    returns:
        a list of ndarray, outer list has n1 sub-lists,
        each sub-list contains indicies of star2
    """
    # if u2 v2 is omitted, means to find neighbor at u1 v1 itself
    if u2 is None: u2 = u1
    if v2 is None: v2 = v1

    n1, n2 = len(u1), len(u2)
    udis_limit = vdis_limit = dis_limit

    # sort items by their v values
    sort1 = np.argsort(v1)
    sort2 = np.argsort(v2)
    # new order of data
    u1s, v1s = u1[sort1], v1[sort1]
    u2s, v2s = u2[sort2], v2[sort2]

    # prepare an empty list
    neighbor = [[]] * n1
    dis = [[]] * n1

    # from top, walk down to match T = O(n1+n2)
    p2f = p2t = 0
    for p1 in range(n1):
        # p2f walk down to the first item gt [p1]-dis, and p2t to first item gt [p1]+dis
        while p2f < n2 and v2s[p2f] <  v1s[p1] - vdis_limit: p2f += 1
        while p2t < n2 and v2s[p2t] <= v1s[p1] + vdis_limit: p2t += 1
        # exit when p2f runs out
        if p2f >= n2:
            break
        # skip when no near star
        if p2t - p2f > 0:
            # find real near stars, consider u1&u2
            testdis = np.sqrt((u1s[p1] - u2s[p2f:p2t]) ** 2.0 +
                              (v1s[p1] - v2s[p2f:p2t]) ** 2.0)
            # tix = np.where((1e-5 < testdis) & (testdis < dis_limit))[0]
            tix = np.where((0 < testdis) & (testdis < dis_limit))[0]
            if len(tix) > 0:
                tixsort = tix[np.argsort(testdis[tix])]
                neighbor[sort1[p1]] = sort2[tixsort + p2f] # this is reverted real index of tix2
                dis[sort1[p1]] = testdis[tixsort]
    return neighbor, dis


def match(x1, y1, m1, x2, y2, m2,
          dis_limit=20.0, mag_limit=None, multi=False):
    """Match 2 list of stars
    Assume all stars are in a small area, and use same ra scale
    arguments:
        u1, v1: coord of star list 1, u&v can be x/y
        u2, v2: list 2
        dis_limit: max match distance, pixels
        mag_limit: max difference, None for no limit, positive as mag limit, negative as n-sigma
        multi: allow multi matching or not
    returns:
        tuple of 2 item: indices 1, and indices 2
    """
    # list size
    n1, n2 = len(x1), len(x2)

    if type(x1) is not np.ndarray: x1 = np.array(x1)
    if type(y1) is not np.ndarray: y1 = np.array(y1)
    if type(m1) is not np.ndarray: m1 = np.array(m1)
    if type(x2) is not np.ndarray: x2 = np.array(x2)
    if type(y2) is not np.ndarray: y2 = np.array(y2)
    if type(m2) is not np.ndarray: m2 = np.array(m2)

    neighbor, nei_dis = findneighbor(x1, y1, x2, y2, dis_limit=dis_limit)

    # extract data from dfind neighbor result
    id1, id2, dis12 = [], [], []
    for p1 in range(n1):
        p2 = len(neighbor[p1])
        if p2 > 0:
            # 190624 multi or not
            if multi:
                id1.extend([p1]*p2)
                id2.extend(neighbor[p1])
                dis12.extend(nei_dis[p1])
            else:
                id1.append(p1)
                id2.append(neighbor[p1][0])
                dis12.append(nei_dis[p1][0])
    id1 = np.array(id1)
    id2 = np.array(id2)
    dis12 = np.array(dis12)

    if mag_limit is not None:
        m12 = m1[id1] - m2[id2]
        m12m = np.median(m12)
        if mag_limit < 0:
            m12s = np.std(m12)
            ix = np.where(np.abs(m12 - m12m) < - mag_limit * m12s)[0]
        else:
            ix = np.where(np.abs(m12 - m12m) < mag_limit)[0]
        id1 = id1[ix]
        id2 = id2[ix]
        dis12 = dis12[ix]

    n1 = len(id1)
    if n1 < 1:
        return [], [], np.nan
    # d1 = np.sqrt(np.sum(dis12 ** 2) / n1)

    stddis = np.sqrt(np.sum(dis12 ** 2) / len(id1))

    return id1, id2, stddis
