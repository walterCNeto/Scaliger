# Como Contribuir

Este projeto é uma tradução de IA publicada como **texto-semente para revisão acadêmica**. Erros são esperados, correções são bem-vindas. Há três níveis de contribuição, do mais leve ao mais técnico.

## Nível 1: reportar erro (qualquer pessoa)

Achou um problema na tradução? Não precisa saber Git nem programar.

1. Vai na URL da página com erro (ex: `https://waltercneto.github.io/Scaliger/pages/0493.html`)
2. Clica no link **"Reportar erro nesta página"** no rodapé
3. Você será levado para o GitHub Issues com um template pré-preenchido
4. Descreve o erro: copia o trecho problemático, escreve o que está errado e (se souber) qual seria a tradução correta

Exemplos de coisas que vale reportar:
- Erro factual de tradução (sentido invertido, número errado, nome próprio mal lido)
- Citação grega/hebraica/árabe transcrita incorretamente
- Referência bíblica errada
- Atribuição equivocada (Scaliger cita Plutarco e a tradução diz Plínio)
- Caracteres especiais corrompidos
- Erro tipográfico do impressor de 1629 não detectado pelo modelo

## Nível 2: anotação inline (pesquisadores)

[Hypothes.is](https://hypothes.is) é o sistema de anotação acadêmica padrão na web. Permite marcar trechos específicos do texto e deixar comentários públicos.

1. Cria conta gratuita em https://hypothes.is
2. Instala a extensão para Chrome/Firefox
3. Navega pela página do site
4. Seleciona o trecho com problema, clica no balão da extensão, escreve o comentário

Suas anotações aparecem para outros pesquisadores que tenham a extensão instalada, formando uma camada de revisão pública sobre o texto.

## Nível 3: pull request (Git)

Se você sabe Git, prefere correção direta:

```bash
# Fork do repositório no GitHub (botão "Fork" canto superior direito)
git clone https://github.com/SEU_USUARIO/Scaliger.git
cd Scaliger

# Edita o JSON da página (translated_opus/page-XXXX.json)
# Os campos editáveis são: pt, en, latin, notes, uncertainty_flags

# Commita
git add translated_opus/page-XXXX.json
git commit -m "Correção p.493: 'Rufus' → 'novamente' (Rursus é advérbio)"
git push origin main

# Abre PR no GitHub
```

O curador (Walter Gaggiato) revisa, e se a correção for válida, faz merge.

## O que NÃO modificar sem discussão

- Estrutura do JSON (campos, ordem)
- Scripts em `scripts/` (mudanças de pipeline merecem issue antes)
- Datasets em `data/` (são gerados, não editados manualmente)
- Configuração do site em `docs/` (HTML/CSS gerado pelo build)

## Áreas onde pesquisadores específicos podem ajudar muito

**Latinistas**: pelas 956 páginas, a tradução tem qualidade variável. Páginas densamente filológicas (Prolegomena, Livros V-VII) merecem revisão por especialista.

**Helenistas**: as transliterações gregas seguem o ductus tipográfico de 1629. Algumas formas podem refletir erros do impressor; outras podem ser normalizações nossas. Preferimos preservar o original e marcar com flag.

**Hebraístas, arabistas, sirólogos**: as páginas de tabelas calendáricas em escritas não-latinas (~p.769, p.798, p.802) têm tradução parcial. Especialistas dessas línguas podem refinar muito.

**Astrônomos históricos**: a auditoria astronômica (audit_highlights.html) tem 8 casos curados, mas o dataset completo tem 30 MATCH_DATE e 1.402 eventos não auditáveis. Há muito espaço para análise crítica caso a caso.

**Filólogos da cronologia bíblica**: Scaliger trabalha extensamente com Septuaginta, Massorético e tradições rabínicas. Pesquisadores familiarizados com essas tradições podem corrigir sutilezas que o modelo perdeu.

**Editores críticos**: comparação contra a edição crítica de Grafton (1983, *Joseph Scaliger: A Study in the History of Classical Scholarship*) e a edição parcial de DomoViridi/Scaliger no GitHub (Prolegomena + Livros I-II).

## Reconhecimento

Toda contribuição fica registrada no histórico do Git. Quando o projeto atingir massa crítica de revisão, vamos compilar uma página de **agradecimentos** com nomes e instituições. Se você quer ser citado de forma específica (acadêmica), inclua isso no comentário do commit ou da issue.

## Código de conduta

- Crítica do conteúdo: bem-vinda, mesmo dura
- Crítica pessoal: não tolerada
- Discussões teológicas/filosóficas tangenciais: levadas para Discussions, não Issues

## Dúvidas

[Abra uma Discussion](https://github.com/walterCNeto/Scaliger/discussions) ou contate o curador via GitHub.
