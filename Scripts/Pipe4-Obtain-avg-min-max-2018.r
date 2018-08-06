{

  # setwd('/home/nicomic/Projects/Chemes/IDPfun/PED-DB2/PED1AAB/')
  # file_name <- 'rg.list'
  
  file_name <- 'temp-arch1'
  
  rg <- read.csv(file_name, head = TRUE, sep="\t");
  
  #x4 <- read.csv("lista_AvgMinMax-color", head = FALSE, sep="\t");
  x4 <-c('average-203-232-107','min-242-233-225','max-28-20-13')
  
  x <- rg[,c(3)]
  
  elegidos <- rg[c(which.min(rg$Rg),
                   which.max(rg$Rg),
                   which.min(abs(rg$Rg - mean(rg$Rg)))
                   ),c(1,3)]
  
  datos <- as.data.frame(cbind(elegidos, x4))
  datos <- datos[c(1:3),c(1,3)]
  
  write.table(datos, "lista_AvgMinMax", sep = "-", quote = F, row.names = F, col.names = F)
}
