#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

from states import *


class BuilderWindow:
    def __init__(self):
        ''' Set up the window '''
        window = self._makeWindow()
        window.show_all()

    def _makeWindow(self):
        ''' Creates the window object '''
        # Create window
        w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.connect('delete_event', self.delete_event)
        w.connect('destroy', self.destroy)
        w.set_default_size(800,600)
        # Set content
        vb = gtk.VBox(False, 0)
        vb.pack_start(self._makeMenuBar(), False, False)
        vb.pack_start(self._makeToolBar(), False, False)
        vb.pack_start(self._makeLayout(), False, False)
        w.add(vb)
        # Return the window
        self.window = w
        self.setTitle()
        return w

    def _makeMenuBar(self):
        ''' Create the menu bar '''
        menu = gtk.MenuBar()
        item = gtk.MenuItem('File')
        menu.add(item)
        self.menuBar = menu
        return menu

    def _makeToolBar(self):
        ''' Create the tool bar '''
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_BOTH)
        toolbar.append_item('Save', None, None, None, None)
        self.toolbar = toolbar
        return toolbar

    def _makeLayout(self):
        ''' Creates the HBox within the window '''
        hb = gtk.HBox(False, 0)
        hb.pack_start(self._makeLeftPane())
        hb.pack_start(self._makeRightPane(), False)
        self.hb = hb
        return hb

    def _makeLeftPane(self):
        ''' Creates the VBox holding the left pane '''
        vb = gtk.VBox(False, 0)
        vb.set_border_width(5)
        vb.pack_start(gtk.Button("abc"), False, False)
        vb.pack_start(gtk.Button("def"), False, False)
        self.leftPane = vb
        return vb

    def _makeRightPane(self):
        ''' Creates the VBox holding the right pane '''
        vb = gtk.VBox(False, 5)
        vb.set_border_width(5)
        vb.set_size_request(300, -1)
        # State select & text
        vb.pack_start(self._makeStateSelection(), False, False)
        vb.pack_start(self._makeStateText(), False, False)
        # Transitions
        frame = gtk.Frame('Transitions')
        trScroll = gtk.ScrolledWindow()
        trScroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        frame.add(trScroll)
        vb.pack_start(frame, False, False)
        # Return pane
        self.rightPane = vb
        return vb

    def _makeStateSelection(self):
        ''' Creates selection box for states '''
        hb = gtk.HBox(False, 0)
        stateLabel = gtk.Label('State: ')
        hb.pack_start(stateLabel)
        stateCombo = gtk.Combo()
        hb.pack_start(stateCombo)
        self.stateCombo = stateCombo
        return hb

    def _makeStateText(self):
        ''' Creates box for entering a state's text '''
        buff = gtk.TextBuffer()
        text = gtk.TextView(buff)
        text.set_cursor_visible(True)
        text.set_wrap_mode(gtk.WRAP_CHAR)
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.stateTextBuffer = buff
        self.stateText = text
        return scroll

    def setTitle(self, fileName=None):
        ''' Sets the title of the window '''
        title = 'DFA editor'
        if fileName:
            title = fileName + ' - ' + title
        self.window.set_title(title)

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == '__main__':
    builder = BuilderWindow()
    builder.main()
