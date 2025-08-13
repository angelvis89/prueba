# Kiosk de impresiones

Este repositorio contiene un prototipo de aplicación de quiosco para Windows.

## Requerimientos
- Windows 10 Pro con **Python 3.10+** y `pip`
- Tkinter (incluido en Windows)
- Los scripts `.bat` instalan automáticamente los módulos `keyboard` (kiosco) y `requests` (reactivación remota) si no están presentes

## Uso
1. En la PC del quiosco ejecutar `run_kiosk.bat` **como administrador**. Si se ejecuta sin privilegios la aplicación mostrará un error y se cerrará. El script comprueba que existan Python y la librería `keyboard`, los instala si faltan y luego lanza `kiosk_app.py` en pantalla completa con dos botones grandes: "Imprimir por USB" e "Imprimir por WhatsApp" y un cronómetro de cinco minutos.
2. Al arrancar se bloquea todo el teclado y la salida a Internet, excepto la combinación `Ctrl+Alt+A`, el sitio `https://web.whatsapp.com` y la IP configurada de la impresora. El usuario sólo puede usar el mouse.
3. El tiempo se agota y las opciones quedan deshabilitadas. Para reactivar el kiosco desde otra PC en la misma red ejecutar `run_remote_activate.bat <IP del kiosco>`, que instalará `requests` si es necesario y enviará la orden de reinicio del temporizador.
4. Combinación y contraseña de administrador por defecto: `Ctrl+Alt+A` y `1234`. Desde el panel de administración se puede añadir tiempo, cambiar contraseña y combinación, activar/desactivar teclado e Internet y **cerrar la aplicación**. Al cerrarla se restauran las reglas de firewall y se vuelve a habilitar el teclado.

## Compilar a ejecutable
En Windows se puede utilizar:

```
pyinstaller --noconsole kiosk_app.py
pyinstaller --noconsole remote_activate.py
```

## Nota
El script utiliza reglas del firewall de Windows y el módulo `keyboard` para bloquear teclas. Se requiere ejecutarlo con privilegios de administrador para aplicar y revertir dichos cambios. Pruebe en un entorno controlado antes de usarlo en producción.
