from funciones import GestorExamen
from interfaz import InterfazGrafica
import sys
import os


if getattr(sys, 'frozen', False):
    #Buscar la ruta correcta cuando se ejecuta como .exe
    os.chdir(os.path.dirname(sys.executable))
else:
    # Si estamos en desarrollo (.py), la ruta base es donde está el script
    base_path = os.path.dirname(os.path.abspath(__file__))

def main():
    # 1. Instanciamos la lógica (Cargamos datos)
    logica = GestorExamen()
    
    # 2. Instanciamos la GUI y le pasamos la lógica
    gui = InterfazGrafica(logica)
    
    # 3. Arrancamos
    gui.bucle_principal()

if __name__ == "__main__":
    main()