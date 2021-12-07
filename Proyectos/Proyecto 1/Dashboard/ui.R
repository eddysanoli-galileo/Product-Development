library(shiny)
library(lubridate)
library(DT)
library(plotly)


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
                          uiOutput("album_cover"),
                          htmlOutput("album_info"),
                          hr(),
                          uiOutput("range_release"),
                          uiOutput("genre_select"),
                          uiOutput("song_duration"),
                          selectInput("explicit",
                                      "Contenido",
                                      choices = list("Explícito / No Explícito",
                                                     "Explícito",
                                                     "No Explícito"),
                                      selected = "Explícito / No Explícito"),
                          verbatimTextOutput("debug_out"),
                          width = 4
                        ),
                        mainPanel(
                          br(),
                          DT::dataTableOutput("songs_tbl")
                        )
                      ))
            )),
    
    tabPanel("Data Exploration",
             fluidRow(
               column(3,
                      br(),
                      uiOutput("variable_1"),
                      uiOutput("variable_2"),
                      uiOutput("variable_3"),
                      actionButton("save_plot", "Guardar Gráfica")
                      ),
               column(9,
                      plotlyOutput("exploratory_plot"))
             )),
    
    tabPanel("Statistics",
             fluidRow(
               column(6,
                      h3("Top 10 Artistas Más Populares"),
                      p("Los artistas con las canciones más populares dentro de los datos disponibles (popularidad promedio)"),
                      plotOutput("most_popular_artist")
               ),
               column(6,
                      h3("Géneros Más Explícitos"),
                      p("Géneros ordenados por el porcentaje de canciones explícitas que se incluyen dentro de dicho género"),
                      plotOutput("most_explicit_genre")
                      )
             ),
             fluidRow(
               column(12,
                      h3("Artistas Más Bailables"),
                      p("Artistas ordenados según su valor de 'danceability'"),
                      plotOutput("most_danceable_artist")
               )
             )),
    
    tabPanel("Recomendador",
             fluidRow(
               column(4,
                      br(),
                      div(style = "text-align: justify; text-justify: inter-word",
                          p("Utiliza los sliders abajo para ajustar las diferentes características que buscas en una canción. 
                             A la derecha se mostrará la canción que mejor se aproxima a tus preferencias. También se pueden
                             pasar los nombres de las características como parámetros de URL en caso se desee.")),
                      hr(),
                      h4("Características de Canción"),
                      uiOutput("slider_dance"),
                      uiOutput("slider_energy"),
                      uiOutput("slider_loud"),
                      uiOutput("slider_speech"),
                      uiOutput("slider_acoustic"),
                      uiOutput("slider_instrumental"),
                      uiOutput("slider_live"),
                      actionButton("reset_sliders", "Reset")
               ),
               column(8,
                      br(),
                      h2("Canción Recomendada"),
                      br(),
                      column(4, 
                             uiOutput("match_album_cover")),
                      column(8,
                             htmlOutput("match_album_info"),
                             verbatimTextOutput("raw_output"))
                      
                      
               )
             ))
  )
  
))
