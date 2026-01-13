from datetime import datetime, date, timedelta
import os
from util.jsonfileHandler import readFile

CATEGORIES=[
    "Comida","Transporte","Hogar","Servicios","Entretenimiento","Salud","Otros"
]

def next_id(items):
    if not items: return 1
    return max(int(i.get("id",0)) for i in items)+1

def gastos_por_categoria(items):
    sums={c:0.0 for c in CATEGORIES}
    for g in items:
        cat=g.get("categoria","Otros")
        sums.setdefault(cat,0.0)
        sums[cat]+=float(g.get("monto",0))
    return sums

def total_gastos(items):
    return sum(float(g.get("monto",0)) for g in items)

def filter_by_category(items,categoria):
    return [g for g in items if str(g.get("categoria","")).lower()==categoria.lower()]

def parse_date(s):
    if not s: return None
    for fmt in ("%Y-%m-%d","%d/%m/%Y"):
        try: return datetime.strptime(s,fmt).date()
        except: pass
    return None

def filter_by_date_range(items,start,end):
    res=[]
    for g in items:
        d=parse_date(g.get("fecha",""))
        if d and start<=d<=end: res.append(g)
    return res

def gastos_diarios(items,target):
    return filter_by_date_range(items,target,target)

def gastos_ultimo_dias(items,days):
    today=date.today()
    start=today-timedelta(days=days-1)
    return filter_by_date_range(items,start,today)

def gastos_mes(items,year,month):
    res=[]
    for g in items:
        d=parse_date(g.get("fecha",""))
        if d and d.year==year and d.month==month:
            res.append(g)
    return res

def pretty_gasto(g):
    return f"ID:{g.get('id')} | {g.get('fecha')} | {g.get('categoria'):<12} | {g.get('monto'):<8} | {g.get('descripcion','')}"

#==Edwin Ocampo==#