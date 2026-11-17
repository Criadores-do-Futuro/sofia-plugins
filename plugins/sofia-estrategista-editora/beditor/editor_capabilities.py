"""Escolha conservadora de editor com base em evidências fornecidas pelo host.

Este módulo não descobre ferramentas, autentica nem executa operações. Os fatos
devem ser recolhidos e atualizados por um adaptador autorizado em cada ambiente.
"""

from dataclasses import dataclass, field
from typing import Literal, Mapping, Sequence

Editor = Literal["capcut", "davinci"]
CapabilityStatus = Literal["verified", "unverified", "unsupported"]
Availability = Literal["available", "unavailable", "unverified"]
_EDITORS = ("capcut", "davinci")
_STATUSES = ("verified", "unverified", "unsupported")


@dataclass(frozen=True)
class CapabilityEvidence:
    status: CapabilityStatus
    # Referência humana à verificação feita, como diagnóstico ou execução.
    source: str = ""

    def __post_init__(self) -> None:
        if self.status not in _STATUSES:
            raise ValueError(f"Estado de capacidade inválido: {self.status}")
        if self.status == "verified" and not self.source.strip():
            raise ValueError("Capacidade verificada exige origem da evidência")


@dataclass(frozen=True)
class EditorEvidence:
    availability: Availability = "unverified"
    capabilities: Mapping[str, CapabilityEvidence] = field(default_factory=dict)
    source: str = ""

    def __post_init__(self) -> None:
        if self.availability not in ("available", "unavailable", "unverified"):
            raise ValueError(f"Disponibilidade inválida: {self.availability}")
        if self.availability == "available" and not self.source.strip():
            raise ValueError("Editor disponível exige origem da evidência")
        if any(not isinstance(value, CapabilityEvidence) for value in self.capabilities.values()):
            raise TypeError("Cada capacidade deve ter CapabilityEvidence")


@dataclass(frozen=True)
class EditorDecision:
    status: Literal["ready", "blocked"]
    editor: Editor | None
    # Motivos por editor; vazio quando ele atende todos os requisitos.
    blockers: Mapping[str, tuple[str, ...]]


def select_editor(
    requested: Literal["auto", "capcut", "davinci"],
    required: Sequence[str],
    evidence: Mapping[str, EditorEvidence],
    preference: Sequence[Editor] = _EDITORS,
) -> EditorDecision:
    """Decide usando somente capacidades verificadas para o host atual.

    Uma escolha explícita nunca muda para outro editor. No modo automático,
    escolhe-se pela ordem informada, entre editores que satisfaçam tudo. Dados
    ausentes significam não verificado, não ausência nem suporte comprovado.
    """
    if requested not in ("auto", *_EDITORS):
        raise ValueError(f"Editor desconhecido: {requested}")
    if isinstance(required, (str, bytes)) or not required:
        raise ValueError("Informe uma lista não vazia de capacidades requeridas")
    if any(not isinstance(item, str) or not item.strip() for item in required):
        raise ValueError("Capacidades requeridas devem ser nomes não vazios")
    if set(preference) != set(_EDITORS) or len(preference) != len(_EDITORS):
        raise ValueError("Preferência deve conter capcut e davinci uma vez cada")
    if any(key not in _EDITORS for key in evidence):
        raise ValueError("Evidência contém editor desconhecido")
    if any(not isinstance(value, EditorEvidence) for value in evidence.values()):
        raise TypeError("Cada editor deve ter EditorEvidence")

    candidates = (requested,) if requested != "auto" else tuple(preference)
    required_unique = tuple(dict.fromkeys(required))
    blockers: dict[str, tuple[str, ...]] = {}
    for editor in candidates:
        facts = evidence.get(editor, EditorEvidence())
        reasons: list[str] = []
        if facts.availability == "unavailable":
            reasons.append("Editor indisponível neste ambiente")
        elif facts.availability == "unverified":
            reasons.append("Disponibilidade do editor não verificada")
        for capability in required_unique:
            fact = facts.capabilities.get(capability)
            if fact is None or fact.status == "unverified":
                reasons.append(f"Capacidade não verificada: {capability}")
            elif fact.status == "unsupported":
                reasons.append(f"Capacidade não suportada: {capability}")
        blockers[editor] = tuple(reasons)
        if not reasons:
            return EditorDecision("ready", editor, blockers)
    return EditorDecision("blocked", None, blockers)
