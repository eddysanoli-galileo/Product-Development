library(shiny)
library(dplyr)
library(ggplot2)
library(readxl)
library(lubridate)
library(plotly)

shinyServer(function(input, output, session) {
  
  # %%%%%%%%%%%%%%%%%%%%%
  # RAW DATA
  # %%%%%%%%%%%%%%%%%%%%%
  
  # ====================================
  # Carga inicial de datos
  # ====================================
  
  # Carga de datos
  df = read_excel("dataset/spotify_genre_final.xlsx", sheet = "data")
  
  # Se agrega mes y día a la "release-date" de albumes con solo año
  df[df$release_date_precision == "year", ]$release_date = paste(
    df[df$release_date_precision == "year", ]$release_date, "-01-01", sep="")
  
  # Columna de duración en segundos
  # (Se reordenan las columnas para que la duración en segundos esté al lado de la de milisegundos)
  df$duration_s = df$duration_ms / 1000
  df = df[,c(1:5, length(names(df)), 6:length(names(df))-1)]
  df$duration_ms = NULL
  
  # ====================================
  # INPUTS
  # ====================================
  
  # Rango de fechas
  output$range_release = renderUI({
    dateRangeInput(inputId = "range_release", 
                   label = "Fecha de Lanzamiento",
                   max = max(df$release_date),
                   min = min(df$release_date),
                   start = min(df$release_date),
                   end = max(df$release_date),
                   language = "es",
                   weekstart = 1,
                   separator = "a",
                   format = "dd-mm-yyyy")
  })
  
  # Géneros
  output$genre_select = renderUI({
    checkboxGroupInput(inputId = "genre_select", 
                       label = "Géneros",
                       choiceNames = tools::toTitleCase(unique(df$Genre)),
                       choiceValues = unique(df$Genre),
                       selected = unique(df$Genre),
                       inline = TRUE)
  })
  
  # Rango de duración en segundos
  output$song_duration = renderUI({
    sliderInput(inputId = "song_duration",
                label = "Duración (s)",
                min = floor(min(df$duration_s)),
                max = ceiling(max(df$duration_s)),
                value = c(floor(min(df$duration_s)), ceiling(max(df$duration_s))),
                round = TRUE,
                step = 1)
  })
  
  # ====================================
  # OUTPUT: Tabla de datos Spotify
  # ====================================
  
  output$songs_tbl = DT::renderDataTable({
    
    # Exclusión de columnas en dataframe
    df_in = df[, !names(df) %in% 
                 c("Album_cover_link", "release_date_precision", "id", "mode", 
                   "key", "duration_ms")]
    
    # Aplicación de filtros:
    # - Género
    # - Fecha de lanzamiento
    # - Duración de canción
    df_in = df_in %>%
      filter(release_date > input$range_release[1],
             release_date < input$range_release[2],
             Genre %in% input$genre_select,
             duration_s > input$song_duration[1],
             duration_s < input$song_duration[2])
    
    # Filtro de contenido explícito
    if (input$explicit == "Explícito"){
      df_in = df_in %>% 
        filter(explicit == TRUE)
    } 
    else if(input$explicit == "No Explícito"){
      df_in = df_in %>% 
        filter(explicit == FALSE)
    }
    
    # Dataframe con selección de filas individuales 
    df_out = 
      df_in %>% DT::datatable(df, selection = list(mode = "single", target = "row"))
    
    return(df_out)
  })
  
  # ====================================
  # OUTPUT: Print para Debugging
  # ====================================
  
  output$debug_out = renderPrint({
    
    input$songs_tbl_rows_selected

  })
  
  # ====================================
  # OUTPUT: Album Cover
  # ====================================
  
  output$album_cover = renderUI({
    
    # Filtros de género, fecha de lanzamiento y duración de canción
    df_filtered = df %>%
      filter(release_date > input$range_release[1],
             release_date < input$range_release[2],
             Genre %in% input$genre_select,
             duration_s > input$song_duration[1],
             duration_s < input$song_duration[2])
    
    # Filtro de contenido explícito
    if (input$explicit == "Explícito"){
      df_filtered = df_filtered %>% 
        filter(explicit == TRUE)
    } 
    else if(input$explicit == "No Explícito"){
      df_filtered = df_filtered %>% 
        filter(explicit == FALSE)
    }
    
    # URI para las imágenes de cada album
    album_cover = df_filtered[input$songs_tbl_rows_selected, "Album_cover_link"]
    
    # Si no se ha seleccionado album:
    # - Se codifica en base 64 el placeholder
    # - Se muestra usando una tag "img"
    if (nrow(album_cover) == 0){
      b64 <- base64enc::dataURI(file="logo_spotify.png", mime="image/png")
      img(src = b64, width = "90%", style="border-radius: 10%")
    }
    
    # Si se seleccionó un album:
    # - Se muestra la imagen en la columna "Album_cover_link"
    else {
      img(src = album_cover[[1]], width = "90%", style="border-radius: 10%")
    }
    
  })
  
  # ====================================
  # OUTPUT: Album Info
  # ====================================
  
  output$album_info = renderText({
    
    # Filtros de género, fecha de lanzamiento y duración de canción
    df_filtered = df %>%
      filter(release_date > input$range_release[1],
             release_date < input$range_release[2],
             Genre %in% input$genre_select,
             duration_s > input$song_duration[1],
             duration_s < input$song_duration[2])
    
    # Filtro de contenido explícito
    if (input$explicit == "Explícito"){
      df_filtered = df_filtered %>% 
        filter(explicit == TRUE)
    } 
    else if(input$explicit == "No Explícito"){
      df_filtered = df_filtered %>% 
        filter(explicit == FALSE)
    }
    
    song_name = df_filtered[input$songs_tbl_rows_selected, "Title"]
    artist_name = df_filtered[input$songs_tbl_rows_selected, "Artist"]
    song_id = df_filtered[input$songs_tbl_rows_selected, "id"]
    
    
    if (nrow(song_name) == 0){
      c("", "")
    }
    else {
      c('<a ', paste('href="https://open.spotify.com/track/', song_id[[1]], sep = "") ,'">
        <h4>',song_name[[1]],'</h4></a>',
        '<p style="line-height:0.7">', artist_name[[1]],'</p>')
    }
    
  })
  
  # %%%%%%%%%%%%%%%%%%%%%
  # DATA EXPLORATION
  # %%%%%%%%%%%%%%%%%%%%%
  
  
  # ====================================
  # INPUTS
  # ====================================
  
  # Selección de Primera Variable
  output$variable_1 = renderUI({
    
    # Extrae las columnas numéricas del dataframe
    numeric_cols = names(select(df, where(is.numeric)))
    
    # Excluye algunas columnas
    numeric_cols = numeric_cols[!(numeric_cols %in% c("duration_ms", "mode", "key"))]
    
    selectInput("variable_1", 
                "Variable 1", 
                choices = numeric_cols,
                selected = numeric_cols[1])
  })
  
  # Selección de Segunda Variable
  output$variable_2 = renderUI({
    
    # Extrae las columnas numéricas del dataframe
    numeric_cols = names(select(df, where(is.numeric)))
    
    # Excluye algunas columnas
    numeric_cols = numeric_cols[!(numeric_cols %in% c("duration_ms", "mode", "key", input$variable_1))]
    
    # Se agrega el elemento "None"
    numeric_cols = append(numeric_cols, "NONE")
    
    selectInput("variable_2", 
                "Variable 2", 
                choices = numeric_cols,
                selected = "NONE")
  })
  
  # Selección de Tercera Variable
  output$variable_3 = renderUI({
    
    if (input$variable_2 != "NONE"){
      
      # Extrae las columnas numéricas del dataframe
      numeric_cols = names(select(df, where(is.numeric)))
      
      # Excluye algunas columnas
      numeric_cols = numeric_cols[!(numeric_cols %in% c("duration_ms", "mode", "key", input$variable_1, input$variable_2))]
      
      # Se agrega el elemento "None"
      numeric_cols = append(numeric_cols, "NONE")
      
      selectInput("variable_3", 
                  "Variable 3", 
                  choices = numeric_cols,
                  selected = "NONE")
    }
    
    
  })
  
  # ====================================
  # OUTPUTS
  # ====================================
  
  # Debugging
  output$debug_out2 = renderPrint({
    
    fig
    
  })
  
  
  # Valor persistente para la figura
  fig = reactiveValues(plot = NULL)
  
  # Plot
  output$exploratory_plot = renderPlotly({
    
    if (input$variable_2 == "NONE"){
      
      data = df[, input$variable_1]
      colnames(data)[1] = "var1"
      
      # Cálculo de densidad de la variable seleccionada
      densidad = density(data$var1)
      
      fig$plot = plot_ly(x = ~densidad$x, y = ~densidad$y, 
                        type="scatter", 
                        mode = "lines",
                        fill = "tozeroy",
                        height = 600,
                        width = 800) %>% 
        layout(xaxis = list(title = input$variable_1), 
               yaxis = list(title = 'Densidad'))
      
    }
    else if (input$variable_2 != "NONE" & input$variable_3 == "NONE"){
      
      data = df[, c(input$variable_1, input$variable_2)]
      colnames(data)[1] = "var1"
      colnames(data)[2] = "var2"
      
      fig$plot = plot_ly(data = data, x = ~var1, y = ~var2,
                         type="scatter", 
                         mode = "markers",
                         color = "black",
                         height = 600,
                         width = 800) %>% 
        layout(xaxis = list(title = input$variable_1), 
               yaxis = list(title = input$variable_2))
      
    }
    else {
      data = df[, c(input$variable_1, input$variable_2, input$variable_3)]
      
      colnames(data)[1] = "var1"
      colnames(data)[2] = "var2"
      colnames(data)[3] = "var3"
      
      fig$plot = plot_ly(data = data, x = ~var1, y = ~var2, z = ~var3,
                          type="scatter3d", 
                          mode = "markers",
                          color = "black",
                          height = 800,
                          width = 800) %>% 
        layout(scene = list(
          xaxis = list(title = input$variable_1), 
          yaxis = list(title = input$variable_2), 
          zaxis = list(title = input$variable_3)))
    }
    
    
  })
  
  
  # ====================================
  # EVENTOS
  # ====================================
  
  observeEvent(input$save_plot, {
    
    if (!is.null(fig$plot)){
      showModal(modalDialog("Guardando gráfica como 'grafica.png'", footer=NULL))
      orca(fig$plot, file = "grafica.png")
      removeModal()
      
    }
    #shinyalert("Descarga Exitosa!", "Gráfica descargada como 'grafica.png'", type = "info")
    #shinyalert(title = "You did it!", type = "success")
  })
  
  # %%%%%%%%%%%%%%%%%%%%%
  # STATISTICS
  # %%%%%%%%%%%%%%%%%%%%%
  
  # ====================================
  # OUTPUTS
  # ====================================
  
  # Artista más popular
  output$most_popular_artist = renderPlot({
    
    data = df[, c("Artist", "popularity")] %>% 
      group_by(Artist) %>% 
      summarise(popularity = mean(popularity)) %>% 
      arrange(desc(popularity)) %>% 
      slice(1:10)
    
    ggplot(data, aes(x = reorder(Artist, +popularity), y = popularity)) +
      xlab("Artist") + 
      ylab("Popularity") +
      geom_bar(stat = "identity") +
      coord_flip(ylim = c(89, 96))
      
  })
  
  # Género más explícito
  output$most_explicit_genre = renderPlot({
    
    data = df[, c("Genre", "explicit")] %>% 
      filter(explicit == TRUE) %>% 
      group_by(Genre) %>%
      summarise(n = n()) %>% 
      mutate(explicit_perc = n / sum(n))
    
    ggplot(data, aes(x = reorder(Genre, -explicit_perc), y = explicit_perc)) +
      xlab("Genre") + 
      ylab("Explicit Percentage") +
      geom_bar(stat = "identity") +
      coord_flip()
    
  })
  
  # Artista más bailable
  output$most_danceable_artist = renderPlot({
    
    data = df[, c("Artist", "danceability")] %>% 
      group_by(Artist) %>% 
      summarise(danceability = median(danceability)) %>% 
      arrange(desc(danceability)) %>% 
      slice(1:10)
    
    ggplot(data, aes(x = reorder(Artist, +danceability), y = danceability)) +
      xlab("Artist") + 
      ylab("Danceability") +
      geom_bar(stat = "identity") +
      coord_flip(ylim = c(0.94, 0.975))
  })
  
  # %%%%%%%%%%%%%%%%%%%%%
  # SONG FINDER
  # %%%%%%%%%%%%%%%%%%%%%
  
  # ====================================
  # INPUTS
  # ====================================
  
  # Se configuran todos los sliders con información de la base de datos
  
  output$slider_dance = renderUI({
    sliderInput("slider_dance", "Danceability",
                min = min(df$danceability), 
                max = max(df$danceability),
                value = 
                  (( max(df$danceability) - min(df$danceability) ) / 2) + min(df$danceability)
                )
    
  })
  output$slider_energy = renderUI({
    sliderInput("slider_energy", "Energy",
                min = min(df$energy), 
                max = max(df$energy), 
                value = 
                  (( max(df$energy) - min(df$energy) ) / 2) + min(df$energy)
                )
  })
  output$slider_loud = renderUI({
    sliderInput("slider_loud", "Loudness",
                min = min(df$loudness), 
                max = max(df$loudness), 
                value = 
                  (( max(df$loudness) - min(df$loudness) ) / 2) + min(df$loudness)
    )
  })
  output$slider_speech = renderUI({
    sliderInput("slider_speech", "Speechiness",
                min = min(df$speechiness), 
                max = max(df$speechiness), 
                value = 
                  (( max(df$speechiness) - min(df$speechiness) ) / 2) + min(df$speechiness)
    )
  })
  output$slider_acoustic = renderUI({
    sliderInput("slider_acoustic", "Acousticness",
                min = min(df$acousticness), 
                max = max(df$acousticness), 
                value = 
                  (( max(df$acousticness) - min(df$acousticness) ) / 2) + min(df$acousticness)
    )
  })
  output$slider_instrumental = renderUI({
    sliderInput("slider_instrumental", "Instrumentalness",
                min = min(df$instrumentalness), 
                max = max(df$instrumentalness), 
                value = 
                  (( max(df$instrumentalness) - min(df$instrumentalness) ) / 2) + min(df$instrumentalness)
    )
  })
  output$slider_live = renderUI({
    sliderInput("slider_live", "Liveness",
                min = min(df$liveness), 
                max = max(df$liveness), 
                value = 
                  (( max(df$liveness) - min(df$liveness) ) / 2) + min(df$liveness)
    )
  })
  
  # ====================================
  # OBSERVERS
  # ====================================
  
  # Reset de Sliders
  observeEvent(input$reset_sliders, {
    updateSliderInput(session, "slider_dance", 
                      value = (( max(df$danceability) - min(df$danceability) ) / 2) + min(df$danceability) )
    updateSliderInput(session, "slider_energy", 
                      value = (( max(df$energy) - min(df$energy) ) / 2) + min(df$energy) )
    updateSliderInput(session, "slider_loud", 
                      value = (( max(df$loudness) - min(df$loudness) ) / 2) + min(df$loudness) )
    updateSliderInput(session, "slider_speech", 
                      value = (( max(df$speechiness) - min(df$speechiness) ) / 2) + min(df$speechiness) )
    updateSliderInput(session, "slider_acoustic", 
                      value = (( max(df$acousticness) - min(df$acousticness) ) / 2) + min(df$acousticness) )
    updateSliderInput(session, "slider_instrumental", 
                      value = (( max(df$instrumentalness) - min(df$instrumentalness) ) / 2) + min(df$instrumentalness) )
    updateSliderInput(session, "slider_live", 
                      value = (( max(df$liveness) - min(df$liveness) ) / 2) + min(df$liveness) )
  })
  
  # ====================================
  # OUTPUTS
  # ====================================
  
  # FUNCIÓN: calcular distancia euclideana entre sliders y data. Se retorna
  # la data de la canción con la menor distancia o el mejor match.
  find_match = function() {
    
    # Se extraen las columnas con sliders de la data
    data = df[, c("danceability", "energy", "loudness", "speechiness", 
                  "acousticness", "instrumentalness", "liveness")]
    
    # Se crea un dataframe de una fila con los datos de todos los sliders
    sliders = data.frame(
      danceability = input$slider_dance,
      energy = input$slider_energy,
      loudness = input$slider_loud,
      speechiness = input$slider_speech,
      acousticness = input$slider_acoustic,
      instrumentalness = input$slider_instrumental,
      liveness = input$slider_live
    )
    
    if (nrow(sliders) != 0){
      
      # Pasos:
      # 1. Se iguala el número de filas de "sliders" con "data"
      # 2. Se restan los valores de los sliders a toda la data
      # 3. Se eleva al cuadrado "element-wise"
      # 4. Se suman las filas (Cada una de las cualidades de canción)
      # 5. Se obtiene la raíz cuadrada, básicamente obteniendo la distancia euclideana
      diff = data - slice(sliders, rep(row_number(), nrow(data)))
      dist = sqrt(rowSums(diff * diff))
      
      # Se obtiene el índice de la canción con la menor distancia
      song_idx = which.min(dist)
      
      # Se extrae toda la data del mejor match usando el index anterior
      return(df[song_idx, ])
    }
    else {
      return(NULL)
    }
    
  }
  
  # OUTPUT: Actualizar cover de canción recomendada
  output$match_album_cover = renderUI({
    
    match_data = find_match()
    
    # Si no se ha seleccionado album:
    # - Se codifica en base 64 el placeholder
    # - Se muestra usando una tag "img"
    if (is.null(match_data)){
      b64 <- base64enc::dataURI(file="logo_spotify.png", mime="image/png")
      img(src = b64, width = "90%", style="border-radius: 10%")
    }
    # Si se seleccionó un album:
    # - Se muestra la imagen en la columna "Album_cover_link"
    else {
      img(src = match_data$Album_cover_link, width = "90%", style="border-radius: 10%")
    }
    
  })
  
  # OUTPUT: Actualizar data de canción recomendada
  output$match_album_info = renderText({
    
    match_data = find_match()
    
    if (is.null(match_data)){
      c("", "")
    }
    else {
      c('<a ', paste('href="https://open.spotify.com/track/', match_data$id, sep = "") ,'">
        <h2>', match_data$Title, '</h4></a>',
        '<h3 style="line-height:0.7">', match_data$Artist, '</h3>',
        '<br>',
        '<h4 style="line-height:0.7">Género: ', tools::toTitleCase(match_data$Genre),'</h4>',
        '<h4 style="line-height:0.7">Duración: ', floor(match_data$duration_s / 60),' m</h4>')
    }
    
  })
  
  
  
})
