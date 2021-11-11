library(shiny)
library(lubridate)

# Opciones para el slider animado abajo.
animationOptions(interval = 500, loop = TRUE)


# Define UI for application that draws a histogram
shinyUI(fluidPage(

    # Application title
    titlePanel("Titulo del App"),
    
    sidebarLayout(
      
      # Sidebar
      sidebarPanel(
        
        # Slider individual
        sliderInput("slider_in", "Seleccione un valor", 
                    min = 0, 
                    max = 100, 
                    value = 50,
                    step = 10,
                    post = "%",
                    animate = animationOptions(interval = 500, loop = TRUE),
        ),
        
        # Slider rango
        sliderInput("slider_multi", "Seleccione un rango",
                    min = -10,
                    max = 10,
                    value = c(-5,5)
        ),
        
        numericInput("num_in", "Ingrese un numero",
                    min = 0,
                    max = 50,
                    value = 25
        ),
        
        dateInput("single_date", "Fecha de Cumpleaños",
                  value = today(),
                  language = "es",
                  weekstart = 1,
                  format = "dd-mm-yyyy"
                  ),
        
        dateRangeInput("range_date", "Seleccione Rango de Fechas",
                       max = today(),
                       min = today() - 365,
                       start = today() - 7,
                       end = today(),
                       language = "es",
                       weekstart = 1,
                       separator = "a",
                       format = "dd-mm-yyyy"),
        
        checkboxInput("single_check", 
                      "Mostrar", 
                      value = TRUE),
        
        checkboxGroupInput("multi_check", "Seleccione Nivel",
                           choices = 1:5,
                           selected = 1),
        
        radioButtons("radio_in", "Seleccione Género",
                     choices = c("Masculino", "Femenino", "Otro"),
                     selected = "Femenino", 
                     inline = F),
        
        actionButton("action_btn", "Refrescar"),
        br(),
        actionLink("action_link", "Salir"), 
        br(),
        
        # Utilizado para que la Shiny App no se auto-actualice, sino que 
        # únicamente se actualice luego de presionar "Ejecutar"
        submitButton("Ejecutar")
        
      ),
      
      # Panel principal
      mainPanel(
        h1("Salidas de los inputs de Shiny"),
        hr(),
        
        h2("Slider IO"),
        verbatimTextOutput("single_slider_out"),
        
        h2("Slider Rango IO"),
        verbatimTextOutput("multi_slider_out"),
        
        h2("Numeric IO"),
        verbatimTextOutput("num_out"),
        
        h2("Date IO"),
        verbatimTextOutput("single_date_out"),
        
        h2("Date Range IO"),
        verbatimTextOutput("range_date_out"),
        
        h2("Checkbox IO"),
        verbatimTextOutput("check_out"),
        
        h2("Checkbox Group IO"),
        verbatimTextOutput("check_group_out"),
        
        h2("Radio IO"),
        verbatimTextOutput("radio_out"),
        
        h2("Action Button IO"),
        verbatimTextOutput("ab_out"),
        
        h2("Action Link IO"),
        verbatimTextOutput("al_out"),
      )
    )
))
