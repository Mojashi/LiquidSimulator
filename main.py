import time
import numpy as np
import os
import math


# def calc_W_row(r):
#     global r_effective
#     r_len = np.linalg.norm(r, ord = 2)
#     if r_len > r_effective:
#         return 0
    
#     return 4/(math.pi*r_effective**8) * (r_effective**2 - r_len**2)**3
    
# def calc_W_prs(r):
#     global r_effective
#     r_len = np.linalg.norm(r, ord = 2)
#     if r_len > r_effective:
#         return np.array((2))
    
#     return -30 / (math.pi * r_effective**5) * (r_effective - r_len)**2 * r / r_len
    
# def calc_W_visc(r):
#     global r_effective
#     r_len = np.linalg.norm(r, ord = 2)
#     if r_len > r_effective:
#         return 0
    
#     return 20 / (3 * math.pi * r_effective**5)*(r_effective - r_len)

def update_state(pos,v, wallcount):
    r_effective = 0.01*2.5
    delta_t = 1/5000
    k = 5
    row_zero = 1000
    m = 1000
    n = pos.shape[0]

    f_prs = np.zeros((n,2), dtype = float)
    f_visc = np.zeros((n,2), dtype = float)
    f_ext = np.zeros((n,2), dtype = float)

    row = np.zeros(n, dtype = float)
    p = np.zeros((n,2), dtype = float)
    myu = 10

    #k1 = 4/(math.pi*r_effective**8)
    k1 = 10 / (math.pi * r_effective**5)
    k2 = -30 / (math.pi * r_effective**5)
    k3 = 20 / (3 * math.pi * r_effective**5)

    for i in range(n):
        for pt in pos:
                r_len = np.linalg.norm(pos[i] - pt, ord = 2)
                if r_len <= r_effective:
                    row[i] += k1*(r_effective - r_len)**3
    
        p[i] = k * (row[i] - row_zero)
        f_ext[i] = row[i] * 9.8
    
    for i in range(n):
        for j in range(n):
            if i != j:
                r_len = np.linalg.norm(pos[i] - pos[j], ord = 2)
                if r_len <= r_effective:
                    f_prs[i] -= m * (p[i] + p[j]) / (2*row[j]) * (k2* (r_effective - r_len)**2 * (pos[i] - pos[j]) / r_len)
                    f_visc[i] += myu * m * (v[j] - v[i]) / row[j] * (k3*(r_effective - r_len))

    for i in range(wallcount, n):
        v[i] = v[i] + delta_t / row[i] * (f_prs[i] + f_visc[i] + f_ext[i])
        pos[i] += delta_t * v[i]

    return

def draw(pos, h, w,wallcount):
    #print("\033[2J", flush=True)
    disp = np.zeros((h,w))
    cou = 0
    for (y,x) in pos:
        y = round(y*100)
        x = round(x * 100)
        if y >= 0 and x >= 0 and y < h and x < w:
            disp[int(y)][int(x)] += 1
        if wallcount > cou:
            disp[int(y)][int(x)] = 99999
        cou+=1
    output_str = ""#"\033["+str(h + 1) + "A"
    for i in range(h):
        for j in range(w):
            if disp[i][j] == 99999:
                output_str += 'K'
            elif disp[i][j] > 0:
                output_str += 'X'
            else:
                output_str += ' '
        output_str += "\n"
    print(output_str)
    return

h = 30
w = 50
num_of_p = 300
haba = 10

wall_haba = 5

pos = np.zeros((num_of_p + wall_haba * (h-wall_haba) * 2 + w * wall_haba,2), dtype = float)
v = np.zeros((num_of_p + wall_haba * (h-wall_haba) * 2 + w * wall_haba,2), dtype = float)

wallcount = 0


for i in range(wall_haba):
    for j in range(h - wall_haba):
        pos[wallcount] = np.array([j, i])/100
        wallcount+=1
        pos[wallcount] = np.array([j, w-i-1])/100
        wallcount+=1
    for j in range(w):
        pos[wallcount] = np.array([h-1-i,j])/100
        wallcount+=1

for i in range(num_of_p):
    pos[i + wallcount] = np.array([int(i / haba),wall_haba + 1 + i % haba])/100

while True:
    update_state(pos,v, wallcount)
    draw(pos, h, w, wallcount)
