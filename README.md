# ProyectoFinal-G6

## Resumen del proyecto

Este repositorio implementa una metodología para calcular una versión alternativa del Índice de Percepción Empresarial de la Coyuntura (IPEC), indicador que Fedesarrollo utiliza para medir el clima y las expectativas económicas de los empresarios en Colombia. A diferencia del índice oficial, que se basa en encuestas, este proyecto construye el IPEC a partir de información textual obtenida mediante la descarga automatizada de noticias económicas y políticas desde diversas fuentes. Los textos son limpiados, clasificados por tema y analizados mediante técnicas de procesamiento de lenguaje natural para extraer señales de sentimiento que permiten aproximar la dinámica del indicador original.

El repositorio genera tres resultados principales: (1) un índice agregado utilizando un conjunto amplio de medios, incluidos medios con orientación política; (2) un índice desagregado por sectores económicos, construido a partir de la clasificación temática de las noticias; y (3) índices independientes por medio de comunicación, lo que permite examinar su contribución diferenciada a la percepción económica mensual. En conjunto, estos productos amplían el alcance del IPEC tradicional y ofrecen una aproximación basada en datos de prensa que permite estudiar la coyuntura económica de manera automatizada y reproducible.

### Estructura de archivos para reproducibilidad


Dado que, tanto la descarga de datos, como su procesamiento para los resultados, tuvieron distintas partes, el código está seccionado, es decir, hay diferentes códigos, fácilitando a cualquier persona interesada reproducir los resultados sin necesidad de repetir el proyecto en su totalidad. Por ejemplo, la descarga de datos demora aproximadamente 4-5 horas, debido a que se hace web-scrapping para obtener las noticias, por lo cual es de nuestro interés que sea posible correr lo demás del código con los datos precargados.

Los archivos están numerados para su fácil reproducibilidad. Para el código, ir a la carpeta "scripts". Las bases de datos, tanto creadas como intermedias, están en "stores". Cada código viene bien documentado, además de tener nombres representativos, para mostrar cada parte del projecto.
 