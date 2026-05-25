from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Prenda
from .forms import PrendaForm
from django.http import HttpResponse
import openpyxl

def lista_prendas(request):
    estado = request.GET.get('estado', 'todas')
    
    busqueda = request.GET.get('busqueda', '')
    filtro_talla = request.GET.get('talla', '')
    filtro_marca = request.GET.get('marca', '')
    orden = request.GET.get('orden', '')

    prendas = Prenda.objects.all()
    if estado != 'todas':
        prendas = prendas.filter(estado=estado)
    if busqueda:
        prendas = prendas.filter(
            tipo_de_prenda__icontains=busqueda
        ) | prendas.filter(
            marca__icontains=busqueda
        ) | prendas.filter(
            color__icontains=busqueda
        )
    if filtro_talla:
        prendas = prendas.filter(talla=filtro_talla)
    if filtro_marca:
        prendas = prendas.filter(marca__icontains=filtro_marca)
    if orden == 'precio_asc':
        prendas = prendas.order_by('precio_vendido')
    elif orden == 'precio_desc':
        prendas = prendas.order_by('-precio_vendido')

    tallas = Prenda.objects.values_list('talla', flat=True).distinct()
    marcas = Prenda.objects.values_list('marca', flat=True).distinct()

    total = Prenda.objects.count()
    vendidas = Prenda.objects.filter(estado='vendido').count()
    disponibles = Prenda.objects.filter(estado='disponible').count()
    borradores = Prenda.objects.filter(estado='borrador').count()

    paginator = Paginator(prendas, 8)
    page_number = request.GET.get('page')
    prendas = paginator.get_page(page_number)

    form = PrendaForm()
    if request.method == 'POST':
        form = PrendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_prendas')
        else:
            print(form.errors)
        
    beneficio_total = sum(
        p.beneficio() for p in Prenda.objects.filter(estado='vendido') if p.beneficio() is not None)

    return render(request, 'prendas/lista_prendas.html', {
        'prendas': prendas,
        'estado': estado,
        'total': total,
        'vendidas': vendidas,
        'disponibles': disponibles,
        'borradores': borradores,
        'form': form,
        'beneficio_total': beneficio_total,
        'busqueda': busqueda,
        'filtro_talla': filtro_talla,
        'filtro_marca': filtro_marca,
        'orden': orden,
        'tallas': tallas,
        'marcas': marcas,
    })

def editar_prenda(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    form = PrendaForm(instance=prenda)
    
    if request.method == 'POST':
        form = PrendaForm(request.POST, instance=prenda)
        if form.is_valid():
            form.save()
            return redirect('lista_prendas')
    
    return render(request, 'prendas/editar_prenda.html', {'form': form, 'prenda': prenda})

def eliminar_prenda(request, pk):
    prenda = get_object_or_404(Prenda, pk=pk)
    if request.method == 'POST':
        prenda.delete()
        return redirect('lista_prendas')
    return render(request, 'prendas/confirmar_eliminar.html', {'prenda': prenda})

def exportar_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Prendas"

    # Cabeceras
    ws.append(['Tipo', 'Talla', 'Color', 'Marca', 'Localizador', 'Donde subido', 'Precio comprado', 'Precio vendido', 'Beneficio', 'Estado'])

    # Datos
    for prenda in Prenda.objects.all():
        ws.append([
            prenda.tipo_de_prenda,
            prenda.talla,
            prenda.color,
            prenda.marca,
            prenda.localizador,
            prenda.donde_esta_subido,
            float(prenda.precio_comprado),
            float(prenda.precio_vendido) if prenda.precio_vendido else '',
            float(prenda.beneficio()) if prenda.beneficio() else '',
            prenda.get_estado_display(),
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="prendas.xlsx"'
    wb.save(response)
    return response