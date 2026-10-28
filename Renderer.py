import numpy as np
from math import floor, cos, sin
import math
import Scene
from numba import njit

@njit
def dda_plot(img: np.ndarray, x0, y0, x1, y1):
    dmax = max(abs(floor(x0) - floor(x1)), abs(floor(y0) - floor(y1)))
    L = dmax + 1
    if L == 1:
        img[floor(x0), floor(y0)] = 0
        return img
    dx = (x1 - x0) / (L - 1)
    dy = (y1 - y0) / (L - 1)
    for _ in range(L + 1):
        img[int(floor(x0)), int(floor(y0))] = 0
        x0 = dx + x0
        y0 = dy + y0
    return img

@njit
def calc_baricentric(x,y, x0, y0, x1, y1, x2, y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y-y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0-y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x-x2) *(y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0-y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return [lambda0, lambda1, lambda2]

@njit
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
               
# ПЕРЕНЕСТИ НА JIT
def draw_model(obj: Scene.Scene, W,H, white : np.ndarray, z_buffer, scale = 1, margin = 10) -> np.ndarray:
    verts = np.array(obj.vertices)
    x_min, x_max = obj.get_X_borders()
    y_min, y_max = obj.get_Y_borders()
    dx = x_max - x_min
    dy = y_max - y_min
    #scale_factor = min((W- 2*margin) / dx, (H - 2*margin) / dy)
    center_x = (x_min + x_max)/2 # центр по x
    center_y = (y_min + y_max)/2 # центр по y
    pic_x = (verts[:,0] - center_x)*scale + W/2 # центр модели перемещаем в начало новых координат, масштабируем и переносим в ценр изображения
    pic_y = -((verts[:,1] - center_y)*scale) + H/2
    for face in obj.faces:
        i0,i1,i2 = face
        с = face_cos(*verts[i0], *verts[i1], *verts[i2], obj.light)
        if(с < 0):
            px0,px1,px2 = pic_x[face[0]], pic_x[face[1]], pic_x[face[2]]
            py0,py1,py2 = pic_y[face[0]], pic_y[face[1]], pic_y[face[2]]
            z0,z1,z2 = verts[face[0],2],verts[face[1],2],verts[face[2],2]
            draw_triangle(white,z_buffer,px0,py0,z0,px1,py1,z1,px2,py2,z2, [-255 * с, 0.0, 0.0])
    return white

@njit
def calc_normal(x0,y0,z0,x1,y1,z1,x2,y2,z2):
    return np.cross([x1 - x2,y1 -y2, z1-z2], [x1-x0, y1-y0, z1-z0])
@njit
def face_cos(x0,y0,z0,x1,y1,z1,x2,y2,z2,light):
    normal = calc_normal(x0,y0,z0,x1,y1,z1,x2,y2,z2)
    return (normal[0]*light[0]+normal[1]*light[1]+normal[2]*light[2])/(
        math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2 ))


class Renderer:
    def __init__(self, H, W, scale, margin = 10):
        self.H = H
        self.W = W
        self.scale = scale
        self.margin = margin
        self.img = None
    
    def render(self, scene):
        white = np.full((self.H, self.W, 3), 255, dtype=np.uint8)
        z_buffer = np.full((self.H,self.W), np.inf, dtype=np.float64)
        self.img = draw_model(scene, self.W,self.H, white, z_buffer, self.scale, self.margin)
    