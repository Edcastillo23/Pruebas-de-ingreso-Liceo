import json
import os
from fpdf import FPDF
from datetime import datetime

class GestorExamen:
    def __init__(self):
        self.banco_completo = self._cargar_banco() # Cargamos TODO el JSON
        self.preguntas = [] # Se llenará al elegir grado
        self.respuestas_usuario = []
        self.estudiante = {"nombre": "", "grado": ""}
        self.indice_actual = 0

    def _cargar_banco(self):
        ruta = 'banco_preguntas.json'
        if not os.path.exists(ruta):
            return {}
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)

    def registrar_estudiante(self, nombre, grado):
        self.estudiante["nombre"] = nombre
        self.estudiante["grado"] = grado
        
        # AQUÍ ESTÁ LA MAGIA: Seleccionamos las preguntas del grado
        if grado in self.banco_completo:
            self.preguntas = self.banco_completo[grado]
        else:
            print(f"Error: No hay preguntas para {grado}")
            self.preguntas = []

    def obtener_pregunta_actual(self):
        if self.indice_actual < len(self.preguntas):
            return self.preguntas[self.indice_actual]
        return None

    def procesar_respuesta(self, opcion_elegida):
        pregunta = self.obtener_pregunta_actual()
        if not pregunta:
            return False

        es_correcta = (opcion_elegida == pregunta["correcta"])
        
        self.respuestas_usuario.append({
            "id": pregunta["id"],
            "tema": pregunta["tema"],
            "seleccion": opcion_elegida,
            "correcta": es_correcta,
            "retroalimentacion": pregunta.get("retroalimentacion", f"Debes repasar {pregunta['tema']}.")
        })
        
        self.indice_actual += 1
        return self.indice_actual >= len(self.preguntas) # Retorna True si terminó

    def generar_reporte_pdf(self):
        if not os.path.exists("reportes"):
            os.makedirs("reportes")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Resultados de Admisión", ln=1, align='C')
        pdf.ln(10)

        # Datos Estudiante
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"Estudiante: {self.estudiante['nombre']}", ln=1)
        pdf.cell(0, 10, txt=f"Grado Aspirado: {self.estudiante['grado']}", ln=1)
        pdf.cell(0, 10, txt=f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
        pdf.cell(0, 10, txt=f"Hora: {datetime.now().strftime('%H:%M')}", ln=1)
        pdf.ln(10)

        # Resultados
        nota = sum(1 for r in self.respuestas_usuario if r["correcta"])
        total = len(self.respuestas_usuario)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=f"Nota Final: {nota} / {total}", ln=1)
        
        # Tabla de detalles
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(90, 10, "Tema", 1)
        pdf.cell(30, 10, "Estado", 1)
        pdf.cell(70, 10, "Recomendación", 1)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        temas_a_revisar = set()

        for resp in self.respuestas_usuario:
            estado = "Correcto" if resp["correcta"] else "Incorrecto"
            recom = "-" if resp["correcta"] else "Estudiar tema"
            
            # Color texto (Verde si bien, Rojo si mal)
            if resp["correcta"]:
                pdf.set_text_color(0, 150, 0)
            else:
                pdf.set_text_color(200, 0, 0)
                temas_a_revisar.add(resp["tema"])

            pdf.cell(90, 10, resp["tema"], 1)
            pdf.cell(30, 10, estado, 1)
            pdf.cell(70, 10, recom, 1)
            pdf.ln()

        pdf.set_text_color(0, 0, 0) # Reset color

        # Resumen final de temas
        if temas_a_revisar:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Plan de mejora sugerido:", ln=1)
            pdf.set_font("Arial", size=11)
            for tema in temas_a_revisar:
                pdf.cell(0, 10, f"- Reforzar ejercicios de: {tema}", ln=1)

        nombre_archivo = f"reportes/Reporte_{self.estudiante['nombre'].replace(' ', '_')}.pdf"
        pdf.output(nombre_archivo)
        return nombre_archivo