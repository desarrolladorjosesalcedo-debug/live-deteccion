# 🚨 Detector de Partidos con 1 Gol (Minuto 60+)

Sistema de monitoreo automático que detecta partidos en vivo de la sección 1X2 de Primatips que:
- Han superado el **minuto 60**
- Tienen exactamente **1 gol** (1-0 o 0-1)
- Hace seguimiento de cuántos superaron **+1.5 goles** al finalizar

## 🎯 Características

- ✅ **Scraping automático** cada 5 minutos
- ✅ **Sin base de datos** - Almacenamiento temporal en JSON
- ✅ **Interfaz en tiempo real** con auto-refresh
- ✅ **Detección inteligente** de partidos en vivo
- ✅ **Seguimiento de resultados finales** (+1.5 goles)
- ✅ **Actualización manual** disponible
- ✅ **Preparado para Render** (despliegue en la nube)

## 📁 Estructura del Proyecto

```
deteccion-live/
├── app.py                              # Aplicación Flask principal
├── scrape_un_gol_live.py              # Script de scraping
├── templates/
│   └── detector_un_gol.html           # Interfaz web
├── data/
│   └── partidos_un_gol_detectados.json # Base de datos JSON
├── requirements.txt                    # Dependencias Python
├── Procfile                           # Configuración Render/Heroku
├── runtime.txt                        # Versión de Python
├── render.yaml                        # Configuración Render
└── README.md                          # Este archivo
```

## 🚀 Instalación Local

### 1. Clonar o descargar el proyecto

```powershell
cd c:\programacion\deteccion-live
```

### 2. Crear entorno virtual (opcional pero recomendado)

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```powershell
python app.py
```

### 5. Acceder a la aplicación

Abre tu navegador en: `http://localhost:2000`

## 🌐 Despliegue en Render

### Opción 1: Deploy Automático desde GitHub

1. **Sube el proyecto a GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - Detector 1 Gol Live"
   git remote add origin https://github.com/TU_USUARIO/deteccion-live.git
   git push -u origin main
   ```

2. **Ve a [Render.com](https://render.com)** y crea una cuenta

3. **Crea un nuevo Web Service**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Selecciona el repositorio `deteccion-live`

4. **Configuración del servicio**
   - **Name:** `deteccion-live` (o el que prefieras)
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Plan:** Free (o el que prefieras)

5. **Deploy**
   - Click en "Create Web Service"
   - Render automáticamente desplegará tu aplicación

### Opción 2: Deploy Manual

1. En Render Dashboard, click en "New +" → "Web Service"
2. Selecciona "Deploy from source control"
3. Sigue los pasos de la Opción 1

### URL de tu aplicación

Una vez desplegado, Render te dará una URL como:
```
https://deteccion-live.onrender.com
```

## 📊 ¿Cómo Funciona?

### 1. Detección Automática

El scheduler ejecuta cada 5 minutos:
```python
scrape_partidos_un_gol_live()
```

### 2. Criterios de Detección

- **Partido en vivo** (clase `lv`)
- **Minuto ≥ 60**
- **Total de goles = 1** (1-0 o 0-1)

### 3. Seguimiento de Resultados

```python
actualizar_resultados_finales()
```

Verifica partidos finalizados y actualiza:
- Resultado final
- Si superó +1.5 goles (más de 1 gol total)

### 4. Almacenamiento

```json
{
  "ultima_actualizacion": "2026-01-13 15:30:45",
  "total_partidos": 5,
  "estadisticas": {
    "finalizados": 3,
    "supero_1_5": 2,
    "no_supero_1_5": 1,
    "en_vivo": 2
  },
  "partidos": [...]
}
```

## 🎨 Interfaz Web

### Panel de Estadísticas

- **Partidos Detectados**: Total acumulado
- **Finalizados**: Partidos terminados
- **Superaron +1.5**: Tuvieron más de 1 gol al final
- **No Superaron +1.5**: Se mantuvieron en 1 gol
- **En Vivo**: Aún en curso

### Controles

- **🏠 Inicio**: Volver a página principal
- **🔄 Actualizar Ahora**: Scraping inmediato
- **📊 Actualizar Resultados**: Verificar finalizados
- **🧹 Limpiar Todo**: Eliminar historial

### Cards de Partidos

Cada partido muestra:
- Estado (DETECTADO / FINALIZADO)
- Equipos y resultado
- Minuto de detección
- Liga y hora
- Cuotas 1X2
- Tip sugerido
- **Resultado final y si superó +1.5** (si finalizó)

## 🔧 Configuración Avanzada

### Cambiar frecuencia de scraping

En [app.py](app.py#L22):
```python
scheduler.add_job(
    func=ejecutar_scraping_un_gol,
    trigger=IntervalTrigger(minutes=5),  # Cambiar aquí
    ...
)
```

### Cambiar minuto mínimo

En [scrape_un_gol_live.py](scrape_un_gol_live.py#L56):
```python
if not minuto or minuto < 60:  # Cambiar 60 por el deseado
    continue
```

### Cambiar criterio de goles

En [scrape_un_gol_live.py](scrape_un_gol_live.py#L70):
```python
if total_goles != 1:  # Cambiar condición
    continue
```

## 🐛 Troubleshooting

### El scheduler no funciona en Render

✅ **Solución**: Ya está configurado con `before_first_request` para iniciar automáticamente.

### Error de timeout en Render

✅ **Solución**: Ya configurado en Procfile con `--timeout 120`

### No se crean los directorios

✅ **Solución**: El código crea automáticamente `data/` si no existe:
```python
os.makedirs('data', exist_ok=True)
```

### Error al scraping

- Verifica que Primatips esté accesible
- Revisa los logs en Render Dashboard
- El scraping continúa aunque falle una vez

## 📝 Endpoints API

### GET /
Página principal con botón al detector

### GET /detector-un-gol
Interfaz del detector

### GET /api/detector/un-gol
Obtener partidos detectados (JSON)

### POST /api/detector/actualizar
Ejecutar scraping manual

### POST /api/detector/actualizar-resultados
Actualizar solo resultados finales

### POST /api/detector/limpiar
Limpiar todos los partidos

### GET /health
Health check para Render

## 📈 Monitoreo en Render

### Ver Logs

1. Ve a tu servicio en Render Dashboard
2. Click en "Logs"
3. Verás el output del scraping cada 5 minutos

### Métricas

Render muestra automáticamente:
- CPU usage
- Memory usage
- Request count
- Response times

## ⚠️ Limitaciones

- **Sin persistencia**: Los datos se pierden al reiniciar
- **Sin autenticación**: El sistema es público
- **Rate limiting**: Depende de Primatips
- **Free tier Render**: Se duerme después de 15 min sin uso

## 🎯 Mejoras Futuras

- [ ] Base de datos PostgreSQL para persistencia
- [ ] Notificaciones por email/Telegram
- [ ] Exportar a Excel/CSV
- [ ] Gráficos estadísticos
- [ ] Filtros avanzados (liga, cuota, etc.)
- [ ] Análisis de efectividad histórica
- [ ] API REST completa
- [ ] Autenticación de usuarios

## 👨‍💻 Autor

**Jose Salcedo**

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## 🆘 Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Verifica los logs en Render
3. Comprueba que todas las dependencias estén instaladas
4. Asegúrate de que Primatips esté accesible

---

**¡Listo para detectar partidos! 🚀⚽**
