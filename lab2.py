import numpy as np
from math import floor, cos, sin
from PIL import Image
import random
import math
import Object3D


def DDA_plot(img: np.ndarray, x0, y0, x1, y1):
    dmax = max(abs(floor(x0) - floor(x1)), abs(floor(y0) - floor(y1)))
    L = dmax + 1
    if L == 1:
        img[floor(x0), floor(y0)] = 0
        return img
    dx = (x1 - x0) / (L - 1)
    dy = (y1 - y0) / (L - 1)
    for i in range(L + 1):
        img[int(floor(x0)), int(floor(y0))] = 0
        x0 = dx + x0
        y0 = dy + y0
    return img

def calc_baricentric(x,y, x0, y0, x1, y1, x2, y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y-y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0-y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x-x2) *(y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0-y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return [lambda0, lambda1, lambda2]

def draw_triangle(img_mat, z_buffer, x0,y0,z0,x1,y1,z1,x2,y2,z2, color):
    xmin = int(max(min(x0,x1,x2),0))
    ymin = int(max(min(y0,y1,y2),0))
    xmax = math.ceil(min(max(x0,x1,x2), len(img_mat[1][:])-1))
    ymax = math.ceil(min(max(y0,y1,y2), len(img_mat[0][:])-1))
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            l0, l1,l2 = calc_baricentric(x+0.5,y+0.5,x0,y0,x1,y1,x2,y2)
            if(min(l0,l1,l2) > 0):
                z = l0*z0 + l1*z1 + l2*z2
                if(z< z_buffer[y,x]):
                    z_buffer[y,x] = z
                    img_mat[y,x,:] = color
                    

def draw_model(obj: Object3D.Object3D):
    white = np.full((H, W, 3), 255, dtype=np.uint8)
    z_buffer = np.full((H,W), np.inf, dtype=np.float64)
    verts = np.array(obj.vertices)
    x_min, x_max = obj.get_X_borders()
    y_min, y_max = obj.get_Y_borders()
    dx = x_max - x_min
    dy = y_max - y_min
    margin = 10 # отступ с каждой стороны
    scale_factor = min((W- 2*margin) / dx, (H - 2*margin) / dy)
    center_x = (x_min + x_max)/2 # центр по x
    center_y = (y_min + y_max)/2 # центр по y
    pic_x = (verts[:,0] - center_x)*scale_factor + W/2 # центр модели перемещаем в начало новых координат, масштабируем и переносим в ценр изображения
    pic_y = -((verts[:,1] - center_y)*scale_factor) + H/2
    for face in obj.faces:
        if(face_cos(*verts[face].ravel()) < 0):
            x0,x1,x2 = pic_x[face[0]], pic_x[face[1]], pic_x[face[2]]
            y0,y1,y2 = pic_y[face[0]], pic_y[face[1]], pic_y[face[2]]
            z0,z1,z2 = verts[face[0],2],verts[face[1],2],verts[face[2],2]
            draw_triangle(white,z_buffer,x0,y0,z0,x1,y1,z1,x2,y2,z2, [-255 * face_cos(*verts[face].ravel()),0,0])
    return white

def calc_normal(x0,y0,z0,x1,y1,z1,x2,y2,z2):
    return np.cross([x1 - x2,y1 -y2, z1-z2], [x1-x0, y1-y0, z1-z0])

def face_cos(x0,y0,z0,x1,y1,z1,x2,y2,z2):
    normal = calc_normal(x0,y0,z0,x1,y1,z1,x2,y2,z2)
    light = [0,0,1]
    return np.dot(normal, light)/(np.linalg.norm(normal)*np.linalg.norm(light))

H = 1000
W = 1000


def Rotate_x_mat(angle):
    mat = [[1, 0, 0], [0, cos(angle), -sin(angle)], [0, sin(angle), cos(angle)]]
    npmat = np.array(mat)
    return npmat


def Rotate_y_mat(angle):
    mat = [[cos(angle), 0, sin(angle)], [0, 1, 0], [-sin(angle), 0, cos(angle)]]
    npmat = np.array(mat)
    return npmat


def Rotate_z_mat(angle):
    mat = [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]
    npmat = np.array(mat)
    return npmat



model = Object3D.Object3D("data/model.obj")
img = draw_model(model)
im = Image.fromarray(img)
im.save("data/triangles_light.png")