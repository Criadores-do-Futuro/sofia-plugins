"""Compara plano com snapshot recebido do CapCut Web, sem chamadas remotas.

IDs precisam ter sido reconciliados ao snapshot efetivamente lido. Não resolve
sozinho URI vid:// -> asset:// nem prova a aparência ou o áudio reproduzido.
"""
from __future__ import annotations

from typing import Any
from scripts.validar_plano_editorial import validate


class InvalidReadback(ValueError):
    """Os dados não permitem realizar uma comparação confiável."""


def compare(plan: dict, snapshot: dict, package_id: str, *, segment_ids: dict[str,str],
            resources: dict[str,str], layers: dict[str,dict[str,int]] | None = None,
            source_proofs: dict[str,dict] | None = None, audio_roles: dict[str,str] | None = None,
            audio_volumes: dict[str,float] | None = None) -> dict[str,Any]:
    """Compara cortes, áudio e lettering com os segmentos associados.

    segment_ids usa `video:<clip id>`, `audio:<clip id>` e `text:<id>` e deve
    conter IDs verificados no snapshot recebido, não IDs presumidos da versão
    anterior. resources associa asset_id à URI original. Ao converter fontes
    para asset://, source_proofs[asset_id] deve conter `expected`, `actual`,
    `package_id` e `evidence` da identidade comprovada; sem isso a fonte fica
    não verificada, jamais equivalente por suposição. layers mapeia cada tipo e
    pista ao layer solicitado; renumeração vira aviso, não erro.
    """
    errors = validate(plan)
    if errors:
        raise InvalidReadback('Plano inválido: ' + '; '.join(errors))
    if plan['project']['editor'] != 'capcut':
        raise InvalidReadback('Plano precisa selecionar CapCut')
    if not isinstance(package_id,str) or not package_id.strip():
        raise InvalidReadback('Informe a versão do snapshot')
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get('segments'),list):
        raise InvalidReadback('Snapshot completo é obrigatório')
    if not isinstance(segment_ids,dict) or not isinstance(resources,dict):
        raise InvalidReadback('Mapeamentos de IDs e fontes são obrigatórios')
    layers = {} if layers is None else layers
    source_proofs = {} if source_proofs is None else source_proofs
    audio_roles = {} if audio_roles is None else audio_roles
    audio_volumes = {} if audio_volumes is None else audio_volumes
    if not all(isinstance(x,dict) for x in (layers,source_proofs,audio_roles,audio_volumes)):
        raise InvalidReadback('Mapeamentos opcionais devem ser objetos')
    index = {}
    for item in snapshot['segments']:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'] or item['id'] in index:
            raise InvalidReadback('Snapshot possui segmento inválido ou ID repetido')
        index[item['id']] = item
    roots = [s['id'] for s in index.values() if s.get('type') == 'DRAFT']
    if len(roots) != 1:
        raise InvalidReadback('Snapshot precisa ter uma raiz')
    root = roots[0]
    findings = []
    used = set()
    def add(level,code,identifier,message,expected=None,actual=None):
        findings.append({'level':level,'code':code,'plan_id':identifier,'message':message,'expected':expected,'actual':actual})
    def check(identifier,code,expected,actual):
        if expected != actual:
            add('erro',code,identifier,'Valor do snapshot difere do plano',expected,actual)
    def find(identifier):
        sid = segment_ids.get(identifier)
        if not isinstance(sid,str) or not sid:
            add('nao_verificado','binding_ausente',identifier,'Associe o segmento ao ID verificado neste snapshot')
            return None
        if sid in used:
            add('erro','binding_duplicado',identifier,'Um mesmo segmento foi vinculado a mais de um item',actual=sid)
            return None
        used.add(sid)
        if sid not in index:
            add('erro','segmento_ausente',identifier,'ID associado não existe no snapshot lido',expected=sid)
            return None
        return index[sid]
    def placement(identifier,segment,interval,group,track):
        timeline = segment.get('timeline',{})
        if not isinstance(timeline,dict):
            add('erro','timeline_invalida',identifier,'Segmento sem timeline válida')
            return
        check(identifier,'inicio',interval['start_ms'],timeline.get('start.ms',0))
        check(identifier,'duracao',interval['end_ms']-interval['start_ms'],timeline.get('duration.ms'))
        mapping=layers.get(group,{})
        if not isinstance(mapping,dict) or track not in mapping:
            add('nao_verificado','layer_sem_referencia',identifier,'Layer solicitado não informado')
        else:
            layout=segment.get('layout',{})
            actual=layout.get('layer',0) if isinstance(layout,dict) else None
            if mapping[track] != actual:
                add('aviso','layer_diferente',identifier,'Layer pode ter sido reindexado; verifique a composição visual ou sonora',mapping[track],actual)
    def source(identifier,asset,attrs):
        expected = resources.get(asset)
        actual = attrs.get('source')
        if not isinstance(expected,str) or not expected:
            add('nao_verificado','fonte_sem_referencia',identifier,'URI original da fonte não informada',actual=actual)
        elif not isinstance(actual,str) or not actual:
            add('erro','fonte_ausente',identifier,'Segmento não tem fonte',expected=expected)
        elif actual != expected:
            proof = source_proofs.get(asset)
            if actual.startswith('asset://'):
                if (not isinstance(proof,dict) or proof.get('expected') != expected or proof.get('actual') != actual
                        or proof.get('package_id') != package_id or not isinstance(proof.get('evidence'),str) or not proof['evidence'].strip()):
                    add('nao_verificado','identidade_asset_nao_comprovada',identifier,'URI asset:// exige vínculo de origem verificado nesta versão',expected,actual)
            else:
                add('erro','fonte_divergente',identifier,'Fonte do segmento difere da URI original',expected,actual)
    assets = {a['id']:a for a in plan['assets']}
    for clip in plan['clips']:
        kind=clip['kind']; identifier=kind+':'+clip['id']; segment=find(identifier)
        if segment is None:
            continue
        check(identifier,'tipo','VIDEO' if kind == 'video' else 'AUDIO',segment.get('type'))
        check(identifier,'pai',root,segment.get('parent_id'))
        attrs=segment.get('attributes',{})
        if not isinstance(attrs,dict):
            add('erro','atributos_invalidos',identifier,'Atributos do segmento inválidos')
            continue
        source(identifier,clip['asset_id'],attrs)
        check(identifier,'origem_inicio',clip['source']['start_ms'],attrs.get('start.ms',0))
        check(identifier,'velocidade',1,attrs.get('speed',1))
        if kind == 'video':
            check(identifier,'tipo_midia','photo' if assets[clip['asset_id']]['kind']=='image' else 'video',attrs.get('meta_type'))
            check(identifier,'volume',1.0 if clip.get('carries_source_audio',False) else 0.0,attrs.get('volume',1.0))
        else:
            role=audio_roles.get(clip['id'])
            if role not in ('fala','musica','efeito'):
                add('nao_verificado','papel_audio_ausente',identifier,'Papel de áudio solicitado não informado')
            else:
                tipo_audio = attrs.get('meta_type')
                check(identifier,'tipo_audio','music' if role=='musica' else 'sound',tipo_audio.lower() if isinstance(tipo_audio, str) else tipo_audio)
            check(identifier,'volume',audio_volumes.get(clip['id'],1.0),attrs.get('volume',1.0))
        placement(identifier,segment,clip['timeline'],kind,clip['track'])
    for text in plan.get('text_layers',[]):
        identifier='text:'+text['id']
        if text['type'] != 'lettering':
            add('nao_verificado','legenda_requer_conferencia',identifier,'Legendas reconhecidas podem gerar múltiplos segmentos; conferência específica é necessária')
            continue
        segment=find(identifier)
        if segment is None:
            continue
        check(identifier,'tipo','TEXT',segment.get('type'))
        check(identifier,'pai',root,segment.get('parent_id'))
        attrs=segment.get('attributes',{})
        if not isinstance(attrs,dict):
            add('erro','atributos_invalidos',identifier,'Atributos do texto inválidos')
            continue
        check(identifier,'texto',text['text'],attrs.get('content'))
        if text.get('style'):
            add('nao_verificado','estilo_texto_nao_comparado',identifier,'Estilo do lettering exige comparação específica')
        placement(identifier,segment,text['timeline'],'text',text['track'])
    levels = {item['level'] for item in findings}
    status = 'divergente' if 'erro' in levels else 'incompleto' if 'nao_verificado' in levels else 'conforme'
    return {'status':status,'package_id':package_id,'findings':findings,
            'notice':'Comparação estrutural, não prova reprodução, aparência, sincronismo percebido, exportação ou fonte asset:// sem evidência.'}
