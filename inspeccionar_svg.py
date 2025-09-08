# inspeccionar_svg.py
import xml.etree.ElementTree as ET

def inspect_svg_paths(svg_file):
    """
    Lee un archivo SVG e imprime los datos 'd' de cada elemento <path> que encuentra.
    """
    print(f"--- Inspeccionando los trazados del archivo: {svg_file} ---\n")
    
    try:
        # Los namespaces son necesarios para que el parser encuentre los elementos SVG
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        tree = ET.parse(svg_file)
        root = tree.getroot()
        
        # Busca todos los elementos <path> en cualquier parte del archivo
        paths_found = root.findall('.//svg:path', namespaces)
        
        if not paths_found:
            print("Resultado: No se encontraron elementos <path> en el archivo.")
            return

        print(f"Resultado: Se encontraron {len(paths_found)} elementos <path>. Sus datos ('d') son:\n")
        
        for i, path_element in enumerate(paths_found):
            path_data = path_element.get('d', '--- ATRIBUTO "d" NO ENCONTRADO ---')
            print(f"Trazado #{i+1}:")
            print(f"{path_data}\n")
            
    except ET.ParseError as e:
        print(f"🛑 ERROR: El archivo '{svg_file}' no es un XML válido. Error de parseo: {e}")
    except Exception as e:
        print(f"🛑 Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    inspect_svg_paths("orquideas.svg")