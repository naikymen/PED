library(ggplot2)
library(readr)
library(ggthemes)


##This is what is has to read from python
df <- read_csv("secondary_structure_table.csv")
ensembles = unique(df$Ensemble)
pedxxxx = unique(df$Entry)
chains = unique(df$Chain)
pedxxxx
for (i in ensembles){
  df_subset_ensemble<-subset(df,df$Ensemble==i)
  for (j in chains){
    df_subset_chain <- subset(df_subset_ensemble, df_subset_ensemble$Chain == j)
    temp_plot<- ggplot(df_subset_chain, color = variable)+
      facet_grid(Chain ~ Ensemble)+
      geom_line(aes(y = Alpha_helix_percentage ,x = Position, color="Alpha_helix_percentage")) + 
      geom_line(aes(y = Beta_strand_percentage, x = Position, color="Beta_strand_percentage")) + 
      geom_line(aes(y = Other_percentage, x= Position, color="Other_percentage")) +
      theme_gdocs()+
      xlab("Position")+
      ylab("Percentage of secondary structure element")+
      scale_color_brewer(palette = "Dark2",name='')+
      #scale_color_brewer(palette = "PRGn",name = " ")+
      theme(plot.title = element_text(size = 13, face = "bold" , hjust = 0) , 
            axis.title=element_text(size=10,face="bold"), legend.text=element_text(size=12, face="italic") , legend.title=element_blank(),legend.direction="vertical",legend.key.size = unit(0.5, "cm"))+
      theme(legend.direction = "horizontal", 
            legend.position = "bottom",
            legend.box = "horizontal"
      )
      temp_plot
      tiff(file = paste0(pedxxxx,"_",i,"_",j,"_secondary_structure_plot.tiff"), width = 5500, height = 3200, units = "px", res = 800) 
      plot(temp_plot)
      dev.off()
  }

}


