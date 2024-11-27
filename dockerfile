# Usa una imagen base de Python 3.12.7
FROM python:3.12.7-slim

# Instala wkhtmltopdf y otras dependencias necesarias
RUN apt-get update && \
    apt-get install -y wkhtmltopdf && \
    apt-get clean

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Establece la variable de entorno para wkhtmltopdf
ENV PATH="/usr/local/bin/wkhtmltopdf:${PATH}"

# Exponer el puerto que usará uvicorn
EXPOSE 3000

# Comando para ejecutar tu aplicación con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]