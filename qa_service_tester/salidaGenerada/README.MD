Excel generado durante la ejecucción
Ruta Servicio Storm: http://172.21.170.81:8080/storm/swagger-ui/index.html

/abq/fronton/altaOrdenRentaFija
Servicio de alta de orden FrontOn de Renta Fija



Ruta: http://172.21.170.81:8081/storm/swagger-ui/index.html#/Servicios%20para%20Interface%20de%20Abaqus%20con%20Fronton/altaOrdenIIF

Lllamada:
{
  "usuario": 10114,
  "operacion": "C", 
  "indPrimarioSecundario": "P",
  "instrumento": 46487,
  "cartera": 706,
  "nominalDiv": 11000,
  "tasaOpe": 1.9,
  "fechaLiquidacion": "16/06/2026",
  "baseCalculo": "2"
}

Respuesta
Server response
Code	Details
500	
Error: response status is 500

Response body
Download
{
  "title": "Errores",
  "descripcion": "Han ocurrido errores",
  "errores": [
    {
      "errorCode": "com.rdsistemas.rdrestbcibankabq.control.GlobalExceptionHandler.handleGenericException.010",
      "errorType": "ERROR",
      "severity": "90",
      "errorOrigin": "com.rdsistemas.rdrestbcibankabq.control.GlobalExceptionHandler.handleGenericException",
      "errorDescription": "Error inesperado en el servicio 'altaOrdenIIF'.",
      "entryDate": "2026-06-15T21:56:40.927Z"
    }
  ]
}
Response headers
 cache-control: no-cache,no-store,max-age=0,must-revalidate 
 connection: close 
 content-type: application/json 
 date: Mon,15 Jun 2026 21:56:40 GMT 
 expires: 0 
 pragma: no-cache 
 transfer-encoding: chunked 
 vary: Origin,Access-Control-Request-Method,Access-Control-Request-Headers 
 x-content-type-options: nosniff 
 x-frame-options: DENY 
 x-xss-protection: 0 
