#Create Stress Scenarios
unit = 30
trail = 24

stress_scenarios<-function(stressed_PC,Date_dmy,PC_stress,PC_Rotation,yield_data,mu){


  df_yield_curve_str<-as.data.frame(yield_data)%>%
    select(-Date)
  PC_stress_up<-PC_stress
  PC_stress_down<-PC_stress
  PC_stress_up[,stressed_PC]<-PC_stress[,paste0("Up_",stressed_PC)]
  PC_stress_down[,stressed_PC]<-PC_stress[,paste0("Down_",stressed_PC)]
  
  ds_yc<-data.frame(Date_dmy, df_yield_curve_str, check.names=FALSE)
  ds_yc <- ds_yc[order(ds_yc$Date),]
  ds_yc$Date<-NULL
  
  
  
  #Yield Curve Stress PCx
  Xhat_up = as.matrix(PC_stress_up[,2:5]) %*% t(PC_Rotation[,1:4])
  Xhat_up = scale(Xhat_up, center = -mu, scale = FALSE)
  ds_Xhat_up<-as.data.frame(Xhat_up)
  Xhat_down = as.matrix(PC_stress_down[,2:5]) %*% t(PC_Rotation[,1:4])
  Xhat_down = scale(Xhat_down, center = -mu, scale = FALSE)
  ds_Xhat_down<-as.data.frame(Xhat_down)
  
  pca_test<-t(rbind(tail(ds_yc,1),tail(ds_Xhat_up,1),tail(ds_Xhat_down,1)))
  colnames(pca_test)<-c("Yield_curve","PC_Stress_up","PC_Stress_down")
  pca_test<-as.data.frame(pca_test)
  
  fig_Stress_scenario<-plot_ly(pca_test, type = 'scatter', mode = 'lines')%>%
                        add_trace( y = ~Yield_curve, name="Yield_curve", hovertemplate = paste('Yield Curve: %{y:.2f} %')) %>%
                        add_trace( y = ~PC_Stress_up, name=paste0(stressed_PC," up"), hovertemplate = paste('Yield Curve stressed score up: %{y:.2f} %')) %>%
                        add_trace( y = ~PC_Stress_down, name=paste0(stressed_PC," down"), hovertemplate = paste('Yield Curve stressed score down: %{y:.2f} %'))
  Stress_Scenarios<-list("ds_yc"=ds_yc,"ds_Xhat_up"=ds_Xhat_up,"ds_Xhat_down"=ds_Xhat_down)
  return(list("Stress_Scenarios"=Stress_Scenarios,"pca_test"=pca_test, "fig_Stress_scenario"=fig_Stress_scenario))
}