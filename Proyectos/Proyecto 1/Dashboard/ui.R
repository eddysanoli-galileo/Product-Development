library(shiny)
library(lubridate)
library(DT)


# Define UI
shinyUI(fluidPage(

  titlePanel("Spotify Genre Audio Features"),
  p("El dataset en cuestión contiene el género, caracterísiticas de audio, data 
     de lanzamiento y el link de portada de album para diferentes canciones en Spotify.
     Obtenido de: https://www.kaggle.com/naoh1092/spotify-genre-audio-features"),
  br(),
  
  tabsetPanel(
    tabPanel("Raw Data",
             fluidRow(
               column(12,
                      sidebarLayout(
                        sidebarPanel(
                          htmlOutput("album_cover"),
                          dateRangeInput("range_release", 
                                         "Fecha de Lanzamiento",
                                         max = today(),
                                         min = today() - 365,
                                         start = today() - 7,
                                         end = today(),
                                         language = "es",
                                         weekstart = 1,
                                         separator = "a",
                                         format = "dd-mm-yyyy"),
                          radioButtons("radio_in", "Seleccione Género",
                                       choices = c("Masculino", "Femenino", "Otro"),
                                       selected = "Femenino", 
                                       inline = F),
                          verbatimTextOutput("debug_out")
                        ),
                        mainPanel(
                          DT::dataTableOutput("songs_tbl")
                        )
                      ))
            ))
  )
  
))
