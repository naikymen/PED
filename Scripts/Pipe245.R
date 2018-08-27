# setwd('/home/nicomic/Projects/Chemes/IDPfun/PED-DB2/PED1AAB')
args <- commandArgs(trailingOnly = TRUE)
scripts_path <- args[1]

# setwd('/home/nicomic/Projects/Chemes/IDPfun/PED/PED1AAA/')
# scripts_path <- '/home/nicomic/Projects/Chemes/IDPfun/PED/Scripts/'
rg <- read.csv("Rg/rg.list", head = TRUE, sep="\t", stringsAsFactors = F);

# Extract ensemble and entry information from the file name
rg$ensemble <- unlist(lapply(strsplit(rg$PDB, split = '[_-]'), function(x) x[2]))
rg$pedxxxx <- unlist(lapply(strsplit(rg$PDB, split = '[_-]'), function(x) x[1]))
rg$PDBname <- unlist(lapply(strsplit(rg$PDB, split = '\\.'), function(x) x[1]))
rg <- rg[order(rg$PDB),]

if(file.exists('Pymol/pymolCalls')) file.remove('Pymol/pymolCalls')
if(file.exists('Pymol/pymolArguments')) file.remove('Pymol/pymolCalls')

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
  #cp Rg-Dmax-mean ./Rg/${dos}_${nue}-Rg-Dmax-mean.txt
  
  
  
  # Obtiene los conformeros con Rg máximo, mínimo y "medio"
  # The order of the rows is important: average, min, max (must match the order in the 'pyMol' matrix defined below)
  elegidos <- rgSub[c(which.min(abs(rgSub$Rg - Rg_mean)),
                      which.min(rgSub$Rg),
                      which.max(rgSub$Rg)),]
  
  
  pyMolColors <- c('average-203-232-107','min-242-233-225','max-28-20-13')  # This is deprecated, i left it there for the record
  datos2 <- as.data.frame(cbind(elegidos[,'PDB'], pyMolColors))
  outputFile2 <- paste("Pymol/",rg$pedxxxx[1], "_" ,ensemble , "-lista_AvgMinMax", sep = "")
  write.table(datos2, outputFile2, sep = "-", quote = F, row.names = F, col.names = F)
  
  
  # New part, replacing Pipe5.pl
  pyMol <- matrix(c('average',203,232,107,'min',242,233,225,'max',28,20,13),
                  nrow = 4,
                  ncol = 3)
  
  # For each type: min, max and average (3 in total)
  for(n in 1:3){
    # -y is quit on error
    pymolCall <- paste(sprintf("pymol -qrcy %s/Pipe5.1.pml --", scripts_path), 
                       elegidos$PDBname[n],
                       elegidos$pedxxxx[n],
                       elegidos$ensemble[n],
                       paste(pyMol[,n], collapse = ' '), 
                       sep = ' ')
    
    pymolArgs <- paste(elegidos$PDBname[n],
                       elegidos$pedxxxx[n],
                       elegidos$ensemble[n],
                       paste(pyMol[,n], collapse = ' '), 
                       sep = ' ')
    
    # "pymol -qrc ../Scripts/Pipe5.1.pml -- PED1AAB_1-2 PED1AAB 1         average 203     232     107"
    #             path/to/script.pml        name        id      ensemble  type    color1  color2  color3
    
    write(pymolCall, file = 'Pymol/pymolCalls', append = TRUE)

    outputFile3 <- "Pymol/pymolArguments"
    write.table(pymolArgs, outputFile3, quote = F, row.names = F, col.names = F, append = TRUE)
    #try(system(pymolCall))
    
    #cat(scripts_path,file="outfile.txt",append=TRUE,sep='\n')
    #cat(pymolCall,file="outfile.txt",append=TRUE,sep='\n')
    #cat(getwd(),file="outfile.txt",append=TRUE,sep='\n')
  }
}
