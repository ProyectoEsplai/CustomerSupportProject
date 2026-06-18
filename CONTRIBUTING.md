# Guía de Contribución y Flujo de Trabajo

Este documento establece las normativas para contribuir al proyecto y proporciona una referencia técnica para el uso de Git y GitHub, diseñada para homologar los procesos del equipo.

## 1. Convenciones del Proyecto

### Nomenclatura de Ramas
Toda nueva rama debe crearse a partir de `main` (o la rama principal de desarrollo) y seguir una estructura categorizada:
`tipo/nombre-descriptivo`

Tipos permitidos:
* `feat/`: Desarrollo de nuevas características o funcionalidades.
* `fix/`: Corrección de errores o bugs.
* `docs/`: Creación o modificación de documentación.
* `refactor/`: Reestructuración de código existente sin alterar su comportamiento externo.
* `test/`: Adición o modificación de pruebas.

*Ejemplo:* `feat/autenticacion-usuarios` o `fix/desbordamiento-buffer`

### Convenciones de Commits
Los mensajes de commit deben ser concisos, estar escritos en tiempo presente y describir exactamente la modificación. Se emplea la estructura de *Conventional Commits*:
`tipo: descripción breve del cambio`

*Ejemplo:* `feat: agregar endpoint para registro` o `fix: corregir error de concurrencia en la base de datos`

### Flujo de Trabajo Principal
1. La rama `main` está protegida. Ningún cambio se aplica directamente sobre ella.
2. Todo desarrollo se aísla en una rama secundaria.
3. La integración de código a `main` se realiza exclusivamente mediante un *Pull Request* (PR).
4. El PR requiere revisión de código (Code Review) y aprobación de al menos un miembro del equipo antes de ejecutar el *merge*.

---

## 2. Guía Técnica de Git y GitHub

Esta sección detalla el ciclo de vida estándar para la gestión del control de versiones.

### 2.1. Clonar el repositorio
Para descargar una copia local del proyecto desde GitHub:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_DIRECTORIO>
```

### 2.2. Crear y cambiar de rama
Antes de modificar el código, es imperativo actualizar la rama principal y crear una rama de trabajo independiente:
```bash
# Cambiar a la rama principal
git checkout main

# Descargar las últimas actualizaciones del servidor
git pull origin main

# Crear y cambiar inmediatamente a la nueva rama
git checkout -b <tipo/nombre-de-la-rama>
```

### 2.3. Registrar los cambios (Add y Commit)
Una vez modificado el código, los archivos deben prepararse (staging) y confirmarse en el historial local:
```bash
# Verificar el estado de los archivos modificados
git status

# Añadir archivos específicos al área de preparación
git add <nombre_del_archivo>
# O añadir todos los archivos modificados en el directorio actual
git add .

# Confirmar los cambios con el mensaje reglamentario
git commit -m "tipo: descripción de los cambios"
```

### 2.4. Subir la rama al servidor (Push)
Para enviar la rama local y sus commits al repositorio remoto en GitHub:
```bash
git push origin <tipo/nombre-de-la-rama>
```

### 2.5. Crear un Pull Request (PR)
1. Acceda a la interfaz web del repositorio en GitHub.
2. GitHub mostrará un banner indicando los cambios recientes en su rama junto con un botón **Compare & pull request**. Haga clic en él.
3. Complete el título (siguiendo la convención de commits) y añada una descripción técnica de los cambios introducidos y el problema que resuelven.
4. Haga clic en **Create pull request**.

### 2.6. Sincronizar el entorno local (Pull)
Para actualizar su copia local con los cambios que otros desarrolladores han integrado en la rama principal:
```bash
git checkout main
git pull origin main
```

### 2.7. Actualizar una rama de trabajo (Merge de actualización)
Si la rama `main` ha recibido actualizaciones críticas mientras usted trabaja en su rama secundaria, debe integrar esos cambios para evitar conflictos futuros:
```bash
# Estando dentro de su rama de trabajo
git merge main
```
*Nota sobre Conflictos: Si Git detecta modificaciones superpuestas en las mismas líneas de código, el proceso se pausará marcando un conflicto. Deberá abrir los archivos afectados, seleccionar manualmente el código correcto, guardar los cambios, ejecutar `git add <archivo>` y finalizar el proceso ejecutando `git commit`.*
