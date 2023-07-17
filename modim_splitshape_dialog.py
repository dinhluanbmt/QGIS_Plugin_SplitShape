# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitShapeDialog
                                 A QGIS plugin
 Split one Shape file into Grid cells and save to shape files
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-07-14
        git sha              : $Format:%H$
        copyright            : (C) 2023 by modim
        email                : dinhluanbmt@naver.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QFileDialog

from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsRectangle, QgsFeature, QgsPalLayerSettings, QgsTextFormat
#from qgis.PyQt.QtCore import QVariant
#import processing

#from qgis.PyQt.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox
#from qgis.PyQt.QtCore import Qt
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'modim_splitshape_dialog_base.ui'))


class SplitShapeDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(SplitShapeDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.shape_to_split = None #global variable
        self.grid_cell_w = 5000
        self.grid_cell_h = 5000
        self.plTxtEdit_ShapeInfo.clear()
        self.le_OriginCoord_X.clear()
        self.le_OriginCoord_Y.clear()
        self.le_GridCell_Width.setText(str(self.grid_cell_w))
        self.le_GridCell_Height.setText(str(self.grid_cell_h))
        self.cb_UseCurrentActiveLayer.stateChanged.connect(self.on_UseCurrentActiveLayer_state_changed)
        self.pbBtn_Open_ShapeFile.clicked.disconnect()
        self.pbBtn_Create_Grid.clicked.disconnect()
        self.pbBtn_Open_ShapeFile.clicked.connect(self.on_pbBtn_Open_ShapeFile_clicked)
        self.pbBtn_Create_Grid.clicked.connect(self.on_pbBtn_Create_Grid_clicked)
    
    #display the area information of the shape file or current active layer
    def display_shape_info(self,layer):
        if layer is not None:
                self.shape_to_split = layer
                self.lineEdit_InputShapeFile.setEnabled(False)
                self.pbBtn_Open_ShapeFile.setEnabled(False)
                str_l1 ="                  Shape Area Information            "
                self.plTxtEdit_ShapeInfo.setPlainText(str_l1)
                # File path of Shape file
                self.plTxtEdit_ShapeInfo.appendPlainText("1. File Path: " + layer.dataProvider().dataSourceUri())
                # get the With, Height information of shape file 
                extent = layer.extent()
                self.plTxtEdit_ShapeInfo.appendPlainText("2. Width: " + str(int(extent.width())) + "  Height: " + str(int(extent.height())))                
                self.plTxtEdit_ShapeInfo.appendPlainText("3. Grid cell size must be smaller than the With, Height of shape file")
                self.plTxtEdit_ShapeInfo.appendPlainText("4. Cell size too small will create a lot of shape files --> must wait for long time")
                # default Origin Coord point is extent.xMinimum(), and extent.yMinimum()
                self.le_OriginCoord_X.setText(str(int(extent.xMinimum())))
                self.le_OriginCoord_Y.setText(str(int(extent.yMinimum())))
                
    def on_UseCurrentActiveLayer_state_changed(self,state):
        if state == Qt.Checked:
            #print("checked")
            layer = self.iface.activeLayer()
            if layer is not None:
                self.shape_to_split = layer
                self.display_shape_info(self.shape_to_split)
        elif state == Qt.Unchecked:
            #print("unchecked")
            self.plTxtEdit_ShapeInfo.clear()
            self.le_OriginCoord_X.clear()
            self.le_OriginCoord_Y.clear()
            self.lineEdit_InputShapeFile.setEnabled(True)
            self.pbBtn_Open_ShapeFile.setEnabled(True)
    def on_pbBtn_Open_ShapeFile_clicked(self):
        # Open file browser dialog with shapefile filter
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Shapefile (*.shp)")
        file_path, _ = file_dialog.getOpenFileName(None, "Select Shapefile")
        if file_path:            
            self.lineEdit_InputShapeFile.setText(file_path)
            shape_name = os.path.splitext(os.path.basename(file_path))[0]
            self.shape_to_split = self.iface.addVectorLayer(file_path,shape_name,'ogr')
            self.display_shape_info(self.shape_to_split)
            #self.lineEdit_InputShapeFile.setText(shape_name)
        file_dialog.done(0)
        
    #function to create grid
    def on_pbBtn_Create_Grid_clicked(self):
        if self.shape_to_split is None:
            return
        # Define the cell size and grid extent        
        extent = self.shape_to_split.extent()
        # Define the offset to move the origin
        offset_x = 0
        offset_y = 0

        # Calculate the number of rows and columns for the grid
        if offset_x == 0 and offset_y == 0 :
            rows = int(extent.height() / self.grid_cell_h) + 1
            columns = int(extent.width() / self.grid_cell_w) + 1
            # Calculate the new origin point
            origin_x = extent.xMinimum()
            origin_y = extent.yMinimum()
        else:
            rows = int(extent.height() / self.grid_cell_h) + 2
            columns = int(extent.width() / self.grid_cell_w) + 2
            # Calculate the new origin point            
            origin_x = extent.xMinimum() - (self.grid_cell_w -(offset_x % self.grid_cell_w))
            origin_y = extent.yMinimum() - (self.grid_cell_h -(offset_y % self.grid_cell_h))



        # Create a new memory vector layer for the grid
        grid_layer = QgsVectorLayer('Polygon?crs=' + self.shape_to_split.crs().toWkt(), 'Grid', 'memory')
        grid_layer.setOpacity(0.2)
        grid_provider = grid_layer.dataProvider()

        # Create grid features
        for row in range(rows):
            for col in range(columns):
                # Calculate the coordinates of the grid cell
                x1 = extent.xMinimum() + col * self.grid_cell_w
                y1 = extent.yMinimum() + row * self.grid_cell_h
                x2 = x1 + self.grid_cell_w
                y2 = y1 + self.grid_cell_h

                # Create a polygon geometry for the grid cell
                geometry = QgsGeometry.fromRect(QgsRectangle(x1, y1, x2, y2))

                # Check if the grid cell's extent intersects with the vector layer extent
                if extent.intersects(geometry.boundingBox()):
                    # Create a new feature and set its geometry
                    feature = QgsFeature()
                    feature.setGeometry(geometry)

                    # Add the feature to the grid layer
                    grid_provider.addFeature(feature)

        # Update the extent
        grid_layer.updateExtents()

        # Add the grid layer to the QGIS project
        QgsProject.instance().addMapLayer(grid_layer)

        # Refresh the map canvas
        self.iface.mapCanvas().refresh()
        
