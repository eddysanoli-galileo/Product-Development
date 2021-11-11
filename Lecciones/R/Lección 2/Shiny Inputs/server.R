library(shiny)


shinyServer(function(input, output) {
  
  output$single_slider_out = renderPrint({
    input$slider_in
  })
  
  output$multi_slider_out = renderPrint({
    input$slider_multi
  })
  
  output$num_out = renderPrint({
    input$num_in
  })
  
  output$single_date_out = renderPrint({
    input$single_date
  })
  
  output$range_date_out = renderPrint({
    input$range_date
  })
  
  output$check_out = renderPrint({
    input$single_check
  })
  
  output$check_group_out = renderPrint({
    input$multi_check
  })
  
  output$radio_out = renderPrint({
    input$radio_in
  })
  
  output$ab_out = renderPrint({
    input$action_btn
  })
  
  output$al_out = renderPrint({
    input$action_link
  })
  
})
