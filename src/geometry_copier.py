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
from PyQt4.QtCore import QFileInfo, QCoreApplication, QTranslator, qVersion, QSettings, QObject, SIGNAL
from PyQt4.QtGui import QMessageBox, QIcon, QAction
from qgis.core import QgsGeometry, QgsApplication, QgsVectorLayer
# Initialize Qt resources from file resources.py
import resources
import sip


class GeometryCopier:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/geometry_copier"
        # initialize locale
        locale_path = ""
        if sip.getapi("QVariant") > 1:
            # new API style
            locale = QSettings().value("locale/userLocale")[0:2]
        else:
            # the old API style
            locale = QSettings().value("locale/userLocale").toString()[0:2]

        if QFileInfo(self.plugin_dir).exists():
            locale_path = self.plugin_dir + "/i18n/geometry_copier_" + locale + ".qm"

        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self._geom_buffer = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.copy_action = QAction(
            QIcon(':/plugins/geometrycopier/mActionEditCopyGeom.png'),
            self.tr(u"Copy geometry"), self.iface.mainWindow())

        self.insert_action = QAction(
            QIcon(':/plugins/geometrycopier/mActionEditPasteGeom.png'),
            self.tr(u"Insert geometry"), self.iface.mainWindow())

        # connect the action to the run method
        QObject.connect(self.copy_action, SIGNAL("triggered()"), self.copy_geometry)
        QObject.connect(self.insert_action, SIGNAL("triggered()"), self.insert_geometry)

        # Add hotkeys
        self.iface.registerMainWindowAction(self.copy_action, "F7")
        self.iface.registerMainWindowAction(self.insert_action, "F8")

        # Add toolbar button and menu item
        self.iface.digitizeToolBar().addAction(self.copy_action)
        self.iface.digitizeToolBar().addAction(self.insert_action)
        self.iface.addPluginToVectorMenu(u"&Geometry copier", self.copy_action)
        self.iface.addPluginToVectorMenu(u"&Geometry copier", self.insert_action)

        # Add global signals
        QObject.connect(self.iface, SIGNAL('currentLayerChanged(QgsMapLayer *)'), self.check_buttons_state)
        QObject.connect(self.iface.mapCanvas(), SIGNAL('selectionChanged(QgsMapLayer *)'), self.check_buttons_state)
        QObject.connect(self.iface.actionToggleEditing(), SIGNAL('triggered()'), self.check_buttons_state)

        #iface.actionToggleEditing().triggered

        # init state
        self.check_buttons_state(None)

    def unload(self):
        self.iface.unregisterMainWindowAction(self.copy_action)
        self.iface.unregisterMainWindowAction(self.insert_action)
        self.iface.removePluginVectorMenu(u"&Geometry copier", self.copy_action)
        self.iface.removePluginVectorMenu(u"&Geometry copier", self.insert_action)
        self.iface.digitizeToolBar().removeAction(self.copy_action)
        self.iface.digitizeToolBar().removeAction(self.insert_action)
        QObject.disconnect(self.iface, SIGNAL('currentLayerChanged(QgsMapLayer *)'), self.check_buttons_state)
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL('selectionChanged(QgsMapLayer *)'), self.check_buttons_state)
        QObject.disconnect(self.iface.actionToggleEditing(), SIGNAL('triggered()'), self.check_buttons_state)

    def check_buttons_state(self, layer=None):
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            self.copy_action.setDisabled(True)
            self.insert_action.setDisabled(True)
            return
        sel_feat_count = layer.selectedFeatureCount()
        if sel_feat_count != 1:
            self.copy_action.setDisabled(True)
            self.insert_action.setDisabled(True)
            return
        self.copy_action.setEnabled(True)  # copy button can be pressed!
        if not layer.isEditable() or not self._geom_buffer or self._geom_buffer.type() != layer.geometryType():
            self.insert_action.setDisabled(True)
            return
        self.insert_action.setEnabled(True)  # insert button can be pressed! (type geom??)

    def copy_geometry(self):
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            QMessageBox.information(None, self.tr('Geometry was not copied'),
                                    self.tr('Select any vector layer and feature!'))
            return
        sel_feat_count = layer.selectedFeatureCount()
        if sel_feat_count != 1:
            QMessageBox.information(None, self.tr('Geometry was not copied'),
                                    self.tr('Select one feature!'))
            return
        feature = layer.selectedFeatures()[0]
        self._geom_buffer = QgsGeometry(feature.geometry())
        self.check_buttons_state()

    def insert_geometry(self):
        layer = self.iface.activeLayer()
        if not isinstance(layer, QgsVectorLayer):
            QMessageBox.information(None, self.tr('Geometry can\'t be inserted'),
                                    self.tr('Select any vector layer and feature for inserting geom!'))
            return
        if not self._geom_buffer:
            QMessageBox.information(None, self.tr('Geometry can\'t be inserted'), self.tr('Buffer is empty!'))
            return
        if not layer.isEditable():
            QMessageBox.critical(None, self.tr('Geometry can\'t be inserted'), self.tr('Layer is not editable!'))
            return
        if self._geom_buffer.type() != layer.geometryType():  # and layer.geometryType() != 2:
            QMessageBox.critical(None, self.tr('Geometry can\'t be inserted'),
                                 self.tr('Target layer has other geometry type!'))
            return
        sel_feat_count = layer.selectedFeatureCount()
        if sel_feat_count != 1:
            QMessageBox.critical(None, self.tr('Geometry can\'t be inserted'),
                                 self.tr('Select one feature for inserting geom!'))
            return
        feature = layer.selectedFeatures()[0]
        layer.changeGeometry(feature.id(), QgsGeometry(self._geom_buffer))
        self.iface.mapCanvas().refresh()

    def tr(self, text):
        return QCoreApplication.translate("GeometryCopier", text)