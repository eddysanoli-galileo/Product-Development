library(shiny)
library(dplyr)
library(ggplot2)

shinyServer(function(input, output, session) {
  
  # =====================
  # COLORES
  
  sel_color = "green"
  hov_color = "grey"
  def_color = "black"
  
  # =====================
  # VARIABLES REACTIVAS
  
  # Array con los colores para cada punto
  data_point = reactiveValues(
    col = rep(def_color, nrow(mtcars))
  )
  
  # Array con los puntos a incluir en la tabla 
  clicked_points = reactiveValues(
    data = mtcars[0,]
  )
  
  # Array con los colores de los puntos antes de haber hecho hover
  prev_colors = reactiveValues(
    col = rep(def_color, nrow(mtcars))
  )
  
  
  out = reactiveValues(
    data = mtcars[0,]
  )
  
  # =====================
  # EVENTO: Click
  observeEvent(input$clk, {
    
    # Se obtiene el punto más cercano al lugar donde se hizo click
    # Se crea un array con las coordenadas X y Y del punto clickeado
    # (Solo se toma la primera fila del dataframe para evitar problemas)
    sel_point = nearPoints(mtcars, input$clk, xvar = "wt", yvar = "mpg")
    sel_coords = c("x" = sel_point[1, "wt"], "y" = sel_point[1, "mpg"])
    
    # Si las coordenadas no están vacías
    # - Se colorea el punto de verde si se le hizo click
    # - De lo contrario se colorea negro
    if (nrow(sel_point) != 0){
      data_point$col = ifelse(
        (mtcars$wt == sel_coords["x"] & mtcars$mpg == sel_coords["y"]) | (data_point$col == sel_color), 
        sel_color, def_color)
    }
    
  })
  
  # =====================
  # EVENTO: Brush
  observeEvent(input$mouse_brush, {
    
    # Se obtienen los puntos a los que se les hizo brush
    sel_points = brushedPoints(mtcars, input$mouse_brush, xvar = "wt", "mpg")
    
    # Si las coordenadas no están vacías
    # - Se colorea el punto de verde si se le hizo click
    # - De lo contrario se colorea negro
    if (nrow(sel_points) != 0){
      data_point$col = ifelse(
        (mtcars$mpg %in% sel_points$mpg & mtcars$wt %in% sel_points$wt) |
        (data_point$col == sel_color),
        sel_color, def_color)
    }
    
  })
  
  # =====================
  # EVENTO: Doble Click
  observeEvent(input$dclk, {
    
    # Se obtiene el punto más cercano al lugar donde se hizo doble click
    # Se crea un array con las coordenadas X y Y del punto doble-clickeado
    # (Solo se toma la primera fila del dataframe para evitar problemas)
    sel_point = nearPoints(mtcars, input$dclk, xvar = "wt", yvar = "mpg")
    sel_coords = c("x" = sel_point[1, "wt"], "y" = sel_point[1, "mpg"])
    
    # Si las coordenadas no están vacías
    # - Se colorea de negro el punto doble-clickeado si ya era verde
    # - De lo contrario se mantiene el color del punto
    if (nrow(sel_point) != 0){
      data_point$col = ifelse(
        (mtcars$wt == sel_coords["x"] & mtcars$mpg == sel_coords["y"]) & 
        ((data_point$col == sel_color) | (prev_colors$col == sel_color)), 
        def_color, data_point$col)
    }
    
  })
  
  # =====================
  # EVENTO: Hover
  observeEvent(input$mouse_hover, {
    sel_point = nearPoints(mtcars, input$mouse_hover, xvar = "wt", yvar = "mpg")
    sel_coords = c("x" = sel_point[1, "wt"], "y" = sel_point[1, "mpg"])
    
    if (nrow(sel_point) != 0){
      
      # Si se encuentra un punto rojo, este se resetea al color que tenía antes
      if (any(data_point$col == hov_color)){
        data_point$col = prev_colors$col
      }
      
      # Se guardan los colores antes de colorearlo de rojo
      prev_colors$col = data_point$col 
      
      # Se setean los colores de los puntos seleccionados
      data_point$col = ifelse(mtcars$wt == sel_coords["x"] & mtcars$mpg == sel_coords["y"], hov_color, data_point$col)
    }
    else {
      data_point$col = ifelse(data_point$col == hov_color, prev_colors$col, data_point$col)
    }
  })
  
  # =====================
  # PLOT: Data de MTCars
  output$plot_cars = renderPlot({
    
    # SI: Todos los colores de los data points están dentro de la lista dada
    if (all(is.element(data_point$col, c(hov_color, def_color, sel_color)))){
      
      plot(mtcars$wt, mtcars$mpg,
           xlab = "Peso", ylab = "Millas por Galón",
           pch = 16, cex = 2,
           col = data_point$col)
    }
    
    # Mouse NO está cerca de ningún punto
    else {
      plot(mtcars$wt, mtcars$mpg,
           xlab = "Peso", ylab = "Millas por Galón",
           pch = 16, cex = 2)
    }
  })
  
  # =====================
  # OUTPUT: Tabla al hacer "brush"
  output$mtcars_tbl = DT::renderDataTable({
    
    # Si se hizo brush:
    # Se despliegan los datos de los puntos "brusheados"
    if (!is.null(input$mouse_brush)){
      brushed_points = brushedPoints(mtcars, input$mouse_brush, xvar = "wt", "mpg")
    }
    
    # Si se hizo click:
    # Se despliegan los datos de los puntos "clickeados"
    else if (!is.null(input$clk)){
      clicked_points$data = nearPoints(mtcars, input$clk, xvar = "wt", yvar = "mpg")
      brushed_points = mtcars[0,]
    }
    
    # Si no se hizo brush o click:
    # Se asume que ningún punto fue brusheado
    else {
      brushed_points = mtcars[0,]
    }
    
    # La tabla desplegada consiste de una combinación
    # de los puntos brusheados y los puntos clickeados
    df = rbind(brushed_points, clicked_points$data)
    
  })
  
  # =====================
  # OUTPUT: Print para debugging
  output$hover_data = renderPrint({
    hover_points = nearPoints(mtcars, input$mouse_hover, xvar = "wt", yvar = "mpg")
    
    if (nrow(hover_points) == 0){
      print("El cursor no se ha aproximado a ningún punto")
    }
    else{
      cat(paste0(
        "Coordenadas de Punto Cercano al Cursor:\n",
        "X (wt): ", hover_points[1, "wt"],
        " Y (mpg): ", hover_points[1, "mpg"]
      ))
    }
  })
  
})
