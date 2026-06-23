# Calculadora de Valorización – Renta Fija

Herramienta Python que genera un archivo Excel (`.xlsx`) completo para valorizar instrumentos de **Renta Fija** (bonos bullet), calcular el **Precio de Mercado**, el **Precio Limpio** y la **TERA** (Tasa de Retorno Anual Efectiva).

---

## 📂 Archivos

| Archivo | Descripción |
|---------|-------------|
| `generar_calculadora_rf.py` | Script principal que genera el Excel |
| `Calculadora_RentaFija.xlsx` | Archivo Excel generado (se crea al ejecutar el script) |
| `requirements.txt` | Dependencias Python |
| `README.md` | Esta documentación |

---

## 🚀 Uso rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Generar el Excel
python generar_calculadora_rf.py
```

Abra `Calculadora_RentaFija.xlsx` en Excel o LibreOffice Calc y modifique las **celdas amarillas** de la hoja **Parámetros**.

---

## 📊 Estructura del Excel

### Hoja 1 – Parámetros

Contiene los inputs del usuario (celdas en amarillo):

| Campo | Descripción |
|-------|-------------|
| Monto Nominal (VN) | Valor par del bono |
| Tasa de Emisión (anual %) | Tasa nominal anual del cupón |
| Fecha de Emisión | Inicio del bono |
| Fecha de Vencimiento | Último pago (cupón + principal) |
| Frecuencia de Pago | 2 = semestral, 4 = trimestral, 12 = mensual |
| TIR de Mercado (anual %) | Yield de mercado para descontar flujos |
| Fecha de Valorización | Fecha en que se calcula el precio |
| Convención de días | 360 (30/360) o 365 (Act/365) |

### Hoja 2 – Flujos

Tabla generada automáticamente con fórmulas Excel:

| Columna | Contenido |
|---------|-----------|
| A | N° Cupón |
| B | Fecha de Pago |
| C | Días desde la Fecha de Valorización hasta la Fecha de Pago |
| D | Factor de Descuento = 1 / (1 + TIR_Mercado)^(días/base) |
| E | Amortización de Capital (solo en el último cupón – bono bullet) |
| F | Intereses = VN × TasaEmisión / Frecuencia |
| G | Flujo Total = E + F |
| H | Flujo Descontado = G × D |

Al pie de la tabla se muestra la **Suma de Flujos Descontados = Precio de Mercado**.

### Hoja 3 – Resultado

Resumen ejecutivo con los indicadores principales:

| Indicador | Descripción |
|-----------|-------------|
| **Precio de Mercado (Precio Sucio)** | Suma de todos los flujos descontados a TIR de mercado |
| **Interés Devengado** | Porción del cupón acumulada desde el último pago |
| **Precio Limpio** | Precio Sucio − Interés Devengado |
| **TIR de Mercado** | Input del usuario |
| **TIR por Período** | (1 + TIR_anual)^(1/Freq) − 1 |
| **TERA** | (1 + TIR_período)^Freq − 1 |
| **Rendimiento (%)** | TERA expresada en porcentaje |

---

## 📐 Marco Conceptual

### ¿Qué es el Precio de Mercado de un Bono?

El **Precio de Mercado** (o *Precio Sucio*) de un bono es el valor presente de todos los flujos futuros (cupones + amortización de capital), descontados a la **TIR de mercado** vigente en la fecha de valorización:

$$P = \sum_{i=1}^{n} \frac{C_i}{\left(1 + r\right)^{t_i}}$$

donde:

| Símbolo | Significado |
|---------|-------------|
| $P$ | Precio de Mercado (Precio Sucio) |
| $C_i$ | Flujo de caja en el período $i$ (cupón ± amortización) |
| $r$ | TIR de Mercado (tasa de descuento) |
| $t_i$ | Tiempo expresado en años (días / base) |

El **Precio Limpio** excluye el interés acumulado desde el último pago de cupón:

$$\text{Precio Limpio} = \text{Precio Sucio} - \text{Interés Devengado}$$

$$\text{Interés Devengado} = VN \times \frac{\text{TasaEmisión}}{\text{Freq}} \times \frac{\text{días desde último cupón}}{\text{Base}}$$

En los mercados secundarios, los bonos generalmente se cotizan por su **Precio Limpio**.

---

### ¿Qué es la TERA?

La **TERA** (*Tasa de Retorno Anual Efectiva*, equivalente a la *Yield to Maturity* en base efectiva anual) es el rendimiento anualizado que obtiene el inversionista si:

1. Compra el bono al **Precio de Mercado** calculado.
2. Lo mantiene hasta el **vencimiento**.
3. **Reinvierte** todos los cupones a la misma tasa.

> La TERA es la métrica estándar para comparar instrumentos con diferentes frecuencias de pago, plazos y tasas nominales, llevándolos a una única base anual efectiva.

#### Cálculo de la TERA

**Paso 1 – Tasa por período:**

$$\text{TIR}_{\text{período}} = \left(1 + \text{TIR}_{\text{anual}}\right)^{1/\text{Freq}} - 1$$

**Paso 2 – Anualización:**

$$\text{TERA} = \left(1 + \text{TIR}_{\text{período}}\right)^{\text{Freq}} - 1$$

Para una TIR anual **efectiva** (no nominal), la TERA coincide con la TIR. La distinción es relevante cuando la TIR de mercado se cotiza como tasa nominal.

#### Ejemplo numérico

| Parámetro | Valor |
|-----------|-------|
| TIR de mercado (anual) | 7,50% |
| Frecuencia | 2 (semestral) |
| TIR por período | (1 + 0,075)^(1/2) − 1 = **3,6822%** |
| TERA | (1 + 0,036822)^2 − 1 = **7,5000%** |

> Cuando la TIR se ingresa ya en base **anual efectiva**, la TERA resultante es idéntica a la TIR. Esto confirma la consistencia del cálculo.

#### Relación Precio–TERA (inversa)

- 📈 Precio **sube** → TERA **baja**
- 📉 Precio **baja** → TERA **sube**

La TERA personal del inversionista queda **fija** en el momento de la compra (precio pactado). Sin embargo, la **TERA de mercado** varía diariamente conforme cambia el precio de negociación en el mercado secundario.

---

## 🔧 Requisitos técnicos

- Python 3.8 o superior
- `openpyxl >= 3.1.0`
- `python-dateutil` (opcional, usado internamente para el cálculo de fechas de cupones)

```bash
pip install openpyxl>=3.1.0
```

---

## 📚 Referencias bibliográficas

- **Fabozzi, F. J.** (2000). *Fixed Income Mathematics: Analytical and Statistical Techniques* (4.ª ed.). McGraw-Hill. ISBN 978-0-07-135423-8.
  - Capítulo 2: Yield Measures, Spot Rates, and Forward Rates
  - Capítulo 4: Price Volatility and Duration

- **Jorion, P.** (2007). *Value at Risk: The New Benchmark for Managing Financial Risk* (3.ª ed.). McGraw-Hill. ISBN 978-0-07-146495-6.
  - Capítulo 6: Fixed Income Risk

- **Hull, J. C.** (2018). *Options, Futures, and Other Derivatives* (10.ª ed.). Pearson. ISBN 978-0-13-447208-8.
  - Capítulo 4: Interest Rates

- **CMF Chile** – *Norma de Carácter General N° 200 y modificaciones posteriores*: Valorización de instrumentos de renta fija a valor de mercado (*mark-to-market*). Disponible en: [https://www.cmfchile.cl](https://www.cmfchile.cl)

- **Banco Central de Chile** – Normas sobre tasas de interés y convenciones de días para instrumentos de renta fija en el mercado local. Disponible en: [https://www.bcentral.cl](https://www.bcentral.cl)

---

## 📝 Notas sobre convenciones de días

| Convención | Descripción | Uso típico |
|------------|-------------|-----------|
| **30/360** (Base 360) | Meses de 30 días, año de 360 días | Bonos corporativos en EEUU y Chile |
| **Act/365** (Base 365) | Días reales, año de 365 días | Bonos soberanos en UK y algunos mercados |
| **Act/360** | Días reales, año de 360 días | Tasas de corto plazo (LIBOR, depósitos) |
| **Act/Act** | Días reales / días reales del año | Bonos del Tesoro EEUU |

Esta calculadora usa la convención ingresada en la celda **"Convención de días"** (360 o 365).

---

*Desarrollado para fines educativos y de análisis de inversiones. No constituye asesoría financiera.*
