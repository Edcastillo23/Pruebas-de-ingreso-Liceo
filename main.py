from funciones import GestorExamen
from interfaz import InterfazGrafica

def main():
    # 1. Instanciamos la lógica (Cargamos datos)
    logica = GestorExamen()
    
    # 2. Instanciamos la GUI y le pasamos la lógica
    gui = InterfazGrafica(logica)
    
    # 3. Arrancamos
    gui.bucle_principal()

if __name__ == "__main__":
    main()