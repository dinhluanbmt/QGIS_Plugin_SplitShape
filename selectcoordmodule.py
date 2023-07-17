from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtCore import Qt

class ClickPointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, iface,txtEdit_X, txtEdit_Y, txtEdit_Message):
        self.canvas = canvas
        self.iface = iface
        self.txtEdit_X = txtEdit_X
        self.txtEdit_Y = txtEdit_Y
        self.txtEdit_Message = txtEdit_Message
        self.original_map_tool = self.canvas.mapTool()
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.point_clicked = False

    def canvasPressEvent(self, event):
        if event.button() == Qt.RightButton and not self.point_clicked:
            layer = self.iface.activeLayer()
            if layer is not None:
                extent = layer.extent()
                point = self.toMapCoordinates(event.pos())

                x = int(point.x())
                y = int(point.y())

                #relative_x = (x - extent.xMinimum())
                #relative_y = (y - extent.yMinimum())

                #print(f"Relative X: {relative_x}, Relative Y: {relative_y}")
                self.txtEdit_Message.clear()
                self.txtEdit_Message.setPlainText("New Origin Coordinate Selected...!")
                self.txtEdit_Message.appendPlainText(f"Selected Coordinate inforation:  [ X: {x}, Y: {y} ]")
                self.txtEdit_X.setText(f"{x}")
                self.txtEdit_Y.setText(f"{y}")
                

                self.point_clicked = True
                self.canvas.unsetMapTool(self)
                self.canvas.setMapTool(self.original_map_tool)        