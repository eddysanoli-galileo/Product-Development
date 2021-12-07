library(shiny)
library(dplyr)
library(ggplot2)

shinyServer(function(input, output, session) {
  
  # TABLA 1:
  output$tabla_1 = DT::renderDataTable({
    mtcars %>% 
      DT::datatable(rownames = FALSE,
                    filter = "top",
                    # Para habilitar botones
                    extensions = "Buttons",
                    # Opciones generales de display
                    options = list(
                      pageLength = 5,
                      lengthMenu = c(5,10,15),
                      dom="Bfrtip",
                      buttons=c("csv")
                    ))
  })
  
  # TABLA 2:
  # Tabla para agregar filtros
  output$tabla_2 = DT::renderDataTable({
    diamonds %>% 
      # Se agregan nuevas columnas
      mutate(vol = x*y*z,
             vol_promedio = mean(vol),
             volp = vol / vol_promedio
             ) %>% 
      DT::datatable() %>% 
      # Se formatea el precio como moneda
      formatCurrency(columns = "price", currency = "$") %>% 
      # Porcentajes con dos dígitos
      formatPercentage(columns = "volp", digits = 2)
  })
  
  
  # TABLA 3:
  # Tabla para selección individual filas
  output$tabla_3 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "single", target = "row"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_1 = renderPrint({
    input$tabla_3_rows_selected
  })
  
  
  # TABLA 4:
  # Tabla para multiple selección filas
  output$tabla_4 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "multiple", target = "row"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_2 = renderPrint({
    input$tabla_4_rows_selected
  })
  
  
  # TABLA 5:
  # Tabla para selección individual filas
  output$tabla_5 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "single", target = "column"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_3 = renderPrint({
    input$tabla_5_columns_selected
  })
  
  
  # TABLA 6:
  # Tabla para multiple selección filas
  output$tabla_6 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "multiple", target = "column"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_4 = renderPrint({
    input$tabla_6_columns_selected
  })
  
  
  # TABLA 7:
  # Tabla para selección individual filas
  output$tabla_7 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "single", target = "cell"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_5 = renderPrint({
    input$tabla_7_cells_selected
  })
  
  
  # TABLA 8:
  # Tabla para multiple selección filas
  output$tabla_8 = DT::renderDataTable({
    mtcars %>% DT::datatable(selection = list(mode = "multiple", target = "cell"))
  })
  
  # Despliegue de la fila seleccionada
  output$output_6 = renderPrint({
    input$tabla_8_cells_selected
  })
  
})
