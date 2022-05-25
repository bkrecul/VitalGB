import pandas
import os
from pdf_reports import CrearReportePDF


class PlanillaPersonal:
    """Clase que se encarga del almacenamiento, exportacion y muestra de datos de la planilla personal de
    cada paciente."""
    def __init__(self, file_location=""):
        self.file_location = file_location

    def exportar(self, tipo_de_archivo, id, nombre_archivo, path, **kwargs)->str:
        """Función que genera un archivo pdf o csv a partir de los datos internos y devuelve el path
        de la ubicación de este archivo generado."""
        self.data_frame = pandas.read_csv(f'{self.file_location}/VitalGB/pacientes/{id}.csv')
        self.data_frame.set_axis(['Fecha', 'Flexión Máxima', 'Extensión Máxima', 'Fuerza Flexión Máxima',
                                  'Fuerza Extensión Máxima'], axis=1, inplace=True)
        working_directory = os.path.join(path, "VitalGB")
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
            if not os.path.exists(os.path.join(working_directory, "reportes")):
                os.makedirs(os.path.join(working_directory, "reportes"))
        if tipo_de_archivo == "csv":
            full_path = f"{working_directory}/reportes/{nombre_archivo}.xlsx"
            writer = pandas.ExcelWriter(full_path)
            self.data_frame.to_excel(writer, sheet_name='Hoja 1', index=False, header=True)
            worksheet = writer.sheets['Hoja 1']
            worksheet.set_column(1, 2, 20)
            worksheet.set_column(3, 4, 25)
            worksheet.set_column(0, 0, 10)
            writer.save()
            # self.data_frame.to_excel(full_path, index=False, header=True, engine='xlsxwriter',)
        if tipo_de_archivo == 'pdf':
            obs = kwargs.get('obs')
            full_path = f"{working_directory}/reportes/{nombre_archivo}.pdf"
            instituto = self.lectura_datos_institucionales()
            # Ejemplo de como deben ser la lista de datos del instituto:
            # formato: instituto = [<nombre_del_servicio>,<dirección>,<telefono>,<sitio_web>]
            # Si no existe algun dato debe reemplazarse por None

            info_paciente = kwargs.get('info')
            encabezados = [None, nombre_archivo, None, None, None, None]
            if info_paciente[5] != '':
                encabezados[2] = info_paciente[5]
            if info_paciente[3] != '':
                encabezados[3] = 'DNI'
                encabezados[4] = info_paciente[3]
            if info_paciente[4] != '':
                encabezados[5] = info_paciente[4]
            CrearReportePDF().crear_reporte(self.data_frame, full_path, encabezados, obs, instituto)
        return full_path

    def lectura_datos_institucionales(self):
        try:
            data = pandas.read_csv(f"{self.file_location}/VitalGB/instituto.csv", keep_default_na=False)
        except FileNotFoundError:
            return [None, None, None, None, None]
        else:
            return [data['nombre_profesional'].tolist()[0].title(),
                    data['nombre_del_servicio'].tolist()[0].title(),
                    data['direccion'].tolist()[0].title(),
                    str(data['telefono'].tolist()[0]),
                    data['sitio_web'].tolist()[0].lower(),
                    data['image_path'].tolist()[0]]

    def lectura(self, id) -> pandas.DataFrame:
        """Función que devuelve los datos del archivo de planilla personal."""
        try:
            self.data_frame = pandas.read_csv(f'{self.file_location}/VitalGB/pacientes/{id}.csv')
        except FileNotFoundError:
            pass
        else:
            return self.data_frame.astype('str')
            # TODO: leer los datos que hayan sido medidos (con el dispositivo) de la planilla

    def crear(self, file_location, id):
        """ Función que crea una planilla personal por cada paciente, donde se almacenarán los datos medidos por el
        dispositivo"""
        # TODO: crear planilla personal que será en base a como se carguen/estructuren los datos dentro de
        #  la planilla
        self.headings = \
            ['fecha', 'flexion_maxima', 'extension_maxima', 'fuerza_flexion_maxima', 'fuerza_extension_maxima']
        self.data_frame = pandas.DataFrame([self.headings])
        self.data_frame.to_csv(f'{file_location}/VitalGB/pacientes/{id}.csv', index=False, header=False)

    def cargar_mediciones(self, id, datos):
        # TODO: cargar las mediciones que se vayan realizando con el dispositivo.
        file_location = f'{self.file_location}/VitalGB/pacientes/{id}.csv'
        self.crear(self.file_location, id)
        for data in datos:
            self.data_frame = pandas.DataFrame(data, index=[0])
            self.data_frame.to_csv(file_location, mode="a", index=False, header=False)


class PlanillaGeneral(PlanillaPersonal):
    """ Esta clase contiene los comandos necesarios para cargar y leer los usuarios dentro de la planilla.
    Contiene a los pacientes que utilicen VitalGB"""

    def __init__(self, file_location=""):
        super().__init__(file_location)
        try:
            pacientes = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv")
            self.id = pacientes['id'].max() + 1
            if pandas.isna(self.id):
                self.id = 0
        except FileNotFoundError:
            working_directory = os.path.join(self.file_location, "VitalGB")
            if not os.path.exists(working_directory):
                os.makedirs(working_directory)
                os.makedirs(os.path.join(working_directory,"pacientes"))
            self.headings = ["id", "Nombre", "Apellido", "DNI", "Sexo", "Fecha de Nacimiento"]
            self.data_frame = pandas.DataFrame([self.headings])
            self.data_frame.to_csv(f"{working_directory}/pacientes.csv", index=False, header=False)
            self.id = 0

    def cargar_paciente(self, nombre, apellido, **kwargs):
        """ Función para la carga de un paciente nuevo dentro de VitalGB"""
        self.informacion_del_paciente  = {'id': self.id, 'Nombre': [nombre], 'Apellido': [apellido],
                                          'DNI': [kwargs.get("dni")], 'Sexo': [kwargs.get("sexo")],
                                          'Fecha de Nacimiento': [kwargs.get("nacimiento")]}
        self.crear(self.file_location, self.id)
        self.id += 1
        self.data_frame = pandas.DataFrame(self.informacion_del_paciente)
        self.data_frame.to_csv(f'{self.file_location}/VitalGB/pacientes.csv', mode="a", index=False, header=False)

    def devolver_pacientes(self) -> list:
        """ Función que devuelve los nombres y apellidos de los pacientes, en formato de lista. """
        pacientes = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv")
        nombres = [{'text': nombre + " " + apellido, 'id': id} for nombre, apellido, id in
                        zip(pacientes['Nombre'].tolist(), pacientes['Apellido'].tolist(), pacientes['id'].tolist())]
        return nombres

    def devolver_paciente(self, id):
        nombres = self.devolver_pacientes()
        for nombre in nombres:
            if nombre['id'] == id:
                return nombre['text']

    def devolver_info_paciente(self, id):
        pacientes = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv", keep_default_na=False, dtype=str)
        return pacientes.loc[id].to_list()

    def guardar_cambios_paciente(self, id, nombre, apellido, **kwargs):
        df = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv", keep_default_na=False)
        df.at[id, 'Nombre'] = nombre
        df.at[id, 'Apellido'] = apellido
        df.at[id, 'DNI'] = kwargs.get("dni")
        df.at[id, 'Sexo'] = kwargs.get("sexo")
        df.at[id, 'Fecha de Nacimiento'] = kwargs.get("nacimiento")
        df.to_csv(f"{self.file_location}/VitalGB/pacientes.csv", index=False)