#!/usr/bin/env python3
"""
HIPAA-Lockdown-CLI: GTK4 Graphical User Interface
"""
import sys
import logging
from io import StringIO
import threading

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw

from hipaa_lockdown.modules import auth, filesystem, audit, network, scanner
from hipaa_lockdown.core.legal import DISCLAIMER_TEXT

# Store logs to a string so we can display them in the GUI
log_stream = StringIO()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=log_stream)
logger = logging.getLogger(__name__)

# Re-add console streaming so CLI execution isn't completely blind if launched from terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

MODULES = {
    'Authentication & Identity': auth,
    'Filesystem & Privacy': filesystem,
    'Auditing & Integrity': audit,
    'Network Security': network,
    'Malware Scanning': scanner
}

class DisclaimerDialog(Gtk.Window):
    def __init__(self, parent):
        super().__init__(transient_for=parent)
        self.set_title("Required Action: Legal Acknowledgment")
        self.set_modal(True)
        self.set_default_size(600, 400)
        self.set_hide_on_close(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)

        # Scrolled Window for the text
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # The disclaimer text
        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        # Using monospace for the format block
        textview.get_buffer().set_text(DISCLAIMER_TEXT)
        textview.add_css_class("monospace")
        
        scrolled.set_child(textview)
        box.append(scrolled)

        # Acknowledge Button
        ack_button = Gtk.Button(label="I Understand and Agree")
        ack_button.add_css_class("suggested-action")
        ack_button.connect("clicked", self.on_acknowledge)
        
        # Decline Button
        dec_button = Gtk.Button(label="Decline and Exit")
        dec_button.add_css_class("destructive-action")
        dec_button.connect("clicked", self.on_decline)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.append(dec_button)
        btn_box.append(ack_button)
        box.append(btn_box)

        self.set_child(box)

        self.connect("close-request", self.on_close_request)
        self.parent_app = parent

    def on_acknowledge(self, button):
        self.parent_app.disclaimer_accepted = True
        self.close()

    def on_decline(self, button):
        sys.exit(0)

    def on_close_request(self, window):
        if not hasattr(self.parent_app, 'disclaimer_accepted') or not self.parent_app.disclaimer_accepted:
            sys.exit(0)

class HIPAAAppWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("HIPAA Lockdown - 2026 Audit Tool")
        self.set_default_size(800, 600)
        
        self.disclaimer_accepted = False

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Header Box
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        header_box.set_margin_top(12)
        
        title_label = Gtk.Label(label="<b>System Audit Checklist</b>")
        title_label.set_use_markup(True)
        title_label.set_halign(Gtk.Align.START)
        
        header_box.append(title_label)
        main_vbox.append(header_box)

        # Scrolled area for modules
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_margin_start(12)
        scrolled.set_margin_end(12)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self.list_box)
        main_vbox.append(scrolled)

        # Action Buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_box.set_margin_start(12)
        action_box.set_margin_end(12)
        action_box.set_margin_bottom(12)
        action_box.set_halign(Gtk.Align.END)

        self.btn_audit = Gtk.Button(label="Run System Audit")
        self.btn_audit.connect("clicked", self.on_btn_audit_clicked)
        action_box.append(self.btn_audit)

        self.btn_apply = Gtk.Button(label="Execute Selected Policies")
        self.btn_apply.add_css_class("suggested-action")
        self.btn_apply.connect("clicked", self.on_btn_apply_clicked)
        action_box.append(self.btn_apply)

        main_vbox.append(action_box)

        # Log Text View
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        log_scrolled = Gtk.ScrolledWindow()
        log_scrolled.set_size_request(-1, 150)
        log_scrolled.set_child(self.log_view)
        main_vbox.append(log_scrolled)

        self.set_child(main_vbox)
        
        self.checkboxes = {}
        self.populate_modules()

    def populate_modules(self):
        for row in self.list_box.get_child_at_index(-1) or []:
             self.list_box.remove(row)
             
        for name, module in MODULES.items():
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row_box.set_margin_start(12)
            row_box.set_margin_end(12)
            row_box.set_margin_top(6)
            row_box.set_margin_bottom(6)
            
            check = Gtk.CheckButton()
            check.set_active(True)
            self.checkboxes[name] = check
            row_box.append(check)
            
            label = Gtk.Label(label=f"<b>{name}</b>")
            label.set_use_markup(True)
            label.set_halign(Gtk.Align.START)
            label.set_hexpand(True)
            row_box.append(label)
            
            self.list_box.append(row_box)

    def refresh_logs_gui(self):
        buffer = self.log_view.get_buffer()
        buffer.set_text(log_stream.getvalue())
        # Scroll to bottom
        adj = self.log_view.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False # don't repeat this timeout
        
    def append_log(self, text):
        log_stream.write(text + "\\n")
        GLib.idle_add(self.refresh_logs_gui)

    def on_btn_audit_clicked(self, button):
        self.btn_audit.set_sensitive(False)
        self.btn_apply.set_sensitive(False)
        log_stream.seek(0)
        log_stream.truncate(0)
        self.refresh_logs_gui()
        
        def run_thread():
            logger.info("Starting System Audit (Dry-Run)...")
            for name, module in MODULES.items():
                 if hasattr(module, "run_audit"):
                      logger.info(f"--- Mod: {name} ---")
                      try:
                          module.run_audit()
                      except Exception as e:
                          logger.error(f"Error auditing {name}: {e}")
                          
            logger.info("Audit Completed. Review warnings above for missing policies.")
            GLib.idle_add(lambda: self.btn_audit.set_sensitive(True))
            GLib.idle_add(lambda: self.btn_apply.set_sensitive(True))
            GLib.idle_add(self.refresh_logs_gui)

        threading.Thread(target=run_thread).start()

    def on_btn_apply_clicked(self, button):
        self.btn_audit.set_sensitive(False)
        self.btn_apply.set_sensitive(False)
        log_stream.seek(0)
        log_stream.truncate(0)
        self.refresh_logs_gui()
        
        def run_thread():
            logger.info("Executing Selected HIPAA Policies...")
            for name, module in MODULES.items():
                if self.checkboxes.get(name) and self.checkboxes[name].get_active():
                    if hasattr(module, "run_apply"):
                        logger.info(f"--- Applying: {name} ---")
                        try:
                            module.run_apply()
                        except Exception as e:
                             logger.error(f"Failed to apply {name}: {e}")
                else:
                    logger.info(f"Skipping {name} (Not Selected).")
                    
            logger.info("Execution complete. Recommend rebooting or running the Audit again.")
            GLib.idle_add(lambda: self.btn_audit.set_sensitive(True))
            GLib.idle_add(lambda: self.btn_apply.set_sensitive(True))
            GLib.idle_add(self.refresh_logs_gui)

        threading.Thread(target=run_thread).start()


class HIPAAApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.example.HIPAALockdown')
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = HIPAAAppWindow(self)
        self.win.present()
        
        # Show disclaimer immediately
        dialog = DisclaimerDialog(self.win)
        dialog.present()

def main():
    app = HIPAAApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()
