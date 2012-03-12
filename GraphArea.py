#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
from math import pi, sqrt, hypot, cos, sin, atan2

from Controller import *
from Model import *

def distance(x1, y1, x2, y2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return sqrt(dx*dx + dy*dy)

class GraphArea(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, controller):
        gtk.DrawingArea.__init__(self)
        self.controller = controller
        # Settings
        self.radius = 10
        self.minDragDist = 5
        self.arcSize = 0.8
        self.arrowLength = 10
        self.arrowAngle = pi/6
        # Information for dragging nodes
        self.stateSelected = None
        self.dragStart = None
        # Setup clicking on the graph
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | \
                        gtk.gdk.BUTTON_RELEASE_MASK | \
                        gtk.gdk.POINTER_MOTION_MASK)
        self.connect('button-press-event', self.cb_button_press)
        self.connect('button-release-event', self.cb_button_release)
        # Set this to be re-rendered upon a state update
        controller.registerListener(self.queue_draw)

    # ----------------------------------
    # Functions for event handling
    # ----------------------------------

    def cb_button_press(self, event, data):
        ''' Handle a mouse button press on the graph area '''
        if data.button == 1:
            self.stateSelected = self.selectNode(data.x, data.y)
            self.dragStart = (data.x, data.y)
        else:
            self.stateSelected = None

    def cb_button_release(self, event, data):
        ''' Handle the end of a mouse button press on the 
        graph area '''
        stateNo = self.stateSelected
        if stateNo is not None:
            x, y = data.x, data.y
            if distance(x, y, *self.dragStart) >= self.minDragDist:
                self.controller.moveState(stateNo, (x,y))

    def selectNode(self, x, y):
        ''' Selects the node (if any) under 
        the mouse click '''
        graph = self.controller.graph
        for stateNo in xrange(graph.numStates()):
             sx, sy = graph.getState(stateNo).getPosition()
             if distance(x, y, sx, sy) <= self.radius:
                 self.controller.selectState(stateNo)
                 return stateNo
        return None
             
    # ----------------------------------
    # Functions for drawing
    # ----------------------------------

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
        cr.set_line_width(1)

        controller = self.controller
        graph = controller.graph
        npoints = graph.numStates()

        green = (0, 0.8, 0)
        red   = (1, 0, 0)
        black = (0, 0, 0)

        # Show current selection
        x, y = controller.getCurrentState().getPosition()
        self.draw_selection(cr, x, y)

        # Draw transitions
        for i in xrange(npoints):
            fromState = graph.getState(i)
            fromXY = fromState.getPosition()
            for (_, toState) in fromState.listTransitions():
                j = graph.getIndex(toState)
                if i == j:
                    self.draw_loop(cr, fromXY)
                else:
                    toXY = graph.getState(j).getPosition()
                    self.draw_transition(cr, fromXY, toXY)

        # Draw vertices
        for i in xrange(npoints):
            xy = graph.getState(i).getPosition()
            if i == 0: 
                color = green
            elif graph.getState(i).end:
                color = red
            else:
                color = black
            self.draw_node(cr, xy, color)

    def draw_selection(self, cr, x, y):
        cr.save()
        cr.set_source_rgb(0.8, 0.8, 1.0)
        cr.arc(x, y, self.radius + 4, 0, 2*pi)
        cr.fill()
        cr.restore()


    def draw_node(self, cr, (x, y), color):
        cr.save()
        cr.set_source_rgb(*color)
        cr.arc(x, y, self.radius, 0, 2 * pi)
        cr.fill()
        cr.restore()

    def draw_transition(self, cr, (fromX, fromY), (toX, toY)):
        # == Math ==
        # Get arc center & radius
        vx, vy = get_vect(fromX, fromY, toX, toY)
        cx, cy = get_offset_pt(fromX, fromY, vx, vy, self.arcSize)
        radius = distance(cx, cy, fromX, fromY)
        # Get starting & ending angles
        v1 = get_vect(cx, cy, fromX, fromY)
        v2 = get_vect(cx, cy, toX, toY)
        angle1 = atan2(v1[1], v1[0])
        angle2 = atan2(v2[1], v2[0])
        # Get point where arc intersection the "to" node
        ix, iy = get_circle_intersection(cx, cy, radius, \
                                         toX, toY, self.radius)
        # Get angle of the arc where it intersects the node
        cix, ciy = get_vect(ix, iy, cx, cy)
        intersectAngle = atan2(ciy, cix) + pi/2

        # == Drawing ==
        cr.save()
        cr.set_source_rgb(0, 0, 0)
        # Draw arc
        cr.arc(cx, cy, radius, angle1, angle2)
        cr.stroke()
        # Draw arrow
        self.draw_arrow(cr, ix, iy, intersectAngle)
        cr.restore()

    def draw_arrow(self, cr, x, y, angle):
        size = self.arrowLength
        theta = self.arrowAngle
        x1 = x + size * cos(angle + theta)
        y1 = y + size * sin(angle + theta)
        x2 = x + size * cos(angle - theta)
        y2 = y + size * sin(angle - theta)
        cr.move_to(x, y)
        cr.line_to(x1, y1)
        cr.stroke()
        cr.move_to(x, y)
        cr.line_to(x2, y2)
        cr.stroke()

    def draw_loop(self, cr, (x, y)):
        r = self.radius
        theta = 3*pi/8
        dx, dy = r * cos(theta), -r * sin(theta)
        startx, starty = x + dx, y + dy
        end_dx, end_dy = -2 * dx, 0
        cp1x, cp1y = 3 * dx, 3 * dy
        cp2x, cp2y = -2 * dx - cp1x, cp1y

        cr.save()
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(startx, starty)
        cr.rel_curve_to(cp1x, cp1y, cp2x, cp2y, end_dx, end_dy)
        cr.stroke()
        self.draw_arrow(cr, startx, starty, -theta)
        cr.restore()


def get_vect(x1, y1, x2, y2):
    ''' Returns the vector between the two points '''
    return (x2 - x1), (y2 - y1)

def get_offset_pt(x, y, vx, vy, scale):
    ''' Calculates a point offset from a line '''
    # 90 degree rotation & scale
    x1, y1 = -vy * scale, vx * scale
    # Midpoint of vector
    x2, y2 = (vx * 0.5 + x), (vy * 0.5 + y)
    # result
    return (x1 + x2), (y1 + y2)

def get_circle_intersection(x0, y0, r0, x1, y1, r1):
    ''' Returns the first intersection of the circle at
    x0, y0 with radius r0 and the circle at x1, y1 with
    radius r1 '''
    # Formule from http://local.wasp.uwa.edu.au/~pbourke/geometry/2circle/ 
    d = hypot(x1 - x0, y1 - y0)
    a = (r0**2 - r1**2 + d**2) / (2 * d)
    h = sqrt(r0**2 - a**2)
    x2 = x0 + (x1 - x0) * a/d
    y2 = y0 + (y1 - y0) * a/d
    x = x2 + (y1 - y0) * h/d
    y = y2 - (x1 - x0) * h/d
    return x, y
    
