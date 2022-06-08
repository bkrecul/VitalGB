import time
from random import randint
import pandas
from kivy.clock import Clock
from kivy.config import Config
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
from PupUps import *
from vitalgb import PlanillaPersonal, PlanillaGeneral
from vitalgb_com import Bluetooth
from kivy.core.window import Window

Window.softinput_mode = 'below_target'

DEVICE_NAME = 'ESP32 BT'  # BTmin

if platform == 'android':
    from android.storage import app_storage_path, primary_external_storage_path
    from android.permissions import request_permissions, Permission
    from plyer import vibrator

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.READ_EXTERNAL_STORAGE,
                         Permission.RECORD_AUDIO])
    working_path = app_storage_path()
    export_path = primary_external_storage_path()
else:
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    working_path = 'files'
    export_path = 'export'


class PantallaPrincipal(MDScreen):
    """ Pantalla principal, contiene el listado de pacientes, el botón para conectarse a bluetooth y el botón para
    agregar paciente."""

    def on_pre_enter(self, *args):
        # Esta función se usa para refrescar el listado de pacientes, en caso de que se cargue uno nuevo
        # en la pantalla Agregar Paciente. Sin embargo dará una excepción en la primera ejecución.
        try:
            self.ids.rv.data = vitalgb_app.planilla_general.devolver_pacientes()
            self.ids.rv.refresh_from_data()
        except NameError as mensaje:
            print(mensaje)
        except AttributeError as mensaje:
            print(mensaje)

    def add_patient_button_press(self):
        self.ids.add_patient_image.source = 'images/add_pressed.png'

    def add_patient_button_release(self):
        self.ids.add_patient_image.source = 'images/add.png'
        self.manager.current = 'pantalla_agregar_paciente'

    def bluetooth(self):
        if not vitalgb_app.bluetooth_disponible:
            try:
                self.recv_stream, self.send_stream = vitalgb_app.bluetooth_connection.get_socket_stream()
            except Exception as mensaje:
                popup = PopUpException(traductor(mensaje))
                popup.open()

            else:
                popup = Popup(title='Información', content=Label(text=f'¡Conexión exitosa!'),
                              size_hint=(0.7, 0.2))
                popup.open()
                self.ids.bt.icon_color = 'green'
                self.ids.bt.text = "Conectado"
                vitalgb_app.bluetooth_disponible = True
                self.verificar_conexion = Clock.schedule_interval(lambda dt: vitalgb_app.verificar_conexion_bluetooth(),
                                                                  1)

    def on_leave(self, *args):
        self.ids.rv.ids.pacientes.clear_selection()


class PantallaAgregarPaciente(MDScreen):
    """ Pantalla utilizada para cargar los datos del paciente y así generar uno nuevo, que será guardado en una base
    de datos (planilla general)."""

    def on_pre_enter(self, *args):
        sexos = ['Femenino', 'Masculino', 'Otro']
        iconos = ['human-female', 'human-male', '']
        menu_sexo_items = [
            {
                "viewclass": "IconListItem",
                "icon": icono,
                "height": dp(56),
                "text": sexo,
                "on_release": lambda x=sexo: self.set_sexo(x),
            } for sexo, icono in zip(sexos, iconos)]
        self.menu_sexo = MDDropdownMenu(
            ver_growth="up",
            caller=self.ids.entrada_sexo,
            items=menu_sexo_items,
            position="auto",
            width_mult=4,
            opening_transition="in_quint",
        )
        if vitalgb_app.patient_selected is not None:
            info = vitalgb_app.planilla_general.devolver_info_paciente(vitalgb_app.patient_selected)
            self.ids.title.title = 'Editar Paciente'
            self.ids.entrada_nombre.text = info[1]
            self.ids.entrada_apellido.text = info[2]
            self.ids.entrada_dni.text = info[3]
            self.ids.entrada_sexo.text = info[4]
            if info[5] != '':
                fecha = info[5].split('/')
                self.ids.entrada_dia.text = fecha[0]
                self.ids.entrada_mes.text = fecha[1]
                self.ids.entrada_year.text = fecha[2]
        else:
            self.ids.title.title = 'Nuevo Paciente'

    def crear_paciente(self):
        # Leer los datos de las entradas
        nombre = self.ids.entrada_nombre.text.title()
        apellido = self.ids.entrada_apellido.text.title()
        dni = self.ids.entrada_dni.text
        try:
            fecha_nacimiento = f'{int(self.ids.entrada_dia.text):02d}/' \
                               f'{int(self.ids.entrada_mes.text):02d}/' \
                               f'{self.ids.entrada_year.text}'
        except ValueError:
            fecha_nacimiento = ""
        sexo = self.ids.entrada_sexo.text
        # Comprobar que estén llenos los campos obligatorios
        if nombre != "" and apellido != "":
            # Si es así, cargarlos
            if vitalgb_app.patient_selected is None:
                vitalgb_app.planilla_general.cargar_paciente(nombre, apellido, dni, sexo, fecha_nacimiento)
                self.manager.current = "pantalla_principal"
            else:
                vitalgb_app.planilla_general.guardar_cambios_paciente(vitalgb_app.patient_selected,
                                                                      nombre, apellido, dni, sexo,
                                                                      fecha_nacimiento)
                self.manager.current = "pantalla_paciente_seleccionado"
        else:
            # Sino, mostrar un mensaje
            popup = Popup(title='Error', content=Label(text='    Los campos Nombre\ny Apellido son obligatorios'),
                          size_hint=(0.7, 0.2))
            popup.open()

    def limpiar_inputs(self):
        self.ids.entrada_nombre.text = ""
        self.ids.entrada_apellido.text = ""
        self.ids.entrada_dni.text = ""
        self.ids.entrada_dia.text = ""
        self.ids.entrada_mes.text = ""
        self.ids.entrada_year.text = ""
        self.ids.entrada_sexo.text = ""

    def open_menu_sexo(self):
        if self.ids.entrada_sexo.focus:
            self.menu_sexo.open()

    def set_sexo(self, sexo):
        self.ids.entrada_sexo.text = sexo
        self.menu_sexo.dismiss()

    def on_leave(self, *args):
        self.limpiar_inputs()


class PantallaPacienteSeleccionado(MDScreen):
    """ Pantalla que muestra los datos medidos del paciente que haya sido seleccionado en la Pantalla Principal.
    En esta pantalla se puede también generar y exportar archivos pdf y excel de los datos medidos. Se encarga también
    de la carga de nuevos datos de medición a través del dispositivo Bluetooth VitalGB."""
    stream = []
    flexion = None
    extension = None
    estudio_seleccionado = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.snackbar_angulos = Snackbar(
            text="Dispositivo Desconectado",
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        self.snackbar_angulos.size_hint_x = (
                                       Window.width - (self.snackbar_angulos.snackbar_x * 2)
                               ) / Window.width
        self.snackbar_angulos.buttons = [
            MDRaisedButton(
                text="Cargar Manualmente",
                text_color=(0, 0, 0, 1),
                on_release=lambda x:self.cargar_manualmente(),
            ),
        ]
        self.snackbar_fuerzas = Snackbar(
            text="Dispositivo Desconectado",
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        self.snackbar_fuerzas.size_hint_x = (
                                            Window.width - (self.snackbar_fuerzas.snackbar_x * 2)
                                    ) / Window.width

    def on_pre_enter(self, *args):
        """ Al pre-entrar se lee una variable de la aplicación que contiene el id del paciente que haya sido
        seleccionado en la pantalla principal. Así, filtra en la tabla de mediciones con ese id y carga los datos en
        la RecycleView (lista desplazable) que muestra los datos."""

        while vitalgb_app.patient_selected is None:
            pass

        self.id = vitalgb_app.patient_selected
        nombre_completo = vitalgb_app.planilla_general.devolver_nombre_paciente(self.id)
        self.ids.titulo_nombre_paciente.text = nombre_completo
        vitalgb_app.patient_selected = None
        self.refresh(magnitud='mediciones_angulos')
        self.refresh(magnitud='mediciones_fuerzas')
        vitalgb_app.root.ids.nav_drawer.swipe_edge_width = 50

    def nueva_medicion(self, instance):
        """ Función del botón medir --> si hay conexión de Bluetooth = Medir por bluetooth."""
        actual = self.obtener_magnitud_actual()
        self.stream.clear()
        if instance.icon == 'angle-obtuse':
            self.ids.tabs_mediciones.switch_tab('Ángulos')
            self.ids.btn_medir.close_stack()
            self.extension = None
            self.flexion = None
            if vitalgb_app.bluetooth_disponible:
                self.popup_elecion_pie = PopUpEleccionDePie(lambda x: self.medir(x))
                self.popup_elecion_pie.open()
            else:
                self.snackbar_angulos.open()
        if instance.icon == 'weight-kilogram':
            self.ids.tabs_mediciones.switch_tab('Fuerzas')
            if vitalgb_app.bluetooth_disponible:
            # if True:
                self.popup_elecion_pie = PopUpEleccionDePie(lambda x: self.eleccion_fuerza(x))
                self.popup_elecion_pie.open()
            else:
                self.snackbar_fuerzas.open()
            self.ids.btn_medir.close_stack()
        if instance.icon == 'delete':
            if not not self.ids[actual].rv.viewclass.selection:
                self.ids.btn_medir.close_stack()
                self.dialog = crear_dialogos(3, funcion_aceptar=lambda x: self.delete())
                self.dialog.buttons[0].on_release = self.dialog.dismiss
                self.dialog.open()

    def cargar_manualmente(self):
        """ Esta función es llamada por un botón dentro del SnackBar que se muestra cuando
        se quiere agregar una medición de ángulos con el dispositivo desconectado. """
        # Lo primero es un truco para que no se abra el menu de elegir medición nuevamente:
        Clock.schedule_once(lambda x: self.ids.btn_medir.close_stack(), 0.1)
        self.popup_elecion_pie = PopUpEleccionDePie(lambda x: self.medir(x, manual=True))
        self.popup_elecion_pie.open()

    def medir(self, pie, **kwargs):
        """ Se transmite el byte para configurar el goniómetro.
        El goniómetro al encenderse estará recibiendo bytes, para poder ajustar su screen en
        caso de tratarse de una medición de pie derecho o izquierdo."""
        if 'manual' in kwargs:
            if kwargs.get('manual'):
                self.dialog = crear_dialogos(1, funcion_aceptar=lambda x: self.carga_angulos_manual(pie))
                self.dialog.buttons[0].on_release = self.dialog.dismiss
                self.dialog.open()
                return

        if self.obtener_magnitud_actual() == 'mediciones_angulos':
            if pie == 'derecha':
                vitalgb_app.byte = 1
            else:
                vitalgb_app.byte = 2
            self.clock = Clock.schedule_interval(lambda dt: self.medir_angulos(pie), 0.2)
            self.dialog = PopUpMeasuring(self.clock)
            self.dialog.open()
        elif self.obtener_magnitud_actual() == 'mediciones_fuerzas':
            vitalgb_app.byte = 3
            self.dialog = PopUpMeasuringFuerza(Clock.schedule_interval(lambda dt: self.medir_fuerza(pie), 0.1))
            self.dialog.open()

    def delete(self):
        self.dialog.dismiss()
        id_medicion = self.obtener_indice_de_medicion()
        magnitud = self.obtener_magnitud_actual()
        vitalgb_app.planilla_personal.borrar_medicion(magnitud, id_medicion)
        self.refresh()

    def eleccion_fuerza(self, pie):
        self.dialog = PopUpEleccionDeFuerza(lambda x: self.medir(x), pie)
        self.dialog.open()

    def carga_angulos_manual(self, pie):
        flexion = self.dialog.content_cls.ids.flexion.text
        extension = self.dialog.content_cls.ids.extension.text
        dict = self._dict_angulos(pie, extension, flexion)

        self.guardar_angulos_en_DB(dict)

    def guardar_angulos_en_DB(self, dict):
        medicion = self.obtener_magnitud_actual()
        if len(self.ids[medicion].rv.viewclass.selection) == 1:
            """ IF: si se seleccionó un estudio (es decir, está en modo editar)"""
            id_medicion = self.obtener_indice_de_medicion()
            vitalgb_app.planilla_personal.editar_mediciones(medicion, id_medicion, **dict)
        else:
            """ ELSE: sino, se generará un nuevo elemento/entrada/fila de estudio."""
            fecha = time.strftime('%d/%m/%y %H:%M'),
            vitalgb_app.planilla_personal.cargar_mediciones(self.id, fecha, medicion, **dict)
        self.dialog.dismiss()
        self.refresh()

    def refresh(self, **kwargs):
        if 'magnitud' in kwargs:
            actual = kwargs.get('magnitud')
        else:
            actual = self.obtener_magnitud_actual()
        self.data = vitalgb_app.planilla_personal.lectura(self.id, actual, formateado=True)
        self.ids[actual].rv.data = self.data
        self.ids[actual].rv.refresh_from_data()
        self.ids[actual].rv.viewclass.selection.clear()
        self.ids[actual].rv.viewclass.anterior.clear()
        try:
            self.ids[actual].rv.ids.estudios.clear_selection()
        except IndexError:
            pass

    def _dict_angulos(self, pie, valor_1, valor_2):
        """ Función que convierte un valor de pie en diccionario para poder enviarlo como **kwargs en guardado de
        datos a la base de datos """
        dict = {}
        if self.obtener_magnitud_actual() == 'mediciones_angulos':
            if valor_2 != "":
                dict[f'flexion_{pie}'] = valor_2
            if valor_1 != "":
                dict[f'extension_{pie}'] = valor_1
        elif self.obtener_magnitud_actual() == 'mediciones_fuerzas':
            if valor_1 != "":
                dict[f'{pie}'] = valor_1
                # se guarda uno solo ya que los datos de fuerza se guardan de a uno
        return dict

    def medir_angulos(self, pie):
        """ Esta función es llamada en intervalos de tiempo (Clock), ya que constantemente revisará si hay datos
        disponibles para la lectura. Como se generó un PopUp, este clock puede ser cancelado. Una vez que hayan datos
        disponibles, primero se revisará si son de flexión o extensión (en Arduino se configuró que los datos salgan
        con un formato "E"+String(ángulo de extensión) o "F"+String(ángulo de flexión)) y luego se verifica que dicho
        ángulo (de flexión o extensión) no haya sido previamente transmitido. Cuando se recepcionen los dos ángulos,
        estos serán cargados a la planilla personal del paciente."""
        try:
            recv_stream = vitalgb_app.root.ids.pantalla_principal.recv_stream
            while recv_stream.ready():
                char = recv_stream.readLine()
                if str(char)[0] == "F" and not self.flexion:
                    self.flexion = str(char).replace("F", "")
                    self.stream.append(str(char))
                    self.dialog.refresh_text(self.flexion, self.extension)
                    vibrator.vibrate(1)
                if str(char)[0] == "E" and not self.extension:
                    self.extension = str(char).replace("E", "")
                    self.stream.append(str(char))
                    self.dialog.refresh_text(self.flexion, self.extension)
                    vibrator.vibrate(1)
        except Exception as mensaje:
            self.dialog.dismiss()
            self.clock.cancel()
            popup = PopUpException(traductor(mensaje))
            popup.open()
        else:
            if len(self.stream) == 2 or self.dialog.wanna_quit:
                dict = self._dict_angulos(pie, self.extension, self.flexion)
                self.guardar_angulos_en_DB(dict)
                self.clock.cancel()

    def medir_fuerza(self, eleccion):
        """ Esta función es llamada en intervalos de tiempo (Clock), ya que constantemente revisará si hay datos
        disponibles para la lectura. Como se generó un PopUp, este clock puede ser cancelado."""
        # eleccion: str -> flexion/extension_derecha/izquierda dependiendo de lo que se elija
        try:
            recv_stream = vitalgb_app.root.ids.pantalla_principal.recv_stream
            if not self.dialog.its_stopped:
                while recv_stream.ready():
                    char = recv_stream.readLine()
                    self.fuerza = float(str(char))
                    self.dialog.medidas.append(self.fuerza)
                    self.dialog.update_points()
                    self.dialog.update_xaxis()
            else:
                vitalgb_app.byte = 1
            # if not self.dialog.its_stopped:
            #     test = randint(1, 20) * 0.1
            #     self.dialog.medidas.append(gay)
            #     self.dialog.update_points()
            #     self.dialog.update_xaxis()
        except Exception as mensaje:
            self.dialog.dismiss()
            popup = PopUpException(traductor(mensaje))
            popup.open()
        else:
            if self.dialog.wanna_quit:
                self.dialog.clock.cancel()
                dict = self._dict_angulos(eleccion, self.dialog.max, 0)
                self.guardar_angulos_en_DB(dict)

    def pedir_observaciones(self):
        self.dialog = crear_dialogos(4, funcion_aceptar=lambda x: self.generate_pdf())
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()

    def generate_pdf(self):
        try:
            observaciones = self.dialog.content_cls.ids.observaciones.text
            nombre_completo = vitalgb_app.planilla_general.devolver_nombre_paciente(self.id)
            info = vitalgb_app.planilla_general.devolver_info_paciente(self.id)
            path = vitalgb_app.planilla_personal.exportar(
                'pdf', self.id, export_path, obs=observaciones, info=info)
            self.dialog.dismiss()
        except Exception as mensaje:
            if ('errno 13' or 'permission denied') in str(mensaje).lower():
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                                     Permission.READ_EXTERNAL_STORAGE])
                popup = Popup(title='Error',
                              content=Label(text=f'No se pudo exportar, por favor\nconceda los permisos.'),
                              size_hint=(0.7, 0.2))
                popup.open()
            else:
                popup = PopUpException(traductor(mensaje))
                popup.open()
        else:
            mensaje = PopUpExportSuccessful(path)
            mensaje.open()

    def generate_csv(self):
        try:
            path = vitalgb_app.planilla_personal.exportar('csv', self.id, export_path)
        except Exception as mensaje:
            if ('errno 13' or 'permission denied') in str(mensaje).lower():
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                                     Permission.READ_EXTERNAL_STORAGE])
                popup = Popup(title='Error',
                              content=Label(text=f'No se pudo exportar, por favor\nconceda los permisos.'),
                              size_hint=(0.7, 0.2))
                popup.open()
            else:
                popup = PopUpException(traductor(mensaje))
                popup.open()
        else:
            mensaje = PopUpExportSuccessful(path)
            mensaje.open()

    def on_leave(self, *args):
        actual = self.obtener_magnitud_actual()
        self.ids[actual].rv.ids.estudios.clear_selection()
        self.ids.btn_medir.close_stack()
        self.ids.btn_medir.icon = 'plus'
        self.ids[actual].rv.viewclass.selection.clear()
        self.ids[actual].rv.viewclass.anterior.clear()
        vitalgb_app.estudio_seleccionado = None
        vitalgb_app.root.ids.nav_drawer.swipe_edge_width = 0

    def obtener_magnitud_actual(self):
        texto = self.ids.tabs_mediciones.carousel.current_slide.tab_label.text
        if texto == 'Ángulos':
            return 'mediciones_angulos'
        elif texto == 'Fuerzas':
            return 'mediciones_fuerzas'
        else:
            raise AttributeError

    def obtener_indice_de_medicion(self):
        actual = self.obtener_magnitud_actual()
        index = self.ids[actual].rv.data.index(self.ids[actual].rv.viewclass.selection[0])
        id_medicion = self.ids[actual].rv.data[index]['id']
        return id_medicion


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class Tab(MDBoxLayout, MDTabsBase):
    orientation = 'vertical'


class ContentNavigationDrawer(MDBoxLayout):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    """ Add selection support to the Label """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    color = (0.01, 0.02, 0.37, 1)
    font_name = "fonts/Ubuntu-L"
    font_size = dp(18)

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        if is_selected:
            vitalgb_app.patient_selected = rv.data[index]['id']
            vitalgb_app.root.ids.screen_manager.current = "pantalla_paciente_seleccionado"


class RVPacientes(RecycleView):
    def __init__(self, **kwargs):
        super(RVPacientes, self).__init__(**kwargs)
        try:
            self.data = vitalgb_app.planilla_general.devolver_pacientes()
        except NameError as mensaje:
            print(mensaje)


class SelectableBox(RecycleDataViewBehavior, BoxLayout):
    """ Add selection support to the BoxLayout """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    selection = []
    anterior = []

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableBox, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableBox, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
        else:
            return False

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected
        self.selection.clear()
        current = rv.data[index]
        vitalgb_app.root.ids.pantalla_paciente_seleccionado.estudio_seleccionado = current
        if is_selected:
            if current not in self.anterior:
                self.anterior.clear()
                self.anterior.append(current)
                self.selection.append(current)
            else:
                self.anterior.clear()
                actual = vitalgb_app.root.ids.pantalla_paciente_seleccionado.obtener_magnitud_actual()
                vitalgb_app.root.ids.pantalla_paciente_seleccionado.ids[actual].rv.ids.estudios.clear_selection()

        vitalgb_app.root.ids.pantalla_paciente_seleccionado.ids.btn_medir.close_stack()

        if len(self.selection) == 0:
            vitalgb_app.root.ids.pantalla_paciente_seleccionado.ids.btn_medir.icon = 'plus'
        else:
            vitalgb_app.root.ids.pantalla_paciente_seleccionado.ids.btn_medir.icon = 'pencil-outline'


class RVEstudios(RecycleView):
    pass


class MainApp(MDApp):
    bluetooth_disponible = False
    comandos = {
        'ELIMINAR': 'delete',
        'FUERZA': 'weight-kilogram',
        'ÁNGULO': 'angle-obtuse',
    }
    anterior = []
    byte = 1

    def __init__(self, **kwargs):
        super().__init__()
        self.path = None
        self.planilla_personal = PlanillaPersonal(working_path)
        self.planilla_general = PlanillaGeneral(working_path)
        self.bluetooth_connection = Bluetooth(DEVICE_NAME)
        self.patient_selected = None

    def verificar_conexion_bluetooth(self):
        try:
            self.bluetooth_connection.enviar_byte(self.byte)
        except:
            popup = Popup(title='Error', content=Label(text='La conexión fue interrumpida. Por favor\n'
                                                            'vuelva a conectarse al dispositivo.'),
                          size_hint=(0.7, 0.2))
            popup.open()
            self.root.ids.pantalla_principal.verificar_conexion.cancel()
            self.root.ids.pantalla_principal.ids.bt.icon_color = 'red'
            self.root.ids.pantalla_principal.ids.bt.text = "Conectar"
            self.bluetooth_disponible = False
            try:
                self.root.ids.pantalla_paciente_seleccionado.popup.dismiss()
                self.root.ids.pantalla_paciente_seleccionado.clock.cancel()
            finally:
                pass
            vibrator.vibrate(0.5)

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        return Builder.load_file('frontend.kv')

    def on_pause(self):
        return True

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            if self.root.ids.screen_manager.current == 'pantalla_agregar_paciente':
                self.root.ids.screen_manager.current_screen.menu_sexo.dismiss()
            self.volver_pantalla_principal()
            return True  # override the default behaviour
        else:  # the key now does nothing
            return False

    def volver_pantalla_principal(self):
        if self.patient_selected is None:
            self.root.ids.screen_manager.current = "pantalla_principal"
        else:
            self.root.ids.screen_manager.current = "pantalla_paciente_seleccionado"

    def cargar_datos_institucionales(self):
        self.dialog = crear_dialogos(5, funcion_aceptar=lambda x: self._guardar_datos_institucionales())
        data = self.planilla_personal.lectura_datos_institucionales()
        index = 0
        for name_field in self.dialog.content_cls.ids:
            if data[index] is not None:
                self.dialog.content_cls.ids[name_field].text = data[index]
                index += 1
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()

    def _guardar_datos_institucionales(self):
        # primero se guardan todos los datos de los campos a rellenar
        headers = ['nombre_profesional',
                   'nombre_del_servicio',
                   'direccion',
                   'telefono',
                   'sitio_web']
        df = pandas.DataFrame({header: [self.dialog.content_cls.ids[field].text]
                               for (header, field) in zip(headers, self.dialog.content_cls.ids)})
        # luego se carga el path del archivo
        df['image_path'] = self.path
        # finalmente se guardan todos los datos en un archivo
        df.to_csv(f"{working_path}/VitalGB/instituto.csv", index=False)
        self.dialog.dismiss()

    def editar_info_paciente(self, id_paciente):
        self.patient_selected = id_paciente
        self.root.ids.nav_drawer.set_state("close")
        self.root.ids.screen_manager.current = "pantalla_agregar_paciente"

    def admin_archivos_abrir(self):
        from filechooser import AndroidFileChooser
        AndroidFileChooser().open_file(on_selection=self.seleccion_de_path, filters=['image'])

    def seleccion_de_path(self, path):
        """ Esta función se llama cuando se hace click archivo
        o el catálogo de selección.
        """
        self.path = path[0]
        toast(self.path)


vitalgb_app = MainApp()
vitalgb_app.run()
