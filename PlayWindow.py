#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class PlayWindow(gtk.Window):
    ''' This is a window for demoing the game '''

    def __init__(self, controller):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.controller = controller
        self.playing = True

        self.connect('delete_event', self.delete_event)
        self.connect('destroy', lambda w: 0)
        self.add_content()
        self.set_title('Preview game')
        self.show_all()
        self.connect('focus-in-event', 
                     lambda w, e: self.entry.grab_focus())

        accel_group = gtk.AccelGroup()
        accel_group.connect_group(
            ord('q'), gtk.gdk.CONTROL_MASK, 0, self.close)
        self.add_accel_group(accel_group)

        self.update()

    def close(self, *args):
        # Probably a hack, don't copy this:
        self.emit('delete-event', None)
        self.destroy()

    def add_content(self):
        vb = gtk.VBox(False, 0)
        vb.set_size_request(400, 400)
        
        # Set up text view
        text = gtk.TextView()
        text.set_editable(False)
        text.set_wrap_mode(gtk.WRAP_WORD)
        textBuffer = text.get_buffer()

        # Scrolled window around text
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        vb.pack_start(scroll, padding=5)

        # Set up the text entry
        entry = gtk.Entry()
        entry.connect('activate', self.select_option)
        vb.pack_start(entry, False, padding=5)

        self.text = text
        self.textBuffer = textBuffer
        self.scroll = scroll
        self.entry = entry
        self.add(vb)

    def update(self):
        state = self.controller.getCurrentState()
        text = state.text + '\n\n'
        self.entry.set_text('')
        if state.end:
            text += 'GAME FINISHED'
            self.entry.set_editable(False)
            self.playing = False
        else:
            text += 'Select an action:\n'
            transitions = state.listTransitions()
            for i,(cmd,st) in enumerate(transitions):
                text += '\t%2d> %s\n' % (i+1, cmd)
            self.entry.grab_focus()
        self.append_text(text)

    def append_text(self, text):
        textBuffer = self.textBuffer
        end = textBuffer.get_end_iter()
        textBuffer.insert(end, text)
        end = textBuffer.get_end_iter()
        mark = textBuffer.create_mark(None, end, True)
        self.text.scroll_to_mark(mark, 0)

    def select_option(self, widget, data=None):
        if not self.playing:
            return
        state = self.controller.getCurrentState()
        # Get & check input
        s = self.entry.get_text()
        if not s.isdigit(): return
        n = int(s)
        if not (0 < n <= len(state.transitions)): return

        # Move to the selected state
        to_state = state.listTransitions()[n - 1][1]
        index = self.controller.graph.getIndex(to_state)
        self.controller.selectState(index)

        # Update display
        self.append_text('-'*40 + '\n')
        self.update()

    def delete_event(self, widget, event, data=None):
        self.controller.stopGame()
        return False
