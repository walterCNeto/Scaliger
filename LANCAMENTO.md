# Guia de Lançamento — Passo a Passo

Este documento descreve exatamente o que fazer para publicar o site no ar. Se algo der errado, esses passos são os pontos de checagem.

## Pré-requisitos

- Git instalado no Windows
- Conta GitHub: ✅ (walterCNeto)
- Repositório criado: ✅ (https://github.com/walterCNeto/Scaliger)

## Passo 1 — Preparar a pasta local

Crie uma pasta de trabalho local. Sugestão:

```
C:\Users\Lenovo\Desktop\Desktop\Mestrado FGV\Tempo\Scaliger-repo\
```

Extraia o conteúdo do `scaliger-repo.tar.gz` nesta pasta. Você deve ter:

```
Scaliger-repo/
├── .github/
│   └── ISSUE_TEMPLATE/
├── docs/
├── data/
├── scripts/
│   └── build_site.py
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── LANCAMENTO.md     (este arquivo)
└── README.md
```

## Passo 2 — Copiar arquivos do projeto

Da sua pasta atual `scaliger-pt\`, copie para o repo local:

```cmd
cd "C:\Users\Lenovo\Desktop\Desktop\Mestrado FGV\Tempo\Scaliger-repo"

REM JSONs traduzidos (956 páginas)
xcopy "..\scaliger-pt\translated_opus" "translated_opus\" /E /I

REM Datasets gerados
copy "..\scaliger-pt\events_normalized.jsonl" "data\"
copy "..\scaliger-pt\audit_eclipses.jsonl" "data\"
copy "..\scaliger-pt\audit_final.jsonl" "data\"
copy "..\scaliger-pt\audit_dataset.csv" "data\"
copy "..\scaliger-pt\audit_summary.json" "data\"
copy "..\scaliger-pt\data\nasa_solar_eclipses.csv" "data\"
copy "..\scaliger-pt\data\nasa_lunar_eclipses.csv" "data\"

REM Audit highlights (Núcleo Sólido)
copy "..\scaliger-pt\audit_highlights.html" "scripts\"
```

## Passo 3 — Construir o site

```cmd
cd scripts
python build_site.py --src ..\translated_opus --out ..\docs --audit-summary ..\data\audit_summary.json --audit-highlights audit_highlights.html
cd ..
```

Após isso, a pasta `docs\` deve conter:
- `index.html` (landing page)
- `pages\` (956 HTMLs, um por página)
- `assets\style.css`
- `about.html`, `methodology.html`, `audit.html`, `audit_highlights.html`
- `.nojekyll`

Abra `docs\index.html` no navegador para verificar se ficou bom localmente, antes de subir.

## Passo 4 — Inicializar Git e fazer primeiro push

```cmd
cd "C:\Users\Lenovo\Desktop\Desktop\Mestrado FGV\Tempo\Scaliger-repo"

git init
git branch -M main
git remote add origin https://github.com/walterCNeto/Scaliger.git

git add .
git commit -m "Lançamento inicial: tradução trilíngue + auditoria astronômica + site"
git push -u origin main
```

Pode demorar alguns minutos por causa do volume (956 JSONs + 956 HTMLs + datasets).

Se pedir login, use seu usuário GitHub e um **Personal Access Token** (não a senha — GitHub não aceita mais). Para gerar token:

1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Escopo: marque `repo`
4. Copie o token e use como senha quando o Git pedir

## Passo 5 — Ativar GitHub Pages

1. Vai em https://github.com/walterCNeto/Scaliger/settings/pages
2. Em **Source**, escolha:
   - Branch: `main`
   - Folder: `/docs`
3. Clica em **Save**
4. Espera 1-2 minutos

URL final do site: **https://waltercneto.github.io/Scaliger/**

## Passo 6 — Habilitar Discussions (opcional mas recomendado)

1. Vai em https://github.com/walterCNeto/Scaliger/settings
2. Role até a seção **Features**
3. Marque o checkbox **Discussions**

Pronto — agora pesquisadores podem criar discussões além de issues.

## Passo 7 — Verificações pós-lançamento

Quando o site estiver no ar, verifique:

- [ ] `https://waltercneto.github.io/Scaliger/` carrega
- [ ] Página de Núcleo Sólido (`audit_highlights.html`) renderiza com fontes corretas
- [ ] Uma página individual (`pages/0493.html`) renderiza com layout trilíngue
- [ ] Botão "Reportar erro" leva ao GitHub Issues com template pré-preenchido
- [ ] Hypothes.is aparece no canto direito da página (ícone)
- [ ] Busca de páginas no index funciona (digite "493")
- [ ] Mobile: abre no celular e fica legível

## Passo 8 — Divulgação

Sugestões pra primeiros canais (em ordem):

1. **Rodrigo Silva (Unasp)** — é teu plano original; pode mostrar o Núcleo Sólido como "vamos ver se gostam"
2. **GitHub Topics** — adiciona tópicos no repo: `chronology`, `scaliger`, `latin`, `humanities`, `digital-humanities`, `nasa`, `eclipse`, `historical-astronomy`. Aumenta descobribilidade.
3. **Reddit r/AskHistorians, r/classics, r/latin** — post curto: "Tradução IA do Opus de Emendatione Temporum publicada para revisão pública"
4. **HN/Lobsters** — depois de feedback inicial. Não é o público-alvo, mas dá tração.
5. **ResearchGate** — perfil acadêmico se você quiser, post linkando o repo

Não sugiro Twitter/X como canal primário. Acadêmicos sérios não usam mais.

## Custos

| Item | Custo mensal |
|------|--------------|
| Hosting (GitHub Pages) | R$ 0 |
| Repositório (GitHub público) | R$ 0 |
| Anotações (Hypothes.is) | R$ 0 |
| Domínio próprio (opcional, depois) | ~R$ 5 |
| **Total atual** | **R$ 0** |

Se quiser domínio próprio depois (`emendatione.org` etc.), Registro.br vende `.com.br` por ~R$ 60/ano. GitHub Pages aceita custom domain de graça.

## Atualizações futuras

Quando quiser atualizar uma tradução (correção de issue):

```cmd
cd "C:\Users\Lenovo\Desktop\Desktop\Mestrado FGV\Tempo\Scaliger-repo"

REM Edita o JSON afetado
notepad translated_opus\page-0493.json

REM Reconstrói o site
cd scripts
python build_site.py --src ..\translated_opus --out ..\docs --audit-summary ..\data\audit_summary.json --audit-highlights audit_highlights.html
cd ..

REM Push
git add .
git commit -m "Correção p.493: rever 'Rufus'"
git push
```

GitHub Pages re-publica automaticamente em 1-2 minutos.

## Problemas comuns

**"git push" falha com 403 Forbidden**
→ Você está usando senha. Gera Personal Access Token (Passo 4).

**Site fora do ar após push**
→ Verifica em Settings → Pages se a branch e folder estão certos.

**Fontes não carregam**
→ Você está abrindo `file:///`. Funciona via HTTPS no GitHub Pages.

**`tar` não é reconhecido como comando**
→ Windows 10+ tem tar nativo. Se for versão antiga, use 7-Zip (clique direito → extrair).

**Push muito lento**
→ Os 956 JSONs + HTMLs somam ~50MB. É normal demorar 2-3 minutos.

## Suporte

Se algo travar, manda print do erro e eu ajudo a resolver. Os passos acima são lineares — se um falha, os seguintes não funcionam.
