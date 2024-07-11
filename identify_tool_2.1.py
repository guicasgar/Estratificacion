# -*- coding: utf-8 -*-
import arcpy, os, string
from arcpy import env
import arcpyproduction

# Set environment settings
env.workspace = arcpy.GetParameterAsText(0) ##"C:\Users\guillermocastro\Desktop\Guillermo\ESYRCE\RIOJA"

# Set local variables
Celdilla = arcpy.GetParameterAsText(1)#"C:\Users\guillermocastro\Desktop\Guillermo\ESYRCE\celdillas\Celdillas_H30"
Regadio = arcpy.GetParameterAsText(2)#"C:\Users\guillermocastro\Desktop\Guillermo\ESYRCE\RIOJA\Regadio"
Recinto = arcpy.GetParameterAsText(3) #"C:\Users\guillermocastro\Desktop\Guillermo\ESYRCE\RIOJA\26_Recintos__Ex"
Linea_dec = arcpy.GetParameterAsText(4)#""
comarcas = arcpy.GetParameterAsText(5)
arroz = arcpy.GetParameterAsText(6) #""
viticola = arcpy.GetParameterAsText(7)#""
temp1 = arcpy.GetParameterAsText(8) #env.workspace+"\Result_temp\temp1"

temp_final = None

# Obtener valores de los campos CA, CP y HUS de la tabla de Celdilla
with arcpy.da.SearchCursor(Celdilla, ["CA", "CP", "HUS"]) as cursor:
    row = next(cursor)  # Suponiendo que solo necesitas la primera fila
    ca_value = str(row[0]) if row[0] is not None else ""
    cp_value = str(row[1]) if row[1] is not None else ""
    hus_value = str(row[2]) if row[2] is not None else ""
    
# Crear el nombre del shapefile
output_filename = "P{}{}_H{}".format(ca_value, cp_value, hus_value)
output_shapefile = os.path.join(env.workspace, output_filename)

# Comprobar el archivo de entrada de celdilla
if Celdilla.endswith("_Huso_28.shp") or Celdilla.endswith("_Huso_29.shp") or Celdilla.endswith("_Huso_31.shp"):
    #Definir la ruta y el nombre del archivo de salida
    #nombre_carpeta = os.path.basename(env.workspace)
    salida = os.path.join(env.workspace, "{}_reproyectada".format(temp1))
    
    # Definir el sistema de coordenadas de destino
    sistema_coordenadas_destino = arcpy.SpatialReference(25830)

    # Proyectar el archivo de entrada al sistema de coordenadas de destino
    arcpy.AddMessage("Iniciando la reproyeccion")
    arcpy.Project_management(Celdilla, salida, sistema_coordenadas_destino)
    arcpy.AddMessage("Archivo proyectado correctamente. Archivo de salida: {}".format(salida))
    
    # Execute Identity
    arcpy.AddMessage("Ejecutando Identity con la capa de recinto")
    temp1 = temp1+"_recinto"
    arcpy.Identity_analysis(salida, Recinto, temp1)
    arcpy.AddMessage("Recinto incorporado")

    if Regadio is not "":
        arcpy.AddMessage("Ejecutando Identity con la capa de regadio")
        temp2= temp1.replace("_recinto","_regadio")
        arcpy.Identity_analysis(temp1, Regadio, temp2) 
        arcpy.AddMessage("Regadio incorporado")
        if Linea_dec is not "":
            arcpy.AddMessage("Ejecutando Identity con la capa de linea declaracion")
            temp3= temp2.replace("_regadio","_linea_dec")
            arcpy.Identity_analysis(temp2, Linea_dec, temp3)
            temp_final = temp3
            arcpy.AddMessage("Linea declaracion incorporada")
            if comarcas is not "":
                arcpy.AddMessage("Ejecutando Identity con la capa de comarcas")
                temp4= temp3.replace("_linea_dec", "_comarcas")
                arcpy.Identity_analysis(temp3, comarcas, temp4)
                temp_final = temp4
                arcpy.AddMessage("comarcas incorporadas")
                if arroz and viticola:
                    arcpy.AddMessage("Ejecutando Identity con la capa de arroz")
                    temp5 = temp4.replace("_comarcas", "_arroz")
                    arcpy.Identity_analysis(temp4, arroz, temp5)
                    arcpy.AddMessage("Arroz incorporado")
                    arcpy.AddMessage("Ejecutando Identity con la capa de viticola")
                    temp6 = temp5.replace("_arroz", "_viticola")
                    arcpy.Identity_analysis(temp5, viticola, temp6)
                    arcpy.AddMessage("Viticola incorporada")
                    # Proyectar nuevamente al sistema de coordenadas original
                    temp_final = arcpy.Project_management(temp6, temp1, arcpy.Describe(Celdilla).spatialReference) 
                    arcpy.AddMessage("Reproyectado a su sistema de coordenadas original")
                elif arroz:
                    arcpy.AddMessage("Ejecutando Identity con la capa de arroz")
                    temp5 = temp4.replace("_comarcas", "_arroz")
                    arcpy.Identity_analysis(temp4, arroz, temp5)
                    arcpy.AddMessage("Arroz incorporado")
                    # Proyectar nuevamente al sistema de coordenadas original
                    temp_final = arcpy.Project_management(temp5, temp1, arcpy.Describe(Celdilla).spatialReference) 
                    arcpy.AddMessage("Reproyectado a su sistema de coordenadas original")
                elif viticola is not "":
                    arcpy.AddMessage("Ejecutando Identity con la capa de viticola")
                    temp5= temp4.replace("_comarcas","_viticola")
                    arcpy.Identity_analysis(temp4, viticola, temp5)
                    arcpy.AddMessage("viticola incorporado")
                    # Proyectar nuevamente al sistema de coordenadas original
                    arcpy.AddMessage("Ejecutando reproyección de la capa final")
                    temp_final = arcpy.Project_management(temp5, temp1, arcpy.Describe(Celdilla).spatialReference) 
                    arcpy.AddMessage("Reproyectado a su sistema de coordenadas original")
                else:
                    # Proyectar nuevamente al sistema de coordenadas original
                    arcpy.AddMessage("Ejecutando reproyeccion de la capa final")
                    temp_final = arcpy.Project_management(temp4, temp1, arcpy.Describe(Celdilla).spatialReference)
                    arcpy.AddMessage("Proceso ejecutado en su sistema de coordenadas original")
            else:
                arcpy.AddMessage("Por favor, introduzca una capa de comarcas")
        else:
            arcpy.AddMessage("Por favor, introduzca una capa de Línea de declaración")
    else:
        arcpy.AddMessage("Por favor, introduzca una capa de regadío")
        
    # Ingresar el resultado final con su nombre estipulado en la gdb
    arcpy.AddMessage(temp_final)
    arcpy.FeatureClassToFeatureClass_conversion(temp_final, env.workspace, output_filename)
    arcpy.AddMessage("Resultado final con nombre: {}".format(output_filename))
else:
    arcpy.AddMessage("El nombre del archivo de entrada termina en 'Huso_30'.")
    
    # Execute Identity
    arcpy.AddMessage("Ejecutando Identity con la capa de recinto")
    temp1 = temp1+"_recinto"
    arcpy.Identity_analysis(Celdilla, Recinto, temp1)
    arcpy.AddMessage("Recinto calculado")

    if Regadio is not "":
        arcpy.AddMessage("Ejecutando Identity con la capa de regadio")
        temp2= temp1.replace("_recinto","_regadio")
        arcpy.Identity_analysis(temp1, Regadio, temp2)
        arcpy.AddMessage("Regadio incorporado")    
        if Linea_dec is not "":
            arcpy.AddMessage("Ejecutando Identity con la capa de linea declaracion")
            temp3= temp2.replace("_regadio","_linea_dec")
            arcpy.Identity_analysis(temp2, Linea_dec, temp3)
            temp_final = temp3
            arcpy.AddMessage("Linea declaracion incorporada")
            if comarcas is not "":
                arcpy.AddMessage("Ejecutando Identity con la capa de comarcas")
                temp4= temp3.replace("_linea_dec", "_comarcas")
                arcpy.Identity_analysis(temp3, comarcas, temp4)
                temp_final = temp4
                arcpy.AddMessage("comarcas incorporadas")
                if arroz is not "":
                    arcpy.AddMessage("Ejecutando Identity con la capa de arroz")
                    temp5= temp4.replace("_comarcas","_arroz")
                    arcpy.Identity_analysis(temp4, arroz, temp5)
                    temp_final = temp5
                    arcpy.AddMessage("Arroz incorporado")
                    if viticola is not "":
                        arcpy.AddMessage("Ejecutando Identity con la capa de viticola")
                        temp6= temp5.replace("_arroz","_viticola")
                        arcpy.Identity_analysis(temp5, viticola, temp6)
                        temp_final = temp6
                        arcpy.AddMessage("Viticola incorporado")
                    else: 
                        arcpy.AddMessage("Proceso ejecutado. A la espera de la exportacion...")
                elif viticola is not "":
                    arcpy.AddMessage("Ejecutando Identity con la capa de viticola")
                    temp5= temp4.replace("_comarcas","_viticola")
                    arcpy.Identity_analysis(temp4, viticola, temp5)
                    temp_final = temp5
                    arcpy.AddMessage("Viticola incorporado")
                else:
                    arcpy.AddMessage("Proceso ejecutado. A la espera de cambiar el nombre final en la gdb...")
            else:
                arcpy.AddMessage("Por favor, introduzca una capa de comarcas")
        else:
            arcpy.AddMessage("Por favor, introduzca una capa de Linea de declaracion")
    else:
        arcpy.AddMessage("Por favor, introduzca una capa de regadio")        
    # Ingresar el resultado final con su nombre estipulado en la gdb
    arcpy.AddMessage(temp_final)
    arcpy.FeatureClassToFeatureClass_conversion(temp_final, env.workspace, output_filename)
    arcpy.AddMessage("Resultado final con nombre: {}".format(output_filename))