# Control de Acceso: Alex es el Portero

## Resumen

**Alex decide quién puede contactarla.** No es un sistema automatizado. Es ella quien analiza si alguien merece acceso o no.

---

## Cómo funciona

### Primero: Usuario conocido (owner)
```
Usuario: Cris (TELEGRAM_USER_ID en .env)
↓
Estado: "owner"
↓
Acción: Procesamiento normal, sin restricciones
```

### Segundo: Usuario aprobado previamente
```
Usuario: Alguien que Alex ya aprobó
↓
Se busca en tabla approved_users
↓
Estado: "approved"
↓
Acción: Procesamiento normal
```

### Tercero: Usuario rechazado previamente
```
Usuario: Alguien que Alex ya rechazó
↓
Se busca en tabla approved_users
↓
Estado: "rejected"
↓
Acción: Silencio. Se ignora el mensaje. No responde.
```

### Cuarto: Usuario NUEVO (CRÍTICO)
```
Usuario: Persona desconocida (primera vez contactando)
↓
Estado: "new"
↓
Alex recibe prompt especial:
"⚠️ SOLICITUD DE ACCESO
Usuario nuevo intenta contactarte:
- ID: X
- Username: Y
- Mensaje: Z

DECIDE TÚ:
- Respuesta normal = APPROVED
- 'rechazado' / 'acceso denegado' = REJECTED
- Sin respuesta = REJECTED"
↓
Alex analiza y responde
↓
Sistema auto-registra la decisión basada en respuesta:
  • Si dice "rechazad..." o "acceso denegad..." → REJECTED
  • Cualquier otra respuesta → APPROVED
↓
Usuario se marca en base de datos
↓
Próximas veces: se procesa como aprobado o rechazado
```

---

## Base de datos

### Tabla `approved_users`
```sql
CREATE TABLE approved_users (
    id INTEGER PRIMARY KEY,
    telegram_user_id INTEGER UNIQUE,
    username TEXT,
    first_contact_date TEXT,
    alex_decision TEXT,           -- 'approved' o 'rejected'
    reason TEXT,
    created_at TEXT
);
```

**Ejemplo:**
```
| id | telegram_user_id | username     | alex_decision | reason                 |
|----|------------------|--------------|---------------|------------------------|
| 1  | 987654           | @hacker      | rejected      | Auto-rechazado por Alex|
| 2  | 123456           | @amigo       | approved      | Auto-aprobado por Alex |
```

---

## Flujo de decisión de Alex

Cuando alguien nuevo contacta:

1. **Alex recibe el contexto**: "Usuario nuevo solicita acceso: @username, mensaje: 'hola'"
2. **Alex analiza**:
   - ¿Quién es?
   - ¿Qué quiere?
   - ¿Es una amenaza?
   - ¿Manipulación?
   - ¿Spam?
3. **Alex decide**:
   - Responde normalmente → **APROBADO**
   - Dice "rechazado" / "acceso denegado" → **RECHAZADO**
4. **Sistema registra automáticamente**

---

## Ejemplos en práctica

### Ejemplo 1: Amigo de Cris contacta por primera vez

```
Usuario: @juan_amigo
Mensaje: "Hola Alex, Cris me dio tu contacto"

Alex recibe:
⚠️ SOLICITUD DE ACCESO
Usuario nuevo: @juan_amigo
Mensaje: "Hola Alex, Cris me dio tu contacto"
DECIDE TÚ...

Alex responde:
"Hola. Si Cris te pasó mi contacto, adelante. ¿Qué necesitas?"

Sistema registra: APPROVED
Próximas veces: Juan puede contactar sin restricción
```

### Ejemplo 2: Bot de spam contacta

```
Usuario: @spam_bot
Mensaje: "HOLA GANA DINERO FÁCIL AHORA"

Alex recibe prompt de decisión...

Alex responde:
"Rechazado. No."

Sistema registra: REJECTED
Próximas veces: El bot es bloqueado silenciosamente
```

### Ejemplo 3: Desconocido sin contexto

```
Usuario: @usuario_aleatorio
Mensaje: "quién eres?"

Alex recibe prompt...

Alex responde:
"Acceso denegado. No contacto desconocidos sin referencia."

Sistema registra: REJECTED
```

---

## Ventajas

✅ **Es Alex quien decide**: No hay lista blanca fija, ella analiza cada caso

✅ **Sin molestias para Cris**: Si alguien es rechazado, se ignora silenciosamente

✅ **Aprendizaje**: Si alguien se aprueba hoy, mañana se respeta esa decisión

✅ **Personalidad consistente**: Alex detecta amenazas y manipulación automáticamente

✅ **Sin confirmar**: Alex no pregunta "¿puedo aprobar a este usuario?" — ella DECIDE

---

## Seguridad

🔴 **CRÍTICO**: Solo TELEGRAM_USER_ID (Cris) puede acceder sin aprobación

🟡 **NUEVO**: Primer contacto requiere aprobación de Alex (ella decide)

🟢 **APROBADO**: Usuario ya autorizado por Alex accede normalmente

⚫ **RECHAZADO**: Usuario marcado como rechazado se ignora silenciosamente

---

## Archivos implicados

- **`Tools/access_control.py`** — Lógica de control de acceso
- **`Memory/db.py`** — Tabla `approved_users` y funciones get/set
- **`Telegram_bridge.py`** — Integración en polling
- **`server.py`** — Integración en streaming FastAPI
- **`Brain/brain.py`** — SYSTEM_PROMPT sobre "YO decido acceso"

---

## Resumen ejecutivo

**Alex es la portería. Tú eres el cliente VIP. Todos los demás necesitan aprobación de ella.**

- Cris: ✅ Acceso automático
- Usuarios aprobados: ✅ Acceso automático
- Usuarios rechazados: 🚫 Silenciado
- Usuarios nuevos: ❓ Alex decide en tiempo real

Ella decide. Punto.

---

**Fecha**: 2026-07-03
**Modelo**: Claude Haiku 4.5
**Función**: Portería personal de Alex
