import sqlite3
import pandas
import os
from pdf_reports import CrearReportePDF


class PlanillaPersonal:
    """Clase que se encarga del almacenamiento, exportacion y muestra de datos de la planilla personal de
    cada paciente."""

    def __init__(self, file_location=""):
        self.file_location = file_location

    def devolver_nombre_paciente(self, id_paciente):
        conexion = self.conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                        SELECT nombre, apellido FROM pacientes WHERE id=?
                        """, [id_paciente])
        paciente = cursor.fetchone()
        conexion.close()
        return f'{paciente[0]} {paciente[1]}'

    def exportar(self, tipo_de_archivo, id_paciente, path, **kwargs) -> str:
        """Función que genera un archivo pdf o csv a partir de los datos internos y devuelve el path
        de la ubicación de este archivo generado."""
        datos = self.lectura(id_paciente)
        nombre_archivo = self.devolver_nombre_paciente(id_paciente)
        df_datos = pandas.DataFrame(datos).drop('id', axis=1)
        df_datos.set_axis(['Fecha', 'Flexión Izquierda', 'Extensión Izquierda', 'Flexión Derecha',
                           'Extensión Derecha'], axis=1, inplace=True)

        working_directory = os.path.join(path, "VitalGB")
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
            if not os.path.exists(os.path.join(working_directory, "reportes")):
                os.makedirs(os.path.join(working_directory, "reportes"))

        if tipo_de_archivo == "csv":
            full_path = f"{working_directory}/reportes/{nombre_archivo}.xlsx"
            writer = pandas.ExcelWriter(full_path)
            df_datos.to_excel(writer, sheet_name='Hoja 1', index=False, header=True)
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

    def lectura(self, id_paciente) -> list:
        """Función que devuelve los datos del archivo de planilla personal."""
        conexion = self.conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                        SELECT * FROM mediciones_angulos WHERE id_paciente=?
                        """, [id_paciente])
        mediciones = cursor.fetchall()
        mediciones = [{'id': medicion[0],
                       'fecha': medicion[2],
                       'flexion_derecha': str(medicion[3]),
                       'extension_derecha': str(medicion[4]),
                       'flexion_izquierda': str(medicion[5]),
                       'extension_izquierda': str(medicion[6])}
                      for medicion in mediciones]
        conexion.close()
        return mediciones

    def _sobreescribir_anterior(self, id_paciente, magnitud_a_medir, fecha, **kwargs):
        """ Esta función revisa si el dato anterior que fue guardado a la tabla mediciones tiene el campo contrario
        del otro pie vacío, y su medición fue efectuado con una antiguedad menor a media hora, para evitar
        generar una nueva fila en caso de que el profesional no haya seleccionado la fila para editar. """
        # TODO: hacer lo que dice la descripción del método
        if len(self.lectura(id_paciente)) == 0:
            return False
        if magnitud_a_medir == 'mediciones_angulos':
            ultima_medicion = self.lectura(id_paciente)[-1]
        else:
            pass  # TODO: Considerar cuando se trate de lectura de fuerzas.
        if fecha[0][0:8] != ultima_medicion.pop('fecha')[0:8]:
            return False
        else:
            id = ultima_medicion.pop('id')
            for key in kwargs.keys():
                if ultima_medicion[key] == ' ':
                    return id
            return False

    def borrar_medicion(self, magnitud_a_medir, id_medicion):
        base_comand = f'DELETE FROM {magnitud_a_medir} WHERE id={id_medicion}'
        conexion = self.conectarse_BD()
        conexion.execute(base_comand)
        conexion.commit()

    def editar_mediciones(self, magnitud_a_medir, id_medicion, **kwargs):
        base_comand = f'UPDATE {magnitud_a_medir} SET '
        for column_name, column_values in kwargs.items():
            base_comand += f'{column_name}={column_values}'
            base_comand += ', '
        base_comand = base_comand[0:-2] + f' WHERE id={id_medicion}'
        conexion = self.conectarse_BD()
        conexion.execute(base_comand)
        conexion.commit()
        conexion.close()

    def cargar_mediciones(self, id_paciente, fecha, magnitud_a_medir, **kwargs):
        # TODO: cargar las mediciones que se vayan realizando con el dispositivo.
        # TODO: agregar notas para las mediciones
        if self._sobreescribir_anterior(id_paciente, magnitud_a_medir, fecha, **kwargs):
            id_medicion = self._sobreescribir_anterior(id_paciente, magnitud_a_medir, fecha, **kwargs)
            self.editar_mediciones(magnitud_a_medir, id_medicion, **kwargs)

        else:
            base_comand = f'INSERT INTO {magnitud_a_medir} ("fecha", "id_paciente"'
            for column_name in kwargs.keys():
                base_comand += f", {column_name}"
            base_comand += f") VALUES ('{fecha[0]}', {id_paciente}"
            for column_values in kwargs.values():
                base_comand += f", {column_values}"
            base_comand += '); '
            conexion = self.conectarse_BD()
            conexion.execute(base_comand)
            conexion.commit()
            conexion.close()

    def conectarse_BD(self):
        return sqlite3.connect('vitalgb.db')


class PlanillaGeneral(PlanillaPersonal):
    """ Esta clase contiene los comandos necesarios para cargar y leer los usuarios dentro de la planilla.
    Contiene a los pacientes que utilicen VitalGB"""

    def __init__(self, file_location=""):
        super().__init__(file_location)

    def cargar_paciente(self, nombre, apellido, dni, sexo, nacimiento):
        """ Función para la carga de un paciente nuevo dentro de VitalGB"""

        conexion = self.conectarse_BD()
        conexion.execute("""INSERT
        INTO pacientes ("nombre", "apellido", "dni", "sexo", "fecha_nacimiento")
        VALUES (?, ?, ?, ?, ?);""", [nombre, apellido, dni, sexo, nacimiento])
        conexion.commit()
        conexion.close()

    def devolver_pacientes(self) -> list:
        """ Función que devuelve los nombres y apellidos de los pacientes, en formato de lista. """

        conexion = self.conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                SELECT * FROM pacientes
                """)
        pacientes = cursor.fetchall()
        conexion.close()

        nombres = [{'text': paciente[1] + " " + paciente[2], 'id': paciente[0]} for paciente in pacientes]
        return nombres

    def devolver_info_paciente(self, id_paciente):
        conexion = self.conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                        SELECT * FROM pacientes WHERE id=?
                        """, [id_paciente])
        paciente = cursor.fetchone()
        conexion.close()
        return [str(dato) if dato is not None else '' for dato in paciente]

    def guardar_cambios_paciente(self, id_paciente, nombre, apellido, dni, sexo, fecha_nacimiento):
        conexion = self.conectarse_BD()
        conexion.execute("""UPDATE pacientes SET nombre=?, apellido=?, dni=?, sexo=?, fecha_nacimiento=?
                            WHERE id=?""", [nombre, apellido, dni, sexo, fecha_nacimiento, id_paciente])
        conexion.commit()
        conexion.close()
