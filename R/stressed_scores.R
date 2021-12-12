#creating Stress Scenarios
unit = 30
trail = 24
stressed_scores<-function(Scores, Date_dmy){

  scores_dmy<-data.frame(Date_dmy, Scores)
  scores_dmy_ordered <- scores_dmy[order(scores_dmy$Date),]
  
  #Stress testing
  rolling_diff_PC<-na.omit(cbind(scores_dmy_ordered[,1], scores_dmy_ordered[names(scores_dmy_ordered)!='Date']-lag(scores_dmy_ordered[names(scores_dmy_ordered)!='Date'],unit)))
  
  stress_date<-as_date(scores_dmy_ordered[,1])
  PC_scores<-scores_dmy_ordered[,-1]
  
  colnames(rolling_diff_PC)[1]="Date"
  rolling_diff_PC_up <- rolling_diff_PC 
  rolling_diff_PC_up[rolling_diff_PC_up < 0] <- 0
  rolling_diff_PC_down <- rolling_diff_PC 
  rolling_diff_PC_down[,-c(1)][rolling_diff_PC_down[, -c(1)] > 0] <- 0
  l_stress<-nrow(PC_scores)-unit
  rolling_diff_PC_q_up<-roll_quantile(as.matrix(rolling_diff_PC_up[,-c(1)]), width = unit*trail,p=0.995, min_obs = 1)
  rolling_diff_PC_q_down<-roll_quantile(as.matrix(rolling_diff_PC_down[,-c(1)]), width = unit*trail,p=0.005, min_obs = 1)
  
  PC_scores_up <-tail(PC_scores,l_stress)+rolling_diff_PC_q_up
  PC_scores_down <-tail(PC_scores,l_stress)+rolling_diff_PC_q_down
  
  colnames(PC_scores_up) <- paste("Up", colnames(PC_scores_up), sep = "_")
  colnames(PC_scores_down) <- paste("Down", colnames(PC_scores_down), sep = "_")
  
  PC_stress<-as.data.frame(cbind(tail(stress_date,l_stress), tail(PC_scores,l_stress),PC_scores_up,PC_scores_down))
  colnames(PC_stress)[1]<-"Date"
  
  

  #Stressed scores PC1  
  fig_Stress_PC1 <- plot_ly(PC_stress, x = ~Date, y = ~Up_PC1, type = 'scatter', mode = 'lines', 
                           line = list(color = 'red'), 
                           showlegend = TRUE, name = 'Stress up PC1',
                           hovertemplate = paste(
                               'Date:  %{x: %Y-%m-%d}<br>',
                               '99,5% Quantil up PC1-Score: %{y:.4f}<br>',
                               '<extra></extra>'
                           )) 
  
  fig_Stress_PC1 <- fig_Stress_PC1 %>% 
    add_trace(y = ~Down_PC1, type = 'scatter', mode = 'lines', 
              fill = 'tonexty', fillcolor='rgba(0,100,80,0.2)', line = list(color = 'blue'),
              showlegend = TRUE, name = 'Stress down PC1', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                '99,5% Quantil down PC1-Score: %{y:.4f}<br>',
                '<extra></extra>'
              )) 
  
  fig_Stress_PC1 <- fig_Stress_PC1 %>% 
    add_trace(y = ~PC1, type = 'scatter', mode = 'lines', 
              line = list(color='rgb(0,100,80)'),
              name = 'PC 1', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                'PC1-Score: %{y:.4f}<br>',
                '<extra></extra>'
              )) 
  #Stressed scores PC2  
  fig_Stress_PC2 <- plot_ly(PC_stress, x = ~Date, y = ~Up_PC2, type = 'scatter', mode = 'lines', 
                            line = list(color = 'red'),
                            showlegend = TRUE, name = 'Stress up PC2',hovertemplate = paste(
                              'Date:  %{x: %Y-%m-%d}<br>',
                              '99,5% Quantil up PC2-Score: %{y:.4f}<br>',
                              '<extra></extra>'
                            )) 
  
  fig_Stress_PC2 <- fig_Stress_PC2 %>% 
    add_trace(y = ~Down_PC2, type = 'scatter', mode = 'lines',
              fill = 'tonexty', fillcolor='rgba(0,100,80,0.2)', line = list(color = 'blue'),
              showlegend = TRUE, name = 'Stress down PC2', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                '99,5% Quantil down PC2-Score: %{y:.4f}<br>',
                '<extra></extra>'
              )) 
  
  fig_Stress_PC2 <- fig_Stress_PC2 %>% 
    add_trace(y = ~PC2, type = 'scatter', mode = 'lines',
              line = list(color='rgb(0,100,80)'),
              name = 'PC 2', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                'PC2-Score: %{y:.4f}<br>',
                '<extra></extra>'
              )) 
  #Stressed scores PC3  
  fig_Stress_PC3 <- plot_ly(PC_stress, x = ~Date, y = ~Up_PC3, type = 'scatter', mode = 'lines', 
                            line = list(color = 'red'),
                            showlegend = TRUE, name = 'Stress up PC3', hovertemplate = paste(
                              'Date:  %{x: %Y-%m-%d}<br>',
                              '99,5% Quantil up PC3-Score: %{y:.4f}<br>',
                              '<extra></extra>'
                            )) 
  
  fig_Stress_PC3 <- fig_Stress_PC3 %>% 
    add_trace(y = ~Down_PC3, type = 'scatter', mode = 'lines',
              fill = 'tonexty', fillcolor='rgba(0,100,80,0.2)', line = list(color = 'blue'),
              showlegend = TRUE, name = 'Stress down PC3', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                '99,5% Quantil down PC3-Score: %{y:.4f}<br>',
                '<extra></extra>'
              )) 
  
  fig_Stress_PC3 <- fig_Stress_PC3 %>% 
    add_trace(y = ~PC3, type = 'scatter', mode = 'lines',
              line = list(color='rgb(0,100,80)'),
              name = 'PC 3', hovertemplate = paste(
                'Date:  %{x: %Y-%m-%d}<br>',
                'PC3-Score:%{y:.4f}<br>',
                '<extra></extra>'
              )) 

  Stress_PC_figures <- list("fig_Stress_PC1" = fig_Stress_PC1, 
                            "fig_Stress_PC2" = fig_Stress_PC2,
                            "fig_Stress_PC3" = fig_Stress_PC3,
                            "PC_stress"=PC_stress)
  return(Stress_PC_figures) 
}