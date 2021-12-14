from kivy.graphics import *
import math




def textured_rect(pos, size, texture,  angle=None, rot_origin=None,):
    if angle is None:
        Color(1,1,1,1)
        Rectangle(size=size, pos=pos,texture=texture.texture)

    else:
        PushMatrix()
        Rotate(angle=math.degrees(angle), origin=list(rot_origin))
        Color(1,1,1,1)
        Rectangle(size=size, pos=pos,texture=texture.texture)
        PopMatrix()