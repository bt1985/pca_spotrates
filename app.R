library(shiny)
library(tidyverse)
library(plotly)
library(lubridate)
library(roll)
library(ggplot2)
library(shinyalert)
library(shinycssloaders)
library(shinyjs)
source("import_yield_curve.R")
source("3dplot_yield_curve.R")
source("Perform_PCA.R")
source("stressed_scores.R")
source("Stress_Scenarios.R")



ui <- fluidPage(
  useShinyalert(),
  useShinyjs(),
  # Application title
  titlePanel("Deriving Stress Scenarios from yield curve using PCA"),
  

      dateInput("start_date", label = h3("Start Date"),value="2004-09-06"),
      dateInput("end_date", label = h3("End Date")),
      actionButton("get_yc", "Generate stress scenario for spot rates."),
    
    # Show a plot of the generated distribution
  hidden(helpText(
    "The model calibration is based on data published by the ECB, which estimates the yield
      curve from Euro-area central government bonds. The resulting yield curve inside the selected period is displayed below.",
    id = "TextYieldCurveECB")),
      withSpinner(plotlyOutput('PlotYC')),
  hidden(helpText(
    "To reduce the complexity of the yield curve a principal component analysis (PCA) is applied to the yield curve. 
    The first prinicipal components are displayed bellow. PC1 is associated with the level of the yield curve, PC2 with the slope and PC3 with the curvature.",
    id = "TextPC1-5")),
      withSpinner(plotlyOutput('PlotPC')),
  hidden(helpText(
    "The the first three Primcipal Components already explain most of the variance in the yieldcurve. 
    To derive the relevant stress scenario it should be sufficent to stress the first three Principal Components",
    id = "TextExplainendVar")),
      withSpinner(plotlyOutput('ExplainedVariance')),
  hidden(helpText(
    "Bellow the scores of the first three principal components are shown including the rolling 99,5% quantil.",
    id = "RollingQuantil")),
      withSpinner(plotlyOutput('Stressedscores')),
  hidden(helpText(
    "Bellow the scores of the first three principal components are shown including the rolling 99,5% quantil.",
    id = "TextStressedCurve")),
      withSpinner(plotlyOutput('StressedCurve'))
  
)

server <- function(input, output) {
  v <- reactiveValues(newsmb = NULL)
  observeEvent(input$get_yc, {
    
    if (input$end_date<input$start_date){
      shinyalert("Oops!", "The start date is after the end date!", type = "error")
    }else{
      
      if (!exists("yield_curve_old")){
        yield_curve_old<- as.data.frame(storage_read_csv(cont, "ecb_spot_yield.csv"))
      }
      v$yc <-ecb_yield_curve_import(input$start_date,input$end_date,yield_curve_old)
      
      
      v$results_pca<-performm_pca(v$yc)
      v$PC<-v$results_pca[3][[1]]
      v$var_explained <-v$PC$sdev^2/sum(v$PC$sdev^2)
      v$stressed_scores <-stressed_scores(v$PC$x, v$results_pca$Date_dmy)
      v$stress_scenario_PC1<-stress_scenarios("PC1",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)
      v$stress_scenario_PC2<-stress_scenarios("PC2",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)
      v$stress_scenario_PC3<-stress_scenarios("PC3",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)  
      plot_yc <- yield_plot(as.character(input$start_date), as.character(input$end_date), v$yc)
      shinyjs::show("TextYieldCurveECB")
      shinyjs::show("TextPC1-5")
      shinyjs::show("TextExplainendVar")
      shinyjs::show("RollingQuantil")
      shinyjs::show("TextStressedCurve")
    }
    
  })
  output$PlotYC <- renderPlotly({
    if (is.null(v$yc)) return(NULL)
    #Plot the yield curve
    yield_plot(as.character(input$start_date), as.character(input$end_date), v$yc)

  })
  output$PlotPC <- renderPlotly({
    #Plot the principal components
    if (is.null(v$yc)) return(NULL)
    as.data.frame(v$PC$rotation)%>%
      plot_ly(type = 'scatter', mode = 'lines')%>%
        add_trace( y = ~PC1, name = "PC 1", hovertemplate = paste('Factor loading PC 1: %{y:.2f}')) %>%
        add_trace( y = ~PC2, name = "PC 2", hovertemplate = paste('Factor loading PC 2: %{y:.2f}')) %>%
        add_trace( y = ~PC3, name = "PC 3", hovertemplate = paste('Factor loading PC 3: %{y:.2f}')) %>%
        add_trace( y = ~PC4, name = "PC 4", hovertemplate = paste('Factor loading PC 4: %{y:.2f}'), visible = "legendonly") %>%
        add_trace( y = ~PC5, name = "PC 5", hovertemplate = paste('Factor loading PC 5: %{y:.2f}'), visible = "legendonly") 
  })
  output$ExplainedVariance <- renderPlotly({
    if (is.null(v$yc)) return(NULL)
    #Plot the variance by PC
    Line<-c(sum(v$var_explained[1:1]),sum(v$var_explained[1:2]),sum(v$var_explained[1:3]),sum(v$var_explained[1:4]),sum(v$var_explained[1:5]))
    plot_ly(x=c("PC1", "PC2", "PC3", "PC4", "PC5"), y=v$var_explained[1:5],type = "bar", name ="Explained variance", hovertemplate = paste(
      'Principal component:  %{x: %Y-%m-%d}<br>',
      'Explained variance:%{y:.2%}<br>',
      '<extra></extra>')) %>%
    add_trace(y = Line, type = 'scatter',  mode = 'lines+markers', name ="Explained variance total", hovertemplate = paste(
      'Explained variance total:%{y:.2%}<br>',
      '<extra></extra>'))
  })
  output$Stressedscores <- renderPlotly({
    if (is.null(v$yc)) return(NULL)
    #Plot the PC scores including rolling quantile
    subplot(v$stressed_scores$fig_Stress_PC1, v$stressed_scores$fig_Stress_PC2, v$stressed_scores$fig_Stress_PC3, nrows = 3, shareX = TRUE) %>% 
      layout(title = list(text = "Apllied Stress to PC1 to PC3"),
             plot_bgcolor='#e5ecf6', 
             xaxis = list( 
               zerolinecolor = '#ffff', 
               zerolinewidth = 2, 
               gridcolor = 'ffff'), 
             yaxis = list( 
               zerolinecolor = '#ffff', 
               zerolinewidth = 2, 
               gridcolor = 'ffff'))
    
    
  })
  output$StressedCurve <- renderPlotly({
    if (is.null(v$yc)) return(NULL)
    
    #Plot the stressed scenarios
    subplot(v$stress_scenario_PC1$fig_Stress_scenario, v$stress_scenario_PC2$fig_Stress_scenario, v$stress_scenario_PC3$fig_Stress_scenario, nrows = 3, shareX = TRUE) %>% 
      layout(title = list(text = paste0("Apllied Stress to yieldcurve from ", v$results_pca$Date_dmy[nrow(v$results_pca$Date_dmy),1]," via up/down quantil scores from PC1 to PC3 ")),
             plot_bgcolor='#e5ecf6', 
             xaxis = list( 
               zerolinecolor = '#ffff', 
               zerolinewidth = 2, 
               gridcolor = 'ffff'), 
             yaxis = list( 
               zerolinecolor = '#ffff', 
               zerolinewidth = 2, 
               gridcolor = 'ffff')) 
    
    
  })
  
}



# Run the app
shinyApp(ui, server)