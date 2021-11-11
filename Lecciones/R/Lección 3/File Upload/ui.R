library(shiny)
library(lubridate)


# Define UI for application that draws a histogram
shinyUI(fluidPage(

    # Application title
    titlePanel("Cargar Archivos a Shiny"),
    
    sidebarLayout(
      
      # Sidebar
      sidebarPanel(
        
        fileInput("cargar_archivo", "Cargar archivo", 
                  buttonLabel = "Seleccionar",
                  placeholder = "No existen archivos seleccionados"),
        
        dateRangeInput("fechas", "Seleccione fechas",
                       start = ymd("1900-01-05"),
                       end = ymd("2007-09-30"),
                       min = ymd("1900-01-05"),
                       max = ymd("2007-09-30")
        ),
        
        downloadButton("download_dataframe",
                       "Descargar Archivo")
        
      ),
      
      # Panel principal
      mainPanel(
        
        # Para no tener que cargar la librería completa se puede usar DT::
        DT::dataTableOutput("contenido_archivo")
                
      )
    )
))
