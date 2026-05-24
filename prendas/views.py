from django.shortcuts import render, redirect, get_object_or_404
from .models import Prenda
from .forms import PrendaForm

def lista_prendas(request):
    estado = request.GET.get('estado', 'todas')
    
    prendas = Prenda.objects.all()
    if estado != 'todas':
        prendas = prendas.filter(estado=estado)

    total = Prenda.objects.count()
    vendidas = Prenda.objects.filter(estado='vendido').count()
    disponibles = Prenda.objects.filter(estado='disponible').count()
    borradores = Prenda.objects.filter(estado='borrador').count()

    form = PrendaForm()
    if request.method == 'POST':
        form = PrendaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_prendas')
        
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