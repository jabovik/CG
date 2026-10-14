import numpy as np
from math import floor, cos, sin
from PIL import Image
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


def draw_model(obj: Object3D.Object3D):
    white = np.full((W, H, 3), 255, dtype=np.uint8)
    obj.vertices = obj.vertices @ Rotate_x_mat(3.1415/2)
    x_min, x_max = obj.get_X_borders()
    x_max = x_max - x_min
    x_coef = floor((W - 10) / x_max)
    y_min, y_max = obj.get_Y_borders()
    y_max = y_max - y_min
    y_coef = floor((H - 10) / y_max)
    coef = min(x_coef, y_coef)
    obj.vertices[:, 0] = obj.vertices[:, 0] - x_min
    obj.vertices[:, 1] = obj.vertices[:, 1] - y_min
    # увеличить модель во сколько то раз
    # прибавить по 1/2 размера кадра к точкам
    # x_max
    # for vertice in obj.vertices:
    #    white[floor(-vertice[1]*5000)+500,floor(vertice[0]*5000)+500,:] = 0
    for face in obj.faces:
        for i in range(3):
            DDA_plot(
                white,
                (-obj.vertices[face[i]][1] * coef),
                (obj.vertices[face[i]][0]) * coef,
                (-obj.vertices[face[(i + 1) % 3]][1] * coef),
                (obj.vertices[face[(i + 1) % 3]][0]) * coef,
            )
    return white


H = 4000
W = 4000


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


black = np.zeros((W, H), dtype=np.uint8)
im = Image.fromarray(black)
im.save("data/black.jpg")
white = np.full((W, H), 255, dtype=np.uint8)
DDA_plot(white, 12.34, 43.21, 123.45, 987.65)
im = Image.fromarray(white)
im.save("data/white.jpg")
red = np.zeros((W, H, 3), dtype=np.uint8)
red[:, :, 0] = 255
im = Image.fromarray(red)
im.save("data/red.jpg")
model = Object3D.Object3D("data/model.obj")
im = Image.fromarray(draw_model(model))
im.save("data/model.png")
