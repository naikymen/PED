# setwd('/home/nicomic/Projects/Chemes/IDPfun/PED-DB2/PED1AAB')
args <- commandArgs(trailingOnly = TRUE)
scripts_path <- args[1]

# For testing
# setwd('/home/nicomic/Projects/Chemes/IDPfun/PED/PED1AAA/')
# scripts_path <- '/home/nicomic/Projects/Chemes/IDPfun/PED/Scripts/'

# Setup
rg <- read.csv("Rg/rg.list", head = TRUE, sep="\t", stringsAsFactors = F);
names(rg) <- c('PDB', 'ensemble', 'Dmax', 'Rg', 'pedxxxx')
rg$PDBname <- unlist(lapply(strsplit(rg$PDB, split = '\\.'), function(x) x[1]))

# This is deprecated, i left it there for the record
#if(file.exists('chosenRg.list')) file.remove('chosenRg.list')

for(ensemble in unique(rg$ensemble)){
  
  ## grafica Rg necesita Rg.list
  #mv rgdist-ens${nue}.jpg ${dos}_${nue}-Rgdist.jpg
  jpeg(paste('Rg/',rg$pedxxxx[1],'_rgdist-ens', "_", ensemble, '-Rgdist.jpg', sep = ''), width=1250, height=400);
  rgSub <- rg[rg$ensemble == ensemble,];
  
  hist(rgSub$Rg, prob=T, main='', xlab='', ylab='');
  title(main='Rg distribution of Ensemble', cex.main=3.5);
  lines(density(rgSub$Rg), lwd=3, col='red');
  dev.off();
  
  outputFile0 <- paste("Rg/", 'rg.list', "-ens_" , ensemble, sep = "")
  write.table(rgSub, outputFile0, sep = '\t', quote = F, row.names = F)
  
  Rg_mean <- mean(rgSub$Rg)
  Rg_sd <- sd(rgSub$Rg)
  
  Dmax_mean <- mean(rgSub$Dmax)
  Dmax_sd <- sd(rgSub$Dmax)
  
  datos1 <- data.frame(Rg_mean = round(Rg_mean,2),
                       Rg_sd = round(Rg_sd,2), 
                       Dmax_mean = round(Dmax_mean,2), 
                       Dmax_sd = round(Dmax_sd,2))
  
  outputFile1 <- paste("Rg/",rg$pedxxxx[1], "_" ,ensemble ,"-Rg-Dmax-mean.txt", sep = "")
  write.table(datos1, outputFile1, sep = "\t", quote = F, row.names = F)
  
  
  # This is deprecated, i left it there for the record
  # Obtiene los conformeros con Rg máximo, mínimo y "medio"
  #elegidos <- rgSub[c(which.min(abs(rgSub$Rg - Rg_mean)),
  #                    which.min(rgSub$Rg),
  #                    which.max(rgSub$Rg)),]
  #write.table(elegidos, 'chosenRg.list', sep = ",", quote = F, row.names = F, col.names = F, append = TRUE)
  
  # This is deprecated, i left it there for the record
  #pyMolColors <- c('average-203-232-107','min-242-233-225','max-28-20-13')
  #datos2 <- as.data.frame(cbind(elegidos[,'PDB'], pyMolColors))
  #outputFile2 <- paste("Pymol/",rg$pedxxxx[1], "_" ,ensemble , "-lista_AvgMinMax", sep = "")
  #write.table(datos2, outputFile2, sep = "-", quote = F, row.names = F, col.names = F)
}
