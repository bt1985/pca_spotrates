yield_plot <- function(start, stop, yield_data) {
  plot_data <- filter(yield_data, Date <= stop & Date >= start)
  plot_data_ordered <- plot_data[order(plot_data$Date),]
  x <- plot_data_ordered$Date
  y <- str_replace(colnames(plot_data_ordered[,2:ncol(plot_data_ordered)]),"SR_","")#names(plot_data_ordered)[!grepl("Date", names(plot_data_ordered))]
  z <- plot_data_ordered %>% 
    select(-Date) %>% 
    as.matrix() %>% 
    t()
  
  plot_ly(x = x, y = y, z = z, type = "surface",
          opacity = 0.9,
          name="Spot Rates",
          hovertemplate = paste(
            'Date:  %{x: %Y-%m-%d}<br>',
            'Maturity:      %{y}<br>',
            'Spot Rate: %{z:.2f} %<br>',
            '<extra></extra>'
          ),) %>% 
    layout(
           scene = list(xaxis = list(title = 'Date', 
                                     titlefont = list(size = 15),
                                     tickfont = list(size = 12),
                                     #backgroundcolor = "#FFFFFF",
                                     #gridcolor = "#000000",
                                     showbackground = FALSE),
                        yaxis = list(title = 'Maturity', 
                                     titlefont = list(size = 15),
                                     tickfont = list(size = 12),
                                     #backgroundcolor = "#FFFFFF",
                                     #gridcolor = "#000000",
                                     showbackground = FALSE),
                        zaxis = list(title = 'Yield (%)', 
                                     titlefont = list(size = 15),
                                     tickfont = list(size = 12),
                                     #backgroundcolor = "#FFFFFF",
                                     #gridcolor = "#000000",
                                     showbackground = FALSE),
                        aspectmode = "manual",
                        aspectratio = list(x = 5, y = 1, z = 1),
                        camera = list(eye = list(x = 1.25, y = -3, z =1.25))
                        )) 
}

