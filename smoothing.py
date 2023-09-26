import numpy as np
import lasio
import os

def x1(i):
    # return (i - (n-1)/2)/((n-1)/2)
    pass

def x2(i):
    x1(i) ** 2

def x3(i):
    x1(i) ** 3

def fo52(y, n):

    c11 = 0
    c21 = 0
    c31 = 0
    c41 = 0
    for i in range(n):
        c11 += y[i]
        c21 += x1(i) * y[i]
        c31 += x2(i) * y[i]
        c41 += x3(i) * y[i]
    
    C = [c11, c21, c31, c41]

    # B = [
    #     [n24, s1, s2, s3],
    #     [s1, s5, s4, s6],
    #     [s2, s4, s8, s7],
    #     [s3, s6, s7, s9],
    # ]

    # u = B
    u = [[]]
    o = [[]]
    a = []

    o1k = []

    for ii in range(4):
        H = u
        for i in range(4):
            H[i][ii] = C[i]
        
        for i in range(3):
            for j in range(3):
                o[i][j] = H(i+1, j+1)
            
        # ccc = fo47(o)
        # dd1 = ccc

        for i in range(3):
            for i in range(2, 3):
                o[i][j] = H(i+1, j+1)

        for i in range(3):
            o[i][1] = H(i+1, 1)

        # ccc = fo47(0)
        # dd2 = ccc

        for i in range(3):
            for i in range(1, 2):
                o[i][j] = H(i+1, j)

        for i in range(3):
            o[i][3] = H(i+1, 4)

        # ccc = fo47(0)
        # dd3 = ccc

        for i in range(3):
            for i in range(3):
                o[i][j] = H(i+1, j)

        for i in range(3):
            o[i][1] = H(i+1, 1)

        # ccc = fo47(0)
        # dd4 = ccc

        # a[ii] = H(1, 1) * dd1 - H(1, 2) * dd2 + H(1, 3) * dd3 - H(1, 4) * dd4

        # o1k.append(a[ii]/ddd)
    
    a0 = o1k[0]
    a1 = o1k[1]
    a2 = o1k[2]
    a3 = o1k[3]

    y1 = []
    n12 = (n - 1) / 2

    for i in range(len(y)):
        y1.append(a0 + a1/n12 + a2/(n12**2) + a3/(n12**3))



# n = 60
# file_path = os.getcwd()
# las = lasio.read(f'{file_path}\\19399001 2023-07-27 09-46-50 ГГКП.rt.las')
# RSD = local_approximation(las["RSD"])
