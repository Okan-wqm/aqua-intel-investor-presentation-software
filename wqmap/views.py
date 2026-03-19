import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .carbonate import (
    generate_deffeyes_data,
    ph_nbs_to_free, calc_dic_of_alk, calc_alk_of_dic,
    generate_uia_boundary, generate_co2_boundary,
    ca_mg_l_to_mol_kg,
    calc_adjustment, REAGENTS,
)
from .models import WQSystem


def _grid_dims(count):
    """Return (cols, rows) for a grid layout."""
    if count <= 1: return 1, 1
    if count <= 2: return 2, 1
    if count <= 4: return 2, 2
    if count <= 8: return 4, 2
    return 4, 4


def _ensure_systems(user, count):
    """Ensure user has exactly `count` systems in DB. Create missing, return all."""
    existing = list(user.wq_systems.all()[:count])
    while len(existing) < count:
        idx = len(existing) + 1
        sys = WQSystem.objects.create(user=user, name=f'System {idx}')
        existing.append(sys)
    return existing[:count]


@login_required
def deffeyes_chart_view(request):
    return multi_chart_view(request, 4)


SLIDES = [1, 2, 4, 8, 16]

@login_required
def multi_chart_view(request, count):
    count = min(max(count, 1), 16)
    if count not in SLIDES:
        count = min([s for s in SLIDES if s >= count], default=16)
    systems = _ensure_systems(request.user, count)
    cols, rows = _grid_dims(count)
    systems_json = json.dumps([s.to_dict() for s in systems])
    idx = SLIDES.index(count)
    return render(request, 'wqmap/multi.html', {
        'count': count,
        'systems': systems,
        'systems_json': systems_json,
        'cols': cols, 'rows': rows,
        'prev_count': SLIDES[idx - 1] if idx > 0 else None,
        'next_count': SLIDES[idx + 1] if idx < len(SLIDES) - 1 else None,
        'slide_index': idx + 1,
        'slide_total': len(SLIDES),
    })


@login_required
def deffeyes_data_api(request):
    try:
        temp_c = float(request.GET.get('temp', 25.0))
        salinity = float(request.GET.get('salinity', 35.0))
        ca_mg_l = float(request.GET.get('calcium', 412.0))
        initial_ph = float(request.GET.get('initial_ph', 7.5))
        initial_alk = float(request.GET.get('initial_alk', 2.0))
        target_ph = float(request.GET.get('target_ph', 8.2))
        target_alk = float(request.GET.get('target_alk', 3.2))
        dic_max = float(request.GET.get('dic_max', 6.0))
        alk_max = float(request.GET.get('alk_max', 6.0))
        volume_l = float(request.GET.get('volume', 1000.0))
        tan_mg_l = float(request.GET.get('tan', 0.0))
        uia_limit = float(request.GET.get('uia_limit', 0.02))
        co2_limit = float(request.GET.get('co2_limit', 0.0))
        data = generate_deffeyes_data(
            temp_c=temp_c, salinity=salinity, ca_mg_l=ca_mg_l,
            initial_ph=initial_ph, initial_alk=initial_alk,
            target_ph=target_ph, target_alk=target_alk,
            dic_min=0.0, dic_max=dic_max, alk_min=0.0, alk_max=alk_max,
            tan_mg_l=tan_mg_l, uia_limit=uia_limit,
            co2_limit_mg_l=co2_limit, volume_l=volume_l,
        )
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def light_update_api(request):
    try:
        temp_c = float(request.GET.get('temp', 25.0))
        salinity = float(request.GET.get('salinity', 35.0))
        dic_max = float(request.GET.get('dic_max', 6.0))
        initial_ph = float(request.GET.get('initial_ph', 7.5))
        initial_alk = float(request.GET.get('initial_alk', 2.0))
        target_ph = float(request.GET.get('target_ph', 8.2))
        target_alk = float(request.GET.get('target_alk', 3.2))
        tan_mg_l = float(request.GET.get('tan', 0.0))
        uia_limit = float(request.GET.get('uia_limit', 0.02))
        co2_limit = float(request.GET.get('co2_limit', 0.0))
        tk = temp_c + 273.15
        sal = salinity
        init_ph_free = ph_nbs_to_free(initial_ph, sal, tk)
        tgt_ph_free = ph_nbs_to_free(target_ph, sal, tk)
        init_dic = calc_dic_of_alk(initial_alk / 1000.0, init_ph_free, tk, sal) * 1000.0
        tgt_dic = calc_dic_of_alk(target_alk / 1000.0, tgt_ph_free, tk, sal) * 1000.0
        uia_data = None
        if tan_mg_l > 0 and uia_limit > 0:
            uia_data = generate_uia_boundary(tk, sal, tan_mg_l, uia_limit, 0.0, dic_max)
        co2_data = None
        if co2_limit > 0:
            co2_data = generate_co2_boundary(tk, sal, co2_limit, 0.0, dic_max)
        return JsonResponse({
            'initial_waypoint': {'dic': round(init_dic, 4), 'alk': round(initial_alk, 4), 'ph': initial_ph},
            'target_waypoint': {'dic': round(tgt_dic, 4), 'alk': round(target_alk, 4), 'ph': target_ph},
            'uia_boundary': uia_data, 'co2_boundary': co2_data,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def adjust_api(request):
    try:
        temp_c = float(request.GET.get('temp', 25.0))
        salinity = float(request.GET.get('salinity', 35.0))
        initial_ph = float(request.GET.get('initial_ph', 7.5))
        initial_alk = float(request.GET.get('initial_alk', 2.0))
        target_ph = float(request.GET.get('target_ph', 8.2))
        target_alk = float(request.GET.get('target_alk', 3.2))
        volume = float(request.GET.get('volume', 1000.0))
        reagent1 = request.GET.get('reagent1', 'nahco3')
        reagent2 = request.GET.get('reagent2', 'hcl')
        tk = temp_c + 273.15
        sal = salinity
        init_ph_free = ph_nbs_to_free(initial_ph, sal, tk)
        tgt_ph_free = ph_nbs_to_free(target_ph, sal, tk)
        init_dic = calc_dic_of_alk(initial_alk / 1000.0, init_ph_free, tk, sal) * 1000.0
        tgt_dic = calc_dic_of_alk(target_alk / 1000.0, tgt_ph_free, tk, sal) * 1000.0
        result = calc_adjustment(init_dic, initial_alk, tgt_dic, target_alk, volume, reagent1, reagent2)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ── CO2 from pH array ──

@login_required
def co2_from_ph_api(request):
    """Calculate CO2 (mg/L) for an array of pH(NBS) values at given T, S, Alk."""
    try:
        temp_c = float(request.GET.get('temp', 15.0))
        salinity = float(request.GET.get('salinity', 34.0))
        alk_meq = float(request.GET.get('alk', 2.5))
        ph_json = request.GET.get('ph_values', '[]')

        import json as _json
        ph_values = _json.loads(ph_json)

        tk = temp_c + 273.15
        sal = salinity
        alk_mol = alk_meq / 1000.0

        from .carbonate import (ph_nbs_to_free, calc_dic_of_alk,
                                calc_k1, calc_k2, alpha_zero)

        k1 = calc_k1(tk, sal)
        k2 = calc_k2(tk, sal)
        co2_values = []
        for ph_nbs in ph_values:
            ph_free = ph_nbs_to_free(ph_nbs, sal, tk)
            dic_mol = calc_dic_of_alk(alk_mol, ph_free, tk, sal)
            h = 10.0 ** (-ph_free)
            a0 = alpha_zero(h, k1, k2)
            co2_mg = dic_mol * a0 * 44009.6
            co2_values.append(round(co2_mg, 2))

        return JsonResponse({'co2': co2_values})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ── Save / Load / List / Delete systems ──

@login_required
def system_save_api(request):
    """Save current parameters as a system. POST with JSON body."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        d = json.loads(request.body)
        sys_id = d.get('id')
        if sys_id:
            sys = WQSystem.objects.get(id=sys_id, user=request.user)
        else:
            sys = WQSystem(user=request.user)

        sys.name = d.get('name', sys.name if sys_id else 'System 1')
        sys.volume = float(d.get('volume', 1000))
        sys.temperature = float(d.get('temperature', 25))
        sys.salinity = float(d.get('salinity', 35))
        sys.initial_ph = float(d.get('initial_ph', 7.5))
        sys.initial_alk = float(d.get('initial_alk', 2.0))
        sys.target_ph = float(d.get('target_ph', 8.2))
        sys.target_alk = float(d.get('target_alk', 3.2))
        sys.tan = float(d.get('tan', 1.0))
        sys.uia_limit = float(d.get('uia_limit', 0.02))
        sys.co2_limit = float(d.get('co2_limit', 15.0))
        sys.calcium = float(d.get('calcium', 412))
        sys.reagent1 = d.get('reagent1', 'nahco3')
        sys.reagent2 = d.get('reagent2', 'naoh')
        sys.show_uia = d.get('show_uia', True)
        sys.show_co2 = d.get('show_co2', True)
        sys.show_omega = d.get('show_omega', True)
        sys.show_adjust = d.get('show_adjust', True)
        sys.show_ph_major = d.get('show_ph_major', True)
        sys.show_ph_minor = d.get('show_ph_minor', True)
        sys.dic_max = float(d.get('dic_max', 6.0))
        sys.alk_max = float(d.get('alk_max', 6.0))
        sys.save()
        return JsonResponse({'id': sys.id, 'name': sys.name, **sys.to_dict()})
    except WQSystem.DoesNotExist:
        return JsonResponse({'error': 'System not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def system_load_api(request, sys_id):
    """Load a saved system's parameters."""
    try:
        sys = WQSystem.objects.get(id=sys_id, user=request.user)
        return JsonResponse(sys.to_dict())
    except WQSystem.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


@login_required
def system_list_api(request):
    """List all saved systems."""
    systems = list(request.user.wq_systems.values('id', 'name'))
    return JsonResponse({'systems': systems})


@login_required
def system_delete_api(request, sys_id):
    """Delete a saved system."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        WQSystem.objects.get(id=sys_id, user=request.user).delete()
        return JsonResponse({'ok': True})
    except WQSystem.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
