import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

def obtener_minuto_partido(texto_minuto):
    """Extrae el minuto actual del partido del texto"""
    if not texto_minuto:
        return None
    
    # Buscar patrones como "65'" o "90'+3"
    match = re.search(r'(\d+)', texto_minuto)
    if match:
        return int(match.group(1))
    return None

def scrape_partidos_un_gol_live():
    """
    Scrapea partidos en vivo de Primatips 1X2 del día actual
    Detecta partidos con exactamente 1 gol después del minuto 60
    """
    try:
        # URL de Primatips del día actual
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        url = f"https://es.primatips.com/tips/{fecha_hoy}"
        
        print(f"\n🔍 Escaneando {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar partidos en vivo (clase 'lv' para live)
        partidos_live = soup.find_all('a', class_='game')
        
        partidos_detectados = []
        
        for partido in partidos_live:
            try:
                # Verificar si está en vivo
                resultado = partido.find('span', class_='res')
                if not resultado or 'lv' not in resultado.get('class', []):
                    continue
                
                # Extraer minuto
                minuto_elemento = resultado.find('span', class_='lvs')
                if not minuto_elemento:
                    continue
                
                minuto_texto = minuto_elemento.get_text(strip=True)
                minuto = obtener_minuto_partido(minuto_texto)
                
                if not minuto or minuto < 60:
                    continue
                
                # Extraer resultado actual
                goles_elementos = resultado.find_all('span', class_='l')
                if len(goles_elementos) < 2:
                    continue
                
                goles_casa = int(goles_elementos[0].get_text(strip=True) or 0)
                goles_visitante = int(goles_elementos[1].get_text(strip=True) or 0)
                
                total_goles = goles_casa + goles_visitante
                
                # Solo detectar si hay exactamente 1 gol
                if total_goles != 1:
                    continue
                
                # Extraer equipos
                equipos = partido.find('span', class_='nms')
                if not equipos:
                    continue
                
                nombres = equipos.find_all('span', class_='nm')
                if len(nombres) < 2:
                    continue
                
                equipo_casa = nombres[0].get_text(strip=True)
                equipo_visitante = nombres[1].get_text(strip=True)
                
                # Extraer hora y liga
                hora = partido.find('span', class_='tm')
                hora_texto = hora.get_text(strip=True) if hora else ''
                
                liga = partido.find('span', class_='cn')
                liga_texto = liga.get_text(strip=True) if liga else ''
                
                # Obtener nombre completo de la liga
                liga_completa = partido.find('span', class_='fl')
                if liga_completa:
                    img = liga_completa.find('img')
                    if img and img.get('title'):
                        liga_texto = img.get('title')
                
                # Extraer cuotas
                cuotas = partido.find_all('span', class_='o')
                cuota_casa = cuotas[0].get_text(strip=True) if len(cuotas) > 0 else ''
                cuota_empate = cuotas[1].get_text(strip=True) if len(cuotas) > 1 else ''
                cuota_visitante = cuotas[2].get_text(strip=True) if len(cuotas) > 2 else ''
                
                # Extraer probabilidades
                probs = partido.find_all('span', class_='t')
                prob_casa = probs[0].get_text(strip=True) if len(probs) > 0 else ''
                prob_empate = probs[1].get_text(strip=True) if len(probs) > 1 else ''
                prob_visitante = probs[2].get_text(strip=True) if len(probs) > 2 else ''
                
                # Extraer tip
                tip_elem = partido.find('span', class_='tip')
                tip = tip_elem.get_text(strip=True) if tip_elem else ''
                
                # Crear registro del partido
                partido_info = {
                    'fecha': fecha_hoy,
                    'hora': hora_texto,
                    'liga': liga_texto,
                    'equipo_casa': equipo_casa,
                    'equipo_visitante': equipo_visitante,
                    'goles_casa': goles_casa,
                    'goles_visitante': goles_visitante,
                    'minuto': minuto,
                    'cuota_casa': cuota_casa,
                    'cuota_empate': cuota_empate,
                    'cuota_visitante': cuota_visitante,
                    'prob_casa': prob_casa,
                    'prob_empate': prob_empate,
                    'prob_visitante': prob_visitante,
                    'tip': tip,
                    'hora_deteccion': datetime.now().strftime('%H:%M:%S'),
                    'estado': 'DETECTADO',
                    'goles_finales_casa': None,
                    'goles_finales_visitante': None,
                    'supero_1_5': None
                }
                
                partidos_detectados.append(partido_info)
                print(f"✅ DETECTADO: {equipo_casa} {goles_casa}-{goles_visitante} {equipo_visitante} (min {minuto})")
                
            except Exception as e:
                print(f"⚠️ Error procesando partido: {e}")
                continue
        
        # Cargar partidos existentes
        archivo_json = 'data/partidos_un_gol_detectados.json'
        partidos_guardados = {'partidos': [], 'total_partidos': 0}
        
        if os.path.exists(archivo_json):
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    partidos_guardados = json.load(f)
            except:
                pass
        
        # Agregar solo partidos nuevos (evitar duplicados)
        for partido_nuevo in partidos_detectados:
            # Verificar si ya existe por equipos y hora
            existe = False
            for partido_existente in partidos_guardados['partidos']:
                if (partido_existente['equipo_casa'] == partido_nuevo['equipo_casa'] and 
                    partido_existente['equipo_visitante'] == partido_nuevo['equipo_visitante'] and
                    partido_existente['fecha'] == partido_nuevo['fecha']):
                    existe = True
                    break
            
            if not existe:
                partidos_guardados['partidos'].append(partido_nuevo)
        
        # Actualizar información
        partidos_guardados['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        partidos_guardados['total_partidos'] = len(partidos_guardados['partidos'])
        
        # Guardar archivo JSON
        os.makedirs('data', exist_ok=True)
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(partidos_guardados, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Total partidos detectados: {len(partidos_detectados)}")
        print(f"💾 Total en base de datos: {partidos_guardados['total_partidos']}")
        
        return {
            'exito': True,
            'nuevos_detectados': len(partidos_detectados),
            'total_guardados': partidos_guardados['total_partidos'],
            'partidos': partidos_detectados
        }
        
    except Exception as e:
        print(f"❌ Error en scraping: {e}")
        return {
            'exito': False,
            'error': str(e),
            'nuevos_detectados': 0,
            'total_guardados': 0,
            'partidos': []
        }

def actualizar_resultados_finales():
    """
    Verifica los partidos detectados que ya finalizaron
    y actualiza si superaron los 1.5 goles
    """
    archivo_json = 'data/partidos_un_gol_detectados.json'
    
    if not os.path.exists(archivo_json):
        return {'actualizados': 0}
    
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        url = f"https://es.primatips.com/tips/{fecha_hoy}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        partidos_pagina = soup.find_all('a', class_='game')
        
        actualizados = 0
        
        for partido_guardado in datos['partidos']:
            if partido_guardado.get('supero_1_5') is not None:
                continue  # Ya fue actualizado
            
            # Buscar el partido en la página
            for partido_web in partidos_pagina:
                try:
                    equipos = partido_web.find('span', class_='nms')
                    if not equipos:
                        continue
                    
                    nombres = equipos.find_all('span', class_='nm')
                    if len(nombres) < 2:
                        continue
                    
                    equipo_casa = nombres[0].get_text(strip=True)
                    equipo_visitante = nombres[1].get_text(strip=True)
                    
                    if (equipo_casa == partido_guardado['equipo_casa'] and
                        equipo_visitante == partido_guardado['equipo_visitante']):
                        
                        # Verificar si el partido finalizó
                        resultado = partido_web.find('span', class_='res')
                        if resultado and 'rsl' in resultado.get('class', []):
                            # Partido finalizado
                            goles = resultado.find_all('span', class_='r')
                            if len(goles) >= 2:
                                goles_casa_final = int(goles[0].get_text(strip=True) or 0)
                                goles_visitante_final = int(goles[1].get_text(strip=True) or 0)
                                total_final = goles_casa_final + goles_visitante_final
                                
                                partido_guardado['goles_finales_casa'] = goles_casa_final
                                partido_guardado['goles_finales_visitante'] = goles_visitante_final
                                partido_guardado['supero_1_5'] = total_final > 1
                                partido_guardado['estado'] = 'FINALIZADO'
                                actualizados += 1
                                
                                print(f"✅ Actualizado: {equipo_casa} {goles_casa_final}-{goles_visitante_final} {equipo_visitante} | +1.5: {'SÍ' if total_final > 1 else 'NO'}")
                        
                        break
                        
                except Exception as e:
                    continue
        
        # Guardar cambios
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        return {'actualizados': actualizados}
        
    except Exception as e:
        print(f"❌ Error actualizando resultados: {e}")
        return {'actualizados': 0, 'error': str(e)}

def obtener_partidos_detectados():
    """Lee el archivo JSON con los partidos detectados"""
    archivo_json = 'data/partidos_un_gol_detectados.json'
    
    if not os.path.exists(archivo_json):
        return {
            'ultima_actualizacion': None,
            'total_partidos': 0,
            'partidos': [],
            'estadisticas': {
                'finalizados': 0,
                'supero_1_5': 0,
                'no_supero_1_5': 0,
                'en_vivo': 0
            }
        }
    
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Calcular estadísticas
        finalizados = sum(1 for p in datos['partidos'] if p.get('estado') == 'FINALIZADO')
        supero = sum(1 for p in datos['partidos'] if p.get('supero_1_5') == True)
        no_supero = sum(1 for p in datos['partidos'] if p.get('supero_1_5') == False)
        en_vivo = datos['total_partidos'] - finalizados
        
        datos['estadisticas'] = {
            'finalizados': finalizados,
            'supero_1_5': supero,
            'no_supero_1_5': no_supero,
            'en_vivo': en_vivo
        }
        
        return datos
    except Exception as e:
        print(f"Error leyendo JSON: {e}")
        return {
            'ultima_actualizacion': None,
            'total_partidos': 0,
            'partidos': [],
            'estadisticas': {
                'finalizados': 0,
                'supero_1_5': 0,
                'no_supero_1_5': 0,
                'en_vivo': 0
            }
        }

def limpiar_partidos_detectados():
    """Limpia el archivo JSON de partidos detectados"""
    archivo_json = 'data/partidos_un_gol_detectados.json'
    
    datos_vacios = {
        'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_partidos': 0,
        'partidos': [],
        'estadisticas': {
            'finalizados': 0,
            'supero_1_5': 0,
            'no_supero_1_5': 0,
            'en_vivo': 0
        }
    }
    
    try:
        os.makedirs('data', exist_ok=True)
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_vacios, f, ensure_ascii=False, indent=2)
        return {'exito': True}
    except Exception as e:
        return {'exito': False, 'error': str(e)}

if __name__ == '__main__':
    print("🚨 Iniciando detector de partidos con 1 gol (60+ min)...")
    resultado = scrape_partidos_un_gol_live()
    print(f"\n✅ Scraping completado. Nuevos: {resultado['nuevos_detectados']}")
    
    print("\n🔄 Actualizando resultados finales...")
    actualizacion = actualizar_resultados_finales()
    print(f"✅ Actualizados: {actualizacion.get('actualizados', 0)} partidos")
