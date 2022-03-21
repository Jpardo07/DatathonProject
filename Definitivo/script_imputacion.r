install.packages("missRanger")

library(missRanger)


#--- Apply library/algorithm to impute NAs.


df_ventas = read.csv("C:/Users/Daniel/Documents/GitHub/DatathonProject/Definitivo/df_ventas_3.csv")
df_ventas["X"] = NULL
names(df_ventas)

df_ventas_imputed <- missRanger(df_ventas, pmm.k = 3, num.trees = 100)

write.csv(df_ventas_imputed, "C:/Users/Daniel/Documents/GitHub/DatathonProject/Definitivo/df_ventas_4.csv")
