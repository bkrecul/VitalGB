from kivy import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from translate import Translator
from plyer import stt
from kivy.garden.graph import Graph, LinePlot
# cambiar por kivy_garden.graph al construir apk


class DialogoCargarAngulos(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.obs = {}

    def abrir_dialogo_notas(self, llamado):
        observaciones = self.app.obtener_nombres_observaciones()
        obs = []
        if llamado in self.obs:
            obs = self.obs[llamado]
        self.popup_notas = PopUpNotas(observaciones, obs, on_dismiss=lambda x: self.get_observaciones(llamado))
        self.popup_notas.open()

    def get_observaciones(self, llamado):
        self.obs[llamado] = self.popup_notas.obs


class DialogoCargarNota(BoxLayout):
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
                                              text_color=(0.4, 0.48, 0.67, 1), ),
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
        return MDDialog(title="Nueva nota:", type="custom", content_cls=DialogoCargarNota(),
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(0.4, 0.48, 0.67, 1), ),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(0.4, 0.48, 0.67, 1), text_color=(1, 1, 1, 1),
                                                on_release=kwargs.get('funcion_aceptar'))])
    if tipo == 3:
        return MDDialog(title='ELIMINAR SELECCIÓN', text="ADVERTENCIA: ESTA ACCIÓN BORRARÁ LOS DATOS PERMANENTEMENTE. "
                                                         "¿CONTINUAR?",
                        buttons=[MDFlatButton(text="CANCELAR", theme_text_color="Custom",
                                              text_color=(1, 0, 0, 1), ),
                                 MDRaisedButton(text="ACEPTAR", theme_text_color="Custom",
                                                md_bg_color=(1, 0, 0, 1), text_color=(1, 1, 1, 1),
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


class ChipNotas(MDChip):
    icon = 'check'

    def __init__(self, id_obs, checked, es_nota, **kwargs):
        super().__init__(**kwargs)
        self.id = id_obs
        self.theme_cls = "Custom"
        self.text_color = (1, 1, 1, 1)
        self.es_nota = es_nota
        self.checked = checked
        if self.checked:
            self.icon_color = (1, 1, 1, 1)
            self.color = (0.2, 0.28, 1, 1)
        else:
            self.icon_color = (1, 1, 1, 0)
            self.color = (0.4, 0.48, 0.67, 1)

    def on_press(self):
        if self.es_nota:
            if self.checked:
                self.checked = False
                self.icon_color = (1, 1, 1, 0)
                self.color = (0.4, 0.48, 0.67, 1)
            else:
                self.checked = True
                self.icon_color = (1, 1, 1, 1)
                self.color = (0.2, 0.28, 1, 1)
        else:
            self.dialog = crear_dialogos(2, funcion_aceptar=lambda x: self.agregar_nota())
            self.dialog.open()

    def agregar_nota(self):
        nota = self.dialog.content_cls.ids.nota.text
        id_nueva_nota = self.parent.vitalgb_app.cargar_nota_de_observaciones(nota)
        chip = ChipNotas(text=nota, es_nota=True, id_obs=id_nueva_nota, checked=True)
        self.parent.add_widget(chip)
        self.dialog.dismiss()


class PopUpNotas(Popup):
    def __init__(self, observaciones, prev_obs, **kwargs):
        super().__init__(**kwargs)
        self.prev_obs = prev_obs
        for observacion in observaciones:
            if observacion[0] not in prev_obs:
                chip = ChipNotas(text=observacion[1], es_nota=True, id_obs=observacion[0], checked=False)
                self.ids.chip_box.add_widget(chip)
            else:
                chip = ChipNotas(text=observacion[1], es_nota=True, id_obs=observacion[0], checked=True)
                self.ids.chip_box.add_widget(chip)
        chip = ChipNotas(text='+ Insertar Nota', es_nota=False, icon='plus', id_obs='NaN', checked=False)
        self.ids.chip_box.add_widget(chip)

    def salvar_notas(self):
        self.obs = []
        for nota in self.ids.chip_box.children:
            if nota.checked:
                self.obs.append(nota.id)
        self.dismiss()


class PopUpMeasuring(Popup):
    medicion = None

    def __init__(self, kivy_clock, **kwargs):
        super().__init__(**kwargs)
        self.wanna_quit = False
        self.clock = kivy_clock
        self.obs = {}

    def refresh_text(self, flexion, extension):
        if not not flexion:
            self.ids.flexion.text = f"{flexion}°"
        if not not extension:
            self.ids.extension.text = f"{extension}°"
        save_button = Button(text='Guardar', on_release=lambda x: self.save())
        self.ids.buttons.add_widget(save_button)

    def abrir_dialogo_notas(self, llamado):
        observaciones = self.app.obtener_nombres_observaciones()
        obs = []
        if llamado in self.obs:
            obs = self.obs[llamado]
        self.popup_notas = PopUpNotas(observaciones, obs, on_dismiss=lambda x: self.get_observaciones(llamado))
        self.popup_notas.open()

    def get_observaciones(self, llamado):
        self.obs[llamado] = self.popup_notas.obs

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
        self.accion(f'extension_{self.pie}')
        self.dismiss()

    def flexion(self):
        self.accion(f'flexion_{self.pie}')
        self.dismiss()


class PopUpMeasuringFuerza(Popup):

    def __init__(self, kivy_clock, **kwargs):
        super().__init__(**kwargs)
        self.wanna_quit = False
        self.its_stopped = False
        self.clock = kivy_clock
        self.medidas = [0] # Lo primero que "mide" es 0, se partirá de allí
        self.graph = Graph(
            xlabel='Tiempo',
            ylabel='Fuerza',
            x_ticks_minor=1,
            x_ticks_major=1,
            y_ticks_major=0.5,
            y_ticks_minor=5,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            xlog=False,
            ylog=False,
            x_grid=True,
            y_grid=True,
            xmax=10,
            ymin=0,
            ymax=2)
        self.ids.graph.add_widget(self.graph)
        self.plot = LinePlot(color=[0, 0, 1, 1], line_width=1.5)
        self.plot.points = [(x, self.medidas[x]) for x in range(len(self.medidas))]
        self.graph.add_plot(self.plot)

    def _round_up_div(self, list, div):
        number = len(list)
        return number//div + (number % div > 0)

    def update_xaxis(self, *args):
        if len(self.medidas) > 100:
            self.graph.xmin = self._round_up_div(self.medidas, 10) - 10
            self.graph.xmax = self._round_up_div(self.medidas, 10)

    def update_points(self, *args):
        self.plot.points = [(x/10, self.medidas[x]) for x in range(len(self.medidas))]

    def continuar(self):
        if not self.its_stopped:
            self.its_stopped = True
            # self.clock.cancel()
            self.max = max(self.medidas)
            self.prom = sum(self.medidas)/len(self.medidas)
            self.text = f'Valor máximo: {self.max}\nPromedio: {self.prom}'
            self.ids.button.text = 'Guardar'
            self.ids.button.on_release()
        else:
            self.terminar()

    def terminar(self):
        self.wanna_quit = True
