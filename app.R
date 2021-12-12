library(shiny)
library(tidyverse)
library(plotly)
library(lubridate)
library(roll)
library(ggplot2)
library(shinyalert)
library(shinycssloaders)
library(shinyjs)
source("R/import_yield_curve.R")
source("R/3dplot_yield_curve.R")
source("R/Perform_PCA.R")
source("R/stressed_scores.R")
source("R/Stress_Scenarios.R")


yield_curve_compl<- isolate(readfromazure("ecb_spot_yield.csv"))

ui <- fluidPage(
  useShinyalert(),
  useShinyjs(),
  titlePanel("Deriving Stress Scenarios from yield curve using PCA"),
  

      dateInput("start_date", label = h3("Start Date"),value="2020-01-01"),
      dateInput("end_date", label = h3("End Date")),
      actionButton("get_yc", "Generate stress scenario for spot rates"),
      br(),br(),
      tags$a(href="https://github.com/bt1985/pca_spotrates", "Please find the source code and a detailed documentation here.",id = "LinkDocumentation"),  
      hidden(helpText(
                  "The model calibration is based on data published by the ECB, which estimates the yield
                  curve from Euro-area central government bonds. The resulting yield curve inside the selected period is displayed below.",
      id = "TextYieldCurveECB")),
      withSpinner(plotlyOutput('PlotYC')),
      hidden(helpText(
        "To reduce the complexity of the yield curve a principal component analysis (PCA) is applied to the yield curve. 
        The first prinicipal components are displayed below. PC1 is associated with the level of the yield curve, PC2 with the slope and PC3 with the curvature.",
        id = "TextPC1-5")),
          withSpinner(plotlyOutput('PlotPC')),
      hidden(helpText(
        "The first three Primcipal Components already explain most of the variance in the yield curve. 
        To derive the relevant stress scenario it should be sufficent to stress the first three Principal Components",
        id = "TextExplainendVar")),
          withSpinner(plotlyOutput('ExplainedVariance')),
      hidden(helpText(
        "Below the scores of the first three principal components are shown including the rolling 99,5% quantil.",
        id = "RollingQuantil")),
          withSpinner(plotlyOutput('Stressedscores')),
      hidden(helpText(
        "Below the scores of the first three principal components are shown including the rolling 99,5% quantil.",
        id = "TextStressedCurve")),
          withSpinner(plotlyOutput('StressedCurve'))
      
)

server <- function(input, output) {
  v <- reactiveValues(newsmb = NULL)
  observeEvent(input$get_yc, {
    v$yc<-NULL
    v$results_pca<-NULL
    v$PC<-NULL
    v$var_explained <-NULL
    v$stressed_scores <-NULL
    v$stress_scenario_PC1<-NULL
    v$stress_scenario_PC2<-NULL
    v$stress_scenario_PC3<-NULL

    if (input$end_date<input$start_date){
      shinyalert("Oops!", "The start date is after the end date!", type = "error")
    }else{
      
      if (!exists("yield_curve_compl")){
        yield_curve_compl<- isolate(readfromazure("ecb_spot_yield.csv"))
      }
      v$yc <-ecb_yield_curve_import(input$start_date,input$end_date,yield_curve_compl)
      v$results_pca<-performm_pca(v$yc)
      v$PC<-v$results_pca[3][[1]]
      v$var_explained <-v$PC$sdev^2/sum(v$PC$sdev^2)
      v$stressed_scores <-stressed_scores(v$PC$x, v$results_pca$Date_dmy)
      v$stress_scenario_PC1<-stress_scenarios("PC1",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)
      v$stress_scenario_PC2<-stress_scenarios("PC2",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)
      v$stress_scenario_PC3<-stress_scenarios("PC3",v$results_pca$Date_dmy,v$stressed_scores$PC_stress,v$PC$rotation,v$yc,v$results_pca$mu)  
      shinyjs::show("LinkDocumentation")
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
        add_trace( y = ~PC1, x= str_replace(rownames(v$PC$rotation),"SR_",""), name = "PC 1", hovertemplate = paste('Factor loading PC 1: %{y:.2f}', '<br>Maturity:%{x}')) %>%
        add_trace( y = ~PC2, x= str_replace(rownames(v$PC$rotation),"SR_",""), name = "PC 2", hovertemplate = paste('Factor loading PC 2: %{y:.2f}', '<br>Maturity:%{x}')) %>%
        add_trace( y = ~PC3, x= str_replace(rownames(v$PC$rotation),"SR_",""), name = "PC 3", hovertemplate = paste('Factor loading PC 3: %{y:.2f}', '<br>Maturity:%{x}')) %>%
        add_trace( y = ~PC4, x= str_replace(rownames(v$PC$rotation),"SR_",""), name = "PC 4", hovertemplate = paste('Factor loading PC 4: %{y:.2f}', '<br>Maturity:%{x}'), visible = "legendonly") %>%
        add_trace( y = ~PC5, x= str_replace(rownames(v$PC$rotation),"SR_",""), name = "PC 5", hovertemplate = paste('Factor loading PC 5: %{y:.2f}', '<br>Maturity:%{x}'), visible = "legendonly") 
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
      layout(title = list(text = "Applied Stress to PC1 to PC3"),
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
      layout(title = list(text = paste0("Applied Stress to yield curve from ", v$results_pca$Date_dmy[nrow(v$results_pca$Date_dmy),1]," via up/down quantil scores from PC1 to PC3 ")),
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