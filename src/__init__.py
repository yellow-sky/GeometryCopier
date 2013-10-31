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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Geometry copier"


def description():
    return "Help to copy geometry in layers"


def version():
    return "Version 0.1"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"


def author():
    return "Nikulin Evgeniy"


def email():
    return "nikulin.e at gmail.com"


def classFactory(iface):
    # load GeometryCopier class from file GeometryCopier
    from geometry_copier import GeometryCopier
    return GeometryCopier(iface)
