import Object3D
class Scene(Object3D.Object3D):
    def __init__(self,filename, light = [0,0,1]):
        super().__init__(filename)
        self.light = light