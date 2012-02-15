#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from Controller import *
from Model import *

class WindowMenu(gtk.MenuBar):
    def __init__(self, controller):
        gtk.MenuBar.__init__(self)
        self.controller = controller
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
    def __init__(self, controller):
        gtk.DrawingArea.__init__(self)
        self.controller = controller
        self.points = []
        self.connect('expose-event', self.draw_graph)
        controller.registerListener(self.queue_draw)

    def draw_graph(self, area, event):
        graph = self.controller.graph
        gc = self.get_style().fg_gc[gtk.STATE_NORMAL]
        npoints = graph.numStates()
        indexes = self.getIndexes(npoints)
        for i in xrange(npoints):
            x, y = indexes[i]
            self.window.draw_rectangle(gc, True, 20 + x*10, 20 + y*10, 10, 10)
        return True

    def getIndexes(self, npoints):
        return [(i/10, i%10) for i in xrange(npoints)]

class StatePane(gtk.VBox):
    def __init__(self, controller):
        gtk.VBox.__init__(self, False, 5)
        self.controller = controller
        self.set_border_width(5)
        self.set_size_request(300, -1)
        self.addStateSelection()
        self.addStateText()
        self.addTransitionAdd()
        self.addTransitionList()
        self.update()
        controller.registerListener(self.update)

    def update(self):
        # Get info
        graph = self.controller.graph
        numStates = graph.numStates()
        currentState = self.controller.getCurrentState()
        # Update the UI
        self.updateStateCombo(numStates)
        self.updateStateText(currentState)
        self.updateTrCombo(numStates)
        self.populateTransitions(currentState, graph)

    def updateStateCombo(self, numStates):
        # Clear existing contents
        model = self.stateCombo.get_model()
        model.clear()
        # Set new contents
        for i in xrange(numStates):
            s = '#' + str(i)
            self.stateCombo.append_text(s)
        self.stateCombo.set_active(self.controller.selection)

    def updateStateText(self, state):
        text = state.text
        self.stateTextBuffer.set_text(text)

    def updateTrCombo(self, numStates):
        self.trCombo.get_model().clear()
        for i in xrange(numStates):
            self.trCombo.append_text('#' + str(i))
            
    def populateTransitions(self, state, graph):
        for child in self.trList.get_children():
            self.trList.remove(child)
        for (cmd, st) in state.listTransitions():
            hb = gtk.HBox()
            text = cmd + ' to #' + str(graph.getIndex(st))
            hb.pack_start(leftLabel(text), False, False, 5)
            hb.pack_start(iconButton(gtk.STOCK_REMOVE), False, False)
            self.trList.pack_start(hb, False, False)

    def addStateSelection(self):
        # Create elements
        self.stateCombo = gtk.ComboBox(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        self.stateCombo.pack_start(cell, True)
        self.stateCombo.add_attribute(cell, 'text', 0)
        self.addBtn = iconButton(gtk.STOCK_ADD, text='Create new state')
        self.addBtn.connect('clicked', self.controller.createState)
        self.rmBtn = iconButton(gtk.STOCK_REMOVE, text='Remove')
        # Make layout
        hb2 = gtk.HBox(False, 0)
        hb2.pack_start(self.addBtn, False, False)
        self.pack_start(hb2)
        hb = gtk.HBox(False, 0)
        hb.pack_start(leftLabel('State:'), False, False, 5)
        hb.pack_start(self.stateCombo, False, False, 5)
        hb.pack_end(self.rmBtn, False, False, 5)
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
        # Set up combo box
        combo = gtk.ComboBox(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        # Make layout
        vb = gtk.VBox(False, 0)
        vb.pack_start(leftLabel('Add a transition:'))
        entry = gtk.Entry(max = 100)
        vb.pack_start(entry)
        hb = gtk.HBox(False, 0)
        hb.pack_start(leftLabel('to'), False, False, 5)
        hb.pack_start(combo, False, False, 5)
        btn = gtk.Button('add')
        hb.pack_start(btn, False, False, 5)
        vb.pack_start(hb)
        self.trEntry = entry
        self.trCombo = combo
        self.trAdd = btn
        self.pack_start(vb, False, False)

    def addTransitionList(self):
        self.pack_start(gtk.HSeparator())
        self.pack_start(leftLabel('Transitions:'))
        # Scrolled Window
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
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
        self.menuBar = WindowMenu(self.controller)
        vb.pack_start(self.menuBar, False, False)
        # Main content
        hb = gtk.HBox(False, 0)
        # Left side
        self.graphPane = GraphPane(self.controller)
        hb.pack_start(self.graphPane)
        # Right side
        self.statePane = StatePane(self.controller)
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

def iconButton(stock_id, text=None):
    btn = gtk.Button()
    img = gtk.Image()
    img.set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
    if text:
        hbx = gtk.HBox(False, 0)
        hbx.pack_start(img, padding=5)
        hbx.pack_start(gtk.Label(text), padding=5)
        btn.add(hbx)
    else:
        btn.add(img)
    return btn

def main():
    ''' This method starts the program '''
    # TODO: parse any args here
    controller = Controller()
    builder = BuilderWindow(controller)
    # Transfer control to GTK event loop
    gtk.main()

if __name__ == '__main__':
    main()
