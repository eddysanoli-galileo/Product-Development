library(shiny)
library(dplyr)
library(ggplot2)

shinyServer(function(input, output, session) {
  
  output$grafica_base_r = renderPlot({
    plot(mtcars$wt, mtcars$mpg,
         xlab = "wt", ylab = "Millas por Galón")
  })
  
  output$Grafica_ggplot = renderPlot({
    diamonds %>% 
      ggplot(aes(x = carat, y = price, color = color)) +
      geom_point() + 
      ylab("Precio") + 
      xlab("Kilates") + 
      ggtitle("Precio de diamantes por kilate")
  })
  
  output$plot_click_options = renderPlot({
    plot(mtcars$wt, mtcars$mpg,
         xlab = "wt", ylab = "Millas por Galón")
  })
  
  output$click_data = renderPrint({
    rbind(
      c(input$clk$x, input$clk$y),
      c(input$dclk$x, input$dclk$y),
      c(input$mouse_hover$x, input$mouse_hover$y),
      c(input$mouse_brush$xmin, input$mouse_brush$ymin),
      c(input$mouse_brush$xmax, input$mouse_brush$ymax)
    )
  })
  
  output$mtcars_tbl = renderTable({
    # Obtener valores cercanos a click
    df = nearPoints(mtcars, input$clk, xvar = "wt", yvar = "mpg")
    df = brushedPoints(mtcars, input$mouse_brush,
                       xvar = "wt", "mpg")
  })
  
})
