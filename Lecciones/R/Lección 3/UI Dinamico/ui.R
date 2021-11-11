library(shiny)
library(lubridate)


# Define UI
shinyUI(fluidPage(

    # Application title
    titlePanel("Cargar Archivos a Shiny"),
    
    tabsetPanel(tabPanel("Ejemplo 1", 
                         numericInput("min", "Límite inferior", value = 5),
                         numericInput("max", "Límite superior", value = 10),
                         sliderInput("slider_eje1", "Seleccione un intervalo",
                                     min = 0,
                                     max = 15,
                                     value = 5)
                         ),
                
                tabPanel("Ejemplo 2", 
                         sliderInput("s1", "s1", value = 0, min = -5, max = 5),
                         sliderInput("s2", "s2", value = 0, min = -5, max = 5),
                         sliderInput("s3", "s3", value = 0, min = -5, max = 5),
                         sliderInput("s4", "s4", value = 0, min = -5, max = 5),
                         actionButton("clean", "Limpiar")),
                
                tabPanel("Ejemplo 3", 
                         numericInput("n", "Corridas", value = 10),
                         actionButton("correr", "Ejecutar n veces")),
                
                tabPanel("Ejemplo 4",
                         numericInput("nvalue", "Valor", value = 0)),
                
                tabPanel("Ejemplo 5",
                         numericInput("celsius", "Temperatura en °C",
                                      value = NA, step = 1),
                         numericInput("farenheit", "Temperatura en °C",
                                      value = NA, step = 1)),
                
                tabPanel("Ejemplo 6",
                         selectInput("dist", "Distribución", 
                                     choices = c("Normal", "Uniforme", "Exponencial")),
                         numericInput("nrandom", "Número de muestras", 
                                      min = 0, 
                                      value = 100),
                         tabsetPanel(id = "params", type="hidden", 
                                     tabPanel("Normal",
                                              numericInput("media", "Media", value = 0),
                                              numericInput("sd", "SD", value = 1)
                                              ),
                                     tabPanel("Uniforme",
                                              numericInput("uni_min", "min", value = 0),
                                              numericInput("uni_max", "max", value = 1)
                                              ),
                                     tabPanel("Exponencial", 
                                              numericInput("razon", "razon", value = 1, min = 0)
                                              )
                                    ),
                         
                         plotOutput("plot_dist")
                        )
        )
))
