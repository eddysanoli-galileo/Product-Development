library(shiny)
library(dplyr)

# NOTAS:

# Para debugging utilizar "browser()":
# Este comando detiene la app donde se colocó "browser" y luego se 
# puede chequear en consola el valor de las diferentes variables.

# Para no importar todo un paquete se puede utilizar "paquete::función"

shinyServer(function(input, output, session) {
  
  observeEvent(input$min, {
    updateSliderInput(session, "slider_eje1", min=input$min)
  })
  
  observeEvent(input$max, {
    updateSliderInput(session, "slider_eje1", max=input$max)
  })
  
  observeEvent(input$clean, {
    updateSliderInput(session, "s1", value = 0)
    updateSliderInput(session, "s2", value = 0)
    updateSliderInput(session, "s3", value = 0)
    updateSliderInput(session, "s4", value = 0)
  })
  
  observeEvent(input$n, {
    
    # Casos:
    # 1. No se introdujo un valor en la text box
    # 2. El número en la text box es mayor a uno (plural de vez)
    # 3. El número en la text box es menor a uno (singular de vez)
    # 4. Situación no esperada
    if (is.na(input$n)){
      label = paste0("Ejecutar")
    }
    else if (input$n > 1){
      label = paste0("Ejecutar ", input$n, " veces")
    }
    else if (input$n == 1){
      label = paste0("Ejecutar", input$n, " vez")
    }
    else {
      label = paste0("Ejecutar")
    }
    
    updateActionButton(session, "correr", label = label)
    
  })
  
  # Contador infinito
  observeEvent(input$nvalue, {
    updateNumericInput(session, "nvalue", value = input$nvalue + 1)
  })
  
  # Update de celsius
  observeEvent(input$farenheit, {
    f = round((input$farenheit - 32) * (5/9))
    updateNumericInput(session, "celsius", value = f)
  })
  
  # Update de farenheit
  observeEvent(input$celsius, {
    f = round(input$celsius * (9/5) + 32)
    updateNumericInput(session, "farenheit", value = f)
  })
  
  observeEvent(input$dist, {
    updateTabsetPanel(session, "params", selected = input$dist)
  })
  
  # Datos para cada distribución
  sample_dist = reactive({
    switch (input$dist,
      "Normal" = rnorm(n = input$nrandom, mean = input$media, sd = input$sd),
      "Uniforme" = runif(input$nrandom, input$uni_min, input$uni_max),
      "Exponencial" = rexp(input$nrandom, rate = input$razon)
    )
  })
  
  # Plot para cada distribución
  output$plot_dist = renderPlot({
    hist(sample_dist())
  })
  
  
  
})
