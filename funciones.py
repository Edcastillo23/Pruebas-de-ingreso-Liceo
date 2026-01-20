import json
import os
from fpdf import FPDF
from datetime import datetime
from pathlib import Path
import os

class GestorExamen:
    def __init__(self):
        self.banco_completo = self._cargar_banco()
        self.preguntas = []
        self.respuestas_usuario = []
        self.estudiante = {"nombre": "", "grado": ""}
        self.indice_actual = 0


    def _cargar_banco(self):

        
        ruta = os.path.join("archivos", 'banco_preguntas.json')
        if not os.path.exists(ruta):
            return {}
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)

    def registrar_estudiante(self, nombre, grado):
        self.estudiante["nombre"] = nombre
        self.estudiante["grado"] = grado
        if grado in self.banco_completo:
            self.preguntas = self.banco_completo[grado]
        else:
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
        
        # Guardamos datos clave para el reporte
        self.respuestas_usuario.append({
            "id": pregunta["id"],
            "materia": pregunta.get("materia", "General"), 
            "tema": pregunta.get("tema", "Tema general"),
            "seleccion": opcion_elegida,
            "correcta": es_correcta
        })
        
        self.indice_actual += 1
        return self.indice_actual >= len(self.preguntas)

    def generar_reporte_pdf(self):
        # --- 1. PROCESAR DATOS (ESTADÍSTICAS Y RECOMENDACIONES) ---
        stats = {}
        # Usamos un diccionario de sets para evitar temas repetidos si fallan varias del mismo tema
        recomendaciones_por_materia = {} 

        # Inicializamos algunas materias para mantener orden (opcional)
        materias_orden = ["Matemáticas", "Lengua Castellana", "Naturales", "Sociales"]
        for m in materias_orden:
            stats[m] = {"total": 0, "bien": 0, "mal": 0}

        for resp in self.respuestas_usuario:
            materia = resp["materia"]
            tema = resp["tema"]
            
            # Inicializar materia si no existe en stats
            if materia not in stats:
                stats[materia] = {"total": 0, "bien": 0, "mal": 0}
            
            # Conteo
            stats[materia]["total"] += 1
            if resp["correcta"]:
                stats[materia]["bien"] += 1
            else:
                stats[materia]["mal"] += 1
                
                # AGREGAR A RECOMENDACIONES
                if materia not in recomendaciones_por_materia:
                    recomendaciones_por_materia[materia] = set()
                recomendaciones_por_materia[materia].add(tema)

        # --- 2. INICIO DEL PDF ---
        pdf = FPDF()
        pdf.add_page()
        
        # --- LOGO ---
        ruta_logo = os.path.join("archivos", "logo.png") 
        if os.path.exists(ruta_logo):
            pdf.image(ruta_logo, x=10, y=8, w=25)

        pdf.set_font("Arial", size=11)

        # Encabezado
        pdf.set_font("Arial", 'B', 16)
        pdf.ln(5)
        pdf.cell(0, 10, "Informe de Resultados - Admisión", ln=1, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=12)
        pdf.ln(5)
        pdf.cell(0, 8, f"Estudiante: {self.estudiante['nombre']}", ln=1)
        pdf.cell(0, 8, f"Grado al que aspira: {self.estudiante['grado']}", ln=1)
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=1)
        pdf.cell(0, 8, f"Hora: {datetime.now().strftime('%H:%M:%S')}", ln=1)
        pdf.ln(10)

        # --- 3. DIBUJAR LA TABLA ---
        w_mat = 50
        w_tot = 30
        w_corr = 25
        w_inc = 25
        w_porc = 30
        w_nota = 25
        h_fila = 10

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, "La siguiente tabla muestra el Resumen de Resultados por Materia:", ln=1)

        # Header Tabla
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        
        pdf.cell(w_mat, h_fila, "Materia", 1, 0, 'C', 1)
        pdf.cell(w_tot, h_fila, "Preguntas", 1, 0, 'C', 1)
        pdf.cell(w_corr, h_fila, "Bien", 1, 0, 'C', 1)
        pdf.cell(w_inc, h_fila, "Mal", 1, 0, 'C', 1)
        pdf.cell(w_porc, h_fila, "% Aprob.", 1, 0, 'C', 1)
        pdf.cell(w_nota, h_fila, "Nota", 1, 1, 'C', 1)

        # Cuerpo Tabla
        pdf.set_font("Arial", size=10)
        
        lista_materias = list(stats.keys())
        
        for materia in lista_materias:
            datos = stats[materia]
            if datos["total"] == 0: continue 

            porcentaje = (datos["bien"] / datos["total"]) * 100
            nota = (datos["bien"] / datos["total"]) * 5.0

            pdf.cell(w_mat, h_fila, materia, 1, 0, 'L')
            pdf.cell(w_tot, h_fila, str(datos["total"]), 1, 0, 'C')
            pdf.cell(w_corr, h_fila, str(datos["bien"]), 1, 0, 'C')
            pdf.cell(w_inc, h_fila, str(datos["mal"]), 1, 0, 'C')
            pdf.cell(w_porc, h_fila, f"{porcentaje:.1f}%", 1, 0, 'C')
            pdf.cell(w_nota, h_fila, f"{nota:.1f}", 1, 1, 'C')

        # --- 4. SECCIÓN RECOMENDACIONES ---
        pdf.ln(15) 
        
        if recomendaciones_por_materia:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Recomendaciones:", ln=1)
            
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 8, "Teniendo en cuenta el desempeño en cada materia, se recomienda practicar los siguientes temas:", ln=1)
            pdf.ln(2)

            for materia, temas_set in recomendaciones_por_materia.items():
                if not temas_set: continue 
                
                pdf.set_font("Arial", 'B', 12)
                pdf.set_text_color(0, 0, 100) 
                pdf.cell(0, 8, f"{materia}:", ln=1)
                
                pdf.set_font("Arial", size=11)
                pdf.set_text_color(0, 0, 0) 
                for tema in temas_set:
                    pdf.cell(10) 
                    pdf.cell(0, 6, f"{chr(149)} {tema}", ln=1)
                
                pdf.ln(3)
        else:
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 150, 0)
            pdf.cell(0, 10, "¡Excelente trabajo! No hay recomendaciones específicas.", ln=1, align='C')

        
        # A. Detectar carpeta de descargas del usuario actual
        ruta_descargas = Path.home() / "Downloads"
        
        # B. Limpiar nombre del estudiante para el archivo
        nombre_limpio = self.estudiante['nombre'].replace(" ", "_")
        
        # C. Crear nombre del archivo
        nombre_archivo = f"Resultado_{nombre_limpio}.pdf"
        
        # D. Unir carpeta descargas + nombre archivo
        ruta_completa = ruta_descargas / nombre_archivo
        
        # E. Convertir a string (necesario para fpdf)
        ruta_final_str = str(ruta_completa)
        
        try:
            pdf.output(ruta_final_str)
            print(f"Reporte guardado exitosamente en: {ruta_final_str}")
        except PermissionError:
            # Fallback por si el archivo está abierto o hay error de permisos
            print("Error: No se pudo guardar en Descargas (¿Archivo abierto?). Guardando en carpeta local.")
            ruta_final_str = f"Resultado_{nombre_limpio}.pdf"
            pdf.output(ruta_final_str)

        return ruta_final_str