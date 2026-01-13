from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from datetime import datetime
import scrape_un_gol_live

app = Flask(__name__)

# Configurar scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def ejecutar_scraping_un_gol():
    """Función que ejecuta el scraping automático"""
    print(f"\n{'='*60}")
    print(f"🤖 Scraping automático - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    resultado = scrape_un_gol_live.scrape_partidos_un_gol_live()
    
    if resultado['exito']:
        print(f"✅ Nuevos detectados: {resultado['nuevos_detectados']}")
        print(f"💾 Total guardados: {resultado['total_guardados']}")
        
        # Actualizar resultados finales
        actualizacion = scrape_un_gol_live.actualizar_resultados_finales()
        print(f"🔄 Partidos actualizados: {actualizacion.get('actualizados', 0)}")
    else:
        print(f"❌ Error: {resultado.get('error', 'Desconocido')}")
    
    print(f"{'='*60}\n")

# Programar scraping cada 5 minutos
scheduler.add_job(
    func=ejecutar_scraping_un_gol,
    trigger=IntervalTrigger(minutes=5),
    id='scraping_un_gol',
    name='Scraping Detector 1 Gol',
    replace_existing=True
)

# Ejecutar scraping inicial al arrancar (compatible con Flask 3.0+)
print("\n🚀 Ejecutando scraping inicial...")
ejecutar_scraping_un_gol()

@app.route('/')
def index():
    """Página principal"""
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Detección Live</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
            }
            h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .button {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 40px;
                border-radius: 10px;
                text-decoration: none;
                font-size: 1.3em;
                font-weight: bold;
                transition: all 0.3s;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .button:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
            }
            .info {
                margin-top: 30px;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 10px;
                text-align: left;
            }
            .info h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .info ul {
                list-style: none;
                padding-left: 0;
            }
            .info li {
                padding: 8px 0;
                color: #555;
            }
            .info li::before {
                content: "✅ ";
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 Sistema de Detección Live</h1>
            <p>Monitoreo automático de partidos en vivo</p>
            
            <a href="/detector-un-gol" class="button">
                🎯 Detector 1 Gol Live
            </a>
            
            <div class="info">
                <h3>📋 Características:</h3>
                <ul>
                    <li>Detección automática cada 5 minutos</li>
                    <li>Partidos con 1 gol después del minuto 60</li>
                    <li>Seguimiento de resultados finales</li>
                    <li>Estadísticas de partidos que superaron +1.5 goles</li>
                    <li>Interfaz en tiempo real</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/detector-un-gol')
def detector_un_gol():
    """Página del detector de 1 gol"""
    return render_template('detector_un_gol.html')

@app.route('/api/detector/un-gol')
def api_partidos_un_gol():
    """API que devuelve los partidos detectados"""
    datos = scrape_un_gol_live.obtener_partidos_detectados()
    return jsonify(datos)

@app.route('/api/detector/actualizar', methods=['POST'])
def api_actualizar():
    """API para ejecutar scraping manual"""
    resultado = scrape_un_gol_live.scrape_partidos_un_gol_live()
    
    # También actualizar resultados
    scrape_un_gol_live.actualizar_resultados_finales()
    
    return jsonify(resultado)

@app.route('/api/detector/actualizar-resultados', methods=['POST'])
def api_actualizar_resultados():
    """API para actualizar solo los resultados finales"""
    resultado = scrape_un_gol_live.actualizar_resultados_finales()
    return jsonify(resultado)

@app.route('/api/detector/limpiar', methods=['POST'])
def api_limpiar():
    """API para limpiar todos los partidos detectados"""
    resultado = scrape_un_gol_live.limpiar_partidos_detectados()
    return jsonify(resultado)

@app.route('/health')
def health():
    """Endpoint de salud para Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scheduler_running': scheduler.running
    })

# Cerrar scheduler limpiamente al terminar
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 2000))
    app.run(host='0.0.0.0', port=port, debug=False)
