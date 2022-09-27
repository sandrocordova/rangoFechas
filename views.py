from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.reportesCredito.models import SCHF03, SCHF05, SCHF11
from apps.reportesCredito.serializer import SCHF03Serializer, SCHF05Serializer, SCHF11Serializer
from django.core.paginator import Paginator
from datetime import datetime

class reportes_search(APIView):
    def post(self, request):
        clienteData = request.data['data']
        agencia = request.data['agen_codigo']
        fecha_desde = request.data['fecha_desde']
        fecha_hasta = request.data['fecha_hasta']
        if clienteData and clienteData.isdigit():
            clienteChecking = SCHF03.objects.using('cartera').filter(AGEN_CODIGO=agencia).filter(CLIE_IDENTIFICACION__startswith=clienteData).filter(CZFCCZ__gte=fecha_desde,CZFCCZ__lte=fecha_hasta).all()
            if clienteChecking:
                #clienteChecking = filtrarFecha(clienteChecking, fecha_desde, fecha_hasta)
                serializer_cliente = SCHF03Serializer(clienteChecking, many=True)
                serializer_cliente = agg_productos(serializer_cliente.data)
                #serializer_cliente = filtrarFecha(serializer_cliente, fecha_desde, fecha_hasta)
                
                paginador = Paginator(serializer_cliente, 10)
                pagina = request.GET.get("page") or 1
                pagina_actual = int(pagina)
                clienteChecking = paginador.get_page(pagina)
                """
                #clienteChecking = filtrarFecha(clienteChecking, fecha_desde, fecha_hasta)
                serializer_cliente = SCHF03Serializer(clienteChecking, many=True)
                serializer_cliente = agg_productos(serializer_cliente.data)
                serializer_cliente = filtrarFecha(serializer_cliente, fecha_desde, fecha_hasta)
                
                paginador = Paginator(serializer_cliente, 10)
                pagina = request.GET.get("page") or 1
                pagina_actual = int(pagina)
                serializer_cliente = paginador.get_page(pagina)
                """
                for item in serializer_cliente:
                    print(item["CZFCCZ"])
                json_response = {
                    'status': True,
                    'message': "Response exitoso",
                    "pagina_actual": pagina_actual,
                    "paginas": clienteChecking.paginator.num_pages,
                    "cliente": serializer_cliente
                    #"paginas": serializer_cliente.paginator.num_pages,
                    #"cliente": list(serializer_cliente)
                }
                return Response(json_response, status=status.HTTP_200_OK)
            return Response({"status":"400","message":"No se encontró un cliente con dicha Cédula, RUC o Pasaporte"})
        
        elif clienteData and len(clienteData) >= 1:
            clienteChecking = SCHF03.objects.using('cartera').filter(AGEN_CODIGO=agencia).filter(CLIE_NOMBRE__icontains=clienteData).all()
            if clienteChecking:
                #return Response(serializer_cliente, status=status.HTTP_200_OK)
                paginador = Paginator(clienteChecking, 10)
                pagina = request.GET.get("page") or 1
                clienteChecking = paginador.get_page(pagina)
                pagina_actual = int(pagina)       
                clienteChecking = filtrarFecha(clienteChecking, fecha_desde, fecha_hasta)
                serializer_cliente = SCHF03Serializer(clienteChecking, many=True)
                serializer_cliente = agg_productos(serializer_cliente.data)
                json_response = {
                    'status': True,
                    'message': "Response exitoso",
                    "pagina_actual": pagina_actual,
                    "paginas": clienteChecking.paginator.num_pages,
                    "cliente": serializer_cliente
                }
                return Response(json_response, status=status.HTTP_200_OK)
            return Response({"status":"400","message":"No se encontró un cliente con nombre: "+clienteData})
        return Response({"status":"400","message":"Información insuficiente para buscar un cliente"})
    
def agg_productos(dataIn):
    #Tipo Cliente
    tipo = SCHF11.objects.using('cartera').all() #Catalogo        
    catTipoClie = SCHF11Serializer(tipo, many=True) #catalogo serializado
    itemCatTipoClie = "PDCDSP" #Identificador del catalogo
    for item in dataIn:
        for itemCat in catTipoClie.data:
            if item[itemCatTipoClie]==itemCat[itemCatTipoClie]:
                item.update({'PRODUCTO':itemCat["PDDSPD"]})
                clienteChecking = SCHF05.objects.using('cartera').filter(CZNUCZ=item['CZNUCZ']).all()
                serrr = SCHF05Serializer(clienteChecking, many=True)
                item.update({'NUM_CREDITO':serrr.data[0]["CTNUCO"]})
                fecha = datetime.strptime(item["CZFCCZ"],'%Y-%m-%dT%H:%M:%SZ')
    return dataIn

def filtrarFecha(dataIn, fecha_desde, fecha_hasta):
    arregloRetornado = []
    fecha_desde = datetime.strptime(fecha_desde,'%Y-%m-%d')
    fecha_hasta = datetime.strptime(fecha_hasta,'%Y-%m-%d')
    for item in dataIn:
        fecha = datetime.strptime(item["CZFCCZ"],'%Y-%m-%dT%H:%M:%SZ')
        print(fecha)
        if fecha_desde == fecha_hasta:
            if fecha.year == fecha_desde.year and fecha.year == fecha_hasta.year:
                if fecha.month == fecha_desde.month and fecha.month == fecha_hasta.month:
                    if fecha.day == fecha_desde.day and fecha.day == fecha_hasta.day:
                        arregloRetornado.append(item)
        elif fecha_desde.year < fecha_hasta.year:
            if fecha.year>=fecha_desde.year and fecha.year<=fecha_hasta.year:
                if fecha.year==fecha_desde.year:
                    if fecha.month>fecha_desde.month:
                        arregloRetornado.append(item)
                    elif fecha.month==fecha_desde.month:
                        if fecha.day>=fecha_desde.day:
                            arregloRetornado.append(item)
                elif fecha.year==fecha_hasta.year:
                    if fecha.month<fecha_hasta.month:
                        arregloRetornado.append(item)
                    elif fecha.month==fecha_hasta.month:
                        if fecha.day<=fecha_hasta.day:
                            arregloRetornado.append(item)
                else:
                    arregloRetornado.append(item)
        elif fecha_desde.year == fecha_hasta.year:                
            if fecha.month==fecha_desde.month:
                if fecha.month>fecha_desde.month:
                    arregloRetornado.append(item)
                elif fecha.month==fecha_desde.month:
                    if fecha.day>=fecha_desde.day:
                        arregloRetornado.append(item)
            if fecha.month==fecha_hasta.month:
                if fecha.month<fecha_hasta.month:
                    arregloRetornado.append(item)
                elif fecha.month==fecha_hasta.month:
                    if fecha.day<=fecha_hasta.day:
                        arregloRetornado.append(item)
    return arregloRetornado