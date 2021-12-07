library(shiny)
library(lubridate)
library(DT)


# Define UI
shinyUI(fluidPage(

  titlePanel("Tablas con DT"),
  tabsetPanel(tabPanel("Tablas en DT", 
                       h1("Vista Básica"),
                       fluidRow(
                         column(12, DT::dataTableOutput("tabla_1"))
                       ),
                       h1("Agregar Filtros"),
                       fluidRow(
                         column(12, DT::dataTableOutput("tabla_2"))
                       )),
              tabPanel("Click en Tablas", 
                       fluidRow(
                         column(6,
                                h2("Single Select Row"),
                                DT::dataTableOutput("tabla_3"),
                                verbatimTextOutput("output_1")),
                         column(6,
                                h2("Multiple Select Row"),
                                DT::dataTableOutput("tabla_4"),
                                verbatimTextOutput("output_2"))
                       ),
                       fluidRow(
                         column(6,
                                h2("Single Select Column"),
                                DT::dataTableOutput("tabla_5"),
                                verbatimTextOutput("output_3")),
                         column(6,
                                h2("Multiple Select Column"),
                                DT::dataTableOutput("tabla_6"),
                                verbatimTextOutput("output_4"))
                       ),
                       fluidRow(
                         column(6,
                                h2("Single Select Cell"),
                                DT::dataTableOutput("tabla_7"),
                                verbatimTextOutput("output_5")),
                         column(6,
                                h2("Multiple Select Cell"),
                                DT::dataTableOutput("tabla_8"),
                                verbatimTextOutput("output_6"))
                       ),
                       ))
  
))
