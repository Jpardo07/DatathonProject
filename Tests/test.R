data1 <- read.csv("Inputs/Modificados - Atmira_Pharma_Visualization/items_ordered_2years_V2.csv", sep="|", header=TRUE, stringsAsFactors=FALSE)

# write.csv(data1,"Inputs/Modificados - Atmira_Pharma_Visualization/new_items_ordered_2years.csv", row.names = FALSE)

print(nrow(data1))

print(tail(data1))

