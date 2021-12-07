library(shiny)
library(dplyr)
library(ggplot2)

shinyServer(function(input, output, session) {
  
  # Se reciben los parámetros del URL
  observe({
    query = parseQueryString(session$clientData$url_search)
    bins = query[["bins"]]
    bar_col = query[["color"]]
    
    # Si "bins" no es nulo, se cambia el valor del slider
    if(!is.null(bins)){
      updateSliderInput(session, "bins", value = as.numeric(bins))
    }
    
    # Si "color" no es nulo, se cambia el color de la gráfica
    if(!is.null(bar_col)){
      updateSelectInput(session, "set_col", selected = bar_col)
    }
  })
  
  
  observe({
    bins = input$bins
    color = input$set_col
    
    host_name = session$clientData$url_hostname
    protocol = session$clientData$url_protocol
    port = session$clientData$url_port
    query = paste("?", "bins=", bins, "&color=", color, sep = "")
    url = paste(protocol, "//", host_name, ":", port, "/", query, sep="")
    updateTextInput(session, "url_param", value = url)
  })
  
  output$distPlot = renderPlot({
    x = faithful[,2]
    hist(x, breaks = input$bins, col = input$set_col, border = "white")
  })
  
})
