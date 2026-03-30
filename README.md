# Proyecto final - Airbnb Market Data Asia-Pacific

## Descripción del proyecto

En este proyecto se trabaja con dos datasets relacionados del mercado de Airbnb en Asia-Pacífico:

- `listings.csv`
- `past_rates.csv`

El objetivo es unir ambos conjuntos de datos para construir una base de datos más completa sobre alojamientos y evolución histórica de precios, que sirva como punto de partida para el análisis posterior.

## Datos
Dado el tamaño de los datasets originales y del dataset final transformado, no se han podido incluir en el repositorio de Github. En su lugar, se ha incluido una muestra representativa de los datos, que es la utilizada en el dashboard de Google Sheets, con el objetivo de facilitar la comprensión del análisis. 

---

## Datasets utilizados

### 1. listings.csv
Este archivo contiene información general de cada alojamiento, como por ejemplo tipo de listing, tipo de habitación, ubicación y otras características del anuncio.

### 2. past_rates.csv
Este archivo contiene información histórica relacionada con precios, ocupación, revenue y otras métricas temporales de cada alojamiento.

Ambos datasets comparten la columna `listing_id`, que es la utilizada para realizar la unión.

---

## Análisis previo de los datasets

### 1. Importación de librerías y preparación de carpetas
Se ha utilizado principalmente la librería `pandas` para la carga, revisión y unión de los datasets, además de `os` para comprobar la carpeta de trabajo y los archivos disponibles.

### 2. Comprobación de la carpeta de trabajo
Antes de cargar los archivos, se comprobó la ruta desde la que se estaba ejecutando el código y los archivos existentes dentro de la carpeta de datos para asegurarse de que Python estaba leyendo desde la ubicación correcta.

### 3. Carga de los datasets
Se cargaron los archivos `listings.csv` y `past_rates.csv`.

Como algunos registros daban problemas al leer el CSV, se utilizó `engine="python"` y `on_bad_lines="skip"` para evitar que errores puntuales impidieran trabajar con el conjunto de datos.

### 4. Revisión inicial de columnas y clave de unión
Se revisaron las dimensiones de ambos datasets y también sus columnas, para entender mejor su contenido y confirmar que la columna `listing_id` estaba presente en ambos.

Se comprobó cuántos `listing_id` únicos había en cada dataset para verificar que la unión tenía sentido:

- `listings.csv` contiene prácticamente un registro por alojamiento.
- `past_rates.csv` contiene varias filas por alojamiento, ya que recoge información histórica.

### 5. Homogeneización del tipo de dato
Antes de unir los datasets, se transformó la columna `listing_id` al mismo tipo de dato en ambos casos, ya que en uno de los archivos aparecía como numérica y en el otro como texto.

Esto fue necesario para poder hacer la unión correctamente.

### 6. Unión de los datasets
La unión se realizó mediante un `left join`, utilizando `past_rates` como tabla principal y `listings` como tabla secundaria.

De esta forma se mantuvieron todas las filas del histórico de precios y se añadieron las características del alojamiento correspondientes a cada `listing_id`.

### 7. Comprobación del merge
Se comprobó que no hubiera valores nulos en `listing_id` tras la unión. Se detectaron 12 registros sin correspondencia tras el merge, correspondientes a un único listing_id, lo que indica ausencia de información en el dataset de listings para ese alojamiento. Se decide mantenerlo en el dataset dado su poco impacto en el mismo (<0.01%).


### 8. Revisión inicial de valores nulos
Una vez creado el dataset final, se revisaron las columnas con mayor cantidad de valores nulos para identificar posibles problemas de calidad de datos y decidir más adelante qué variables mantener, transformar o eliminar. 

## Limpieza y transformación

### 1. Eliminación de columnas con alto porcentaje de nulos
Se aplicó un criterio de eliminación de variables con más del 80% de valores nulos.
cols_to_drop = null_percentage[null_percentage > 80].index

En este caso, únicamente una variable cumplía este criterio: 'instant_book'.

### 2. Conversión de la variable 'date'
Se realizó una revisión de los tipos de variables del dataset final mediante df.dtypes.
Se detectó que la variable date se encontraba en formato string, por lo que se convirtió a formato datetime para permitir análisis temporales:

df_final["date"] = pd.to_datetime(df_final["date"], errors="coerce")

### 3. Resolución de columnas duplicadas tras el merge
Tras el merge, se generaron columnas duplicadas con terminaciones _x e _y en las variables country, state y city.
Se comprobó que más del 99% de los valores coincidían y tan solo había diferencias en 12 filas, las cuales correspondían a valores nulos en _y.
Por tanto, se decide mantener columnas _x y eliminar columnas _y. 

df_final = df_final.drop(columns=["country_y", "state_y", "city_y"])

### 4. Renombrar las variables anteriores eliminando su terminación _x:
df_final = df_final.rename(columns={
    "country_x": "country",
    "state_x": "state",
    "city_x": "city"
})

### 5. Eliminar variables categóricas irrelevantes

- listing_id: nos ha servido para hacer el merge pero no aporta valor analítico al estudio, por lo que la eliminamos. 
- cover_photo_url: solo nos indica el link de las fotos de los alojamientos pero no aporta valor alguno, por lo que también se elimina
- host_id: solo es un indicador numérico pero no es útil para el análisis.

### 6. Agrupamos tipos de alojamiento menos comunes
Dado que comprobamos que existen muchos tipos diferentes de alojamiento, agrupamos los menos comunes y dejamos los 5 más frecuentes en una nueva variable (listing_type_grouped). De esta manera será más sencilla la interpretación de los resultados. 

### 7. Sustituimos valores nulos de variables categóricas por "Unknown"
Se revisaron las variables categóricas y se sustituyeron los valores nulos por “Unknown”. De esta forma se evita perder información al eliminar filas. Además, se comprobó previamente que las columnas existieran para evitar errores en el proceso.
### 8. Tratamiento de valores nulos en variables numéricas
Primero se analizó el porcentaje de valores nulos en las variables numéricas. Se eliminaron aquellas columnas con más de un 30% de valores faltantes, ya que su información se consideró poco fiable.
Para el resto de variables numéricas, los valores nulos se sustituyeron por la mediana, ya que permite mantener la distribución de los datos sin introducir sesgos importantes.
### 9. Revisión de duplicados
Por último, se comprobó si existían registros duplicados en el dataset. No se detectaron duplicados, por lo que no fue necesario realizar ninguna acción adicional en este sentido.

## Análisis descriptivo y estadístico

### 1. Variables numéricas

Analizamos las variables numéricas más significativas: 

- Capacidad del alojamiento (guests): tiene una media de 4,8, lo cual indica que los alojamientos están diseñados para grupos pequeños-medianos.
- Ocupación (occupancy): se aprecia que la ocupación es moderada, pues la media se sitúa en un 29% y el 75% de los alojamientos tiene una ocupación menor o igual al 52%.  
- Precio (rate_avg): la media es 117$, es un precio medio moderado y no tanto de lujo.
- Ingresos (revenue): la media de los ingresos por alojamiento son de 1072$, sin embargo el máximo se sitúa en 79.956$ y la desviación estándar es elevada. Por lo que hay una gran variabilidad entre los ingresos de los alojamientos y algunos generan ingresos muy superiores al resto. 
- Valoraciones (rating_overall): la valoración media es de 4,8, por lo que la mayoría de valoraciones suelen ser bastante positivas. 
- Días reservados (reserved_days): la media de días reservados es de aproximadamente 9 días al mes. De nuevo muestra una ocupación muy baja.
- Días vacíos/disponibles (vacant_days): la media es de 21,5 días disponibles (vacíos) al mes. Es una cifra muy elevada.

### 2. Variables categóricas

Analizamos las variables categóricas más significativas: 

- country: los países donde más alojamientos existen son Filipinas, Malasia, Australia y Corea del sur. 
- state: los dos estados con más alojamientos Airbnb son Manila y Bali.
- city: los valores son muy similares para todas las ciudades (aprox. 1%), lo cual indica que no hay ninguna ciudad que destaque a nivel de volumen de alojamientos. 
- listing_type: la oferta más abundante es la de alojamientos enteros (pisos, casas enteras, villas, etc.). La oferta del resto de tipos de alojamientos es minoritaria. 
- room_type: la gran mayoría (75%) de los alojamientos son viviendas enteras. El resto de alojamientos son minoritarios. 
- superhost: es una variable muy equilibrada, siendo ambos valores cercanos al 50%. 
- registration: aproximadamente el 82% de los alojamientos no tienen número de registro, lo cual podría indicar que existe un volumen importante de oferta sin regular. 
- professional management: prácticamente la totalidad de los alojamientos están gestionados por particulares (97,4%), y tan solo una minoría por profesionales (2,6%).
- cancellation_policy: más de la mitad de alojamientos disponen de políticas de cancelación firmes o moderadas, lo cual implica que pueden cancelar la reserva con reembolso total si lo hacen con diversos días de antelación a la fecha de entrada. El resto de políticas de cancelación son menos abundantes, con una proporción inferior al 20% del total. 
- currency: las monedas más utilizadas a la hora de indicar el precio de los alojamientos coinciden con los países donde más alojamientos Airbnb hay (PHP, MYR y AUD).

### 3. Análisis de relación entre variables categóricas
#### Superhost vs rate_avg
Comprobamos que el precio medio es algo superior cuando el gestor del alojamiento es superhost.
#### room_type vs rate_avg
Vemos grandes diferencias entre el precio de las casas enteras (media de 139$) y el resto de tipos de alojamientos: habitación de hotel (84$), habitación privada (56$), habitación compartida (29$).
#### listing_type vs rate_avg
Confirmamos que los alojamientos más caros son las villas, seguido de las casas enteras y los apartamentos. Los más económicos son los pisos y habitaciones compartidas. 
#### listing_type_grouped + superhost vs rate_avg
Comprobamos que no existen grandes diferencias en los precios medios de los alojamientos si el gestor de los mismos es superhost o no lo es. 
### 4. Correlación entre variables numéricas
#### Correlaciones altas entre todas las variables numéricas
Las correlaciones más altas, tanto positivas como negativas, corresponden principalmente a variables derivadas o complementarias (como días reservados vs disponibles), lo que refleja relaciones matemáticas más que dependencias reales entre variables.

#### Correlaciones con la variable rate_avg 
Se aprecia una relación positiva entre el precio medio y los ingresos, lo cual es lógico dado que ambas están directamente relacionadas.  
Existe también relación débil entre el precio medio y el número de habitaciones y baños. 
Por el contrario, se comprueba una relación ligeramente negativa entre la latitud y el precio medio. Esto podría indicar que cuando los alojamientos se ubican en determinadas zonas tienden a tener menor precio medio. 
Aparecen variables muy correlacionadas (TTM, L90D), pero en el fondo son el mismo precio en distintos horizontes temporales. Por eso no aportan valor adicional y no se consideran variables influyentes en el precio.
El resto de variables no parecen influir significativamente al precio medio de los alojamientos. 

## Visualización de datos

### Exclusión alojamientos precio medio>500
Se excluyen alojamientos que tengan precios medios superiores a 500$ para reducir el impacto de valores extremos en la visualización de los gráficos.

### 1. Histograma de precio
Inicialmente hemos generado un histograma sin limitar el precio medio de los alojamientos y hemos visto que existen valores extremos del precio medio que dificultan la lectura del gráfico. Por ello limitamos el precio medio, haciendo que solo consten en el gráfico los precios medios menores o iguales a 500. 
Podemos observar que los precios medios suelen situarse entre 30$ y 120$. Hay pocos alojamientos con precios medios mayores que 300$. 

### 2. Boxplot de precio según tipo de propiedad
Se observan diferencias claras en el precio según el tipo de propiedad, siendo las villas y las viviendas enteras las opciones más caras, mientras que las habitaciones privadas presentan precios significativamente más bajos. Además, todos los tipos muestran una alta variabilidad de precios incluso dentro del mismo tipo de propiedad.

### 3. Scatter número de habitaciones vs precio medio
No se observa una relación clara entre el número de habitaciones y el precio. Aunque parece existir una ligera tendencia creciente, se observa una alta dispersión de los precios medios. Por lo que para alojamientos con el mismo número de habitaciones se observan precios medios muy dispersos. Por ello no podemos confirmar que el nº de habitaciones influya de forma clara en el precio medio.  

### 4. Gráfico de barras precio medio según tipo de propiedad
El análisis muestra diferencias claras en el precio medio según el tipo de propiedad. Las villas presentan los precios más elevados, seguidas por las viviendas enteras, mientras que las habitaciones privadas y los condominios son las opciones más económicas. 

## Datos transformados finales
Para la realización del análisis estadístico se ha trabajado con el dataset completo en VS Code, con el fin de evitar sesgos y garantizar la máxima precisión en los resultados.

Sin embargo, para la construcción del dashboard en Google Sheets se ha utilizado una muestra representativa del dataset, debido a limitaciones técnicas de la herramienta en cuanto al volumen de datos.

Esta muestra permite mantener la coherencia en los resultados y facilita la visualización de la información sin afectar a las conclusiones principales del análisis.

## Análisis exploratorio y dashboard en Google Sheets
Se ha creado un dashboard para visualizar los datos de forma dinámica. 
Incluye:
- Análisis de precio medio por país
- Análisis de la relación entre el número de reseñas y la ocupación
- Distribución de los tipos de alojamiento
- Análisis de la correlación entre el precio medio y la capacidad del alojamiento
- Distribución de los tipos de políticas de cancelación
- Análisis de los ingresos medios según política de cancelación

### 1. Limpieza y validación de datos
Se realizaron algunos ajustes para garantizar la calidad del análisis:
- Identificación y eliminación de dos filas completamente vacías que generaban errores #DIV/0! en algunas tablas dinámicas.
- Sustitución previa en Python de valores nulos en variables categóricas por "Unknown" evitando categorías vacías en los análisis y visualizaciones.
- Eliminación previa en Python de variables numéricas cuyos valores nulos superasen el 30% del total. 
- Sustitución previa en Python de valores nulos en el resto de variables numéricas por la mediana
### 2. Transformaciones realizadas
Creación de variables derivadas para mejorar el análisis de datos:
  
Rango de número de reseñas: se creó una agrupación del número de reseñas.

Rango de precios: también se creó una variable de rango de precios para poder segmentar los datos en el dashboard.

Estas variables permitieron estructurar mejor el análisis y facilitar el uso de filtros interactivos.

### 3. Construcción de tablas dinámicas
Se crearon varias tablas dinámicas como base del dashboard:

- Precio medio por país
  
Filas: country

Valores: media de rate_avg

- Número de reseñas vs ocupación
  
Filas: rango de reseñas

Valores: media de occupancy

- Distribución de tipos de alojamiento
  
Filas: room_type

Valores: conteo de registros

Representación: porcentaje sobre el total

- Distribución de políticas de cancelación
  
Filas: cancellation_policy

Valores: conteo de registros

Representación: porcentaje sobre el total

- Ingresos medios por política de cancelación
  
Filas: cancellation_policy

Valores: media de revenue

- Relación entre precio medio y capacidad del alojamiento
  
Variables empleadas:

rate_avg

guests

### 4. Visualizaciones creadas
A partir de las tablas dinámicas y de los datos del dataset, se desarrollaron los siguientes gráficos en el dashboard:
- Gráfico de barras verticales → Precio medio por país
- Gráfico de líneas → Número de reseñas vs ocupación
- Gráfico circular → Distribución de tipos de habitación
- Gráfico de dispersión → Relación entre precio medio y capacidad del alojamiento
- Gráfico circular → Distribución de políticas de cancelación
- Gráfico de barras horizontales → Ingresos medios por política de cancelación
### 5. Controles de filtro
Se añadieron controles de filtro para mejorar la exploración de los datos:
- country
- tipo de propiedad
- rango de precios
Estos filtros permiten analizar dinámicamente la información según distintos segmentos del mercado.
### 6. Creación de macros
Se implementó una macro para facilitar la navegación a la sección de gráficos de cancelación. 
Permite desplazarse automáticamente hasta los gráficos relacionados con las políticas de cancelación.

### Enlace al Dashboard en Google Sheets
[Acceso al dashboard](https://docs.google.com/spreadsheets/d/1pZzfNsiMx0gPC5TuvEGmls1XJW8UoDtWkXv4-TGfeVE/edit?gid=391893926#gid=391893926)

## Conclusiones finales
El análisis del mercado de alojamientos en la región Asia-Pacífico, a partir de datos de propiedades registradas en Airbnb, muestra un mercado variado tanto en precios como en comportamiento de la demanda.
En primer lugar, se observa que la ocupación media es moderada-baja, situándose en torno al 29%, lo que además se refleja en que, de media, los alojamientos registran aproximadamente 9 días reservados al mes frente a 21,5 días vacíos. 
En cuanto al perfil de la oferta, el mercado está dominado por los alojamientos completos. La mayor parte de los alojamientos corresponden a viviendas enteras, mientras que las habitaciones privadas, de hotel o compartidas tienen un peso mucho menor.
Respecto al precio, el precio medio se sitúa en 117$, aunque con una distribución muy asimétrica y con presencia de valores extremos. La mayor parte de los precios medios se concentra aproximadamente entre 30$ y 120$, mientras que los alojamientos muy caros representan una minoría. Por tanto, no puede afirmarse que el mercado analizado sea predominantemente de lujo, sino más bien de precio medio con algunos casos muy premium.
También se observan diferencias claras de precio según el tipo de propiedad. Las villas y las viviendas enteras presentan los precios medios más elevados, mientras que las habitaciones privadas, los condominios y otros alojamientos compartidos resultan mucho más económicas. Esto confirma que el tipo de propiedad es uno de los factores que más influye en el precio.
Sin embargo, aunque existe una relación positiva entre precio e ingresos, no se observa una relación fuerte entre el precio y la mayoría de variables numéricas. La correlación entre el precio medio y el número de habitaciones o baños existe, pero es débil, y el gráfico de dispersión entre número de habitaciones y precio muestra mucha dispersión. Por tanto, no puede concluirse que a mayor número de habitaciones el precio aumente de forma clara o proporcional. Se observa una ligera relación positiva entre la capacidad del alojamiento y el precio medio. Sin embargo, existe una alta dispersión, por lo que la capacidad no explica por sí sola el precio.
Existen también diferencias relevantes entre países. En el dashboard se observa que Australia, Tailandia y Nueva Zelanda presentan algunos de los precios medios más elevados, mientras que India y Filipinas se sitúan entre los mercados con precios más bajos. Además, a nivel de volumen, los países con mayor presencia de alojamientos son Filipinas, Malasia, Australia y Corea del Sur.
La reputación del alojamiento aparece como un factor relevante. El análisis por rangos de reseñas muestra que, a medida que aumenta el número de reseñas, también aumenta la ocupación media. Esto sugiere que las reseñas del alojamiento influyen de forma importante en su rendimiento.
Por otro lado, las valoraciones generales son muy altas, con una media de 4,8, lo que sugiere que la mayoría de usuarios tiene valoraciones positivas.
También se observa que los alojamientos gestionados por superhosts tienen un precio medio ligeramente superior pero la diferencia no es especialmente grande cuando se compara dentro de los principales tipos de alojamiento. Además, casi la totalidad de los alojamientos están gestionados por particulares y no por profesionales.
En cuanto a la regulación, destaca que aproximadamente el 82% de los alojamientos no tienen número de registro, lo que podría reflejar un volumen importante de oferta poco regularizada.
Por último, el análisis del dashboard sugiere que la política de cancelación muestra relación con los ingresos. Las políticas más estrictas tienden a asociarse con ingresos medios más elevados que las políticas flexibles.
En resumen, puede concluirse que el rendimiento de los alojamientos registrados en Airbnb en Asia-Pacífico no depende de un único factor, sino de la combinación de varios elementos: tipo de propiedad, reputación, localización y estrategia de precios. De todos ellos, el tipo de propiedad parece ser el factor más claro a la hora de explicar diferencias de precio, mientras que el número de reseñas destaca especialmente en la explicación de la ocupación.
