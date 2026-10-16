"""Pruebas de regresión de los hallazgos de auditoría v0.2."""
import json
from pathlib import Path
from calc.config import cargar_config
from calc.situacion import Situacion, GrupoAtendido, PersonalDisponible, Alternativa
from calc.evaluador import evaluar_situacion, _horas_requeridas_por_rol
from calc.alternativas import evaluar_alternativa
from calc.preguntas import responder_preguntas
BASE=Path(__file__).parent.parent
CFG=BASE/"config"/"caif_san_carlos.json"
def load_situation(path):
 d=json.loads(path.read_text(encoding="utf-8"))
 return Situacion(id=d["id"],ubicacion=d.get("ubicacion",""),origen=d.get("origen","observada"),poblacion_ninos=d.get("poblacion_ninos",0),grupos=[GrupoAtendido(**x) for x in d.get("grupos",[])],personal_disponible=[PersonalDisponible(**x) for x in d.get("personal_disponible",[])],recursos_materiales=[],presupuesto_disponible_ur=d.get("presupuesto_disponible_ur"),problema_declarado=d.get("problema_declarado"),notas=d.get("notas",[]),fecha=d.get("fecha"))
def test_population_group_discrepancy_is_reported():
 cfg=cargar_config(CFG); s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json"); e=evaluar_situacion(s,cfg)
 assert e.capacidad["poblacion_declarada"]==40 and e.capacidad["ninos_totales"]==53
 assert any(r.id=="R0_POBLACION" and r.estado=="indeterminado" for r in e.restricciones)
def test_group_scaled_hours_are_not_full_unit_hours():
 cfg=cargar_config(CFG)
 s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json")
 r=_horas_requeridas_por_rol(s,cfg)
 # For a 12-child group within a two-group 1A_4H unit, the contribution
 # is 80 * 12/(12*2) = 40 educator hours, not 80.
 from calc.evaluador import _unidad_para_grupo
 u=_unidad_para_grupo(s.grupos[1],cfg)
 assert u["horas_semana_total_unidad"]["educador"] * 12/(u["ninos_por_grupo_max"]*u["grupos"]) == 40
 assert r.valor["educador"] < 390
def test_epistemic_state_not_marked_verified():
 cfg=cargar_config(CFG); s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json"); e=evaluar_situacion(s,cfg)
 assert all(b.estado.value != "V" for b in e.brechas if b.diferencia is not None)
def test_missing_role_data_is_indeterminate_not_sufficient():
 cfg=cargar_config(CFG); s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json")
 s.personal_disponible=[p for p in s.personal_disponible if p.rol!="psicologo"]
 e=evaluar_situacion(s,cfg)
 b=next(x for x in e.brechas if x.elemento=="psicologo")
 assert b.diferencia is None and b.estado_operativo=="indeterminado"
 assert any(r.id=="R3_psicologo" and r.estado=="indeterminado" for r in e.restricciones)
def test_questions_always_return_seven_and_flag_unknowns():
 cfg=cargar_config(CFG); s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json"); e=evaluar_situacion(s,cfg)
 q=responder_preguntas(e)
 assert len(q)==7 and q[0].estado.value!="V" and q[2].estado.value!="V"
def test_alternative_does_not_claim_viability_when_unknowns_remain():
 cfg=cargar_config(CFG); s=load_situation(BASE/"escenarios"/"tacuarembo_40ninos.json"); base=evaluar_situacion(s,cfg)
 alt=Alternativa("A","test",s)
 result=evaluar_alternativa(alt,cfg,base)
 assert result.veredicto in {"no_evaluable","viola_restriccion","viola_invariante","evaluable"}
 assert result.veredicto!="evaluable" or not any(r.estado=="indeterminado" for r in result.estado.restricciones)
