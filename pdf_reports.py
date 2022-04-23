import datetime
from table_class import PDF
from PIL import Image, ImageDraw, ImageFont
import pandas


class CrearReportePDF:
    image_path = 'images/logo.png'
    encabezados = ['AUTOR:','PACIENTE:','FEC.NAC.:','TIPO DOCUMENTO:','NRO. DOCUMENTO:','SEXO:']

    def crear_reporte(self, datos_de_mediciones: pandas.DataFrame, filepath, datos_encabezado, obs, *args, **kwargs):
        nombre_del_servicio = None
        all_data = self.formatear(datos_de_mediciones.to_dict())

        selected_data = all_data

        # selected_data = {}
        # for arg in args:
        #     selected_data[arg] = all_data[arg]
        # nombre_completo = kwargs.get("nombre_completo")

        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        if "datos_del_instituto" in kwargs:
            datos_del_instituto = kwargs.get("datos_del_instituto")
            nombre_del_servicio = datos_del_instituto[0]
        if "image" in kwargs:
            self.image_path = kwargs.get("image")
        img = Image.open(self.image_path)

        w, h = img.size
        factor = h // 25
        w //= factor
        h //= factor

        pdf.image(self.image_path, w=w, h=h)

        pdf.set_xy(200, pdf.t_margin + 5)
        pdf.set_font(family="Times", size=9)
        index = 0
        while pdf.y < pdf.t_margin + h + 3:
            try:
                dato = datos_del_instituto[index]
            except IndexError:
                break
            except UnboundLocalError:
                break
            else:
                if dato is not None:
                    pdf.cell(w=0, h=0, txt=f"{dato}", border=0, align="R")
                    pdf.set_y(pdf.y + 5)
                index += 1

        pdf.set_x(pdf.l_margin)

        if pdf.y < pdf.t_margin + h:
            pdf.set_y(pdf.t_margin + h + 3)

        if nombre_del_servicio is not None:
            pdf.set_font("Helvetica", size=8, style="B")
            pdf.cell(w=46, h=5, txt="SERVICIO:", border=0, align="L")
            pdf.set_font("Helvetica", size=8)
            if datos_encabezado[0] is None:
                pdf.cell(w=46, h=5, txt=f"{nombre_del_servicio}", border=0, align="L")
            else:
                pdf.cell(w=46, h=5, txt=f"{nombre_del_servicio}", border=0, align="L",ln=1)
                pdf.set_font("Helvetica", size=8, style="B")
                pdf.cell(w=46, h=5, txt=f"{self.encabezados[0]}", border=0, align="L")
                pdf.set_font("Helvetica", size=8)
                pdf.cell(w=46, h=5, txt=f"{datos_encabezado[0]}", border=0, align="L")

        pdf.set_font("Helvetica", size=8, style="B")
        pdf.cell(w=46, h=5, txt=f"FECHA: ", border=0, align="L")
        pdf.set_font("Helvetica", size=8)
        pdf.cell(w=46, h=5, txt=datetime.datetime.now().strftime("%d/%m/%Y"), border=0, align="L", ln=1)

        data_counter = 0
        for dato,encabezado in zip(datos_encabezado[1:],self.encabezados[1:]):
            data_counter += 1
            if dato is not None:
                pdf.set_font("Helvetica", size=8, style="B")
                pdf.cell(w=46, h=5, txt=encabezado, border=0, align="L")
                pdf.set_font("Helvetica", size=8)
                if data_counter % 2 == 0:
                    pdf.cell(w=46, h=5, txt=dato, border=0, align="L", ln=1)
                else:
                    pdf.cell(w=46, h=5, txt=dato, border=0, align="L")

        pdf.cell(w=46, h=5, txt="", border=0, align="L", ln=1)

        pdf.set_font("Helvetica", size=8, style="B")
        pdf.cell(w=46, h=5, txt='OBSERVACIONES:', border=0, align="L", ln=1)
        pdf.set_font("Helvetica", size=8)
        pdf.multi_cell(w=184, h=5, txt=obs, border=0, align="L")

        pdf.create_table(table_data=selected_data, title='Resultados', cell_width='even')
        pdf.ln()

        pdf.output(f"{filepath}")

    def formatear(self, tabla_del_paciente: dict) -> dict:
        """ Recibe un diccionario de formato {key:{key: value}}, lo convierte al formato {key:[value]} y a su vez
        convierte a todos los elementos value en string.
        Esto es necesario para trabajar con el comando Create Table de la clase PDF."""

        valores = []
        for item in tabla_del_paciente.values():
            sub_valor = []
            for subitem in item.values():
                if pandas.isna(subitem):
                    sub_valor.append("")
                else:
                    sub_valor.append(str(subitem))
            valores.append(sub_valor)

        llaves = [item for item in tabla_del_paciente.keys()]

        diction = {key: value for key, value in zip(llaves, valores)}
        return diction
