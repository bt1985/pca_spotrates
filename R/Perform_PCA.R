performm_pca<-function(yield_data){
df_yield_curve_str<-as.data.frame(yield_data)%>%
  select(-Date)

df_yield_curve <- sapply(df_yield_curve_str, as.numeric)
mu = colMeans(df_yield_curve)
fit <- prcomp(df_yield_curve)
Date_dmy<-yield_data %>%
  select(Date) %>%
  mutate(Date=ymd(Date))%>%
  as.data.frame() 
  
return(list("df_yield_curve"=df_yield_curve, "mu"=mu, "fit"=fit,"Date_dmy"=Date_dmy))
}
