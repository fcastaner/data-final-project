# =========================================================
# PROYECTO FINAL - AIRBNB MARKET DATA ASIA-PACIFIC
# =========================================================

# CARGA, REVISIÓN INICIAL Y UNIÓN DE DATASETS

# 1. Importación de librerías y preparación de carpetas
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

os.makedirs("GRÁFICOS", exist_ok=True)
os.makedirs("DATASETS/TRANSFORMADO", exist_ok=True)

# 2. Comprobación carpeta de trabajo y archivos
print(os.getcwd())
print(os.listdir("DATASETS/BRUTO"))

# 3. Carga de los datasets
df_listings = pd.read_csv(
    "DATASETS/BRUTO/listings.csv",
    sep=",",
    engine="python",
    on_bad_lines="skip"
)

df_past_rates = pd.read_csv(
    "DATASETS/BRUTO/past_rates.csv",
    sep=",",
    engine="python",
    on_bad_lines="skip"
)

print(df_listings.shape)
print(df_past_rates.shape)

# 4. Revisión inicial de columnas y clave de unión
print(df_listings.columns)
print(df_past_rates.columns)

print(df_listings["listing_id"].nunique())
print(df_listings.shape[0])

print(df_past_rates["listing_id"].nunique())
print(df_past_rates.shape[0])

# 5. Homogenización del tipo de dato de la clave 
df_listings["listing_id"] = df_listings["listing_id"].astype(str)
df_past_rates["listing_id"] = df_past_rates["listing_id"].astype(str)

# 6. Unión de los datasets
df_final = df_past_rates.merge(
    df_listings,
    on="listing_id",
    how="left",
    indicator=True
)

# 7. Comprobación del resultado del merge
print(df_final["_merge"].value_counts())

print(df_final[df_final["_merge"]=="left_only"])
print(df_final[df_final["_merge"] == "left_only"]["listing_id"].nunique())
df_final = df_final.drop(columns="_merge")

# 8. Revisión de valores nulos
print(df_final.isnull().sum().sort_values(ascending=False).head(10))

null_percentage = df_final.isnull().mean() * 100

# LIMPIEZA Y TRANSFORMACIÓN DE DATASETS

# 1. Eliminar columnas con más del 80% de nulos
cols_to_drop = null_percentage[null_percentage > 80].index

print(cols_to_drop)
print(len(cols_to_drop))

df_final = df_final.drop(columns=cols_to_drop)

print(df_final.shape)

# 2. Conversión de la variable "Date"
print(df_final.dtypes)
df_final["date"] = pd.to_datetime(df_final["date"], errors="coerce")
print(df_final["date"].isna().sum())

# 3. Resolución de columnas duplicadas tras el merge
print(df_final.columns)

#Comprobación igualdad variables 'country', 'state' y 'city'
print((df_final["country_x"] == df_final["country_y"]).all())
print((df_final["state_x"] == df_final["state_y"]).all())
print((df_final["city_x"] == df_final["city_y"]).all())

print((df_final["country_x"] != df_final["country_y"]).sum())
print((df_final["state_x"] != df_final["state_y"]).sum())
print((df_final["city_x"] != df_final["city_y"]).sum())

print(df_final[df_final["country_x"] != df_final["country_y"]][["listing_id", "country_x", "country_y"]])
print(df_final[df_final["state_x"] != df_final["state_y"]][["listing_id", "state_x", "state_y"]])
print(df_final[df_final["city_x"] != df_final["city_y"]][["listing_id", "city_x", "city_y"]])

#Eliminamos las columnas country, state y city repetidas (y con algunos valores nulos)
df_final = df_final.drop(columns=["country_y", "state_y", "city_y"])

# 4. Renombramos las columnas country_x, state_x, city_x
df_final = df_final.rename(columns={
    "country_x": "country",
    "state_x": "state",
    "city_x": "city"
})

print(df_final[["country", "state", "city"]].head())

# 5. Eliminamos variables categóricas irrelevantes

cols_to_drop = [
    "listing_id",
    "host_id",
    "cover_photo_url"
]

df_final = df_final.drop(columns=cols_to_drop, errors="ignore")

print(df_final.shape)

# 6. Agrupamos tipos de alojamiento menos comunes
top_types = df_final['listing_type'].value_counts().nlargest(5).index

df_final['listing_type_grouped'] = df_final['listing_type'].apply(
    lambda x: x if x in top_types else 'other'
)
print(df_final.groupby('listing_type_grouped')['rate_avg'].mean().sort_values(ascending=False))

# 7. Sustituimos valores nulos de variables categóricas por "Unknown"
cols_categoricas = [
    'cancellation_policy',
    'amenities',
    'room_type',
    'listing_type',
    'listing_type_grouped',
    'superhost',
    'country',
    'state',
    'city',
    'currency',
    'professional_management',
    'registration'
]

cols_existentes = [col for col in cols_categoricas if col in df_final.columns]

df_final[cols_existentes] = df_final[cols_existentes].fillna('Unknown')

# 8. Tratamiento valores nulos de variables numéricas 
## Análisis valores nulos de variables numéricas
print(df_final.select_dtypes(include=['number']).isnull().sum().sort_values(ascending=False))

null_percentage_num = df_final.select_dtypes(include=['number']).isnull().mean() * 100
print(null_percentage_num.sort_values(ascending=False))

## Eliminamos columnas con valores nulos>30%
cols_to_drop_num = null_percentage_num[null_percentage_num > 30].index

print(cols_to_drop_num)

df_final = df_final.drop(columns=cols_to_drop_num)

## Sustituimos valores nulos del resto de variables numéricas por la mediana
num_cols = df_final.select_dtypes(include=['number']).columns

df_final[num_cols] = df_final[num_cols].fillna(df_final[num_cols].median())

print(df_final.select_dtypes(include=['number']).isnull().sum().sum())

# 9. Revisión de duplicados
print(df_final.duplicated().sum())

print(df_final.describe())


# ANÁLISIS DESCRIPTIVO Y ESTADÍSTICO

# 1. Análisis de variables numéricas
print(df_final.describe().T)

# 2. Análisis de variables categóricas
for col in df_final.select_dtypes(include='object').columns:
    print(f"\n--- {col} ---")
    print(df_final[col].value_counts(normalize=True).head(10))

# 3. Relación entre variables categóricas
# Superhost vs rate_avg
print(df_final.groupby('superhost')['rate_avg'].mean())

# room_type vs rate_avg
print(df_final.groupby('room_type')['rate_avg'].mean())

# listing_type vs rate_avg
print(df_final.groupby('listing_type')['rate_avg'].mean().sort_values(ascending=False))

# listing_type_grouped + superhost vs rate_avg
print(df_final.groupby(['listing_type_grouped', 'superhost'])['rate_avg'].mean())

# 4. Correlación entre variables numéricas
# Correlaciones altas entre todas las variables numéricas
corr_matrix = df_final.corr(numeric_only=True)

high_corr = corr_matrix[(corr_matrix.abs() > 0.8) & (corr_matrix < 1)]

print(high_corr.dropna(how='all').dropna(axis=1, how='all'))

high_corr_clean=high_corr.dropna(how='all').dropna(axis=1, how='all')
high_corr_clean.to_csv("DATASETS/TRANSFORMADO/high_correlations.csv")

# Correlaciones con la variable rate_avg 
corr_target = (
    df_final.corr(numeric_only=True)['rate_avg']
    .drop('rate_avg') 
    .sort_values(ascending=False)
)

print(corr_target)

# VISUALIZACIÓN DE DATOS

# Se excluyen alojamientos con precio medio superior a 500 para reducir el impacto de outliers en la visualización
price_threshold = 500
df_filtered = df_final[df_final['rate_avg'] < price_threshold]

# 1. Histograma de precio

sns.histplot(df_filtered['rate_avg'], bins=50)
plt.title('Distribución de precios')
plt.xlabel('Precio medio')
plt.ylabel('Número de alojamientos')

plt.savefig('GRÁFICOS/histograma_precios.png')
plt.show()

# 2. Boxplot de precio según tipo de propiedad 

plt.figure(figsize=(10,6))

sns.boxplot(x='listing_type_grouped', y='rate_avg', data=df_final)

plt.title('Distribución de precios por tipo de propiedad')
plt.xlabel('Tipo de propiedad')
plt.ylabel('Precio medio')

plt.savefig('GRÁFICOS/boxplot_precio_por_tipo_propiedad.png', dpi=300, bbox_inches='tight')

plt.show()

# 3. Scatter número de habitaciones vs precio medio
plt.figure(figsize=(10,6))

sns.scatterplot(
    x='bedrooms',
    y='rate_avg',
    data=df_filtered
)

plt.title('Relación entre número de habitaciones y precio')
plt.xlabel('Número de habitaciones')
plt.ylabel('Precio medio')

plt.savefig('GRÁFICOS/scatter_habitaciones_precio.png', dpi=300, bbox_inches='tight')

plt.show()

# 4. Gráfico de barras precio medio por tipo de propiedad
plt.figure(figsize=(12,6))

order = (
    df_filtered
    .groupby('listing_type_grouped')['rate_avg']
    .mean()
    .sort_values(ascending=False)
    .index
)

sns.barplot(
    x='listing_type_grouped',
    y='rate_avg',
    data=df_filtered,
    order=order
)

plt.title('Precio medio por tipo de propiedad')
plt.xlabel('Tipo de propiedad')
plt.ylabel('Precio medio')

plt.savefig('GRÁFICOS/barras_precio_tipo_propiedad.png', dpi=300, bbox_inches='tight')

plt.show()

# DATOS TRANSFORMADOS FINALES

# Guardar dataset final
df_final.to_csv('DATASETS/TRANSFORMADO/dataset_final.csv', index=False)

# Creación de un dataset con muestra aleatoria
sample_size = min(20000, len(df_final))
df_sample = df_final.sample(n=sample_size, random_state=42)

# Guardar dataset para dashboard Google Sheets
df_sample.to_csv('DATASETS/TRANSFORMADO/dataset_muestra.csv', index=False)

