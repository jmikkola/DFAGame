#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
from math import pi

from Controller import *
from Model import *

class GraphArea(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, controller):
        gtk.DrawingArea.__init__(self)
        self.controller = controller
        self.graph = controller.graph
        #self.connect('expose-event', self.draw_graph)
        controller.registerListener(self.queue_draw)

    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context
        cr = self.window.cairo_create()

        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()

        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        # Fill the background with white
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

    def draw_graph(self, cr):
        npoints = self.graph.numStates()
        indexes = self.getIndexes(npoints)
        for i in xrange(npoints):
            x, y = indexes[i]
            self.draw_node(x, y, cr, (0,1,0))
        return True

    def draw_node(self, x, y, cr, color):
        cr.set_source_rgb(*color)
        width, height = 20, 20
        cr.move_to(0.5, 0.5)
        cr.arc(width / 2.0, height / 2.0, radius / 2.0 - 20, 0, 2 * pi)
        cr.stroke()
        cr.arc(width / 2.0, height / 2.0, radius / 3.0 - 10, pi / 3, 2 * pi / 3)
        cr.stroke()

    def getIndexes(self, npoints):
        return [(i%10, i/10) for i in xrange(npoints)]
