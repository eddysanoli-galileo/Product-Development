library(shiny)
library(lubridate)
library(DT)


# Define UI
shinyUI(fluidPage(

  titlePanel("Tarea - Shiny Plots"),
  tabsetPanel(
    tabPanel("Scatter Dots Dinámicos",
             fluidRow(
               column(6,
                      plotOutput("plot_cars",
                                 click = "clk",
                                 dblclick = "dclk",
                                 hover = "mouse_hover", 
                                 brush = "mouse_brush"),
                      verbatimTextOutput("hover_data")
                      ),
               column(6,
                      DT::dataTableOutput("mtcars_tbl")
                      )
             ))
  )
  
))
