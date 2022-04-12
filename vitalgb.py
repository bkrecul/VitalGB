import pandas
import os
from pdf_reports import CrearReportePDF


# class ReportePDF:
#     def generar_pdf(self,dataframe:pandas.DataFrame,path_to_file:str):
#
#         pass


class PlanillaPersonal:
    """Clase que se encarga del almacenamiento, exportacion y muestra de datos de la planilla personal de
    cada paciente."""
    def __init__(self, file_location=""):
        self.file_location = file_location

    def exportar(self, tipo_de_archivo, nombre, apellido, path)->str:
        """Función que genera un archivo pdf o csv a partir de los datos internos y devuelve el path
        de la ubicación de este archivo generado."""
        self.data_frame = pandas.read_csv(f'{self.file_location}/VitalGB/pacientes/{nombre}_{apellido}.csv')
        self.data_frame.set_axis(['Fecha', 'Flexión Máxima', 'Extensión Máxima', 'Fuerza Flexión Máxima',
                                  'Fuerza Extensión Máxima'], axis=1, inplace=True)
        working_directory = os.path.join(path, "VitalGB")
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
            if not os.path.exists(os.path.join(working_directory, "reportes")):
                os.makedirs(os.path.join(working_directory, "reportes"))
        if tipo_de_archivo == "csv":
            full_path = f"{working_directory}/reportes/{nombre}_{apellido}.xlsx"
            writer = pandas.ExcelWriter(full_path)
            self.data_frame.to_excel(writer, sheet_name='Hoja 1', index=False, header=True)
            worksheet = writer.sheets['Hoja 1']
            worksheet.set_column(1, 2, 20)
            worksheet.set_column(3, 4, 25)
            worksheet.set_column(0, 0, 10)
            writer.save()
            # self.data_frame.to_excel(full_path, index=False, header=True, engine='xlsxwriter',)
        if tipo_de_archivo == 'pdf':
            full_path = f"{working_directory}/reportes/{nombre}_{apellido}.pdf"
            CrearReportePDF().crear_reporte(self.data_frame, full_path)
        return full_path

    def lectura(self, nombre, apellido) -> pandas.DataFrame:
        """Función que devuelve los datos del archivo de planilla personal."""
        try:
            self.data_frame = pandas.read_csv(f'{self.file_location}/VitalGB/pacientes/{nombre}_{apellido}.csv')
        except FileNotFoundError:
            pass
        else:
            return self.data_frame.astype('str')
            # TODO: leer los datos que hayan sido medidos (con el dispositivo) de la planilla

    def crear(self, file_location, nombre, apellido):
        """ Función que crea una planilla personal por cada paciente, donde se almacenarán los datos medidos por el
        dispositivo"""
        # TODO: crear planilla personal que será en base a como se carguen/estructuren los datos dentro de
        #  la planilla
        self.headings = \
            ['fecha', 'flexion_maxima', 'extension_maxima', 'fuerza_flexion_maxima', 'fuerza_extension_maxima']
        self.data_frame = pandas.DataFrame([self.headings])
        self.data_frame.to_csv(f'{file_location}/VitalGB/pacientes/{nombre}_{apellido}.csv', index=False, header=False)

    def cargar_mediciones(self, nombre, apellido, datos):
        # TODO: cargar las mediciones que se vayan realizando con el dispositivo.
        file_location = f'{self.file_location}/VitalGB/pacientes/{nombre}_{apellido}.csv'
        self.crear(self.file_location, nombre, apellido)
        for data in datos:
            self.data_frame = pandas.DataFrame(data, index=[0])
            self.data_frame.to_csv(file_location, mode="a", index=False, header=False)


class PlanillaGeneral(PlanillaPersonal):
    """ Esta clase contiene los comandos necesarios para cargar y leer los usuarios dentro de la planilla.
    Contiene a los pacientes que utilicen VitalGB"""

    def __init__(self, file_location=""):
        super().__init__(file_location)
        try:
            self.pacientes = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv")
        except FileNotFoundError:
            working_directory = os.path.join(self.file_location, "VitalGB")
            if not os.path.exists(working_directory):
                os.makedirs(working_directory)
                os.makedirs(os.path.join(working_directory,"pacientes"))
            self.headings = ["Nombre", "Apellido", "Edad", "Peso", "Sexo", "Patologia"]
            self.data_frame = pandas.DataFrame([self.headings])
            self.data_frame.to_csv(f"{working_directory}/pacientes.csv", index=False, header=False)

    def cargar_paciente(self, nombre, apellido, **kwargs):
        """ Función para la carga de un paciente nuevo dentro de VitalGB"""
        self.informacion_del_paciente  = {'Nombre': [nombre], 'Apellido': [apellido], 'Edad': [kwargs.get("edad")],
                                          'Peso': [kwargs.get("peso")], 'Sexo': [kwargs.get("sexo")],
                                          'Patologia': [kwargs.get("patologia")]}
        self.crear(self.file_location,nombre, apellido)
        self.data_frame = pandas.DataFrame(self.informacion_del_paciente)
        self.data_frame.to_csv(f'{self.file_location}/VitalGB/pacientes.csv', mode="a", index=False, header=False)

    def devolver_pacientes(self) -> list:
        """ Función que devuelve los nombres y apellidos de los pacientes, en formato de lista. """
        self.pacientes = pandas.read_csv(f"{self.file_location}/VitalGB/pacientes.csv")
        self.nombres = [{'text': nombre + " " + apellido} for nombre, apellido in
                        zip(self.pacientes['Nombre'].tolist(), self.pacientes['Apellido'].tolist())]
        return self.nombres

