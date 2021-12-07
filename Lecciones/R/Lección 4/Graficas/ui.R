library(shiny)
library(lubridate)
library(DT)


# Define UI
shinyUI(fluidPage(

  titlePanel("Interacciones de Usuario con Gráficas"),
  tabsetPanel(
    tabPanel("plot",
             h1("Gráficas en Shiny"),
             plotOutput("grafica_base_r"),
             plotOutput("Grafica_ggplot")
             ),
    tabPanel("Clicks Plots",
             fluidRow(
               column(6,
                      plotOutput("plot_click_options",
                                 click = "clk",
                                 dblclick = "dclk",
                                 hover = "mouse_hover", 
                                 brush = "mouse_brush"),
                      verbatimTextOutput("click_data")
                      ),
               column(6,
                      tableOutput("mtcars_tbl")
                      )
             ))
  )
  
))
