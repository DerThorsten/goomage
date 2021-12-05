from kivy.logger import Logger

import networkx

class MetaWorld(object):
    def __init__(self, level_cls):
        self.world = b2d.world(gravity=(0,10))

        self.goo_graph = networkx.Graph()
        Logger.info("construct level")
        self.level = level_cls(root=self)
        Logger.info("construct level done")
        self.goo_cls = PlainGoo
        self._insert_info = InsertInfo(InsertType.CANNOT_INSERT)