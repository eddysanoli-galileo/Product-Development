library(shiny)
library(dplyr)
library(ggplot2)
library(readxl)

shinyServer(function(input, output, session) {
  
  # ====================================
  # Carga inicial de datos
  # ====================================
  
  # Carga de datos
  df = read_excel("dataset/spotify_genre_final.xlsx", sheet = "data")
  
  # Se elimina la columna de ID para evitar redundancia
  #df$release_date_precision = NULL
  df$id = NULL
  #df$Album_cover_link = NULL
  
  # ====================================
  # OUTPUT: Tabla de datos Spotify
  # ====================================
  
  output$songs_tbl = DT::renderDataTable({
    
    df_out = 
      df %>% DT::datatable(df, selection = list(mode = "single", target = "row"))
    
    return(df_out)
  })
  
  # ====================================
  # OUTPUT: Print para Debugging
  # ====================================
  
  output$debug_out = renderPrint({
    album_selected = df[input$songs_tbl_rows_selected, "Album_cover_link"]
    
    c('<img src="', album_selected[[1]], '">')
  })
  
  # ====================================
  # OUTPUT: Album Cover
  # ====================================
  
  output$album_cover = renderText({
    
    album_selected = df[input$songs_tbl_rows_selected, "Album_cover_link"]
    
    if (nrow(album_selected) == 0){
      list(src = "logo_spotify.png", width = "90%")
      #c('<img src="', "logo_spotify.png", '">')
    }
    else {
      c('<img src="', album_selected[[1]], '" width = 95%>')
      #list(src = "https://i.scdn.co/image/ab67616d0000b273c8a11e48c91a982d086afc69", width = "90%")
    }
    
  })
  
})
