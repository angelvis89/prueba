import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import threading
import http.server
import socketserver
import subprocess
import webbrowser
import os
import socket
import keyboard

ADMIN_PASSWORD = "1234"
# combinación por defecto ctrl+alt+a
ADMIN_COMBO = 'ctrl+alt+a'
# IP de la impresora en la red local
PRINTER_IP = '192.168.0.100'

class KioskApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Kiosk de Impresiones')
        self.geometry('800x600')
        self.attributes('-fullscreen', True)
        self.time_left = 300
        self.is_locked = False
        self.protocol('WM_DELETE_WINDOW', lambda: None)
        self.create_widgets()
        self.admin_password = ADMIN_PASSWORD
        self.admin_combo = ADMIN_COMBO
        self.keyboard_blocked = False
        self.internet_blocked = False
        self.apply_restrictions()
        threading.Thread(target=self.start_server, daemon=True).start()
        self.after(1000, self.update_timer)

    def create_widgets(self):
        self.timer_label = tk.Label(self, text='Tiempo restante: 05:00', font=('Arial', 24))
        self.timer_label.pack(pady=20)
        self.usb_btn = tk.Button(self, text='Imprimir por USB', font=('Arial', 32), width=20, height=3, command=self.print_usb)
        self.usb_btn.pack(pady=20)
        self.whats_btn = tk.Button(self, text='Imprimir por WhatsApp', font=('Arial', 32), width=20, height=3, command=self.print_whatsapp)
        self.whats_btn.pack(pady=20)

    def update_timer(self):
        if self.time_left > 0 and not self.is_locked:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f'Tiempo restante: {mins:02d}:{secs:02d}')
            self.after(1000, self.update_timer)
        else:
            self.lock_kiosk()

    def lock_kiosk(self):
        self.is_locked = True
        self.usb_btn.config(state='disabled')
        self.whats_btn.config(state='disabled')
        self.timer_label.config(text='Tiempo agotado')

    def reset_timer(self, seconds=300):
        self.time_left = seconds
        self.is_locked = False
        self.usb_btn.config(state='normal')
        self.whats_btn.config(state='normal')
        self.update_timer()

    def print_usb(self):
        filetypes = [
            ('Archivos permitidos', ('*.pdf', '*.docx', '*.xlsx', '*.pptx', '*.jpg', '*.jpeg', '*.png', '*.zip', '*.rar'))
        ]
        path = filedialog.askopenfilename(title='Seleccione archivo', filetypes=filetypes, initialdir='D:/')
        if path:
            try:
                os.startfile(path, 'print')
                messagebox.showinfo('Impresión', 'Archivo enviado a la impresora')
            except Exception as e:
                messagebox.showerror('Error', str(e))

    def print_whatsapp(self):
        webbrowser.open('https://web.whatsapp.com')

    def show_admin_menu(self, event=None):
        # permitir escribir la contraseña
        self.unblock_keyboard()
        pwd = simpledialog.askstring('Admin', 'Contraseña:', show='*')
        if pwd != self.admin_password:
            self.block_keyboard()
            return
        menu = tk.Toplevel(self)
        menu.title('Panel de Administración')
        menu.geometry('400x400')
        tk.Button(menu, text='Aumentar 5 minutos', command=lambda: self.reset_timer(self.time_left + 300)).pack(pady=10)
        tk.Button(menu, text='Activar/Desactivar teclado', command=self.toggle_keyboard).pack(pady=10)
        tk.Button(menu, text='Activar/Desactivar internet', command=self.toggle_internet).pack(pady=10)
        tk.Button(menu, text='Cambiar contraseña', command=self.change_password).pack(pady=10)
        tk.Button(menu, text='Cambiar combinación', command=self.change_combo).pack(pady=10)
        tk.Button(menu, text='Cerrar aplicación', command=self.admin_quit).pack(pady=10)

        def close_menu():
            menu.destroy()
            self.block_keyboard()

        menu.protocol('WM_DELETE_WINDOW', close_menu)

    # --- Restricciones -------------------------------------------------
    def apply_restrictions(self):
        if not self.keyboard_blocked:
            self.block_keyboard()
        if not self.internet_blocked:
            self.block_internet()

    def admin_quit(self):
        self.remove_restrictions()
        self.destroy()

    def block_keyboard(self):
        # registrar combinación de administración y bloquear el resto de teclas
        self.combo_keys = [k.strip() for k in self.admin_combo.split('+')]
        self.hotkey = keyboard.add_hotkey(self.admin_combo, lambda: self.show_admin_menu(), suppress=True)
        keyboard.hook(self._keyboard_blocker)
        self.keyboard_blocked = True

    def _keyboard_blocker(self, event):
        if all(keyboard.is_pressed(k) for k in self.combo_keys):
            return
        event.suppress = True

    def unblock_keyboard(self):
        keyboard.unhook_all()
        keyboard.clear_all_hotkeys()
        self.keyboard_blocked = False

    def toggle_keyboard(self):
        if self.keyboard_blocked:
            self.unblock_keyboard()
        else:
            self.block_keyboard()

    def block_internet(self):
        whatsapp_ip = socket.gethostbyname('web.whatsapp.com')
        rules = [
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=KioskBlockAll', 'dir=out', 'action=block', 'remoteip=any'],
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=KioskAllowWhatsApp', 'dir=out', 'action=allow', f'remoteip={whatsapp_ip}'],
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=KioskAllowPrinter', 'dir=out', 'action=allow', f'remoteip={PRINTER_IP}'],
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=KioskInbound', 'dir=in', 'action=allow', 'localport=5000', 'protocol=TCP']
        ]
        for cmd in rules:
            try:
                subprocess.run(cmd, check=False)
            except Exception:
                pass
        self.internet_blocked = True

    def unblock_internet(self):
        rules = [
            ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=KioskBlockAll'],
            ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=KioskAllowWhatsApp'],
            ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=KioskAllowPrinter'],
            ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=KioskInbound']
        ]
        for cmd in rules:
            try:
                subprocess.run(cmd, check=False)
            except Exception:
                pass
        self.internet_blocked = False

    def toggle_internet(self):
        if self.internet_blocked:
            self.unblock_internet()
        else:
            self.block_internet()

    def change_password(self):
        new_pwd = simpledialog.askstring('Admin', 'Nueva contraseña:', show='*')
        if new_pwd:
            self.admin_password = new_pwd

    def change_combo(self):
        new_combo = simpledialog.askstring('Admin', 'Nueva combinación (ej. ctrl+alt+w):')
        if new_combo:
            self.admin_combo = new_combo
            if self.keyboard_blocked:
                self.unblock_keyboard()
                self.block_keyboard()

    def remove_restrictions(self):
        self.unblock_keyboard()
        self.unblock_internet()

    def start_server(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(inner_self):
                if inner_self.path == '/reset':
                    self.reset_timer()
                    inner_self.send_response(200)
                    inner_self.end_headers()
                    inner_self.wfile.write(b'OK')
                else:
                    inner_self.send_error(404)
        with socketserver.TCPServer(('', 5000), Handler) as httpd:
            httpd.serve_forever()

if __name__ == '__main__':
    app = KioskApp()
    app.mainloop()
