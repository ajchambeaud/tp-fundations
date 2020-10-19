# TP Fundations

## Dataset

Se selecciono para el trabajo el dataset "Book-Crossing: User review ratings" tomado de https://www.kaggle.com/

https://www.kaggle.com/ruchi798/bookcrossing-dataset

La base original contiene 278,858 usuarios (anonimizados pero con información demográfica) que brindan 1,149,780 calificaciones (explícitas / implícitas) alrededor de 271,379 libros.

## Estructura del proyecto.

El sistema consiste en en 3 containers de docker orquestados con docker-compose.

### database

Se utilizo postgres:12 como container de base usando un bash script para crear la estructura de datos inicial.

### raw-data

En este directorio se incluyen los archivos de datos crudos. El mismo sera utilizado como volumen para el container de data-etl.

### data-etl

Este container corre un script de python encargado de procesar e importar los datos al la base de datos. Si ocurre un error al intentar conectarse a la base, el proceso esta preparado para reintentar cada 10 segundos.

Los datos del csv original son curados (existían algunos registros repetidos que rompen la integridad de los datos, algunos errores en ids, etc).
De la información demográfica se extrajo unicamente el país.

Se intento importar los datos usando instrucciones SQL INSERT, pero por cuestiones de performance finalmente el proceso se realizó usando la utilidad de postgres copy_from generando un buffer en memoria como fuente de datos.

### data-server

Este container consiste en un servicio python encargado de atender y procesar las consultas contra la base de datos. Se expone una API GraphQL que puede ser accedida desde el browser a través de la interfaz grafica GraphiQL.

Se utilizó el framework fastapi junto con la librería graphene para generar el servicio.

## Instrucciones

1)

Desde el directorio del proyecto, comprobar que exista una carpeta db-data que sera utilizada como volumen para el container de postgresql.
La misma debe encontrarse vacia.
Es posible utilizar otro directorio como volumen, modificando el archivo docker-compose.yml (linea 20).

2)

Correr desde el directorio del proyecto el comando

```
docker-compose up
```

comprobar que los tres procesos finalicen su ejecución correctamente. Al final del proceso de ETL se debería ver un mensaje similar al siguiente:

```
etl_1         | Attempting to import data to database.
etl_1         | Importing 274251 users...
etl_1         | Importing 271375 books...
etl_1         | Importing 1149715 ratings...
etl_1         | ETL Finished.
```

3) Conectarse al servicio web

Desde un navegador web dirigirse a la url http://localhost:8000/.

La interfaz grafica del cliente de GraphQL GraphiQL permite acceder a los datos de forma sencilla y navegar la documentación de las consultas disponibles.

## Consultas

Las siguientes consultas estan disponibles

### Obtener lista de los 10 países con más usuarios.

```
{
 getCountriesWithMoreUsers {
   country
   numberOfUsers
 }
}
```

### Obtener lista de los 10 países con más calificaciones realizadas.

```
{
 getCountriesWithMoreRatings {
   country
   numberOfRatings
 }
}
```

### Obtener lista de los 10 autores más calificados.

```
{
 getMoreRatedAuthors {
   author,
   numberOfRatings
 }
}
```

### Obtener lista de los 10 libros más calificados.

```
{
 getMoreRatedBooks {
   book,
   author,
   numberOfRatings
 }
}
```

### Obtener lista de los 10 libros mejor calificados.

```
{
 getBestRatedBooks {
   book,
   averageRating
 }
}
```

### Obtener lista de los 10 libros más calificados por país.

```
{
 getMoreRatedBooksByCountry (country: "argentina") {
   book,
   author,
   numberOfRatings
 }
}
```