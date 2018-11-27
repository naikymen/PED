library(ggplot2)
library(readr)
library(ggthemes)


##This is what is has to read from python
##This is what is has to read from python
df <- read_csv("end_to_end_table.csv")
ensembles = unique(df$Ensemble)
pedxxxx = unique(df$Entry)
chains = unique(df$Chain)
pedxxxx
for (i in ensembles){
  df_subset_ensemble<-subset(df,df$Ensemble==i)
  for (j in chains){
    df_subset_chain <- subset(df_subset_ensemble, df_subset_ensemble$Chain == j)
    temp_plot <- ggplot(df_subset_chain, aes(x=End_to_End), fill = variable) +   
      geom_histogram(aes(y=..density..),color="gray21", fill="white",binwidth = 8) + 
      geom_density(aes(y=..density..), color="red", alpha=0.5) +
      facet_grid(Chain ~ Ensemble)+
      theme_gdocs()+
      xlab("End_to_End_distance")+
      ylab("Density")+
      theme(plot.title = element_text(size = 13, face = "bold" , hjust = 0) , 
            axis.title=element_text(size=10,face="bold"), legend.text=element_text(size=12, face="italic") , legend.title=element_blank(),legend.direction="vertical",legend.key.size = unit(0.5, "cm"))+
      theme(legend.direction = "horizontal", 
            legend.position = " ",
            legend.box = "horizontal"
      )
    temp_plot
    tiff(file = paste0(pedxxxx,"_",i,"_",j,"_end_to_end_distance_plot.tiff"), width = 5500, height = 3200, units = "px", res = 800) 
    plot(temp_plot)
    dev.off()
  }
  
}



all_together<- ggplot(df, aes(x=End_to_End), fill = variable) +
  facet_grid(Chain ~ Ensemble)+
  geom_histogram(aes(y=..density..),color="gray21", fill="white",binwidth = 8) + 
  geom_density(aes(y=..density..), color="red", alpha=0.5) +
  theme_gdocs()+
  xlab("End_to_End_distance")+
  ylab("Density")+
  theme(plot.title = element_text(size = 13, face = "bold" , hjust = 0) , 
        axis.title=element_text(size=10,face="bold"), legend.text=element_text(size=12, face="italic") , legend.title=element_blank(),legend.direction="vertical",legend.key.size = unit(0.5, "cm"))+
  theme(legend.direction = "horizontal", 
        legend.position = " ",
        legend.box = "horizontal"
  )
tiff(file = paste0(pedxxxx,"_end_to_end_distance_plot_all.tiff"), width = 5500, height = 3200, units = "px", res = 800) 
plot(all_together)
dev.off()


