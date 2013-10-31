# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeometryCopier
                                 A QGIS plugin
 Help to copy geometry in layers
                              -------------------
        begin                : 2013-03-22
        copyright            : (C) 2013 by Nikulin Evgeniy
        email                : nikulin.e at gmail.com
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
#import resources_rc


class GeometryCopier:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/geometry_copier"
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale").toString()[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/geometry_copier_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self._geom_buffer = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.copy_action = QAction(
            QIcon.fromTheme('edit-copy'),
            u"Copy", self.iface.mainWindow())

        self.insert_action = QAction(
            QIcon.fromTheme('edit-insert'),
            u"Insert", self.iface.mainWindow())

        # connect the action to the run method
        QObject.connect(self.copy_action, SIGNAL("triggered()"), self.copy_geometry)
        QObject.connect(self.insert_action, SIGNAL("triggered()"), self.insert_geometry)

        # Add hotkeys
        self.iface.registerMainWindowAction(self.copy_action, "F7")
        self.iface.registerMainWindowAction(self.insert_action, "F8")

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.copy_action)
        self.iface.addToolBarIcon(self.insert_action)
        self.iface.addPluginToMenu(u"&Geometry copier", self.copy_action)
        self.iface.addPluginToMenu(u"&Geometry copier", self.insert_action)

    def unload(self):
        self.iface.unregisterMainWindowAction(self.copy_action)
        self.iface.unregisterMainWindowAction(self.insert_action)
        self.iface.removePluginMenu(u"&Geometry copier", self.copy_action)
        self.iface.removePluginMenu(u"&Geometry copier", self.insert_action)
        self.iface.removeToolBarIcon(self.copy_action)
        self.iface.removeToolBarIcon(self.insert_action)

    def copy_geometry(self):
        layer = self.iface.activeLayer()
        if not layer:
            QMessageBox.information(None, 'Geometry was not copied', 'Select any layer and feature!')
            return
        features = layer.selectedFeatures()
        if len(features) < 1:
            QMessageBox.information(None, 'Geometry was not copied', 'Select any feature!')
            return
        feature = features[0]
        self._geom_buffer = QgsGeometry(feature.geometry())
        #icon change

    def insert_geometry(self):
        layer = self.iface.activeLayer()
        if not layer:
            QMessageBox.information(None, 'Geometry can\'t be inserted', 'Select any layer and feature for inserting!')
            return
        if not self._geom_buffer:
            QMessageBox.information(None, 'Geometry can\'t be inserted', 'Buffer is empty!')
            return
        if not layer.isEditable():
            QMessageBox.critical(None, 'Geometry can\'t be inserted', 'Layer is not editable!')
            return
        if layer.geometryType() != 2 and self._geom_buffer.type() != layer.geometryType():
            QMessageBox.critical(None, 'Geometry can\'t be inserted',
                                 'Layer has other geometry type!\n{0} {1}'.format(str(self._geom_buffer.type()),
                                                                                  str(layer.geometryType())))
            return
        features = layer.selectedFeatures()
        if len(features) < 1:
            QMessageBox.critical(None, 'Geometry can\'t be inserted', 'Select feature for inserting geom!')
            return
        feature = features[0]
        layer.changeGeometry(feature.id(), QgsGeometry(self._geom_buffer))
        self.iface.mapCanvas().refresh()


