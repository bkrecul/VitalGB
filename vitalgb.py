import pandas
import os

# import fpdf       # ----> No se puede usar en APK, se crashea
# from reportlab.platypus.tables import Table
# from reportlab.pdfgen import canvas
# from reportlab.platypus.paragraph import Paragraph
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.rl_config import defaultPageSize
# from reportlab.lib.units import inch
# PAGE_HEIGHT=defaultPageSize[1]
# PAGE_WIDTH=defaultPageSize[0]
# styles = getSampleStyleSheet()
#
#
# Title = "Hello world"
# pageinfo = "platypus example"
# def myFirstPage(canvas, doc):
#  canvas.saveState()
#  canvas.setFont('Times-Bold',16)
#  canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
#  canvas.setFont('Times-Roman',9)
#  canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
#  canvas.restoreState()
#
#
# def myLaterPages(canvas, doc):
#  canvas.saveState()
#  canvas.setFont('Times-Roman',9)
#  canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
#  canvas.restoreState()
#
#
# def go():
#  doc = SimpleDocTemplate("phello.pdf")
#  Story = [Spacer(1,2*inch)]
#  style = styles["Normal"]
#  for i in range(100):
#     bogustext = ("This is Paragraph number %s. " % i) *20
#     p = Paragraph(bogustext, style)
#     Story.append(p)
#     Story.append(Spacer(1,0.2*inch))
#  doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
#
#
# go()
#
#
# # I = Image('../images/replogo.gif')
# # I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
# # I.drawWidth = 1.25*inch
# # P0 = Paragraph('''
# #  <b>A pa<font color=red>r</font>a<i>graph</i></b>
# #  <super><font color=yellow>1</font></super>''',
# #  styleSheet["BodyText"])
# # P = Paragraph('''
# #  <para align=center spaceb=3>The <b>ReportLab Left
# #  <font color=red>Logo</font></b>
# #  Image</para>''',
# #  styleSheet["BodyText"])
# # data= [['A', 'B', 'C', P0, 'D'],
# #  ['00', '01', '02', [I,P], '04'],
# #  ['10', '11', '12', [P,I], '14'],
# #  ['20', '21', '22', '23', '24'],
# #  ['30', '31', '32', '33', '34']]
# # t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
# #  ('BOX',(0,0),(1,-1),2,colors.red),
# #  ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
# #  ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
# #  ('BACKGROUND', (0, 0), (0, 1), colors.pink),
# #  ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
# #  ('BACKGROUND', (2, 2), (2, 3), colors.orange),
# #  ('BOX',(0,0),(-1,-1),2,colors.black),
# #  ('GRID',(0,0),(-1,-1),0.5,colors.black),
# #  ('VALIGN',(3,0),(3,0),'BOTTOM'),
# #  ('BACKGROUND',(3,0),(3,0),colors.limegreen),
# #  ('BACKGROUND',(3,1),(3,1),colors.khaki),
# #  ('ALIGN',(3,1),(3,1),'CENTER'),
# #  ('BACKGROUND',(3,2),(3,2),colors.beige),
# #  ('ALIGN',(3,2),(3,2),'LEFT'),
# #  ])
# # t._argW[3]=1.5*inch
# #
# #
# #
# #
# # def hello(c):
# #     c.drawString(100,100,"Hello World")
# # c = canvas.Canvas("hello.pdf")
# # hello(c)
# # c.showPage()
# # c.save()
# #
# # data= [['00', '01', '02', '03', '04'],
# #  ['10', '11', '12', '13', '14'],
# #  ['20', '21', '22', '23', '24'],
# #  ['30', '31', '32', '33', '34']]
# # t=Table(data)
# # # t=Table(data,style=[
# # #  ('GRID',(0,0),(-1,-1),0.5,colors.grey),
# # #  ('GRID',(1,1),(-2,-2),1,colors.green),
# # #  ('BOX',(0,0),(1,-1),2,colors.red),
# # #  ('BOX',(0,0),(-1,-1),2,colors.black),
# # #  ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
# # #  ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
# # #  ('BACKGROUND', (0, 0), (0, 1), colors.pink),
# # #  ('BACKGROUND', (1, 1), (1, 2), colors.lavender),
# # #  ('BACKGROUND', (2, 2), (2, 3), colors.orange),
# # #  ])
# # print(t)

# class CrearReportePDF:
#     def crear_reporte(self, tabla_del_paciente:pandas.DataFrame, *args):
#         all_data = self.formatear(tabla_del_paciente.to_dict())
#
#         selected_data = {}
#         for arg in args:
#             selected_data[arg] = all_data[arg]
#
#         pdf = PDF()
#         pdf.add_page()
#
#         pdf.set_font("Times", size=10)
#
#         pdf.set_font(family="Times",size=24,style="B")
#         pdf.image("logo.png",h=40,w=40)
#         pdf.cell(w=0,h=0, txt="Pacientes", border=0, align="C", ln=1)
#
#         pdf.set_font("Times", size=10)
#         pdf.create_table(table_data=selected_data,title='I\'m the first title', cell_width='even')
#         pdf.ln()
#
#         pdf.output("pacientes.pdf")
#
#     def formatear(self, tabla_del_paciente:dict) -> dict:
#         """ Recibe un diccionario de formato {key:{key: value}}, lo convierte al formato {key:[value]} y a su vez
#         convierte a todos los elementos value en string.
#         Esto es necesario para trabajar con el comando Create Table de la clase PDF."""
#
#         valores = []
#         for item in tabla_del_paciente.values():
#             sub_valor = []
#             for subitem in item.values():
#                 if pandas.isna(subitem):
#                     sub_valor.append("")
#                 else:
#                     sub_valor.append(str(subitem))
#             valores.append(sub_valor)
#
#         llaves = [item for item in tabla_del_paciente.keys()]
#
#         diction = {key: value for key, value in zip(llaves, valores)}
#         return diction


class ReportePDF:
    def generar_pdf(self,dataframe:pandas.DataFrame,path_to_file:str):

        pass


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
            ReportePDF().generar_pdf(self.data_frame,full_path)
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


# ======================== Los siguientes modulos no funcionan cuando se portan con buildozer ==================

# class PDF(fpdf.FPDF):
#     def create_table(self, table_data, title='', data_size=10, title_size=12, align_data='L', align_header='L',
#                      cell_width='even', x_start='x_default', emphasize_data=[], emphasize_style=None,
#                      emphasize_color=(0, 0, 0)):
#         """
#         table_data:
#                     list of lists with first element being list of headers
#         title:
#                     (Optional) title of table (optional)
#         data_size:
#                     the font size of table data
#         title_size:
#                     the font size fo the title of the table
#         align_data:
#                     align table data
#                     L = left align
#                     C = center align
#                     R = right align
#         align_header:
#                     align table data
#                     L = left align
#                     C = center align
#                     R = right align
#         cell_width:
#                     even: evenly distribute cell/column width
#                     uneven: base cell size on lenght of cell/column items
#                     int: int value for width of each cell/column
#                     list of ints: list equal to number of columns with the widht of each cell / column
#         x_start:
#                     where the left edge of table should start
#         emphasize_data:
#                     which data elements are to be emphasized - pass as list
#                     emphasize_style: the font style you want emphaized data to take
#                     emphasize_color: emphasize color (if other than black)
#
#         """
#         default_style = self.font_style
#         if emphasize_style == None:
#             emphasize_style = default_style
#
#         # default_font = self.font_family
#         # default_size = self.font_size_pt
#         # default_style = self.font_style
#         # default_color = self.color # This does not work
#
#         # Get Width of Columns
#         def get_col_widths():
#             col_width = cell_width
#             if col_width == 'even':
#                 col_width = self.epw / len(data[
#                                                0]) - 1  # distribute content evenly   # epw = effective page width (width of page not including margins)
#             elif col_width == 'uneven':
#                 col_widths = []
#
#                 # searching through columns for largest sized cell (not rows but cols)
#                 for col in range(len(table_data[0])):  # for every row
#                     longest = 0
#                     for row in range(len(table_data)):
#                         cell_value = str(table_data[row][col])
#                         value_length = self.get_string_width(cell_value)
#                         if value_length > longest:
#                             longest = value_length
#                     col_widths.append(longest + 4)  # add 4 for padding
#                 col_width = col_widths
#
#                 ### compare columns
#
#             elif isinstance(cell_width, list):
#                 col_width = cell_width  # TODO: convert all items in list to int
#             else:
#                 # TODO: Add try catch
#                 col_width = int(col_width)
#             return col_width
#
#         # Convert dict to lol
#         # Why? because i built it with lol first and added dict func after
#         # Is there performance differences?
#         if isinstance(table_data, dict):
#             header = [key for key in table_data]
#             data = []
#             for key in table_data:
#                 value = table_data[key]
#                 data.append(value)
#             # need to zip so data is in correct format (first, second, third --> not first, first, first)
#             data = [list(a) for a in zip(*data)]
#
#         else:
#             header = table_data[0]
#             data = table_data[1:]
#
#         line_height = self.font_size * 2.5
#
#         col_width = get_col_widths()
#         self.set_font(size=title_size)
#
#         # Get starting position of x
#         # Determin width of table to get x starting point for centred table
#         if x_start == 'C':
#             table_width = 0
#             if isinstance(col_width, list):
#                 for width in col_width:
#                     table_width += width
#             else:  # need to multiply cell width by number of cells to get table width
#                 table_width = col_width * len(table_data[0])
#             # Get x start by subtracting table width from pdf width and divide by 2 (margins)
#             margin_width = self.w - table_width
#             # TODO: Check if table_width is larger than pdf width
#
#             center_table = margin_width / 2  # only want width of left margin not both
#             x_start = center_table
#             self.set_x(x_start)
#         elif isinstance(x_start, int):
#             self.set_x(x_start)
#         elif x_start == 'x_default':
#             x_start = self.set_x(self.l_margin)
#
#         # TABLE CREATION #
#
#         # add title
#         if title != '':
#             self.multi_cell(0, line_height, title, border=0, align='j', ln=3, max_line_height=self.font_size)
#             self.ln(line_height)  # move cursor back to the left margin
#
#         self.set_font(size=data_size)
#         # add header
#         y1 = self.get_y()
#         if x_start:
#             x_left = x_start
#         else:
#             x_left = self.get_x()
#         x_right = self.epw + x_left
#         if not isinstance(col_width, list):
#             if x_start:
#                 self.set_x(x_start)
#             for datum in header:
#                 self.multi_cell(col_width, line_height, datum, border=0, align=align_header, ln=3,
#                                 max_line_height=self.font_size)
#                 x_right = self.get_x()
#             self.ln(line_height)  # move cursor back to the left margin
#             y2 = self.get_y()
#             self.line(x_left, y1, x_right, y1)
#             self.line(x_left, y2, x_right, y2)
#
#             for row in data:
#                 if x_start:  # not sure if I need this
#                     self.set_x(x_start)
#                 for datum in row:
#                     if datum in emphasize_data:
#                         self.set_text_color(*emphasize_color)
#                         self.set_font(style=emphasize_style)
#                         self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
#                                         max_line_height=self.font_size)
#                         self.set_text_color(0, 0, 0)
#                         self.set_font(style=default_style)
#                     else:
#                         self.multi_cell(col_width, line_height, datum, border=0, align=align_data, ln=3,
#                                         max_line_height=self.font_size)  # ln = 3 - move cursor to right with same vertical offset # this uses an object named self
#                 self.ln(line_height)  # move cursor back to the left margin
#
#         else:
#             if x_start:
#                 self.set_x(x_start)
#             for i in range(len(header)):
#                 datum = header[i]
#                 self.multi_cell(col_width[i], line_height, datum, border=0, align=align_header, ln=3,
#                                 max_line_height=self.font_size)
#                 x_right = self.get_x()
#             self.ln(line_height)  # move cursor back to the left margin
#             y2 = self.get_y()
#             self.line(x_left, y1, x_right, y1)
#             self.line(x_left, y2, x_right, y2)
#
#             for i in range(len(data)):
#                 if x_start:
#                     self.set_x(x_start)
#                 row = data[i]
#                 for i in range(len(row)):
#                     datum = row[i]
#                     if not isinstance(datum, str):
#                         datum = str(datum)
#                     adjusted_col_width = col_width[i]
#                     if datum in emphasize_data:
#                         self.set_text_color(*emphasize_color)
#                         self.set_font(style=emphasize_style)
#                         self.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3,
#                                         max_line_height=self.font_size)
#                         self.set_text_color(0, 0, 0)
#                         self.set_font(style=default_style)
#                     else:
#                         self.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3,
#                                         max_line_height=self.font_size)  # ln = 3 - move cursor to right with same vertical offset # this uses an object named self
#                 self.ln(line_height)  # move cursor back to the left margin
#         y3 = self.get_y()
#         self.line(x_left, y3, x_right, y3)
#
#
# class CrearReportePDF:
#     def crear_reporte(self, tabla_del_paciente:pandas.DataFrame, *args):
#         all_data = self.formatear(tabla_del_paciente.to_dict())
#
#         selected_data = {}
#         for arg in args:
#             selected_data[arg] = all_data[arg]
#
#         pdf = PDF()
#         pdf.add_page()
#
#         pdf.set_font("Times", size=10)
#
#         pdf.set_font(family="Times",size=24,style="B")
#         pdf.image("logo.png",h=40,w=40)
#         pdf.cell(w=0,h=0, txt="Pacientes", border=0, align="C", ln=1)
#
#         pdf.set_font("Times", size=10)
#         pdf.create_table(table_data=selected_data,title='I\'m the first title', cell_width='even')
#         pdf.ln()
#
#         pdf.output("pacientes.pdf")
#
#     def formatear(self, tabla_del_paciente:dict) -> dict:
#         """ Recibe un diccionario de formato {key:{key: value}}, lo convierte al formato {key:[value]} y a su vez
#         convierte a todos los elementos value en string.
#         Esto es necesario para trabajar con el comando Create Table de la clase PDF."""
#
#         valores = []
#         for item in tabla_del_paciente.values():
#             sub_valor = []
#             for subitem in item.values():
#                 if pandas.isna(subitem):
#                     sub_valor.append("")
#                 else:
#                     sub_valor.append(str(subitem))
#             valores.append(sub_valor)
#
#         llaves = [item for item in tabla_del_paciente.keys()]
#
#         diction = {key: value for key, value in zip(llaves, valores)}
#         return diction