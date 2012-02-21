#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from Controller import *
from Model import *
from GraphArea import *

def fileDialog(save=False):
    filename = None
    if save:
        action = gtk.FILE_CHOOSER_ACTION_SAVE
    else:
        action = gtk.FILE_CHOOSER_ACTION_OPEN

    # Set up dialog
    dialog = gtk.FileChooserDialog(
        title = None, 
        action = action,
        buttons = (gtk.STOCK_CANCEL, 
                   gtk.RESPONSE_CANCEL,
                   gtk.STOCK_OPEN,
                   gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)

    # Show dialog & get result
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        filename = dialog.get_filename()
    dialog.destroy()
    return filename


def askYesNO(question):
    # Build dialog
    dialog = gtk.MessageDialog(
        type = gtk.MESSAGE_QUESTION,
        buttons = gtk.BUTTONS_YES_NO, 
        message_format = question)

    # Show dialog & get result
    response = dialog.run()
    dialog.destroy()
    return (response == gtk.RESPONSE_YES)

def askUnsavedChanges(quitting):
    question = 'There are unsaved changed.'
    if quitting:
        close = 'Close without saving'
    else:
        close = 'Discard changes'

    # Build dialog
    dialog = gtk.MessageDialog(
        type = gtk.MESSAGE_WARNING,
        buttons = gtk.BUTTONS_NONE,
        message_format = question)
    dialog.add_button('Save', 1)
    dialog.add_button('Cancel', 2)
    dialog.add_button(close, 3)
    dialog.set_default_response(1)

    # Show dialog & get result
    response = dialog.run()
    dialog.destroy()
    if response < 1: 
        response = 2 # default to Cancel
    return response

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
        miOpen = gtk.MenuItem('Open')
        miOpen.connect_object(
            'activate', self.controller.openGame, 'file.open')
        menu.add(miOpen)
        miSave = gtk.MenuItem('Save')
        miSave.connect_object(
            'activate', self.controller.saveGame, 'file.save')
        menu.add(miSave)
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

class StatePane(gtk.VBox):
    def __init__(self, controller):
        gtk.VBox.__init__(self, False, 5)
        self.updating = False
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
        if self.updating: 
            return
        self.updating = True
        # Get info
        graph = self.controller.graph
        numStates = graph.numStates()
        currentState = self.controller.getCurrentState()
        # Update the UI
        self.updateStateCombo(numStates)
        self.updateStateText(currentState)
        self.updateTrCombo(numStates)
        self.populateTransitions(currentState, graph)
        self.updating = False

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
            btn = iconButton(gtk.STOCK_REMOVE)
            btn.connect('clicked', self.controller.removeTransition, cmd)
            hb.pack_start(btn, False, False, 5)
            self.trList.pack_start(hb, False, False)
            hb.show_all()

    def addStateSelection(self):
        # Create elements
        self.stateCombo = gtk.ComboBox(gtk.ListStore(str))
        cell = gtk.CellRendererText()
        self.stateCombo.pack_start(cell, True)
        self.stateCombo.add_attribute(cell, 'text', 0)
        self.stateCombo.connect('changed', self.controller.selectState)
        self.addBtn = iconButton(gtk.STOCK_ADD, text='Create new state')
        self.addBtn.connect('clicked', self.controller.createState)
        self.rmBtn = iconButton(gtk.STOCK_REMOVE, text='Remove')
        self.rmBtn.connect('clicked', self.controller.removeState)
        # Make layout
        hb2 = gtk.HBox(False, 0)
        hb2.pack_start(self.addBtn, False, False)
        self.pack_start(hb2, False)
        hb = gtk.HBox(False, 0)
        hb.pack_start(leftLabel('State:'), False, False, 5)
        hb.pack_start(self.stateCombo, False, False, 5)
        hb.pack_end(self.rmBtn, False, False, 5)
        self.pack_start(hb, False)
        self.pack_start(gtk.HSeparator(), False)

    def addStateText(self):
        self.pack_start(leftLabel('State text:'), False)
        # Text box
        text = gtk.TextView()
        text.set_cursor_visible(True)
        text.set_wrap_mode(gtk.WRAP_CHAR)
        text.set_size_request(0, 100)
        textBuffer = text.get_buffer()
        textBuffer.connect('end-user-action', \
                           self.controller.updateStateText)
        # Scrolled window
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        # Store
        self.stateTextBuffer = textBuffer
        self.stateText = text
        self.pack_start(scroll, False, False)
        self.pack_start(gtk.HSeparator(), False)

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
        btn.connect('clicked', self.cb_add_transition)
        hb.pack_start(btn, False, False, 5)
        vb.pack_start(hb)
        self.trEntry = entry
        self.trCombo = combo
        self.trAdd = btn
        self.pack_start(vb, False, False)

    def addTransitionList(self):
        self.pack_start(gtk.HSeparator(), False)
        self.pack_start(leftLabel('Transitions:'), False)
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

    def cb_add_transition(self, widget):
        command = self.trEntry.get_text()
        endNo = self.trCombo.get_active()
        self.controller.createTransition(widget, (command, endNo))
        self.trEntry.set_text('')

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
        self.graphPane = GraphArea(self.controller)
        hb.pack_start(self.graphPane)
        # Right side
        self.statePane = StatePane(self.controller)
        hb.pack_start(self.statePane, False)
        # Setup
        vb.pack_start(hb, True, True)
        self.window.add(vb)
        self.setTitle()

    def setTitle(self, fileName=None):
        ''' Sets the title of the window '''
        title = 'DFA editor'
        if fileName:
            title = fileName + ' - ' + title
        self.window.set_title(title)

    def delete_event(self, widget, event, data=None):
        ''' Handle the event to delete the window '''
        if self.controller.checkClose():
            return False
        return True


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
