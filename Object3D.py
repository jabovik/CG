# .obj file format
class Object3D:
    
    def __init__(self, filename):
        self.vertices = []
        self.faces = []
        self.open(filename)

    def open(self, filename):
        self.vertices.clear()
        self.faces.clear()
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    _, v1, v2, v3 = line.split()
                    vertex = [float(v1), float(v2), float(v3)] # x y z
                    self.vertices.append(vertex)
                elif line.startswith("f"):
                    _, *verts = line.split()
                    face = [int(vertex_num.split("/")[0]) - 1 for vertex_num in verts] # vert1 vert2 vert3
                    self.faces.append(face)

    def get_X_borders(self):
        min_x = min(vertex[0] for vertex in self.vertices)
        max_x = max(vertex[0] for vertex in self.vertices)
        return (min_x, max_x)

    def get_Y_borders(self):
        min_y = min(vertex[1] for vertex in self.vertices)
        max_y = max(vertex[1] for vertex in self.vertices)
        return (min_y, max_y)

    def get_Z_borders(self):
        min_z = min(vertex[2] for vertex in self.vertices)
        max_z = max(vertex[2] for vertex in self.vertices)
        return(min_z,max_z)

    def get_borders(self):
        return (*self.get_X_borders(), *self.get_Y_borders(), *self.get_Z_borders())
