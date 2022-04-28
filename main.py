import time
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
from PupUps import *
from vitalgb import PlanillaPersonal, PlanillaGeneral
from vitalgb_com import Bluetooth
from kivy.core.window import Window

# from plyer import vibrator


Window.softinput_mode = 'below_target'

DEVICE_NAME = 'ESP32 BT'  # BTmin

if platform == 'android':
    from android.storage import app_storage_path, primary_external_storage_path
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.READ_EXTERNAL_STORAGE])
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
                self.recv_stream, self.send_stream = vitalgb_app.bluetooth_conection.get_socket_stream()
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
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": icono,
                "height": dp(56),
                "text": sexo,
                "on_release": lambda x=sexo: self.set_sexo(x),
            } for sexo, icono in zip(sexos, iconos)]
        self.menu = MDDropdownMenu(
            ver_growth="up",
            caller=self.ids.entrada_sexo,
            items=menu_items,
            position="auto",
            width_mult=4,
            opening_transition="in_quint",
        )

    def crear_paciente(self):
        # Leer los datos de las entradas
        nombre = self.ids.entrada_nombre.text.title()
        apellido = self.ids.entrada_apellido.text.title()
        edad = self.ids.entrada_edad.text
        peso = self.ids.entrada_peso.text
        patologia = self.ids.entrada_patologia.text
        sexo = self.ids.entrada_sexo.text
        # Comprobar que estén llenos los campos obligatorios
        if nombre != "" and apellido != "":
            # Si es así, cargarlos
            vitalgb_app.planilla_general.cargar_paciente(nombre, apellido, edad=edad,
                                                         patologia=patologia, peso=peso, sexo=sexo)
            self.manager.current = "pantalla_principal"
        else:
            # Sino, mostrar un mensaje
            popup = Popup(title='Error', content=Label(text='    Los campos Nombre\ny Apellido son obligatorios'),
                          size_hint=(0.7, 0.2))
            popup.open()

    def limpiar_inputs(self):
        self.ids.entrada_nombre.text = ""
        self.ids.entrada_apellido.text = ""
        self.ids.entrada_edad.text = ""
        self.ids.entrada_peso.text = ""
        self.ids.entrada_patologia.text = ""
        self.ids.entrada_sexo.text = ""

    def open_menu(self):
        if self.ids.entrada_sexo.focus:
            self.menu.open()

    def set_sexo(self, sexo):
        self.ids.entrada_sexo.text = sexo
        self.menu.dismiss()

    def on_leave(self, *args):
        self.limpiar_inputs()


class PantallaPacienteSeleccionado(MDScreen):
    """ Pantalla que muestra los datos medidos del paciente que haya sido seleccionado en la Pantalla Principal.
    En esta pantalla se puede también generar y exportar archivos pdf y excel de los datos medidos. Se encarga también
    de la carga de nuevos datos de medición a través del dispositivo Bluetooth VitalGB."""
    stream = []
    flexion = None
    extension = None

    def pedir_observaciones(self):
        self.dialog = crear_dialogos(4, funcion_aceptar=lambda x: self.generate_pdf())
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()

    def generate_pdf(self):
        try:
            observaciones = self.dialog.content_cls.ids.observaciones.text
            nombre_completo = vitalgb_app.planilla_general.devolver_paciente(self.id)
            path = vitalgb_app.planilla_personal.exportar(
                'pdf', self.id, nombre_completo, export_path, obs=observaciones)
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
            nombre_completo = vitalgb_app.planilla_general.devolver_paciente(self.id)
            path = vitalgb_app.planilla_personal.exportar('csv', self.id, nombre_completo, export_path)
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

    def on_pre_enter(self, *args):
        """ Al pre-entrar se lee una variable de la aplicación que contiene el nombre y apellido del paciente que haya
        sido seleccionado en la pantalla principal. Así, busca el archivo csv con ese nombre y carga los datos en
        la RecycleView (lista desplazable) que muestra los datos."""
        while vitalgb_app.patient_selected is None:
            pass
        self.id = vitalgb_app.patient_selected
        nombre_completo = vitalgb_app.planilla_general.devolver_paciente(self.id)
        self.ids.titulo_nombre_paciente.text = nombre_completo
        vitalgb_app.patient_selected = None
        self.ids.rv.data.clear()
        self.data = vitalgb_app.planilla_personal.lectura(self.id)
        self.ids.rv.data = self.data.to_dict(orient='records')
        self.ids.rv.refresh_from_data()
        vitalgb_app.root.ids.nav_drawer.swipe_edge_width = 50

    def nueva_medicion(self, instance):
        """ Función del botón medir --> si hay conexión de Bluetooth = Medir por bluetooth."""
        self.stream.clear()
        if instance.icon == 'angle-obtuse':
            self.ids.btn_medir.close_stack()
            self.extension = None
            self.flexion = None
            if vitalgb_app.bluetooth_disponible:
                self.clock = Clock.schedule_interval(lambda dt: self.medir_angulos(), 0.2)
                self.popup = PopUpMeasuring(self.clock)
                self.popup.open()
            else:
                self.dialog = crear_dialogos(0, funcion_aceptar=lambda x: self.pedir_angulos())
                self.dialog.buttons[0].on_release = self.dialog.dismiss
                self.dialog.open()
        if instance.icon == 'weight-kilogram':
            self.ids.btn_medir.close_stack()
            self.popup = PopUpEleccionDeFuerza(lambda x: self.eleccion_fuerza(x))
            self.popup.open()
        if instance.icon == 'delete':
            if not not self.ids.rv.viewclass.selection:
                self.ids.btn_medir.close_stack()
                self.dialog = crear_dialogos(3, funcion_aceptar=lambda x: self.delete())
                self.dialog.buttons[0].on_release = self.dialog.dismiss
                self.dialog.open()

    def delete(self):
        self.dialog.dismiss()
        for row in self.ids.rv.viewclass.selection:
            self.ids.rv.data.remove(row)
        self.guardado()

    def guardado(self):
        vitalgb_app.planilla_personal.cargar_mediciones(self.id, self.ids.rv.data)
        self.ids.rv.refresh_from_data()
        self.ids.rv.viewclass.selection.clear()
        self.ids.rv.viewclass.anterior.clear()
        try:
            self.ids.rv.ids.estudios.clear_selection()
        except IndexError:
            pass

    def eleccion_fuerza(self, eleccion):
        if vitalgb_app.bluetooth_disponible:
            self.clock = Clock.schedule_interval(lambda dt: self.medir_fuerza(eleccion), 0.2)
            self.popup = PopUpMeasuring(self.clock)
            self.popup.text = ''
            self.popup.open()
        else:
            self.dialog = crear_dialogos(0, funcion_aceptar=lambda x: self.pedir_fuerza(eleccion))
            self.dialog.buttons[0].on_release = self.dialog.dismiss
            self.dialog.open()

    def pedir_fuerza(self, eleccion):
        self.dialog.dismiss()
        self.dialog = crear_dialogos(2, funcion_aceptar=lambda x: self.cargar_fuerza(eleccion))
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()

    def pedir_angulos(self):
        self.dialog.dismiss()
        self.dialog = crear_dialogos(1, funcion_aceptar=lambda x: self.cargar_angulos())
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()

    def cargar_angulos(self):
        if len(self.ids.rv.viewclass.selection) == 1:
            index = self.ids.rv.data.index(self.ids.rv.viewclass.selection[0])
            self.ids.rv.viewclass.selection[0]['flexion_maxima'] = self.dialog.content_cls.ids.flexion.text
            self.ids.rv.viewclass.selection[0]['extension_maxima'] = self.dialog.content_cls.ids.extension.text
            self.ids.rv.data[index] = self.ids.rv.viewclass.selection[0]
            self.guardado()
        else:
            medicion = {
                'fecha': time.strftime('%d/%m/%y %H:%M'),
                'flexion_maxima': self.dialog.content_cls.ids.flexion.text,
                'extension_maxima': self.dialog.content_cls.ids.extension.text,
                'fuerza_flexion_maxima': "-",
                'fuerza_extension_maxima': "-",
            }
            self.ids.rv.data.append(medicion)
            self.guardado()
        self.dialog.dismiss()

    def cargar_fuerza(self, eleccion):
        if len(self.ids.rv.viewclass.selection) == 1:
            index = self.ids.rv.data.index(self.ids.rv.viewclass.selection[0])
            self.ids.rv.viewclass.selection[0][eleccion] = self.dialog.content_cls.ids.fuerza.text
            self.ids.rv.data[index] = self.ids.rv.viewclass.selection[0]
        else:
            if eleccion == 'fuerza_flexion_maxima':
                medicion = {
                    'fecha': time.strftime('%d/%m/%y %H:%M'),
                    'flexion_maxima': "-",
                    'extension_maxima': "-",
                    'fuerza_flexion_maxima': self.dialog.content_cls.ids.fuerza.text,
                    'fuerza_extension_maxima': "-",
                }
            else:
                medicion = {
                    'fecha': time.strftime('%d/%m/%y %H:%M'),
                    'flexion_maxima': "-",
                    'extension_maxima': "-",
                    'fuerza_flexion_maxima': "-",
                    'fuerza_extension_maxima': self.dialog.content_cls.ids.fuerza.text,
                }
            self.ids.rv.data.append(medicion)
        self.guardado()
        self.dialog.dismiss()

    def medir_angulos(self):
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
                    self.popup.refresh_text(self.flexion, self.extension)
                    vibrator.vibrate(1)
                if str(char)[0] == "E" and not self.extension:
                    self.extension = str(char).replace("E", "")
                    self.stream.append(str(char))
                    self.popup.refresh_text(self.flexion, self.extension)
                    vibrator.vibrate(1)
        except Exception as mensaje:
            self.popup.dismiss()
            self.clock.cancel()
            popup = PopUpException(traductor(mensaje))
            popup.open()
        else:
            if len(self.stream) == 2 or self.popup.wanna_quit:
                if len(self.ids.rv.viewclass.selection) == 1:
                    index = self.ids.rv.data.index(self.ids.rv.viewclass.selection[0])
                    if self.flexion is not None:
                        self.ids.rv.viewclass.selection[0]['flexion_maxima'] = self.flexion
                    if self.extension is not None:
                        self.ids.rv.viewclass.selection[0]['extension_maxima'] = self.extension
                    self.ids.rv.data[index] = self.ids.rv.viewclass.selection[0]
                else:
                    if self.flexion is None:
                        self.flexion = '-'
                    elif self.extension is None:
                        self.extension = '-'
                    medicion = {
                        'fecha': time.strftime('%d/%m/%y %H:%M'),
                        'flexion_maxima': self.flexion,
                        'extension_maxima': self.extension,
                        'fuerza_flexion_maxima': "-",
                        'fuerza_extension_maxima': "-",
                    }
                    self.ids.rv.data.append(medicion)
                self.popup.dismiss()
                self.clock.cancel()
                self.guardado()

    def medir_fuerza(self, eleccion):
        """ Esta función es llamada en intervalos de tiempo (Clock), ya que constantemente revisará si hay datos
        disponibles para la lectura. Como se generó un PopUp, este clock puede ser cancelado."""
        try:
            recv_stream = vitalgb_app.root.ids.pantalla_principal.recv_stream
            while recv_stream.ready():
                char = recv_stream.readLine()
                self.fuerza = str(char)
                self.stream.append(self.fuerza)
                vibrator.vibrate(1)
        except Exception as mensaje:
            self.popup.dismiss()
            self.clock.cancel()
            popup = PopUpException(traductor(mensaje))
            popup.open()
        else:
            if len(self.stream) == 1:
                if len(self.ids.rv.viewclass.selection) == 1:
                    index = self.ids.rv.data.index(self.ids.rv.viewclass.selection[0])
                    self.ids.rv.viewclass.selection[0][eleccion] = self.fuerza
                    self.ids.rv.data[index] = self.ids.rv.viewclass.selection[0]
                else:
                    if eleccion == 'fuerza_flexion_maxima':
                        medicion = {
                            'fecha': time.strftime('%d/%m/%y %H:%M'),
                            'flexion_maxima': "-",
                            'extension_maxima': "-",
                            'fuerza_flexion_maxima': self.fuerza,
                            'fuerza_extension_maxima': "-",
                        }
                    else:
                        medicion = {
                            'fecha': time.strftime('%d/%m/%y %H:%M'),
                            'flexion_maxima': "-",
                            'extension_maxima': "-",
                            'fuerza_flexion_maxima': "-",
                            'fuerza_extension_maxima': self.fuerza,
                        }
                    self.ids.rv.data.append(medicion)
                self.popup.dismiss()
                self.clock.cancel()
                self.guardado()

    def on_leave(self, *args):
        self.ids.rv.ids.estudios.clear_selection()
        self.ids.btn_medir.close_stack()
        self.ids.btn_medir.icon = 'plus'
        self.ids.rv.viewclass.selection.clear()
        self.ids.rv.viewclass.anterior.clear()
        vitalgb_app.estudio_seleccionado = None
        vitalgb_app.root.ids.nav_drawer.swipe_edge_width = 0


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class ContentNavigationDrawer(MDBoxLayout):
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    color = (0.01, 0.02, 0.37, 1)
    font_name = "fonts/Ubuntu-L"
    font_size = dp(18)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
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
    ''' Add selection support to the BoxLayout '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    selection = []
    anterior = []

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableBox, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBox, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
        else:
            return False

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        self.selection.clear()
        current = rv.data[index]
        if is_selected:
            if current not in self.anterior:
                self.anterior.clear()
                self.anterior.append(current)
                self.selection.append(current)
            else:
                self.anterior.clear()
                vitalgb_app.root.ids.pantalla_paciente_seleccionado.ids.rv.ids.estudios.clear_selection()

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

    def __init__(self, **kwargs):
        super().__init__()
        self.planilla_personal = PlanillaPersonal(working_path)
        self.planilla_general = PlanillaGeneral(working_path)
        self.bluetooth_conection = Bluetooth(DEVICE_NAME)
        self.patient_selected = None

    def verificar_conexion_bluetooth(self):
        try:
            self.bluetooth_conection.enviar_byte()
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
                self.root.ids.screen_manager.current_screen.menu.dismiss()
            self.volver_pantalla_principal()
            return True  # override the default behaviour
        else:  # the key now does nothing
            return False

    def volver_pantalla_principal(self):
        self.root.ids.screen_manager.current = "pantalla_principal"

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
        headers = ['nombre_profesional',
                   'nombre_del_servicio',
                   'direccion',
                   'telefono',
                   'sitio_web']
        df = pandas.DataFrame({header: [self.dialog.content_cls.ids[field].text]
                               for (header, field) in zip(headers, self.dialog.content_cls.ids)})
        df.to_csv(f"{working_path}/VitalGB/instituto.csv", index=False)


vitalgb_app = MainApp()
vitalgb_app.run()
