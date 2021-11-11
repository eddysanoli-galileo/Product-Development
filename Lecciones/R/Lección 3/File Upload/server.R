library(shiny)
library(dplyr)

# NOTAS:

# Para debugging utilizar "browser()":
# Este comando detiene la app donde se colocó "browser" y luego se 
# puede chequear en consola el valor de las diferentes variables.

# Para no importar todo un paquete se puede utilizar "paquete::función"

shinyServer(function(input, output) {
  
  archivo_cargado = reactive({
    # browser()
    contenido_archivo = input$cargar_archivo

    if(is.null(contenido_archivo)){
      return(NULL)
    }
    
    # Si es un CSV
    if(stringr::str_detect(contenido_archivo$name, "csv")){
      out = readr::read_csv(contenido_archivo$datapath)
    }
    
    # Si el CSV no está separado por comas
    else if(stringr::read_csv()){
      out = readr::read_tsv(contenido_archivo$datapath)
    }
    
    # Si el archivo no está soportado
    else {
      out = data.frame(extension_archivo="La extensión del archivo no es compatible")
    }
    
    # Filtrar por las fechas en el rango dado
    if (!is.null(contenido_archivo)){
      
      out = out %>% 
        mutate(Date = ymd(Date)) %>% 
        filter(Date >= input$fechas[1],
               Date <= input$fechas[2])
    }
    
    return(out)
    
  })
  
  # Función para cambiar data frame según filtro de fecha
  output_df = reactive({
    
    # Filtrar por las fechas en el rango dado
    if (!is.null(archivo_cargado())){
      
      out = archivo_cargado() %>% 
        mutate(Date = ymd(Date)) %>% 
        filter(Date >= input$fechas[1],
               Date <= input$fechas[2])
      
      return(out)
    }
    
    return(NULL)
  })
  
  # Renderizar tabla en pantalla
  output$contenido_archivo = DT::renderDataTable({
    DT::datatable(output_df())
  })
  
  # Descargar archivo
  output$download_dataframe = downloadHandler(
    filename = function(){
      paste("data-", Sys.Date(), ".csv", sep = "")
    },
      
    content = function(file){
      write.csv(archivo_cargado(), file)
    }
    
  )
  
})
