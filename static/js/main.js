/**
 * LexNum - Script principal del cliente
 * ======================================
 *
 * Maneja la conversión en tiempo real de números a texto y
 * el procesamiento de archivos Excel en el lado del cliente.
 *
 * @author Omar Gabriel Salvatierra Garcia
 * @organization Órgano de Fiscalización Superior del Estado de Tlaxcala
 */

// =========================================================
// CONFIGURACIÓN
// =========================================================
const CONFIG = {
    endpoints: {
        convertirTexto: "/convertir_texto",
        convertirExcel: "/convertir_excel"
    },
    messages: {
        processing: "Procesando…",
        downloading: "Generando archivo…",
        success: "Archivo generado y descargado.",
        errorNetwork: "Error de conexión. Por favor intente nuevamente.",
        errorConversion: "Error al convertir.",
        errorProcessing: "Error al procesar el archivo."
    },
    debounceDelay: 300, // ms de retraso para debounce
};

// =========================================================
// ELEMENTOS DEL DOM
// =========================================================
const elementos = {
    inputNumero: null,
    resultadoTexto: null,
    spinner: null,
    excelForm: null,
    statusMessage: null
};

// =========================================================
// UTILIDADES
// =========================================================

/**
 * Implementación de debounce para limitar llamadas a funciones.
 *
 * @param {Function} func - Función a ejecutar
 * @param {number} wait - Tiempo de espera en ms
 * @returns {Function} Función con debounce aplicado
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Muestra u oculta el spinner de carga.
 *
 * @param {boolean} mostrar - True para mostrar, false para ocultar
 */
function toggleSpinner(mostrar) {
    if (elementos.spinner) {
        elementos.spinner.hidden = !mostrar;
    }
}

/**
 * Actualiza el mensaje de estado.
 *
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de mensaje: 'info', 'success', 'error'
 */
function actualizarStatus(mensaje, tipo = 'info') {
    if (elementos.statusMessage) {
        elementos.statusMessage.textContent = mensaje;
        elementos.statusMessage.className = `status status-${tipo}`;
    }
}

// =========================================================
// CONVERSIÓN DE TEXTO EN TIEMPO REAL
// =========================================================

/**
 * Convierte un número a texto llamando al endpoint del servidor.
 *
 * @param {string} numero - Número a convertir
 */
async function convertirNumeroATexto(numero) {
    // Limpiar resultado previo
    if (elementos.resultadoTexto) {
        elementos.resultadoTexto.textContent = "";
    }

    // Si no hay número, no hacer nada
    if (!numero || numero.trim() === "") {
        return;
    }

    toggleSpinner(true);

    try {
        const response = await fetch(CONFIG.endpoints.convertirTexto, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ numero })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (elementos.resultadoTexto) {
            elementos.resultadoTexto.textContent = data.texto || CONFIG.messages.errorConversion;
        }

    } catch (error) {
        console.error("Error en conversión:", error);
        if (elementos.resultadoTexto) {
            elementos.resultadoTexto.textContent = CONFIG.messages.errorNetwork;
        }
    } finally {
        toggleSpinner(false);
    }
}

// Crear versión con debounce de la función
const convertirNumeroDebounced = debounce(convertirNumeroATexto, CONFIG.debounceDelay);

/**
 * Manejador del evento input del campo de número.
 */
function handleNumeroInput(event) {
    const numero = event.target.value.trim();
    convertirNumeroDebounced(numero);
}

// =========================================================
// PROCESAMIENTO DE ARCHIVOS EXCEL
// =========================================================

/**
 * Descarga un blob como archivo.
 *
 * @param {Blob} blob - Blob a descargar
 * @param {string} filename - Nombre del archivo
 */
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.style.display = "none";

    document.body.appendChild(link);
    link.click();

    // Limpiar
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Procesa el archivo Excel y descarga el resultado.
 *
 * @param {Event} event - Evento de submit del formulario
 */
async function procesarExcel(event) {
    event.preventDefault();

    actualizarStatus(CONFIG.messages.processing, 'info');

    try {
        const formData = new FormData(event.target);
        const response = await fetch(CONFIG.endpoints.convertirExcel, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            // Intentar parsear error JSON
            let errorMessage = CONFIG.messages.errorProcessing;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch {
                // Si no es JSON, usar mensaje por defecto
            }

            actualizarStatus(errorMessage, 'error');
            return;
        }

        // Descargar archivo
        actualizarStatus(CONFIG.messages.downloading, 'info');
        const blob = await response.blob();
        downloadBlob(blob, "resultado_lexnum.xlsx");

        actualizarStatus(CONFIG.messages.success, 'success');

        // Limpiar formulario después de 2 segundos
        setTimeout(() => {
            event.target.reset();
            actualizarStatus('', 'info');
        }, 2000);

    } catch (error) {
        console.error("Error procesando Excel:", error);
        actualizarStatus(CONFIG.messages.errorNetwork, 'error');
    }
}

// =========================================================
// INICIALIZACIÓN
// =========================================================

/**
 * Inicializa la aplicación cuando el DOM está listo.
 */
function inicializarApp() {
    // Obtener referencias a elementos del DOM
    elementos.inputNumero = document.getElementById("numero");
    elementos.resultadoTexto = document.getElementById("resultadoTexto");
    elementos.spinner = document.getElementById("spinner");
    elementos.excelForm = document.getElementById("excelForm");
    elementos.statusMessage = document.getElementById("statusMessage");

    // Agregar event listeners
    if (elementos.inputNumero) {
        elementos.inputNumero.addEventListener("input", handleNumeroInput);
    }

    if (elementos.excelForm) {
        elementos.excelForm.addEventListener("submit", procesarExcel);
    }

    console.log("LexNum inicializado correctamente");
}

// Inicializar cuando el DOM esté listo
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", inicializarApp);
} else {
    // DOM ya está listo
    inicializarApp();
}
