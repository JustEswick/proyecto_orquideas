import xml.etree.ElementTree as ET
import json
import re
from svg.path import parse_path, CubicBezier, Line, Arc, QuadraticBezier

# La función parse_color no necesita cambios
def parse_color(style_string):
    if not style_string:
        return (0, 0, 0)
    match = re.search(r'fill:#([0-9a-fA-F]{6})', style_string)
    if match:
        hex_color = match.group(1)
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    match = re.search(r'fill:rgb\((\d+),(\d+),(\d+)\)', style_string)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return (0, 0, 0)

def svg_to_json(svg_file, json_file, segments=40): # Aumentamos los segmentos por defecto
    print(f"Iniciando conversión de '{svg_file}' a JSON de alta calidad...")
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    tree = ET.parse(svg_file)
    root = tree.getroot()
    regions_data = []

    for path_element in root.findall('.//svg:path', namespace):
        path_data = path_element.get('d')
        style = path_element.get('style', '')
        fill = path_element.get('fill')
        color = parse_color(style) if 'fill' in style else parse_color(f'fill:{fill}')

        if not path_data:
            continue

        path_obj = parse_path(path_data)
        contour_points = []

        for segment in path_obj:
            if isinstance(segment, (Line, CubicBezier, QuadraticBezier, Arc)):
                num_steps = segments if not isinstance(segment, Line) else 2
                for i in range(num_steps):
                    t = i / (num_steps - 1)
                    point = segment.point(t)
                    contour_points.append([point.real, point.imag])
        
        if contour_points:
            regions_data.append({
                "color": color,
                "contour": contour_points
            })

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(regions_data, f, indent=2) # Usamos indent=2 para un archivo más compacto
        
    print(f"✅ ¡Éxito! Archivo '{json_file}' generado con {len(regions_data)} regiones y alta definición.")

if __name__ == "__main__":
    svg_input = "orquideas.svg"
    json_output = "orquideas_hq.json" # Guardamos con un nuevo nombre
    # Aumentamos los segmentos a 40 para curvas muy suaves
    svg_to_json(svg_input, json_output, segments=40)