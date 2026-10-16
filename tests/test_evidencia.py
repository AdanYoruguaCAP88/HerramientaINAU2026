"""Tests del módulo de evidencia."""
import json
from pathlib import Path
import pytest
from calc.config import cargar_config
from calc.situacion import Situacion, GrupoAtendido, PersonalDisponible
from calc.evaluador import evaluar_situacion
from calc.evidencia import cargar_repositorio, buscar_evidencia
from calc.preguntas import responder_preguntas_con_evidencia

BASE = Path(__file__).parent.parent
CFG = BASE / "config" / "caif_san_carlos.json"
REPO = BASE / "repositorio" / "experiencias.json"


@pytest.fixture
def cfg():
    return cargar_config(CFG)


@pytest.fixture
def repo():
    return cargar_repositorio(REPO)


@pytest.fixture
def situacion_base():
    d = json.loads((BASE / "escenarios" / "tacuarembo_40ninos.json").read_text("utf-8"))
    return Situacion(id=d["id"], ubicacion=d["ubicacion"], origen=d["origen"],
        poblacion_ninos=d["poblacion_ninos"],
        grupos=[GrupoAtendido(**g) for g in d["grupos"]],
        personal_disponible=[PersonalDisponible(**p) for p in d["personal_disponible"]])


def test_evidencia_repositorio_carga(repo):
    assert len(repo) >= 5
    ids = {e.id for e in repo}
    assert {"FIN_ECEC_RATIO_2018", "NOR_MENTORING_2025", "URU_SIPIAV_2017"} <= ids


def test_evidencia_recupera_para_brecha(cfg, repo, situacion_base):
    estado = evaluar_situacion(situacion_base, cfg)
    ev = buscar_evidencia(estado, repo)
    assert len(ev) > 0
    assert any(e.experiencias_relevantes for e in ev)


def test_evidencia_declara_ausencia(cfg, repo):
    d = json.loads((BASE / "escenarios" / "tacuarembo_40ninos.json").read_text("utf-8"))
    d["id"] = "CAIF_SIN_EVIDENCIA"
    d["personal_disponible"] = [{"rol": "educador", "horas_semana": 10}]
    sit = Situacion(id=d["id"], ubicacion="Test", origen="observada", poblacion_ninos=40,
        grupos=[GrupoAtendido(**g) for g in d["grupos"]],
        personal_disponible=[PersonalDisponible(**p) for p in d["personal_disponible"]])
    estado = evaluar_situacion(sit, cfg)
    ev = buscar_evidencia(estado, repo)
    assert any(e.sin_evidencia_suficiente for e in ev)


def test_evidencia_pertinencia_por_evaluacion(cfg, repo):
    from calc.evidencia import _evaluar_pertinencia
    exp_fin = next(e for e in repo if e.id == "FIN_ECEC_RATIO_2018")
    exp_uru = next(e for e in repo if e.id == "URU_SIPIAV_2017")
    ctx = {"pais": "Uruguay", "nivel_descentralizacion": "centralizado", "territorio": "mixto"}
    assert _evaluar_pertinencia(exp_fin, "dimensionamiento_personal", ctx).puntaje >= 0
    assert _evaluar_pertinencia(exp_uru, "coordinacion_interinstitucional", ctx).puntaje >= 0


def test_preguntas_con_evidencia(cfg, repo, situacion_base):
    estado = evaluar_situacion(situacion_base, cfg)
    respuestas = responder_preguntas_con_evidencia(estado, [], repo)
    assert len(respuestas) == 7
    assert "Mecanismos documentados" in respuestas[3]["respuesta"] or "Sin evidencia" in respuestas[3]["respuesta"]
