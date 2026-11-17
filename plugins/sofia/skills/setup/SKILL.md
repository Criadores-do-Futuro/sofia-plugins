---
name: setup
description: Configura a pasta de trabalho e verifica recursos locais da Sofia sem
  instalar programas ou ativar serviços pagos sem autorização.
---

# Preparar o ambiente

Leia [comportamento](../../comportamento.md). Este plugin contém instruções e utilitários locais; não depende de um conector de conteúdo.

1. Identifique ferramentas de arquivo, terminal e imagens disponíveis. Texto e roteiro funcionam mesmo sem execução local; explique apenas o recurso que falta para a tarefa atual.
2. Pergunte onde salvar se ainda não houver uma pasta escolhida. A configuração opcional está exemplificada em [configuração](../../knowledge/config.exemplo.yaml). A configuração real e os perfis ficam fora da instalação, em `~/.sofia/`; nunca grave chaves nesse modelo.
3. Para preparar vídeo, verifique Python 3.10 ou posterior, `ffmpeg` e `ffprobe`. `yt-dlp` só é necessário se houver download autorizado. Informe dependências ausentes, proponha o comando oficial adequado ao sistema e instale apenas com autorização. Não execute comandos que aceitem termos ou exijam senha no lugar da pessoa.
4. Serviços externos são opcionais. Não prometa que um conector está instalado. Use variáveis de ambiente para credenciais configuradas pela pessoa; nunca peça seu valor na conversa, imprima-o ou inclua-o em arquivos de saída.
5. Para aprender voz, peça amostras reais, extraia tom, ritmo, vocabulário, aberturas e finais; mostre o perfil e salve apenas quando houver pedido ou autorização. Separe perfis de clientes e escolha o perfil correto antes de usá-lo.

Confirme o que foi realmente configurado e o que permanece indisponível. Não execute uma chamada paga para testar a configuração sem autorização correspondente.
