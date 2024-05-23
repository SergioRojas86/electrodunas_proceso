# Electrodunas Proceso

Bienvenidos al repositorio de **electrodunas_proceso**. Un proyecto realizado para la Universidad de los Andes en la Maestría en Inteligencia Analítica de Datos. Aquí encontrarán toda la información necesaria para entender y utilizar este proyecto. A continuación, se detallan las diferentes carpetas y archivos presentes en este repositorio. Haz clic en cada uno de los enlaces para navegar directamente a la carpeta correspondiente.

---

## Carpetas y Archivos

### [API](./API)
Encontrarás el código para el despliegue de un endpoint creado con Flask y desplegado a través de una instancia EC2 en AWS.

### [aws_lambda_function](./aws_lambda_function)
Código de la función lambda la cual es ejecutada por un trigger de S3 al detectar un archivo con extensión *.confirm* y ejecuta el código que se encuentra dentro de la instancia EC2. Se encuentra comprimido en .zip para una facil importación al servicio de AWS.

### [src](./src)
Es un pipeline encargado de verificar la estructura de los archivos suministrados y realizar la transformación de los datos para la creación de la base que va a recibir el modelo entrenado y finalmente ejecutando este mismo. Todo acerca del modelo utilizado lo puedes encontrar en este archivo [model.py](./src/model.py)

### [files_and_logs](./files_and_logs)
Se encuentra una muestra de los logs generados por el proceso.

### [main.py](./main.py)
Archivo principal de ejecución del pipeline.

# Despliegue
Para realizar el despliegue de la solución se necesita una instancia EC2, el tamaño de esta depende de la escalabilidad que se le desee dar a la información a procesar. El SO debe ser linux.
Como paso inicial debes asegurarte que la EC2 este preparada para el código a ejecutar, estos son los comandos principales:
```
> sudo yum update -y 
> sudo yum install git -y
> sudo yum install python3 -y
> sudo pip install Flask
> sudo pip install boto3
> sudo pip install scikit-learn
> sudo pip install gunicorn
> sudo amazon-linux-extras install nginx1.12 -y
> sudo yum install git -y
```
Una vez ejecutados las lineas ed comando anteriormente mencionadas, puedes clonar el repositorio.

Luego se debe crear el archivo /etc/systemd/system/myproject.service
```
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/home/ec2-user/electrodunas_proceso/API
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind unix:/home/ec2-user/electrodunas_proceso/API/myproject.sock -m 007 --umask 0007 run:app

[Install]
WantedBy=multi-user.target
```

```
> sudo systemctl daemon-reload
> sudo systemctl restart myprojec
> sudo systemctl status myproject
> sudo systemctl start myproject
> sudo systemctl enable myproject
```

Configurar NGINX editando el archivo /etc/nginx/nginx.conf o creando un archivo de configuración específico para tu sitio en /etc/nginx/conf.d/ colocando el dominio publico de tu instancia:
```
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
```
> sudo systemctl restart nginx
```

Una vez realizados estos pasos en la instancia, podemos crear la función lambda subiendo el zip que encontramos en [aws_lambda_function](./aws_lambda_function).

Y finalmente, crear los buckets especificados en el manual de usuario.

## Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactar a los creadores del proyecto a través de [correo electrónico](mailto:contacto@example.com):

- Sergio Rojas [s.rojasz@uniandes.edu.co](mailto:s.rojasz@uniandes.edu.co)
- Gloria Ramos [gm.ramos@uniandes.edu.co](mailto:gm.ramos@uniandes.edu.co)
- Eniver Pino [e.pinog@uniandes.edu.co](mailto:e.pinog@uniandes.edu.co)

---

Gracias por tu interés en **electrodunas_proceso**. ¡Esperamos que encuentres útil este proyecto!
