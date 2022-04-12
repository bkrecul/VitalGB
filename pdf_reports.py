from table_class import PDF
from PIL import Image
import pandas


class CrearReportePDF:
    image_path = 'images/logo.png'

    def crear_reporte(self, tabla_del_paciente: pandas.DataFrame, filepath, *args, **kwargs):
        all_data = self.formatear(tabla_del_paciente.to_dict())

        selected_data = all_data

        # selected_data = {}
        # for arg in args:
        #     selected_data[arg] = all_data[arg]

        pdf = PDF()
        pdf.add_page()

        pdf.set_font("Times", size=10)

        if "image" in kwargs:
            self.image_path = kwargs.get("image")
        w, h = Image.open(self.image_path).size
        factor = w // 75
        w //= factor
        h //= factor

        pdf.set_font(family="Times", size=24, style="B")
        pdf.image(self.image_path, h=h, w=w)
        pdf.cell(w=0, h=0, txt="Pacientes", border=0, align="C", ln=1)

        pdf.set_font("Times", size=10)
        pdf.create_table(table_data=selected_data, title='I\'m the first title', cell_width='even')
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
