# Lección 1

## Ejercicio 1: Instalación Docker

Se consiguió instalar correctamente Docker Desktop en Windows 10 luego de habilitar la creación de máquinas virtuales, instalar Ubuntu y finalmente, luego de descargar Docker para Windows. Para más información sobre el proceso, ver [aquí](https://docs.docker.com/desktop/windows/install/).

![docker](./Media/Screenshot1.PNG)

**IMPORTANTE**: No instalar Docker en Windows 10 sin antes haber activado WSL 2. Si se hace esto, se corre el riesgo de "brickear" la PC (Sucedió con mi laptop 😢)

---

## Ejercicio 2: Conexión con MySQL

Se consiguió instalar MySQL dentro de un contenedor de Docker, utilizando el siguiente comando:

```sh
docker run -it --network test_network -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=root123" -e "MYSQL_USER=test" -e "MYSQL_PASSWORD=test123" -e "MYSQL_DATABASE=test" mysql:5.7.35
```

Una vez el contenedor estaba corriendo, se conectó a la base de datos y se realizó un query simple utilizando DataGrip:

![MySQL](./Media/Screenshot2.PNG)

---

## Ejercicio 3: Docker Compose

Se ensambló un cluster de dos contenedores empleando Docker Compose: Un contenedor para Jupyter y otro contenedor para MySQL. Ambos contenedores se interconectaron entre si y se utilizaron para desarrollar notebooks de Python en un entorno totalmente aislado. El archivo YAML que se empleó como "blueprint" está contenido en este mismo repositorio y puede ejecutarse utilizando el comando:

```sh
docker-compose up
```

Una vez habilitado, se accesó a la IP especificada por el contenedor de Jupyter (127.0.0.1:8888) y se instaló el conector de MySQL y Pandas al colocar lo siguiente en una celda del notebook:

```python
!pip install mysql-connector-python pandas
```

Luego, se conectó a la base de datos desde Python. Para esto, se debe ir a buscar la IP interna del contenedor ("IPAddress") utilizando el siguiente comando:

```sh
docker inspect NOMBRE-CONTENEDOR-MYSQL
```

Con esta IP, se ensambla el siguiente comando (Luego del @) y se ejecuta.

```sh
from sqlalchemy import create_engine

source = create_engine('mysql+mysqlconnector://test:test123@172.19.0.3/test')
```

Finalmente se realizó un query a la base de datos y se desplegó en la forma de un Dataframe:

![Jupyter](./Media/Screenshot3.PNG)

