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
        self.draw_graph(cr)

    def draw_graph(self, cr):
        npoints = self.graph.numStates()
        indexes = self.getIndexes(npoints)
        scale = lambda p: 20 + 20*p
        green = (0, 0.5, 0)

        # Draw vertices
        for i in xrange(npoints):
            x, y = indexes[i]
            self.draw_node(cr, scale(x), scale(y), green)

        # Draw transitions
        for i in xrange(npoints):
            print "drawing transitions for state", i
            fromX, fromY = indexes[i]
            fromState = self.graph.getState(i)
            for (_, toState) in fromState.listTransitions():
                j = self.graph.getIndex(toState)
                print "\tto state", j
                toX, toY = indexes[j]
                self.draw_transition(cr, scale(fromX), scale(fromY), scale(toX), scale(toY))
        return True

    def draw_node(self, cr, x, y, color):
        cr.save()
        cr.set_source_rgb(*color)
        cr.arc(x, y, 5, 0, 2 * pi)
        cr.fill()
        cr.restore()

    def draw_transition(self, cr, fromX, fromY, toX, toY):
        cr.save()
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(fromX, fromY)
        cr.line_to(toX, toY)
        cr.stroke()
        cr.restore()

    def getIndexes(self, npoints):
        return [(i%10, i/10) for i in xrange(npoints)]
