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
        datos_angulos = self.lectura(id_paciente, 'mediciones_angulos')
        datos_fuerzas = self.lectura(id_paciente, 'mediciones_fuerzas')
        nombre_archivo = self.devolver_nombre_paciente(id_paciente)
        df_datos_angulos = pandas.DataFrame(datos_angulos).drop('id', axis=1)
        df_datos_fuerzas = pandas.DataFrame(datos_fuerzas).drop('id', axis=1)
        df_datos_angulos.set_axis(['Fecha', 'Flexión Izquierda', 'Extensión Izquierda', 'Flexión Derecha',
                                   'Extensión Derecha'], axis=1, inplace=True)
        df_datos_fuerzas.set_axis(['Fecha', 'Flexión Izquierda', 'Extensión Izquierda', 'Flexión Derecha',
                                   'Extensión Derecha'], axis=1, inplace=True)
        working_directory = os.path.join(path, "VitalGB")
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
            if not os.path.exists(os.path.join(working_directory, "reportes")):
                os.makedirs(os.path.join(working_directory, "reportes"))

        if tipo_de_archivo == "csv":
            full_path = f"{working_directory}/reportes/{nombre_archivo}.xlsx"
            writer = pandas.ExcelWriter(full_path, engine='xlsxwriter')
            workbook = writer.book
            format1 = workbook.add_format({'num_format': '0°'})
            df_datos_angulos.to_excel(writer, sheet_name='Ángulos', index=False, header=True)
            worksheet_angulos = writer.sheets['Ángulos']
            worksheet_angulos.set_column(1, 4, 20, format1)
            worksheet_angulos.set_column(0, 0, 14)
            format2 = workbook.add_format({'num_format': '0.00 "Kgf"'})
            df_datos_fuerzas.to_excel(writer, sheet_name='Fuerzas', index=False, header=True)
            worksheet_fuerzas = writer.sheets['Fuerzas']
            worksheet_fuerzas.set_column(1, 4, 20, format2)
            worksheet_fuerzas.set_column(0, 0, 14)

            writer.save()

            # import pandas as pd
            # import pandas.io.data as web
            #
            # # Some sample data to plot.
            # all_data = {}
            # for ticker in ['AAPL', 'GOOGL', 'IBM', 'YHOO', 'MSFT']:
            #     all_data[ticker] = web.get_data_yahoo(ticker, '1/1/2012', '1/1/2013')
            #
            # # Create a Pandas dataframe from the data.
            # df = pd.DataFrame({tic: data['Adj Close']
            #                    for tic, data in all_data.items()})
            #
            # # Create a Pandas Excel writer using XlsxWriter as the engine.
            # excel_file = 'legend_stock.xlsx'
            # sheet_name = 'Sheet1'
            #
            # writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            # df.to_excel(writer, sheet_name=sheet_name)
            #
            # # Access the XlsxWriter workbook and worksheet objects from the dataframe.
            # workbook = writer.book
            # worksheet = writer.sheets[sheet_name]
            #
            # # Adjust the width of the first column to make the date values clearer.
            # worksheet.set_column('A:A', 20)
            #
            # # Create a chart object.
            # chart = workbook.add_chart({'type': 'line'})
            #
            # # Configure the series of the chart from the dataframe data.
            # max_row = len(df) + 1
            # for i in range(len(['AAPL', 'GOOGL'])):
            #     col = i + 1
            #     chart.add_series({
            #         'name': ['Sheet1', 0, col],
            #         'categories': ['Sheet1', 2, 0, max_row, 0],
            #         'values': ['Sheet1', 2, col, max_row, col],
            #         'line': {'width': 1.00},
            #     })
            #
            # # Configure the chart axes.
            # chart.set_x_axis({'name': 'Date', 'date_axis': True})
            # chart.set_y_axis({'name': 'Price', 'major_gridlines': {'visible': False}})
            #
            # # Position the legend at the top of the chart.
            # chart.set_legend({'position': 'top'})
            #
            # # Insert the chart into the worksheet.
            # worksheet.insert_chart('H2', chart)
            #
            # # Close the Pandas Excel writer and output the Excel file.
            # writer.save()

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

    def lectura(self, id_paciente, magnitud_a_medir, **kwargs) -> list:
        """Función que devuelve los datos del archivo de planilla personal."""
        base_command = f'SELECT * FROM {magnitud_a_medir} WHERE id_paciente={id_paciente}'
        conexion = self.conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute(base_command)
        mediciones = cursor.fetchall()
        mediciones = [{'id': medicion[0],
                       'fecha': medicion[2],
                       'flexion_izquierda': medicion[5],
                       'extension_izquierda': medicion[6],
                       'flexion_derecha': medicion[3],
                       'extension_derecha': medicion[4]}
                      for medicion in mediciones]
        conexion.close()
        if kwargs.get('formateado'):
            return self._agregar_unidades(mediciones, magnitud_a_medir)
        return mediciones

    def _agregar_unidades(self, mediciones, magnitud):
        if magnitud == 'mediciones_angulos':
            unidad = "°"
        else:
            unidad = " Kgf"
        for fila in mediciones:
            for elemento in fila:
                if elemento != 'id' and elemento != 'fecha' and fila[elemento] != " ":
                    fila[elemento] = str(fila[elemento]) + unidad
        return mediciones


    def _sobreescribir_anterior(self, id_paciente, magnitud_a_medir, fecha, **kwargs):
        """ Esta función revisa si el dato anterior que fue guardado a la tabla mediciones tiene el campo contrario
        del otro pie vacío, y su medición fue efectuado con una antiguedad menor a media hora, para evitar
        generar una nueva fila en caso de que el profesional no haya seleccionado la fila para editar. """
        # TODO: hacer lo que dice la descripción del método
        if len(self.lectura(id_paciente, magnitud_a_medir)) == 0:
            return False
        ultima_medicion = self.lectura(id_paciente, magnitud_a_medir)[-1]
        if fecha[0][0:8] != ultima_medicion.pop('fecha')[0:8]:
            return False
        else:
            id = ultima_medicion.pop('id')
            for key in kwargs.keys():
                if ultima_medicion[key] == ' ':
                    return id
            return False

    def borrar_medicion(self, magnitud_a_medir, id_medicion):
        base_command = f'DELETE FROM {magnitud_a_medir} WHERE id={id_medicion}'
        conexion = self.conectarse_BD()
        conexion.execute(base_command)
        conexion.commit()

    def editar_mediciones(self, magnitud_a_medir, id_medicion, **kwargs):
        base_command = f'UPDATE {magnitud_a_medir} SET '
        for column_name, column_values in kwargs.items():
            base_command += f'{column_name}={column_values}'
            base_command += ', '
        base_command = base_command[0:-2] + f' WHERE id={id_medicion}'
        conexion = self.conectarse_BD()
        conexion.execute(base_command)
        conexion.commit()
        conexion.close()

    def cargar_mediciones(self, id_paciente, fecha, magnitud_a_medir, **kwargs):
        # TODO: cargar las mediciones que se vayan realizando con el dispositivo.
        # TODO: agregar notas para las mediciones
        if self._sobreescribir_anterior(id_paciente, magnitud_a_medir, fecha, **kwargs):
            id_medicion = self._sobreescribir_anterior(id_paciente, magnitud_a_medir, fecha, **kwargs)
            self.editar_mediciones(magnitud_a_medir, id_medicion, **kwargs)

        else:
            base_command = f'INSERT INTO {magnitud_a_medir} ("fecha", "id_paciente"'
            for column_name in kwargs.keys():
                base_command += f", {column_name}"
            base_command += f") VALUES ('{fecha[0]}', {id_paciente}"
            for column_values in kwargs.values():
                base_command += f", {column_values}"
            base_command += '); '
            conexion = self.conectarse_BD()
            conexion.execute(base_command)
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
