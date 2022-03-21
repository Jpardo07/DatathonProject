install.packages("missRanger")

library(missRanger)

# Carga de datos

df_ventas = read.csv("C:/Users/Daniel/Documents/GitHub/DatathonProject/Definitivo/df_ventas_3.csv")
df_ventas["X"] = NULL
col_names = names(df_ventas)

# Convertir elementos vacios por NA's

for (col in col_names){
  df_ventas[[col]][df_ventas[[col]] == ""] = NA
}

# Imputacion mediante randomforest de la libreria missRanger

df_ventas_imputed <- missRanger(df_ventas[1:400000,], pmm.k = 1, num.trees = 10)


# Escritura del archivo

write.csv(df_ventas_imputed, "C:/Users/Daniel/Documents/GitHub/DatathonProject/Definitivo/df_ventas_4.csv")






