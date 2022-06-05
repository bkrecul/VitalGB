from kivy import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from translate import Translator
from plyer import stt


class DialogoCargarAngulos(BoxLayout):
    pass


class DialogoCargarFuerza(BoxLayout):
    pass


class DialogoObservaciones(BoxLayout):
    def activar_microfono(self):
        from kivy.clock import Clock
        if not stt.listening:
            self.ids.icono.text_color = 0, 1, 0, 1
            try:
                stt.start()
                self.escuchar = Clock.schedule_interval(lambda dt: self.revisar_microfono(), 1)
            except Exception as mensaje:
                popup = PopUpException(traductor(mensaje))
                popup.open()
        else:
            stt.stop()
            self.copiar_texto()

    def revisar_microfono(self):
        # popup = PopUpException(str(stt.listening))
        # popup.open()
        if not stt.listening:
            self.ids.icono.text_color = 1, 0, 0, 1
            self.escuchar.cancel()
            self.copiar_texto()

    def copiar_texto(self):
        try:
            lectura = f'{stt.results[0]} '
            texto_anterior = self.ids.observaciones.text
            self.ids.observaciones.text = f'{texto_anterior}{lectura}'
        except:
            pass


class DialogoCargarDatosInstitucionales(BoxLayout):
    pass


def traductor(mensaje):
    mensaje = str(mensaje)
    translator = Translator(to_lang='es')
    try:
        mensaje_translated = translator.translate(mensaje)
    except:
        return mensaje
    else:
        return mensaje_translated


def crear_dialogos(tipo, **kwargs):
    if tipo == 0:
        return MDDialog(title='Dispositivo desconectado', text="Usted no está conectado al dispositivo, "
                                                               "¿quiere agregar medidas manualmente?",
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1),),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 1:
        return MDDialog(title="Ángulos:", type="custom", content_cls=DialogoCargarAngulos(),
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1), ),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 2:
        return MDDialog(title="Esfuerzo:", type="custom", content_cls=DialogoCargarFuerza(),
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1), ),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 3:
        return MDDialog(title='ELIMINAR SELECCIÓN', text="ADVERTENCIA: ESTA ACCIÓN BORRARÁ LOS DATOS PERMANENTEMENTE. "
                                                               "¿CONTINUAR?",
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(1,0,0,1),),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(1,0,0,1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 4:
        return MDDialog(title='Añadir observaciones', type="custom", content_cls=DialogoObservaciones(),
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1), ),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 5:
        return MDDialog(title='Agregar datos institucionales', type='custom', auto_dismiss=False,
                        content_cls=DialogoCargarDatosInstitucionales(),
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1)),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])


class PopUpExportSuccessful(Popup):  # Message box if user inputs an existent module name

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def enviar(self):
        if platform == 'android':
            from jnius import autoclass
            from jnius import cast
            try:
                StrictMode = autoclass('android.os.StrictMode')
                StrictMode.disableDeathOnFileUriExposure()
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                shareIntent = Intent(Intent.ACTION_SEND)  # ACTION_OPEN_DOCUMENT #ACTION_SEND #ACTION_VIEW
                imageFile = File(self.path)
                uri = Uri.fromFile(imageFile)
                shareIntent.setData(uri)
                shareIntent.setType("*/*")
                parcelable = cast('android.os.Parcelable', uri)
                shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                shareIntent.putExtra(Intent.EXTRA_STREAM, parcelable)
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(shareIntent)
            except:
                popup = Popup(title='Ops!', content=Label(text=f'Algo salió mal.'),
                              size_hint=(0.7, 0.2))
                popup.open()
            self.dismiss()

    def abrir(self):
        if platform == 'android':
            from jnius import autoclass
            from jnius import cast
            try:
                StrictMode = autoclass('android.os.StrictMode')
                StrictMode.disableDeathOnFileUriExposure()
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                shareIntent = Intent(Intent.ACTION_VIEW)  # ACTION_OPEN_DOCUMENT #ACTION_SEND #ACTION_VIEW
                shareIntent.setType("*/*")
                imageFile = File(self.path)
                uri = Uri.fromFile(imageFile)
                shareIntent.setData(uri)
                parcelable = cast('android.os.Parcelable', uri)
                shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                shareIntent.putExtra(Intent.EXTRA_STREAM, parcelable)
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivity(shareIntent)
            except:
                popup = Popup(title='Ops!', content=Label(text=f'Algo salió mal.'),
                              size_hint=(0.7, 0.2))
                popup.open()
            self.dismiss()


class PopUpException(Popup):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class PopUpMeasuring(Popup):
    medicion = None
    wanna_quit = False

    def __init__(self, kivy_clock, **kwargs):
        super().__init__(**kwargs)
        self.clock = kivy_clock

    def refresh_text(self, flexion, extension):
        self.text = ''
        if not not flexion:
            self.text += f"Flexión máxima medida: {flexion}°\nExtensión máxima medida:"
        if not not extension:
            self.text += f"Flexión máxima medida:\nExtensión máxima medida: {extension}°\n"
        save_button = Button(text='Guardar',on_release=lambda x: self.save())
        self.ids.buttons.add_widget(save_button)

    def save(self):
        self.wanna_quit = True


class PopUpEleccionDePie(Popup):
    def __init__(self, funcion, **kwargs):
        super().__init__(**kwargs)
        self.funcion = funcion

    def eleccion(self, pie):
        self.funcion(pie)
        self.dismiss()


class PopUpEleccionDeFuerza(Popup):
    def __init__(self, accion, pie, **kwargs):
        super().__init__(**kwargs)
        self.accion = accion
        self.pie = pie

    def extension(self):
        self.accion(f'fuerza_extension_{self.pie}')
        self.dismiss()

    def flexion(self):
        self.accion(f'fuerza_flexion_{self.pie}')
        self.dismiss()


