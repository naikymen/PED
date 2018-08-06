# Use require() to try loading pakcages. library() will produce an error if they are not installed.
library(data.table)
library(Cairo)

# This script will process SAXS data and produce th normalized Kratky plots
# It reads the following arguments:
#   PEDXXXX-autorg.out XXXX-saxs.dat /path/to/reference/saxs/ XXXX
# It is called from bash like this:
#   Rscript /path/to/scripts/Pipe6-SAXS.R PEDXXXX-autorg.out XXXX-saxs.dat /path/to/reference/saxs/ XXXX

test=F
if(test){
  setwd('/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/PED1AAA/')
  setwd('/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/PED1AAA/SAXS-PED1AAA')
  autorg_file <- '/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/PED1AAA/SAXS-PED1AAA/PED1AAA-autorg.out'
  saxs_file <-'/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/PED1AAA/SAXS-PED1AAA/1AAA-saxs.dat'
  bsa_file <- '/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/Reference_data-Kratky_plots/bsa.csv'
  dis_file <- '/home/nicomic/Projects/Chemes/IDPfun/PED-DB3/Reference_data-Kratky_plots/dis.csv'
  entry_name <- '1AAA'
}
# 

# Read input arguments: (1) autorg.out (2) saxs.dat ...
args <- commandArgs(trailingOnly = TRUE)

# trailingOnly	logical. Should only arguments after --args be returned?
# args <- strsplit("PED1AAB-autorg.out 1AAB-saxs.dat ../SAXS-dat/ 1AAB", split = ' ')[[1]]

exec = FALSE
if(length(args) != 5){
  stop("Incorrect number of arguments! Please provide (1) autorg file (2) SAXS file (3) Path to the reference SAXS data (4) The PEDB entry ID (e.g. 1AAB)")
} else {
  exec = TRUE
  #print(getwd())
}

if(exec){
  # Entry ID: XXXX
  entry_name <- args[5]  
  
  # Load the autorg output
  autorg_file <- args[1]
  # autorg_file <- 'PED1AAB-autorg.out'
  autorg <- read.csv(autorg_file)
  rg <- autorg$Rg
  i0 <- autorg$I.0.
  firstPoint <- autorg$First.point
  lastPoint <- autorg$Last.point
  
  # Load the SAXS data
  saxs_file <- args[2]
  # saxs_file <- '1AAB-saxs.dat'
  saxs <- fread(saxs_file,header = FALSE)
  
  ## Reference SAXS curves
  bsa_file <- paste(args[3],'bsa.csv',sep = '')
  bsa <- read.csv(bsa_file, sep='\t', head=F)
  
  dis_file <- paste(args[3],'dis.csv',sep = '')
  dis <- read.csv(dis_file, sep='\t', head=F)
  
  # datgnom Output
  datgnom_file <- args[4]
  pr_file <- paste(entry_name,'-saxs.dat.rPr.datgnom',sep = '')

  ## Normalized Kratky plots
  if(TRUE){
    plot_name <- paste(entry_name,"normkrat.png",sep = '-')
    
    CairoPNG(file = plot_name, width = 800, height = 600, bg="white",
             pointsize = 12,  res = NA, family = "Ubuntu");
    
    # PLot: s * Rg VS. (I(s) / I(0)) * (s * Rg)^2
    plot((saxs$V1 * rg), (saxs$V2 / i0) * (saxs$V1 * rg)^2, col="black",
         type="l", pch=2, main=paste(entry_name,"Normalized Kratky plot"),
         xlab="s x Rg", ylab="I(s) / I0 x (s x Rg)^2",
         family="Ubuntu", font=1, font.lab=2, ps = 11,
         cex.main=1.5, cex.lab=1.25, cex.axis=1.00,
         ylim=c(0, 2.5),
         mgp=c(2.5,0.8,0))
    # Add error ¿arrows?
    arrows(saxs$V1 * rg, ((saxs$V2 * (saxs$V1 * rg)^2) - (saxs$V3 * (saxs$V1 * rg)^2)) / i0, 
           saxs$V1 * rg, ((saxs$V2 * (saxs$V1 * rg)^2) + (saxs$V3 * (saxs$V1 * rg)^2)) / i0,
           length=0, angle=90, code=3, col = 'gray')
    
    # Add reference SAXS curves
    lines(bsa$V1 * 2.985, (bsa$V2 / 77.336) * (bsa$V1 * 2.985)^2, col="green")
    lines(dis$V1 * 6.031, (dis$V2 / 69.586) * (dis$V1 * 6.031)^2, col="red")
    
    # Write output
    dev.off()
  }
  
  ## Guinier Plot
  if(TRUE){
    s2 <- ((saxs$V1)^2)
    ln_i <- log(saxs$V2)
    ln_i_lm <- lm(ln_i[firstPoint:lastPoint] ~ s2[firstPoint:lastPoint])
    ln_i_lmResiduals <- resid(ln_i_lm)
    
    baseLine <- ln_i[lastPoint] - 0.2*abs(ln_i[firstPoint]-ln_i[lastPoint])
    
    plot_name <- paste(entry_name,"guinier.png",sep = '-')
    CairoPNG(file = plot_name, width = 522, height = 522,
             pointsize = 12, bg = "white",  res = NA, family = "Ubuntu");
    plot(s2 , ln_i , col='black', 
         type='p', pch=16, cex=0.6, family= 'Ubuntu', main=paste(entry_name,"Guinier plot"), 
         xlab= expression(bold(S^{"2"})), ylab=expression(bold("ln (I)")),
         cex.main=1.5, cex.lab=1.25, font = 1, cex.axis = 1
         #ylim=c(1.9,2.5), mgp=c(2.5,0.8,0)  # Editar acá
    )
    abline(v = c(s2[firstPoint],s2[lastPoint]), col='lightblue3')
    abline(h = baseLine, col='lightblue3')
    lines(s2[firstPoint:lastPoint], predict.lm(ln_i_lm),lwd=2, col='red')  
    lines(s2[firstPoint:lastPoint], baseLine + resid(ln_i_lm), lwd=1.5, col='darkgreen')
    
    dev.off()
  }
  
  ## Scattering Plot
  if(T){
    datgnom_file <- datgnom_file
    sj <- fread(datgnom_file, header = F, col.names = c('S', 'J', 'EXP_ERROR', 'J_REG', 'I_REG'))
    plot_name <- paste(entry_name, '-scatteringPlot.png', sep = '')
    # Reference: https://www.embl-hamburg.de/biosaxs/manuals/gnom.html#runtime
    CairoPNG(file = plot_name, width = 522, height = 522,
             pointsize = 12, bg = "white",  res = NA, family = "Ubuntu");
    
    plot(sj$S, log(sj$J), col='black', 
         type='l', pch=16, cex=0.6, family= 'Ubuntu', main=paste(entry_name,"Scattering intensity plot"), 
         xlab= expression(bold(S)), ylab=expression(bold("ln (I)")),
         cex.main=1.5, cex.lab=1.25, font = 1, cex.axis = 1
         #ylim=c(1.9,2.5), mgp=c(2.5,0.8,0)  # Editar acá
    )
    
    # Add error ¿arrows?
    arrows(sj$S, log(sj$J - sj$EXP_ERROR), 
           sj$S, log(sj$J + sj$EXP_ERROR),
           length=0, angle=90, code=3, col = 'gray')
    
    
    lines(sj$S, log(sj$J_REG), col = 'red', pch = 3, lty = 2, lwd = 1)
    lines(sj$S, log(sj$I_REG), col = 'red', pch = 4, lty = 3)
    
    dev.off()
  }
  
  ## r vs P(r) Plot
  if(T){
    pr_file <- pr_file
    rPr_data <- fread(pr_file, header=TRUE, col.names = c('r', 'Pr', 'Error'))
    plot_name <- paste(entry_name, '-rPrPlot.png', sep = '')
    
    CairoPNG(file = plot_name, width = 522, height = 522,
             pointsize = 12, bg = "white",  res = NA, family = "Ubuntu");
    
    plot(rPr_data$r, rPr_data$Pr, col='black', 
         type='l', pch=16, cex=0.6, family= 'Ubuntu', main=paste(entry_name,"Pairwise distance distribution plot"), 
         xlab= expression(bold(S)), ylab=expression(bold("ln (I)")),
         cex.main=1.5, cex.lab=1.25, font = 1, cex.axis = 1
         #ylim=c(1.9,2.5), mgp=c(2.5,0.8,0)  # Editar acá
    )
    
    # Add error ¿arrows?
    arrows(rPr_data$r, rPr_data$Pr - rPr_data$Error, 
           rPr_data$r, rPr_data$Pr + rPr_data$Error,
           length=0, angle=90, code=3, col = 'gray')
    
    dev.off()
  }
}