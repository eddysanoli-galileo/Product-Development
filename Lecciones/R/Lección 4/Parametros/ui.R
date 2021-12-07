library(shiny)
library(lubridate)
library(DT)


# Define UI
shinyUI(fluidPage(

  titlePanel("Parámetros Shiny"),
  sidebarLayout(
    sidebarPanel(
      sliderInput("bins",
                  "Número de bins:", 
                  min = 1,
                  max = 50,
                  value = 30),
      selectInput("set_col",
                  "Escoger el Color:",
                  choices = c("aquamarine", "blue", "blueviolet",
                              "darkgray", "chocolate"),
                  selected = "darkgray"),
      textInput("url_param", "Marcador:", value = "")
    ),
    mainPanel(
      plotOutput("distPlot")
    )
  )
  
  
))
