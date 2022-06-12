import sqlite3
import pandas
# import pandas.io.formats.excel
#
# pandas.io.formats.excel.ExcelFormatter.header_style = None
import os
from pdf_reports import CrearReportePDF


class PlanillaPersonal:
    """Clase que se encarga del almacenamiento, exportacion y muestra de datos de la planilla personal de
    cada paciente."""

    def __init__(self, file_location=""):
        self.file_location = file_location
        self.data_path = os.path.join(self.file_location, 'vitalgb.db')
        if not os.path.exists(self.data_path):
            self._crear_base_de_datos()

    def devolver_nombre_paciente(self, id_paciente):
        conexion = self._conectarse_BD()
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
        nombre_archivo = self.devolver_nombre_paciente(id_paciente)
        datos_paciente = kwargs.get('info_paciente')

        working_directory = os.path.join(path, "VitalGB")
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
            if not os.path.exists(os.path.join(working_directory, "reportes")):
                os.makedirs(os.path.join(working_directory, "reportes"))

        if tipo_de_archivo == "csv":
            datos_angulos = self.lectura(id_paciente, 'mediciones_angulos')
            datos_fuerzas = self.lectura(id_paciente, 'mediciones_fuerzas')
            full_path = f"{working_directory}/reportes/{nombre_archivo}.xlsx"
            self.excel_export(full_path, datos_paciente, datos_angulos, datos_fuerzas)

        if tipo_de_archivo == 'pdf':
            datos_angulos = self.lectura(id_paciente, 'mediciones_angulos', fixed_header=True)
            datos_fuerzas = self.lectura(id_paciente, 'mediciones_fuerzas', fixed_header=True)
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
            CrearReportePDF().crear_reporte(datos_angulos, datos_fuerzas, full_path, encabezados, obs, instituto)
        return full_path

    def excel_export(self, full_path, datos_paciente, datos_angulos, datos_fuerzas):

        writer = pandas.ExcelWriter(full_path, engine='xlsxwriter')
        workbook = writer.book

        # Creamos la primera hoja que contendrá los datos del paciente y gráficos
        df_datos_paciente = pandas.DataFrame.from_dict(datos_paciente, orient='index').drop('id', axis=0)
        df_datos_paciente.to_excel(writer, sheet_name='Paciente', index=True, header=False)
        worksheet_principal = writer.sheets['Paciente']
        worksheet_principal.set_column('A:B', 20, None)

        # Seguiremos con la hoja 2 de los ángulos
        if datos_angulos:
            df_datos_angulos = pandas.DataFrame(datos_angulos).drop('id', axis=1)
            df_datos_angulos.set_axis(['Fecha', 'Flexión Izquierda', 'Extensión Izquierda', 'Flexión Derecha',
                                       'Extensión Derecha'], axis=1, inplace=True)
            max_row = len(df_datos_angulos)

            # calculamos el rango de movimiento de cada pie
            resultados = self.calcular_rango_movil(datos_angulos)[0]
            df_resultados = pandas.DataFrame(resultados)
            df_resultados.to_excel(writer, sheet_name='Resultados', index=False, header=True)

            format0 = workbook.add_format({'num_format': '0°', 'align': 'left', 'valign': 'vjustify'})
            format1 = workbook.add_format({'num_format': '0°', 'align': 'center', 'valign': 'vcenter'})

            worksheet_resultados = writer.sheets['Resultados']
            for n_row in range(1, max_row + 1):
                worksheet_resultados.set_row(n_row, 30)
            worksheet_resultados.set_column('B:B', 20, format1)
            worksheet_resultados.set_column('D:D', 20, format1)
            worksheet_resultados.set_column('C:C', 30, format0)
            worksheet_resultados.set_column('E:E', 30, format0)
            worksheet_resultados.set_column(0, 0, 12)

            chart_resultados = workbook.add_chart({'type': 'line'})

            chart_resultados.add_series({
                'name': ['Resultados', 0, 1],
                'categories': ['Resultados', 1, 0, max_row, 0],
                'values': ['Resultados', 1, 1, max_row, 1],
                'line': {'width': 1.00},
            })
            chart_resultados.add_series({
                'name': ['Resultados', 0, 3],
                'categories': ['Resultados', 1, 0, max_row, 0],
                'values': ['Resultados', 1, 3, max_row, 3],
                'line': {'width': 1.00},
            })

            # Configure the chart axes.
            chart_resultados.set_x_axis({'name': 'Fecha', 'date_axis': True,
                                         'minor_gridlines': {'visible': True}})  # 'num_font':  {'rotation': 45}
            chart_resultados.set_y_axis({'name': 'Angulo', 'major_gridlines': {'visible': True}})

            # Position the legend at the top of the chart.
            chart_resultados.set_legend({'position': 'top'})

            # Insert the chart into the worksheet.
            worksheet_resultados.insert_chart(f'A{max_row + 2}', chart_resultados)

            df_datos_angulos.to_excel(writer, sheet_name='Ángulos', index=False, header=True)

            worksheet_angulos = writer.sheets['Ángulos']
            for n_row in range(1, max_row + 1):
                worksheet_angulos.set_row(n_row, 30)  # set_row(row, height, cell_format, options)
            worksheet_angulos.set_column(1, 4, 20, format1)
            worksheet_angulos.set_column(0, 0, 12)

            # Generamos las gráficas que irán en la primer hoja
            # Se generan los objetos chart
            chart_angulos = workbook.add_chart({'type': 'line'})

            chart_angulos.add_series({
                'name': ['Ángulos', 0, 1],
                'categories': ['Ángulos', 1, 0, max_row, 0],
                'values': ['Ángulos', 1, 1, max_row, 1],
                'line': {'width': 1.00},
            })
            chart_angulos.add_series({
                'name': ['Ángulos', 0, 3],
                'categories': ['Ángulos', 1, 0, max_row, 0],
                'values': ['Ángulos', 1, 3, max_row, 3],
                'line': {'width': 1.00},
            })

            # Configure the chart axes.
            chart_angulos.set_x_axis({'name': 'Fecha', 'date_axis': True,
                                      'minor_gridlines': {'visible': True}})  # 'num_font':  {'rotation': 45}
            chart_angulos.set_y_axis({'name': 'Angulo', 'major_gridlines': {'visible': True}})

            # Position the legend at the top of the chart.
            chart_angulos.set_legend({'position': 'top'})

            # Insert the chart into the worksheet.
            worksheet_principal.insert_chart('E2', chart_angulos)

            chart_angulos_2 = workbook.add_chart({'type': 'line'})

            chart_angulos_2.add_series({
                'name': ['Ángulos', 0, 2],
                'categories': ['Ángulos', 1, 0, max_row, 0],
                'values': ['Ángulos', 1, 2, max_row, 2],
                'line': {'width': 1.00},
            })
            chart_angulos_2.add_series({
                'name': ['Ángulos', 0, 4],
                'categories': ['Ángulos', 1, 0, max_row, 0],
                'values': ['Ángulos', 1, 4, max_row, 4],
                'line': {'width': 1.00},
            })

            # Configure the chart axes.
            chart_angulos_2.set_x_axis({'name': 'Fecha', 'date_axis': True,
                                        'minor_gridlines': {'visible': True}})  # 'num_font':  {'rotation': 45}
            chart_angulos_2.set_y_axis({'name': 'Angulo', 'major_gridlines': {'visible': True}})

            # Position the legend at the top of the chart.
            chart_angulos_2.set_legend({'position': 'top'})

            # Insert the chart into the worksheet.
            worksheet_principal.insert_chart('E17', chart_angulos_2)

        if datos_fuerzas:

            df_datos_fuerzas = pandas.DataFrame(datos_fuerzas).drop('id', axis=1)
            df_datos_fuerzas.set_axis(['Fecha', 'Flexión Izquierda', 'Extensión Izquierda', 'Flexión Derecha',
                                       'Extensión Derecha'], axis=1, inplace=True)

            format2 = workbook.add_format({'num_format': '0.00 "Kgf"', 'align': 'center', 'valign': 'vcenter'})

            df_datos_fuerzas.to_excel(writer, sheet_name='Fuerzas', index=False, header=True)
            worksheet_fuerzas = writer.sheets['Fuerzas']
            for n_row in range(1, len(df_datos_fuerzas) + 1):
                worksheet_fuerzas.set_row(n_row, 30)
            worksheet_fuerzas.set_column(1, 4, 20, format2)
            worksheet_fuerzas.set_column(0, 0, 12)

        writer.save()

    def lectura_datos_institucionales(self):
        try:
            data = pandas.read_csv(os.path.join(self.file_location, 'instituto.csv'), keep_default_na=False)
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
        conexion = self._conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute(base_command)
        mediciones = cursor.fetchall()
        if kwargs.get('fixed_header'):
            encabezados = ['Fecha', 'Flexion izquierda', 'Extension izquierda',
                           'Flexion derecha', 'Extension derecha']
        else:
            encabezados = ['fecha', 'flexion_izquierda', 'extension_izquierda',
                           'flexion_derecha', 'extension_derecha']
        mediciones = [{'id': medicion[0],
                       encabezados[0]: medicion[2].replace(" ", '\n'),
                       encabezados[1]: medicion[5],
                       encabezados[2]: medicion[6],
                       encabezados[3]: medicion[3],
                       encabezados[4]: medicion[4]}
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
        conexion = self._conectarse_BD()
        conexion.execute(base_command)
        conexion.commit()

    def editar_mediciones(self, magnitud_a_medir, id_medicion, **kwargs):
        base_command = f'UPDATE {magnitud_a_medir} SET '
        for column_name, column_values in kwargs.items():
            base_command += f'{column_name}={column_values}'
            base_command += ', '
        base_command = base_command[0:-2] + f' WHERE id={id_medicion}'
        conexion = self._conectarse_BD()
        conexion.execute(base_command)
        conexion.commit()
        conexion.close()

    def cargar_mediciones(self, id_paciente, fecha, magnitud_a_medir, **kwargs):
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
            conexion = self._conectarse_BD()
            conexion.execute(base_command)
            conexion.commit()
            conexion.close()
            id_medicion = self.lectura(id_paciente, magnitud_a_medir)[-1]['id']

        return id_medicion

    def calcular_rango_movil(self, mediciones_angulos):
        resultados = []
        indice_datos_ausentes = []
        for medicion in mediciones_angulos:
            calculo = {}
            indice = None
            notas = self._cargar_notas_guardadas_angulos(medicion['id'])
            calculo['Fecha'] = medicion['fecha']
            try:
                calculo['Rango izquierdo'] = medicion['flexion_izquierda'] + medicion['extension_izquierda']
            except TypeError:
                indice = medicion['id']
                # TODO: Cambiar reemplazo de dato ausente por un promedio de los datos ya existentes
                calculo['Rango izquierdo'] = 65
            if notas[0] != "":
                calculo['Notas pie izquierdo'] = notas[0]
            else:
                calculo['Notas pie izquierdo'] = ""
            try:
                calculo['Rango derecho'] = medicion['flexion_derecha'] + medicion['extension_derecha']
            except TypeError:
                calculo['Rango derecho'] = 65
                indice = medicion['id']
            if notas[1] != "":
                calculo['Notas pie derecho'] = notas[1]
            else:
                calculo['Notas pie derecho'] = ""
            if indice is not None:
                indice_datos_ausentes.append(indice)
            resultados.append(calculo)
        return resultados, indice_datos_ausentes

    def guardar_nombre_de_nota_de_medicion(self, id_medicion, magnitud, pie, observaciones: dict):
        base_command = f'INSERT INTO {magnitud} ("id_medicion", "tipo", "id_observacion") VALUES ' \
                       f'({id_medicion}, '
        for key in observaciones.keys():
            part_command = base_command
            part_command += f'"{key}_{pie}", '
            for id_obs in observaciones[key]:
                final_command = part_command
                final_command += f'{id_obs}); '
                conexion = self._conectarse_BD()
                conexion.execute(final_command)
                conexion.commit()
                conexion.close()

    def _cargar_notas_guardadas_angulos(self, id_medicion):
        conexion = self._conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute(""" SELECT * FROM observaciones_angulos WHERE id_medicion=?
                                """, [id_medicion])
        notas = cursor.fetchall()
        conexion.close()
        notas_pie_izquierdo = ""
        notas_pie_derecho = ""
        for nota in notas:
            tipo = nota[2]
            if tipo == 'flexion_izquierda' or tipo == 'extension_izquierda':
                notas_pie_izquierdo += self.obtener_nombres_observaciones(id=nota[3])[1] + ", "
            if tipo == 'flexion_derecha' or tipo == 'extension_derecha':
                notas_pie_derecho += self.obtener_nombres_observaciones(id=nota[3])[1] + ", "
        return notas_pie_izquierdo, notas_pie_derecho

    def obtener_nombres_observaciones(self, **kwargs):
        if 'id' in kwargs:
            conexion = self._conectarse_BD()
            cursor = conexion.cursor()
            cursor.execute(""" SELECT * FROM observacion WHERE id=?""", [kwargs.get('id')])
            return cursor.fetchone()
        conexion = self._conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute(""" SELECT * FROM observacion """)
        return cursor.fetchall()

    def cargar_nota(self, nota):
        conexion = self._conectarse_BD()
        conexion.execute("""INSERT INTO observacion ("nombre")
                VALUES (?); """, [nota])
        conexion.commit()
        conexion.close()
        return self.obtener_nombres_observaciones()[-1][0]

    def _conectarse_BD(self):
        return sqlite3.connect(self.data_path)

    def _crear_base_de_datos(self):
        sqlite3.connect(self.data_path)
        conexion = self._conectarse_BD()
        conexion.execute("""CREATE TABLE "pacientes" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "nombre"	TEXT NOT NULL,
                                "apellido"	TEXT NOT NULL,
                                "dni"	INTEGER,
                                "sexo"	TEXT,
                                "fecha_nacimiento"	TEXT,
                                PRIMARY KEY("id" AUTOINCREMENT)
                                )""")
        conexion.commit()
        conexion.close()
        conexion = self._conectarse_BD()
        conexion.execute("""CREATE TABLE "observacion" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "nombre"	TEXT,
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )""")
        conexion.commit()
        conexion.close()
        conexion = self._conectarse_BD()
        conexion.execute("""CREATE TABLE "mediciones_fuerzas" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "id_paciente"	INTEGER NOT NULL,
                                "fecha"	TEXT NOT NULL,
                                "flexion_derecha"	REAL NOT NULL DEFAULT ' ',
                                "extension_derecha"	REAL NOT NULL DEFAULT ' ',
                                "flexion_izquierda"	REAL NOT NULL DEFAULT ' ',
                                "extension_izquierda"	REAL NOT NULL DEFAULT ' ',
                                FOREIGN KEY("id_paciente") REFERENCES "pacientes"("id"),
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )""")
        conexion.commit()
        conexion.close()
        conexion = self._conectarse_BD()
        conexion.execute(""" CREATE TABLE "mediciones_angulos" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "id_paciente"	INTEGER NOT NULL,
                                "fecha"	TEXT NOT NULL,
                                "flexion_derecha"	INTEGER NOT NULL DEFAULT ' ',
                                "extension_derecha"	INTEGER NOT NULL DEFAULT ' ',
                                "flexion_izquierda"	INTEGER NOT NULL DEFAULT ' ',
                                "extension_izquierda"	INTEGER NOT NULL DEFAULT ' ',
                                FOREIGN KEY("id_paciente") REFERENCES "pacientes"("id"),
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )""")
        conexion.commit()
        conexion.close()
        conexion = self._conectarse_BD()
        conexion.execute("""CREATE TABLE "observaciones_angulos" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "id_medicion"	INTEGER NOT NULL,
                                "tipo"	TEXT NOT NULL,
                                "id_observacion"	INTEGER NOT NULL,
                                FOREIGN KEY("id_observacion") REFERENCES "observacion"("id"),
                                FOREIGN KEY("id_medicion") REFERENCES "mediciones_angulos"("id"),
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )""")
        conexion.commit()
        conexion.close()
        conexion = self._conectarse_BD()
        conexion.execute("""CREATE TABLE "observaciones_fuerzas" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "id_medicion"	INTEGER NOT NULL,
                                "tipo"	TEXT NOT NULL,
                                "id_observacion"	INTEGER NOT NULL,
                                FOREIGN KEY("id_observacion") REFERENCES "observacion"("id"),
                                FOREIGN KEY("id_medicion") REFERENCES "mediciones_fuerzas"("id"),
                                PRIMARY KEY("id" AUTOINCREMENT)
                            )""")
        conexion.commit()
        conexion.close()


class PlanillaGeneral(PlanillaPersonal):
    """ Esta clase contiene los comandos necesarios para cargar y leer los usuarios dentro de la planilla.
    Contiene a los pacientes que utilicen VitalGB"""

    def __init__(self, file_location=""):
        super().__init__(file_location)

    def cargar_paciente(self, nombre, apellido, dni, sexo, nacimiento):
        """ Función para la carga de un paciente nuevo dentro de VitalGB"""

        conexion = self._conectarse_BD()
        conexion.execute("""INSERT
        INTO pacientes ("nombre", "apellido", "dni", "sexo", "fecha_nacimiento")
        VALUES (?, ?, ?, ?, ?);""", [nombre, apellido, dni, sexo, nacimiento])
        conexion.commit()
        conexion.close()

    def devolver_pacientes(self) -> list:
        """ Función que devuelve los nombres y apellidos de los pacientes, en formato de lista. """

        conexion = self._conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                SELECT * FROM pacientes
                """)
        pacientes = cursor.fetchall()
        conexion.close()

        nombres = [{'text': paciente[1] + " " + paciente[2], 'id': paciente[0]} for paciente in pacientes]
        return nombres

    def devolver_info_paciente(self, id_paciente, **kwargs):
        conexion = self._conectarse_BD()
        cursor = conexion.cursor()
        cursor.execute("""
                        SELECT * FROM pacientes WHERE id=?
                        """, [id_paciente])
        paciente = cursor.fetchone()
        conexion.close()
        if kwargs.get('dict_mode'):
            headers = ['id', 'Nombre', 'Apellido', 'DNI', 'Sexo', 'Fecha de Nacimiento']
            return {header: str(dato) for header, dato in zip(headers, paciente) if dato is not None}
        return [str(dato) if dato is not None else '' for dato in paciente]

    def guardar_cambios_paciente(self, id_paciente, nombre, apellido, dni, sexo, fecha_nacimiento):
        conexion = self._conectarse_BD()
        conexion.execute("""UPDATE pacientes SET nombre=?, apellido=?, dni=?, sexo=?, fecha_nacimiento=?
                            WHERE id=?""", [nombre, apellido, dni, sexo, fecha_nacimiento, id_paciente])
        conexion.commit()
        conexion.close()
