import pygame
import sys
import os

# --- CONSTANTES DE DISEÑO ---
ANCHO, ALTO = 1000, 750
C_FONDO = (245, 245, 245)
C_BOTON = (70, 130, 180)       # Azul estandar
C_BOTON_SEL = (0, 150, 100)    # Verde para selección
C_HOVER = (100, 180, 255)      # Azul claro
C_TEXTO = (50, 50, 50)
C_BLANCO = (255, 255, 255)
C_NEGRO = (0, 0, 0)

class InterfazGrafica:
    def __init__(self, gestor_logica):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Prueba de admisión Liceo Los Ángeles")
        self.gestor = gestor_logica
        
    # --- CARGA DE SONIDOS ---
        try:
            ruta_sonido = os.path.join("archivos", "sonido.wav")
            self.sonido_click = pygame.mixer.Sound(ruta_sonido)
            self.sonido_click.set_volume(0.5) # Volumen al 50%
        except:
            print("Advertencia: No se encontró 'sonido.wav' en la carpeta archivos.")
            self.sonido_click = None # Para evitar errores si falta

        # Fuentes
        self.fuente = pygame.font.SysFont("Arial", 30)
        self.fuente_peq = pygame.font.SysFont("Arial", 22)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Estado
        self.estado = "MENU" # MENU, EXAMEN, FINAL
        self.nombre_input = ""
        self.grado_seleccionado = None
        self.mensaje_final = ""
        
        # Botones de Opción (A, B, C, D) para el Examen
        y_pos = 630
        ancho_btn = 180
        espacio = 50 # Espacio entre botones

        inicio_x = 65

        self.rect_botones_examen = {
            "A": pygame.Rect(inicio_x, y_pos, ancho_btn, 60),
            "B": pygame.Rect(inicio_x + (ancho_btn + espacio), y_pos, ancho_btn, 60),
            "C": pygame.Rect(inicio_x + (ancho_btn + espacio)*2, y_pos, ancho_btn, 60),
            "D": pygame.Rect(inicio_x + (ancho_btn + espacio)*3, y_pos, ancho_btn, 60)
        }

        # Botones de Selección de Grado para el Menú
        # Keys deben coincidir con las claves del JSON
        y_f1 = 420
        y_f2 = 480     
        
        self.rect_botones_grado = {
            # Fila 1
            "Grado 1": pygame.Rect(260, y_f1, 80, 40),
            "Grado 2": pygame.Rect(360, y_f1, 80, 40),
            "Grado 3": pygame.Rect(460, y_f1, 80, 40),
            "Grado 4": pygame.Rect(560, y_f1, 80, 40),
            "Grado 5": pygame.Rect(660, y_f1, 80, 40),
            
            # Fila 2
            "Grado 6": pygame.Rect(310, y_f2, 80, 40),
            "Grado 7": pygame.Rect(410, y_f2, 80, 40),
            "Grado 8": pygame.Rect(510, y_f2, 80, 40),
            "Grado 9": pygame.Rect(610, y_f2, 80, 40)
        }

    def escalar_imagen(self, imagen):
        # Ajusta la imagen a max 700x400 manteniendo proporción
        w, h = imagen.get_size()
        max_w, max_h = 950, 543
        ratio = min(max_w/w, max_h/h)
        nuevo_tamano = (int(w*ratio), int(h*ratio))
        return pygame.transform.smoothscale(imagen, nuevo_tamano)

    def bucle_principal(self):
        reloj = pygame.time.Clock()
        ejecutando = True

        while ejecutando:
            reloj.tick(30) # 30 FPS
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                
                self.procesar_eventos(evento)

            self.dibujar_pantalla()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def procesar_eventos(self, evento):
        # --- LÓGICA DEL MENÚ ---
        if self.estado == "MENU":
            # 1. Clics para seleccionar grado
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    for nombre_grado, rect in self.rect_botones_grado.items():
                        if rect.collidepoint(evento.pos):
                            self.grado_seleccionado = nombre_grado

            # 2. Teclado para nombre e inicio
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Solo inicia si hay nombre Y grado seleccionado
                    if len(self.nombre_input) > 0 and self.grado_seleccionado:
                        self.gestor.registrar_estudiante(self.nombre_input, self.grado_seleccionado)
                        
                        if self.gestor.preguntas:
                            self.estado = "EXAMEN"
                        else:
                            print(f"Advertencia: No hay preguntas cargadas para {self.grado_seleccionado}")
                
                elif evento.key == pygame.K_BACKSPACE:
                    self.nombre_input = self.nombre_input[:-1]
                else:
                    if len(self.nombre_input) < 25:
                        self.nombre_input += evento.unicode

        # --- LÓGICA DEL EXAMEN ---
        elif self.estado == "EXAMEN":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    for op, rect in self.rect_botones_examen.items():
                        if rect.collidepoint(evento.pos):
                            # Sonido
                            if self.sonido_click:
                                self.sonido_click.play()
                            termino = self.gestor.procesar_respuesta(op)
                            if termino:
                                self.estado = "FINAL"
                                try:
                                    ruta_pdf = self.gestor.generar_reporte_pdf()
                                    self.mensaje_final = f"Nombre del archivo: {os.path.basename(ruta_pdf)}"
                                except Exception as e:
                                    self.mensaje_final = f"Error generando PDF: {str(e)}"

    def dibujar_pantalla(self):
        self.pantalla.fill(C_FONDO)

        # ---------------------------------------------------------
        # PANTALLA: MENÚ DE INICIO
        # ---------------------------------------------------------
        if self.estado == "MENU":
            # Título
            txt_titulo = self.fuente_grande.render("Bienvenido a la Prueba de Admisión", True, C_TEXTO)
            rect_tit = txt_titulo.get_rect(center=(ANCHO//2, 100))
            self.pantalla.blit(txt_titulo, rect_tit)

            # --- Sección Nombre ---
            txt_label_nombre = self.fuente.render("Ingrese nombre del aspirante:", True, C_TEXTO)
            self.pantalla.blit(txt_label_nombre, (150, 180))
            
            # Caja de texto
            caja_x = (ANCHO - 600) // 2
            pygame.draw.rect(self.pantalla, C_BLANCO, (caja_x, 220, 600, 50))
            pygame.draw.rect(self.pantalla, C_BOTON, (caja_x, 220, 600, 50), 2)
            
            txt_nombre = self.fuente.render(self.nombre_input, True, C_TEXTO)
            self.pantalla.blit(txt_nombre, (caja_x + 10, 230))

            # --- Sección Grados ---
            txt_label_grado = self.fuente.render("Seleccione el Grado al que aspira:", True, C_TEXTO)
            rect_lbl_grado = txt_label_grado.get_rect(center=(ANCHO//2, 370))
            self.pantalla.blit(txt_label_grado, rect_lbl_grado)

            # IMPORTANTE: Capturamos posición del mouse para el efecto hover
            mouse_pos = pygame.mouse.get_pos()

            for nombre_grado, rect in self.rect_botones_grado.items():
                # Lógica de Color: 1. Seleccionado -> 2. Hover -> 3. Normal
                if self.grado_seleccionado == nombre_grado:
                    color_fondo = C_BOTON_SEL    # Verde (Seleccionado)
                    color_borde = C_NEGRO
                elif rect.collidepoint(mouse_pos):
                    color_fondo = C_HOVER        # Azul Claro (Hover recuperado)
                    color_borde = C_HOVER
                else:
                    color_fondo = C_BOTON        # Azul Oscuro (Normal)
                    color_borde = C_BOTON
                
                # Dibujar botón
                pygame.draw.rect(self.pantalla, color_fondo, rect, border_radius=6)
                pygame.draw.rect(self.pantalla, color_borde, rect, 2, border_radius=6)
                
                # Texto corto (ej: "Grado 1" -> "1°")
                lbl = nombre_grado.replace("Grado ", "") + "°"
                txt_btn = self.fuente.render(lbl, True, C_BLANCO)
                rect_txt = txt_btn.get_rect(center=rect.center)
                self.pantalla.blit(txt_btn, rect_txt)
            # --- INSTRUCCIÓN FINAL (ABAJO CENTRADA) ---
                if self.nombre_input and self.grado_seleccionado:
                    info = "Presiona ENTER para empezar"  # <--- Texto exacto solicitado
                    color_info = C_BOTON_SEL
                else:
                    info = "Complete nombre y seleccione grado"
                    color_info = (150, 100, 100)

                txt_inst = self.fuente_peq.render(info, True, color_info)
                # Posición Y=680 (Cerca del fondo 750)
                rect_inst = txt_inst.get_rect(center=(ANCHO//2, 680))
                self.pantalla.blit(txt_inst, rect_inst)

        # ---------------------------------------------------------
        # PANTALLA: EXAMEN
        # ---------------------------------------------------------
        elif self.estado == "EXAMEN":
            pregunta = self.gestor.obtener_pregunta_actual()
            
            if pregunta:
                if getattr(sys, 'frozen', False):
                    # Si es un ejecutable (.exe), la ruta base es donde está el archivo .exe
                    base_path = os.path.dirname(sys.executable)
                else:
                    # Si estamos en desarrollo (.py), la ruta base es donde está el script
                    base_path = os.path.dirname(os.path.abspath(__file__))

                # ---------------------------------------------------------
                # 2. PREPARAR LA RUTA DE LA IMAGEN
                # ---------------------------------------------------------
                ruta_del_json = pregunta["imagen"]
                
                # Limpiamos la ruta:
                # a. Reemplazamos las barras según el sistema operativo (Win/Mac/Linux)
                ruta_del_json = ruta_del_json.replace("\\", os.sep).replace("/", os.sep)
                
                # b. Quitamos barras al inicio si las hay (ej: "\archivos" -> "archivos")
                #    Esto es vital, porque si tiene barra al inicio, os.path.join falla.
                ruta_del_json = ruta_del_json.lstrip(os.sep)

                # c. Unimos la ruta base + la ruta del json
                ruta_final_absoluta = os.path.join(base_path, ruta_del_json)

                # ---------------------------------------------------------
                # 3. CARGAR LA IMAGEN
                # ---------------------------------------------------------
                try:
                    # Imprimimos para depurar (solo se ve si lanzas con consola)
                    # print(f"Intentando cargar: {ruta_final_absoluta}")
                    
                    img = pygame.image.load(ruta_final_absoluta)
                    img_esc = self.escalar_imagen(img)
                    x_pos = (ANCHO - img_esc.get_width()) // 2
                    self.pantalla.blit(img_esc, (x_pos, 50))
                    
                except Exception as e:
                    # Fallback visual si no encuentra la imagen
                    # Esto ayuda a saber qué ruta intentó buscar
                    print(f"Error cargando imagen: {e}") 
                    pygame.draw.rect(self.pantalla, (0, 0, 0), (50, 50, 700, 400)) # C_NEGRO directo por si acaso
                    
                    # Mostramos en pantalla qué ruta falló (útil para corregir)
                    mensaje_error = f"No se halló: {ruta_del_json}"
                    txt_err = self.fuente_peq.render(mensaje_error, True, (255, 255, 255))
                    self.pantalla.blit(txt_err, (60, 200))

                # 2. Botones de opciones (A, B, C, D)
                mouse_pos = pygame.mouse.get_pos()
                
                for op, rect in self.rect_botones_examen.items():
                    # Efecto Hover
                    color = C_HOVER if rect.collidepoint(mouse_pos) else C_BOTON
                    
                    pygame.draw.rect(self.pantalla, color, rect, border_radius=10)
                    pygame.draw.rect(self.pantalla, C_NEGRO, rect, 2, border_radius=10)
                    
                    txt = self.fuente.render(op, True, C_BLANCO)
                    rect_txt = txt.get_rect(center=rect.center)
                    self.pantalla.blit(txt, rect_txt)
                
                # Indicador de progreso
                idx = self.gestor.indice_actual + 1
                total = len(self.gestor.preguntas)
                txt_prog = self.fuente_peq.render(f"Pregunta {idx} de {total}", True, C_TEXTO)
                self.pantalla.blit(txt_prog, (20, 20))

        # ---------------------------------------------------------
        # PANTALLA: FINAL
        # ---------------------------------------------------------
        elif self.estado == "FINAL":
            txt_fin = self.fuente_grande.render("¡Examen Finalizado!", True, C_BOTON)
            rect_fin = txt_fin.get_rect(center=(ANCHO//2, ALTO//2 - 40))
            self.pantalla.blit(txt_fin, rect_fin)

            txt_fin = self.fuente_grande.render("Encontrarás el reporte en la carpeta DESCARGAS", True, C_BOTON)
            rect_fin = txt_fin.get_rect(center=(ANCHO//2, ALTO//2 + 40))
            self.pantalla.blit(txt_fin, rect_fin)
            
            txt_ruta = self.fuente_peq.render(self.mensaje_final, True, C_BOTON_SEL)
            rect_ruta = txt_ruta.get_rect(center=(ANCHO//2, ALTO//2 + 100))
            self.pantalla.blit(txt_ruta, rect_ruta)
            
            txt_salir = self.fuente_peq.render("Avísale a la persona encargada de tu prueba", True, C_TEXTO)
            rect_salir = txt_salir.get_rect(center=(ANCHO//2, ALTO - 100))
            self.pantalla.blit(txt_salir, rect_salir)

            txt_salir = self.fuente_peq.render("Cierra la ventana para salir", True, C_TEXTO)
            rect_salir = txt_salir.get_rect(center=(ANCHO//2, ALTO - 50))
            self.pantalla.blit(txt_salir, rect_salir)