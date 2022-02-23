data1 <- read.csv("Inputs/Modificados - Atmira_Pharma_Visualization/items_ordered_2years.txt", sep="|", header=TRUE, stringsAsFactors=FALSE)

write.csv(data1,"Inputs/Modificados - Atmira_Pharma_Visualization/new_items_ordered_2years.csv", row.names = FALSE)

