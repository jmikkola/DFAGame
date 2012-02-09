#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from Controller import *
from states import *

class WindowMenu(gtk.MenuBar):
    def __init__(self):
        gtk.MenuBar.__init__(self)
        self.fileMenu = self.makeFileMenu()
        self.editMenu = self.makeEditMenu()
        self.playMenu = self.makePlayMenu()

    def makeFileMenu(self):
        mi = gtk.MenuItem('File')
        menu = gtk.Menu()
        miQuit = gtk.MenuItem('Quit')
        menu.add(miQuit)
        mi.set_submenu(menu)
        self.add(mi)
        return mi

    def makeEditMenu(self):
        mi = gtk.MenuItem('Edit')
        menu = gtk.Menu()
        mi.set_submenu(menu)
        self.add(mi)
        return mi

    def makePlayMenu(self):
        mi = gtk.MenuItem('Play')
        menu = gtk.Menu()
        mi.set_submenu(menu)
        self.add(mi)
        return mi

class GraphPane(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.points = []
        self.connect('expose-event', self.draw_graph)

    def draw_graph(self, area, event):
        gc = self.get_style().fg_gc[gtk.STATE_NORMAL]
        for (x, y) in self.points:
            self.window.draw_rectangle(gc, True, x, y, 10, 10)
        return True

    def update(self, points):
        self.points = points
        self.queue_draw()

class StatePane(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 5)
        self.set_border_width(5)
        self.set_size_request(300, -1)
        self.addStateSelection()
        self.addStateText()
        self.addTransitionAdd()
        self.addTransitionList()

    def addStateSelection(self):
        hb = gtk.HBox(False, 0)
        stateLabel = leftLabel('State: ')
        hb.pack_start(stateLabel)
        self.stateCombo = gtk.ComboBox()
        hb.pack_start(self.stateCombo)
        self.pack_start(hb)
        self.pack_start(gtk.HSeparator())

    def addStateText(self):
        self.pack_start(leftLabel('State text:'))
        # Text box
        text = gtk.TextView()
        text.set_cursor_visible(True)
        text.set_wrap_mode(gtk.WRAP_CHAR)
        text.set_size_request(0, 100)
        # Scrolled window
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        # Store
        self.stateTextBuffer = text.get_buffer()
        self.stateText = text
        self.pack_start(scroll, False, False)
        self.pack_start(gtk.HSeparator())

    def addTransitionAdd(self):
        vb = gtk.VBox(False, 0)
        entry = gtk.Entry(max = 100)
        vb.pack_start(entry)
        hb = gtk.HBox(False, 0)
        hb.pack_start(leftLabel('to'), False, False, 5)
        combo = gtk.ComboBox()
        hb.pack_start(combo, False, False, 5)
        btn = gtk.Button('add')
        hb.pack_start(btn, False, False, 5)
        vb.pack_start(hb)
        self.trEntry = entry
        self.trCombo = combo
        self.trAdd = btn
        self.pack_start(vb, False, False)

    def addTransitionList(self):
        # Scrolled Window
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        # List of transitions
        vb = gtk.VBox(False, 0)
        scroll.add_with_viewport(vb)
        self.trList = vb
        self.pack_start(scroll, False, False)

    def setTransitionItems(self, items):
        ''' Creates an element in the list of 
        transitions '''
        self.trList.clear()
        for (n, s) in items:
            row = (n, s, gtk.Button('-'))
            self.trList.append(row)                

class BuilderWindow:
    def __init__(self, controller):
        ''' Set up the window '''
        assert(controller is not None)
        self.controller = controller
        self.setupWindow()
        self.setContent()
        self.window.show_all()

    def setupWindow(self):
        w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.connect('delete_event', self.delete_event)
        w.connect('destroy', lambda w: gtk.main_quit())
        w.set_default_size(800,600)
        self.window = w

    def setContent(self):
        vb = gtk.VBox(False, 0)
        # Menu bar
        self.menuBar = WindowMenu()
        vb.pack_start(self.menuBar, False, False)
        # Main content
        hb = gtk.HBox(False, 0)
        # Left side
        self.graphPane = GraphPane()
        hb.pack_start(self.graphPane)
        # Right side
        self.statePane = StatePane()
        hb.pack_start(self.statePane, False)
        # Setup
        vb.pack_start(hb, False, False)
        self.window.add(vb)
        self.setTitle()

    def setTitle(self, fileName=None):
        ''' Sets the title of the window '''
        title = 'DFA editor'
        if fileName:
            title = fileName + ' - ' + title
        self.window.set_title(title)

    def delete_event(self, widget, event, data=None):
        return False


def leftLabel(text):
    label = gtk.Label(text)
    label.set_alignment(0, 0.5)
    return label

def main():
    controller = Controller()
    builder = BuilderWindow(controller)
    gtk.main()

if __name__ == '__main__':
    main()
