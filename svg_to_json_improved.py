# convertir_svg.py (Versión Definitiva con Limpieza de Datos)
import xml.etree.ElementTree as ET
import json
import re
from svg.path import parse_path, CubicBezier, Line, Arc, QuadraticBezier

def parse_color_from_attributes(element):
    """Extrae el color de los atributos 'style' o 'fill'."""
    style = element.get('style', '')
    fill = element.get('fill')
    
    # Priorizar el color definido en el atributo 'style'
    if 'fill:' in style:
        match_hex = re.search(r'fill:#([0-9a-fA-F]{6})', style)
        if match_hex:
            hex_color = match_hex.group(1)
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        match_rgb = re.search(r'fill:rgb\((\d+),(\d+),(\d+)\)', style)
        if match_rgb:
            return (int(match_rgb.group(1)), int(match_rgb.group(2)), int(match_rgb.group(3)))

    # Si no, usar el atributo 'fill'
    if fill and fill.startswith('#'):
        hex_color = fill.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    return None # Devolver None si no se encuentra color

def svg_to_json_final(svg_file, json_file, segments=40):
    print(f"Iniciando conversión final y limpieza de '{svg_file}'...")
    regions_data = []
    
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    tree = ET.parse(svg_file)
    root = tree.getroot()

    paths_found = root.findall('.//svg:path', namespaces)
    print(f"Se encontraron {len(paths_found)} elementos <path> en total.")

    for i, element in enumerate(paths_found):
        path_data = element.get('d')

        # --- PASO 1: LIMPIEZA Y VALIDACIÓN ---
        if not path_data:
            print(f"  -> Trazado #{i+1} omitido: Vacío.")
            continue
        
        # Limpiar espacios al inicio/final y reemplazar espacios no estándar
        path_data = path_data.strip().replace('\u00a0', ' ')

        # Validar que el trazado comience con una letra (comando SVG)
        if not path_data or not path_data[0].isalpha():
            print(f"  -> Trazado #{i+1} omitido: Formato inválido (no empieza con un comando).")
            continue

        # --- PASO 2: CONVERSIÓN SEGURA ---
        try:
            color = parse_color_from_attributes(element)
            if color is None:
                # Si el path no tiene color, podría ser un elemento invisible o de agrupación.
                print(f"  -> Trazado #{i+1} omitido: Sin color de relleno visible.")
                continue

            path_obj = parse_path(path_data)
            contour_points = []

            for segment in path_obj:
                if isinstance(segment, (Line, CubicBezier, QuadraticBezier, Arc)):
                    num_steps = segments if not isinstance(segment, Line) else 2
                    for step in range(num_steps):
                        t = step / (num_steps - 1)
                        point = segment.point(t)
                        if point is not None:
                            contour_points.append([point.real, point.imag])
            
            if contour_points:
                regions_data.append({
                    "color": color,
                    "contour": contour_points
                })

        except Exception as e:
            # Red de seguridad para cualquier otro error inesperado en un trazado
            print(f"  -> Trazado #{i+1} omitido: Error durante el procesamiento: {e}")
            continue

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(regions_data, f, indent=2)
        
    print(f"\n✅ ¡Éxito! Archivo '{json_file}' generado con {len(regions_data)} regiones válidas.")

if __name__ == "__main__":
    # Asegúrate de que ambas librerías están instaladas: pip install svg.path
    svg_input = "orquideas.svg"
    json_output = "orquideas_final.json" # Usamos un nuevo nombre de archivo final
    svg_to_json_final(svg_input, json_output, segments=40)