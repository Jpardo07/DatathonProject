# ---
#   Author: Javier Pardo
#   Date: 2022_02_11-12
#   title: "Model Pump it Up Prediction"
#   output: Submissions
#   123123
# ---
  
#-- Libraries
library(dplyr)          # Data Manipulation
library(data.table)     # Fast Data Manipulation
library(inspectdf)      # EDA automatic
library(ranger)         # Randomforest más rápido. Sin hacer train-test es capaz de decirte el error.
library(tictoc)         # Measure execution time
library(magrittr)
library(ggplot2)        # Very nice charts
library(forcats)
library(ggcharts)
# Library(tidytable)
# Library(poorman)
# 
# --- Data Loading,
datTrainori <- fread("data/training.csv", nThread = 3)
names(datTrainori)
datTrainorilab <- fread("data/train-labels.csv", nThread = 3, data.table = FALSE)
datTestori <- fread("data/test.csv", nThread = 3, data.table = F)
datTrainorilab %>% head(n = 10)

#--- Confirm "target" distribution
datTrainorilab %>%
  count(status_group) %>%
  arrange(-n)

# status_group     n
# 1              functional 32259
# 2          non functional 22824
# 3 functional needs repair  4317


#--- EDA (Explorarory Data Analytics)

# Load 'datTrainorilab' data
data("datTrainorilab", package = "dplyr")

# Horizontal bar plot for categorical column composition
x <- inspect_cat(datTrainori) 
show_plot(x)

# Correlation betwee numeric columns + confidence intervals
x <- inspect_cor(datTrainori)
show_plot(x)

# Bar plot of most frequent category for each categorical column
x <- inspect_imb(datTrainori)
show_plot(x)

# Bar plot showing memory usage for each column
x <- inspect_mem(datTrainori)
show_plot(x)

# Occurence of NAs in each column ranked in descending order
x <- inspect_na(datTrainori)
show_plot(x)

# Histograms for numeric columns
x <- inspect_num(datTrainori)
show_plot(x)

# Barplot of column types
x <- inspect_types(datTrainori)
show_plot(x)


# Results:
# extraction_type_class and group are very similar (not equal)
# payment and payment_type, equal??
# quantity and quantity_group, equal??
# recorded_by is constant.
# source and source_type, very similar
# 
# Correlation - No es significativa
# 
# NAs
# public_meeting, permit -> 5%.
# 
# Numeric
#  amount_tsh: has a few outliers.
#  construction_year: 30% 0 -> NA
#  gps_height:
#       - negative values??
#       - around 40% are 0??
# latitude: suspicious 0s (5%)
# longitude: anomalous 0s (5%)
# num_private: a few outliers
# population: a few outliers
# region_code: more pumps < 25.
# 
# ___ MODEL ___
# Put together train + labels
# Append labels to train?
# Dplyr
datTrainoritarget <- datTrainori %>%
  left_join(datTrainorilab)

#-- Now what I have is: train + target. Ready to model...
datTrainoritargetnum <- 
  datTrainoritarget %>%
  select(where(is.numeric), status_group) %>%
  mutate(status_group = as.factor(status_group))


#-- Apply algorithm --> Random forest con ranger
mymodel <- ranger(
                  status_group ~ .,
                  data = datTrainoritargetnum,
                  num.trees = 500,
                  mtry = 3,
                  importance = "impurity"
                  )

error_val <- mymodel$prediction.error
accu_val <- 1 - error_val

# DIA 2

#¿Cómo sabemos si el id es importante?

#Aquí vemos la importancia de cada variable

#--- Variable importance
varImp <- mymodel$variable.importance %>%
  as.data.frame()
varImp   %<>%
  mutate( vars = rownames(varImp)) %>%
  arrange(-.)
rownames(varImp) <- NULL
names(varImp)[1] <- "Importance"
varImp %<>%
  arrange(-Importance)
#--- Chart Importance
ggplot(varImp, aes(x = fct_reorder(vars, Importance), y = Importance, alpha = Importance)) +
  geom_col( fill = "darkred") +
  coord_flip() +
  labs(
    title = "Relative Variable Importance",
    subtitle = paste("Accuracy: ", round(100*accu_val,2), "%", sep = ""), 
    x = "Variables",
    y = "Relative Importance",
    caption = paste("model num vars: ", ncol(datTrainoritargetnum) ,sep = "") 
  ) +
  theme_bw()
ggsave(paste("./charts/Variable_Importance_", ncol(datTrainoritargetnum), ".png", sep = ""))

# fill = vars te pone colorinchis
#color = vars te pone el borde de las barras de color
#coord_flip le da la vuelta al grafico
#themw_bw = te pone el tema blanco y negro
#Y ES MUY IMPORTANTE PONERLAS EN ORDEN!! Y eso lo hacemos con el parquete forcats
#ese paquete tiene la cosa esta de ordenar que es el fct_reorder que hemos puesto arriba
#Y bueno tenemos que poner los nombres entendibles o ke. Pues eso lo hacemsos con labs()
#y con alpha = lo que sea pues lo ponemos en degradado
#con el paste_rund ponemos ai la formulita que te saca el accuracy

#☻Otra opcion es una flipada de un pavo que ha hecho que se señale la variable mas importante y se hace con highlight o algo asi y es con la library(ggcharts)

bar_chart(
  varImp,
  vars,
  Importance,
  tpop_n = 10,
  highlight = "longitude"
)

# ES IMPRESCINDIBLE QUE LA COMUNICACION SEA EFECTIVA

#lo que vemos es que "El estado de las bombas está condicionado por variables gegográficas"

# MATRIZ DE CONFUSION

#se puede hacer así:
table(mymodel$predictions, datTrainOritargetnum$status_group)
#o así:
mymodel$confusion.matrix



#----SUBMISSION
#-- Prediction
#Quiero hacer una prediccion del modelo

pred_val <- predict(mymodel, data = datTestori)$predictions
head(pred_val)
#la clase de pred_val es un factor
class(pred_val)
#y ha clasficiado en funcionales y no funcionales las bombas

#Prepare submission
sub_df <- data.frame(
  id = datTestori$id,
  status_group = pred_val
)

head(sub_df)

#save submission
fwrite(sub_df, "./submissions/ranger_vars_11_acc_o71.csv", nThread = 3)


#si te sale una variable super tocha megapredictora al final te la tienes que cargar porque te espicha el modelo
#cuando pasa esto es porque son variables que estan muy relacionadas con la variable a predecir y esto hace que no sea valida
#variable hiper predictora = DANGER


#El resultado es de 0.71 y si quiero mejorarlo puedo meter variables nuevas pero sin cambiar el algoritmo. No lo cambio porque así puedo comparar un resultado con otro.




#---------END OF FILE-----------

#-----RESULTS
# MODELO 1: ranger* -11 vars - 71% local -->