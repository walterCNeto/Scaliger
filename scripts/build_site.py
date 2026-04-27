#!/usr/bin/env python3
"""
build_site.py — Constrói o site público de docs/ a partir dos JSONs traduzidos.

Cada página gera HTML estático, com:
- Layout trilíngue (latim · português · inglês)
- Botão "Reportar erro" (link direto pro GitHub Issues com template)
- Anotação inline pelo Hypothes.is (script automático)
- Navegação entre páginas
- Link pro scan original no diretório data

Configuração:
- GITHUB_USER + GITHUB_REPO definidos abaixo
- Pasta de origem: ../translated_opus/
- Pasta de destino: ../docs/  (usada pelo GitHub Pages)
"""
import argparse
import json
import re
from pathlib import Path
from html import escape

GITHUB_USER = "walterCNeto"
GITHUB_REPO = "Scaliger"
SITE_BASE = f"https://{GITHUB_USER.lower()}.github.io/{GITHUB_REPO}/"
ISSUE_BASE = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues/new"


CSS = """
:root {
  --paper: #faf7f2;
  --ink: #1a1614;
  --ink-soft: #4a443e;
  --ink-faint: #8a8278;
  --rule: #d4cdc0;
  --rule-soft: #e8e2d5;
  --accent: #1e3a5f;
  --accent-warm: #8b3a2f;
  --highlight: #f5e8c8;
  --code-bg: #f0ebe0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 17px; scroll-behavior: smooth; }
body {
  font-family: 'EB Garamond', Georgia, serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.65;
}
.display {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 500;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.meta {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ink-faint);
}
header {
  border-bottom: 1px solid var(--rule);
  padding: 1.2rem 0;
  background: rgba(250, 247, 242, 0.92);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 2rem;
  flex-wrap: wrap;
}
header .title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-weight: 500;
  font-style: italic;
}
header nav a {
  color: var(--ink-soft);
  text-decoration: none;
  margin-left: 1.2rem;
  font-size: 0.88rem;
}
header nav a:hover { color: var(--accent); }

main { max-width: 1100px; margin: 0 auto; padding: 3rem 2rem; }

/* HOME */
.hero {
  max-width: 900px;
  margin: 0 auto;
  padding: 5rem 2rem 3rem;
  border-bottom: 1px solid var(--rule);
}
.hero h1 { margin-bottom: 1.5rem; font-size: clamp(2rem, 5vw, 3.6rem); }
.hero h1 em { color: var(--accent); font-style: italic; }
.hero .lede {
  font-size: 1.2rem;
  color: var(--ink-soft);
  font-style: italic;
  max-width: 700px;
  line-height: 1.5;
}
.disclaimer-banner {
  background: #fff8dc;
  border-left: 4px solid #d4a017;
  padding: 1rem 1.4rem;
  margin: 2rem 0;
  font-size: 0.95rem;
}
.disclaimer-banner strong { color: #8b4513; }

/* GRID DE PÁGINAS */
.pages-section {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 2rem;
}
.pages-section h2 { margin-bottom: 1.5rem; font-size: 2rem; }
.page-search {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--rule);
  background: white;
  font-family: inherit;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 2px;
}
.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
  margin-bottom: 3rem;
}
.page-grid a {
  display: block;
  padding: 0.6rem 0.5rem;
  background: white;
  border: 1px solid var(--rule);
  text-decoration: none;
  color: var(--ink);
  font-size: 0.85rem;
  text-align: center;
  border-radius: 2px;
  transition: all 0.15s;
}
.page-grid a:hover {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
.page-grid a small {
  display: block;
  font-size: 0.65rem;
  color: var(--ink-faint);
  margin-top: 0.2rem;
  text-transform: uppercase;
}
.page-grid a:hover small { color: rgba(255,255,255,0.7); }

/* PÁGINA INDIVIDUAL */
.page-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--rule-soft);
  font-size: 0.9rem;
}
.page-nav a {
  color: var(--accent);
  text-decoration: none;
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--rule);
  border-radius: 2px;
  background: white;
}
.page-nav a:hover { background: var(--accent); color: white; }
.page-nav .center {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--ink-faint);
}

.scan-link {
  display: inline-block;
  margin: 0 0 2rem 0;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid var(--rule);
  border-radius: 2px;
  text-decoration: none;
  color: var(--accent);
  font-size: 0.9rem;
}
.scan-link:hover { background: var(--code-bg); }

.trilingual {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 2rem 0;
}
.trilingual section {
  background: white;
  padding: 1.5rem 1.6rem;
  border: 1px solid var(--rule);
  border-radius: 2px;
}
.trilingual h3 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem;
  font-weight: 500;
  color: var(--accent);
  border-bottom: 1px solid var(--rule);
  padding-bottom: 0.6rem;
  margin-bottom: 1rem;
}
.trilingual p {
  font-size: 0.97rem;
  line-height: 1.6;
}
.trilingual em { font-style: italic; }
.trilingual section.empty p { color: var(--ink-faint); font-style: italic; }

.events-list {
  background: #f0f7ff;
  padding: 1.2rem 1.5rem;
  border-left: 4px solid var(--accent);
  margin: 2rem 0;
  border-radius: 2px;
}
.events-list h4 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: var(--accent);
}
.event-item {
  margin: 0.5rem 0;
  padding: 0.6rem 0.8rem;
  background: white;
  border-radius: 2px;
  font-size: 0.92rem;
}
.event-item strong { color: var(--accent-warm); }

.flag-list {
  background: #fff0f0;
  padding: 1rem 1.4rem;
  border-left: 4px solid #c44;
  margin: 2rem 0;
  font-size: 0.92rem;
  border-radius: 2px;
}
.flag-list strong { color: #b22; }
.flag-list ul { margin: 0.6rem 0 0 1.2rem; }
.flag-list li { margin: 0.3rem 0; }

.notes-block {
  background: var(--rule-soft);
  padding: 1rem 1.4rem;
  margin: 2rem 0;
  font-size: 0.92rem;
  border-radius: 2px;
}
.notes-block strong { color: var(--ink); }

table {
  border-collapse: collapse;
  margin: 1.5rem 0;
  width: 100%;
  background: white;
  font-size: 0.88rem;
}
th, td {
  border: 1px solid var(--rule);
  padding: 0.5rem 0.8rem;
  text-align: left;
}
th { background: var(--code-bg); font-weight: 600; }

.tables-section h4 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem;
  margin: 2rem 0 0.5rem;
}
.tables-section .table-caption {
  font-size: 0.88rem;
  color: var(--ink-soft);
  font-style: italic;
  margin-bottom: 0.5rem;
}

/* RODAPÉ DE COLABORAÇÃO */
.contribute-block {
  margin-top: 4rem;
  padding: 1.8rem;
  background: var(--code-bg);
  border-radius: 4px;
  border: 1px solid var(--rule);
}
.contribute-block h4 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem;
  margin-bottom: 0.8rem;
  color: var(--accent);
}
.contribute-block p {
  font-size: 0.95rem;
  margin-bottom: 0.8rem;
}
.contribute-block a {
  display: inline-block;
  margin-right: 0.8rem;
  padding: 0.5rem 1rem;
  background: var(--accent);
  color: white;
  text-decoration: none;
  border-radius: 2px;
  font-size: 0.9rem;
}
.contribute-block a:hover { background: var(--accent-warm); }
.contribute-block a.secondary {
  background: white;
  color: var(--accent);
  border: 1px solid var(--accent);
}
.contribute-block a.secondary:hover { background: var(--accent); color: white; }

footer {
  border-top: 1px solid var(--rule);
  margin-top: 5rem;
  padding: 3rem 2rem;
  background: var(--ink);
  color: var(--paper);
}
.footer-inner { max-width: 1100px; margin: 0 auto; }
footer h3 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem;
  margin-bottom: 1rem;
}
footer p {
  font-size: 0.9rem;
  color: rgba(250, 247, 242, 0.7);
  margin-bottom: 1rem;
  max-width: 700px;
}
footer a { color: rgba(250, 247, 242, 0.85); }
footer .meta { color: rgba(250, 247, 242, 0.5); margin-top: 2rem; }

@media (max-width: 768px) {
  html { font-size: 15px; }
  .trilingual { grid-template-columns: 1fr; }
  .header-inner { flex-direction: column; align-items: flex-start; gap: 0.6rem; }
  header nav a { margin-left: 0; margin-right: 1rem; }
  main { padding: 2rem 1.2rem; }
}
"""


HEADER_TEMPLATE = """<header>
  <div class="header-inner">
    <span class="title">De Emendatione Temporum · Joseph Scaliger (1583)</span>
    <nav>
      <a href="{base}index.html">Início</a>
      <a href="{base}index.html#paginas">Páginas</a>
      <a href="{base}audit_highlights.html">Núcleo Sólido</a>
      <a href="{base}audit.html">Auditoria</a>
      <a href="{base}methodology.html">Método</a>
      <a href="{base}about.html">Sobre</a>
    </nav>
  </div>
</header>
"""


# Hypothes.is integração: carrega script do Hypothesis em todas as páginas
HYPOTHESIS_SCRIPT = '<script src="https://hypothes.is/embed.js" async></script>'


GOOGLE_FONTS = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&'
    'family=JetBrains+Mono:wght@400;500&'
    'family=Cormorant+Garamond:wght@500;700&'
    'display=swap" rel="stylesheet">'
)


def safe_text(s):
    if not s:
        return ""
    return escape(s).replace("\n", "<br>")


def issue_url(page_num, lang_section=None):
    """Cria URL do GitHub Issues pré-preenchida."""
    title = f"p.{page_num} — sugestão de revisão"
    body = (
        f"**Página afetada**: {page_num}\n\n"
        f"**URL**: {SITE_BASE}pages/{page_num:04d}.html\n\n"
        f"**Seção com erro**: {lang_section or '(português / inglês / latim)'}\n\n"
        f"**Trecho problemático**:\n> \n\n"
        f"**Problema identificado**:\n\n\n"
        f"**Correção sugerida** (se souber):\n\n\n"
        f"**Sua afiliação** (opcional):\n\n"
    )
    from urllib.parse import quote
    return f"{ISSUE_BASE}?title={quote(title)}&body={quote(body)}&labels=correção"


def render_table_html(table_data):
    """Converte markdown table simples em HTML."""
    md = table_data.get("markdown", "")
    rows = [r for r in md.split("\n") if r.strip().startswith("|")]
    if not rows:
        return ""
    html = "<table>"
    for j, row in enumerate(rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        # pular linha separadora ---|---
        if j == 1 and all(re.match(r"^[-:]+$", c) for c in cells if c):
            continue
        tag = "th" if j == 0 else "td"
        html += "<tr>" + "".join(f"<{tag}>{escape(c)}</{tag}>" for c in cells) + "</tr>"
    html += "</table>"
    return html


def render_page(data, prev_p, next_p, total):
    pn = data.get("page", 0)
    pt = (data.get("pt") or "").strip()
    en = (data.get("en") or "").strip()
    latin = (data.get("latin") or "").strip()
    tables = data.get("tables") or []
    figures = data.get("figures") or []
    events = data.get("astronomical_events") or []
    flags = data.get("uncertainty_flags") or []
    notes = (data.get("notes") or "").strip()

    # navegação
    nav_prev = (f'<a href="{prev_p:04d}.html">← p.{prev_p}</a>'
                if prev_p else '<span></span>')
    nav_next = (f'<a href="{next_p:04d}.html">p.{next_p} →</a>'
                if next_p else '<span></span>')

    # seções trilíngues
    pt_html = (f'<section><h3>Português</h3><p>{safe_text(pt)}</p></section>'
               if pt else
               '<section class="empty"><h3>Português</h3><p>(página sem texto corrente — ver tabelas/figuras)</p></section>')
    en_html = (f'<section><h3>English</h3><p>{safe_text(en)}</p></section>'
               if en else
               '<section class="empty"><h3>English</h3><p>(no running text — see tables/figures)</p></section>')
    lat_html = (f'<section><h3>Latim (transcrito)</h3><p>{safe_text(latin)}</p></section>'
                if latin else
                '<section class="empty"><h3>Latin</h3><p>(página sem texto latino corrente — pode ser tabela ou conteúdo em outro alfabeto)</p></section>')

    # eventos astronômicos
    events_html = ""
    if events:
        items = ""
        for e in events:
            items += (f'<div class="event-item"><strong>{escape(e.get("type","?"))}</strong>: '
                      f'{escape((e.get("description") or "")[:300])}')
            if e.get("historical_date_as_cited"):
                items += f' <em>· data: {escape(e["historical_date_as_cited"])}</em>'
            if e.get("ancient_source"):
                items += f' <em>· fonte: {escape(e["ancient_source"])}</em>'
            items += '</div>'
        events_html = (f'<div class="events-list">'
                       f'<h4>Eventos astronômicos detectados</h4>{items}</div>')

    # tabelas
    tables_html = ""
    if tables:
        tables_html = '<div class="tables-section">'
        for i, t in enumerate(tables, 1):
            cap = t.get("caption_pt", "")
            tables_html += f"<h4>Tabela {i}</h4>"
            if cap:
                tables_html += f'<div class="table-caption">{escape(cap)}</div>'
            tables_html += render_table_html(t)
        tables_html += "</div>"

    # figuras
    figures_html = ""
    for i, f in enumerate(figures, 1):
        desc = f.get('description_pt', '')
        if desc:
            figures_html += f"<p><em>Figura {i}: {safe_text(desc)}</em></p>"

    # flags
    flags_html = ""
    if flags:
        items = "".join(f"<li>{safe_text(fl)}</li>" for fl in flags)
        flags_html = (f'<div class="flag-list"><strong>'
                      f'Flags de incerteza (pontos para revisão humana)</strong>'
                      f'<ul>{items}</ul></div>')

    # notas do tradutor
    notes_html = ""
    if notes:
        notes_html = (f'<div class="notes-block"><strong>Notas do tradutor:</strong> '
                      f'{safe_text(notes)}</div>')

    body = f"""<main>
  <div class="page-nav">{nav_prev}<span class="center">p. {pn} de {total}</span>{nav_next}</div>

  <a href="../assets/scans/{pn:04d}.png" class="scan-link" target="_blank">📄 Ver scan original (p.{pn})</a>

  <div class="trilingual">
    {pt_html}
    {en_html}
    {lat_html}
  </div>

  {tables_html}
  {figures_html}
  {events_html}
  {flags_html}
  {notes_html}

  <div class="page-nav" style="margin-top: 2rem;">{nav_prev}<span class="center">p. {pn} de {total}</span>{nav_next}</div>

  <div class="contribute-block">
    <h4>Encontrou um erro nesta página?</h4>
    <p>Esta tradução é texto-semente gerado por IA — erros são esperados e correções são bem-vindas. Há três caminhos:</p>
    <a href="{issue_url(pn)}" target="_blank">Reportar erro no GitHub</a>
    <a href="https://hypothes.is" target="_blank" class="secondary">Anotar via Hypothes.is</a>
    <a href="{SITE_BASE}about.html" class="secondary">Como contribuir</a>
  </div>
</main>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>p. {pn} — De Emendatione Temporum</title>
<link rel="stylesheet" href="../assets/style.css">
{GOOGLE_FONTS}
{HYPOTHESIS_SCRIPT}
</head>
<body>
{HEADER_TEMPLATE.format(base="../")}
{body}
{render_footer()}
</body>
</html>"""


def render_footer():
    return f"""<footer>
  <div class="footer-inner">
    <h3>Sobre o projeto</h3>
    <p>Tradução colaborativa do <em>Opus de Emendatione Temporum</em> de Joseph Scaliger (Genebra, 1629). Iniciativa pessoal de Walter Gaggiato (São Paulo, 2026), patrocínio próprio. Tradução por IA (Claude Opus 4.7), publicada como texto-semente para revisão acadêmica colaborativa.</p>
    <p>Repositório: <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}" target="_blank">github.com/{GITHUB_USER}/{GITHUB_REPO}</a></p>
    <p>Tradução licenciada sob <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">CC BY-SA 4.0</a>. Texto original de Scaliger em domínio público.</p>
    <p class="meta">Última atualização: abril de 2026</p>
  </div>
</footer>"""


def render_index(pages_meta):
    page_grid = ""
    for p in pages_meta:
        pn = p["page"]
        ptype = p["type"]
        page_grid += f'<a href="pages/{pn:04d}.html" data-page="{pn}">p. {pn}<small>{escape(ptype)}</small></a>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>De Emendatione Temporum — Tradução Colaborativa</title>
<link rel="stylesheet" href="assets/style.css">
{GOOGLE_FONTS}
{HYPOTHESIS_SCRIPT}
</head>
<body>
{HEADER_TEMPLATE.format(base="")}

<section class="hero">
  <div class="meta">Tradução colaborativa · {len(pages_meta)} páginas trilíngues · Lançado em abril de 2026</div>
  <h1 class="display">Em <em>443 anos</em>, ninguém traduziu a obra fundadora da cronologia moderna. Esta é uma <em>primeira tentativa</em>.</h1>
  <p class="lede">
    O <em>Opus de Emendatione Temporum</em> de Joseph Scaliger (1583) introduziu o Período Juliano e organizou pela primeira vez os calendários antigos num quadro coerente. Em latim humanista denso, com citações em grego, hebraico, árabe e siríaco, ficou inacessível a quase todos. Esta página oferece uma tradução de IA das 956 páginas, em português e inglês, publicada como texto-semente para revisão pública por especialistas.
  </p>
</section>

<main>

<div class="disclaimer-banner">
<strong>Aviso essencial.</strong> Esta tradução foi gerada por inteligência artificial (Claude Opus 4.7, da Anthropic). <strong>Contém erros.</strong> Não cite passagens em trabalhos acadêmicos sem verificar contra o original latino. As "flags de incerteza" em cada página marcam pontos onde o modelo registrou dúvida — convite explícito a especialistas para correção via <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues" target="_blank">GitHub Issues</a> ou <a href="https://hypothes.is" target="_blank">Hypothes.is</a>.
</div>

<h2 class="display" style="margin-top: 3rem;">Pontos de entrada</h2>
<p style="font-size: 1.1rem; color: var(--ink-soft); margin: 1rem 0 2rem; max-width: 700px;">
Para começar, recomenda-se a página de <a href="audit_highlights.html"><strong>Núcleo Sólido</strong></a>: oito eclipses datados por Scaliger em 1583 e confirmados pela NASA em 2026. É o melhor cartão de visita do projeto. Para entender método, veja <a href="methodology.html">Metodologia</a>. Para navegar páginas individuais do livro, use a busca abaixo.
</p>

<section class="pages-section" id="paginas">
  <h2>Navegar pelas {len(pages_meta)} páginas</h2>
  <input type="text" class="page-search" placeholder="Buscar página por número (ex: 493) ou tipo (text, table, mixed, frontmatter)" id="page-search-input">
  <div class="page-grid" id="page-grid">
    {page_grid}
  </div>
</section>

<div class="contribute-block">
  <h4>Quer contribuir?</h4>
  <p>Encontrou erro? Quer revisar uma página específica? Há três caminhos diferentes, do mais leve ao mais técnico.</p>
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/issues/new/choose" target="_blank">Abrir issue no GitHub</a>
  <a href="https://hypothes.is" target="_blank" class="secondary">Instalar Hypothes.is</a>
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/CONTRIBUTING.md" target="_blank" class="secondary">Guia de contribuição</a>
</div>

</main>

{render_footer()}

<script>
// Filtro simples no grid de páginas
const input = document.getElementById('page-search-input');
const grid = document.getElementById('page-grid');
const links = grid.querySelectorAll('a');

input.addEventListener('input', e => {{
  const q = e.target.value.toLowerCase().trim();
  links.forEach(a => {{
    const text = a.textContent.toLowerCase();
    a.style.display = text.includes(q) ? 'block' : 'none';
  }});
}});
</script>

</body>
</html>"""


def render_about():
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sobre — De Emendatione Temporum</title>
<link rel="stylesheet" href="assets/style.css">
{GOOGLE_FONTS}
{HYPOTHESIS_SCRIPT}
</head>
<body>
{HEADER_TEMPLATE.format(base="")}

<main>
<h1 class="display">Sobre o projeto</h1>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Quem fez isto</h2>
<p>Iniciativa pessoal de <strong>Walter Gaggiato</strong> (São Paulo, Brasil, 2026), com patrocínio próprio. Não há vínculo institucional. O projeto procura ativamente colaboração de pesquisadores de Letras Clássicas, História da Ciência, Cronologia Bíblica, Astronomia Histórica, e áreas afins.</p>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Por que</h2>
<p>O <em>Opus de Emendatione Temporum</em> nunca foi integralmente traduzido para nenhuma língua vernácula em 443 anos. É a obra fundadora da cronologia histórica como disciplina, e ainda assim permanece acessível apenas a quem domina o latim humanista do século XVI. Este projeto existe para mudar isso — primeiro em português e inglês, depois em outras línguas conforme houver demanda e colaboração.</p>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Como contribuir</h2>
<p>Há três níveis de contribuição, do mais leve ao mais técnico. Detalhes completos em <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/CONTRIBUTING.md" target="_blank">CONTRIBUTING.md</a>.</p>
<ul style="margin-left: 1.5rem; line-height: 2;">
<li><strong>Reportar erro</strong>: clique em "Reportar erro" no rodapé de qualquer página. Não precisa saber Git.</li>
<li><strong>Anotação inline</strong>: instale a extensão <a href="https://hypothes.is" target="_blank">Hypothes.is</a> e marque trechos diretamente nas páginas.</li>
<li><strong>Pull Request</strong>: para quem sabe Git, edite os JSONs e abra PR.</li>
</ul>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Honestidade radical</h2>
<p>A tradução é gerada por IA. Não há garantia de fidelidade absoluta. Erros sistemáticos do modelo Sonnet inicial foram detectados (advérbios latinos confundidos com nomes próprios, números trocados) e corrigidos no segundo passe com Opus 4.7. Mas erros novos podem existir — incluindo erros que humanos detectariam imediatamente e o modelo não. Por isso a publicação aberta com revisão pública é parte essencial do método, não detalhe.</p>

<p>Páginas em árabe, siríaco e hebraico têm tradução parcial e dependem de revisão por especialistas dessas línguas. Tabelas calendáricas densas (~p.769, p.798, p.802) também merecem atenção especialista.</p>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Licença</h2>
<p>Tradução: <strong>CC BY-SA 4.0</strong>. Você pode copiar, modificar, redistribuir, comercializar, desde que atribua e mantenha a mesma licença. O texto original de Scaliger está em domínio público.</p>

<div class="contribute-block">
  <h4>Próximo passo</h4>
  <p>Veja a página de <a href="audit_highlights.html"><strong>Núcleo Sólido</strong></a> — apresenta oito eclipses datados por Scaliger e confirmados pela NASA. É o melhor exemplo do que o projeto busca.</p>
  <a href="audit_highlights.html">Ver Núcleo Sólido</a>
  <a href="methodology.html" class="secondary">Ver Metodologia</a>
</div>

</main>
{render_footer()}
</body>
</html>"""


def render_methodology():
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Metodologia — De Emendatione Temporum</title>
<link rel="stylesheet" href="assets/style.css">
{GOOGLE_FONTS}
{HYPOTHESIS_SCRIPT}
</head>
<body>
{HEADER_TEMPLATE.format(base="")}

<main>
<h1 class="display">Metodologia</h1>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Pipeline</h2>
<ol style="margin-left: 1.5rem; line-height: 2;">
<li><strong>Rasterização</strong>: PDF do Google Books (cópia da edição de Genebra 1629) → 956 PNGs em 200 DPI</li>
<li><strong>Tradução trilíngue</strong>: cada PNG enviado a Claude Opus 4.7 com prompt customizado, gerando JSON estruturado com latim transcrito + tradução pt + tradução en + tabelas + figuras + eventos astronômicos extraídos + flags de incerteza + notas do tradutor</li>
<li><strong>QA estrutural</strong>: validação automática de razão pt/latim, presença de seções, integridade JSON. 96.3% das páginas passaram sem flags; as restantes foram inspecionadas manualmente (em sua maioria, falsos positivos: páginas tabulares, em árabe ou siríaco, ou índices remissivos).</li>
<li><strong>Extração estruturada</strong>: 1.643 eventos astronômicos catalogados em formato auditável (tipo, data citada, fonte antiga, localização)</li>
<li><strong>Auditoria astronômica</strong>: cruzamento com NASA Five Millennium Canon of Solar Eclipses e Lunar Eclipses (Espenak/Meeus). Resultado: 30 MATCH_DATE (data exata confirmada), 10 MATCH_MONTH, 29 MATCH_YEAR_ONLY. <a href="audit_highlights.html">Ver Núcleo Sólido</a> com 8 casos curados narrativamente.</li>
<li><strong>Publicação estática</strong>: HTML+CSS simples, GitHub Pages, custo zero</li>
</ol>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Modelo de IA</h2>
<p>Claude Opus 4.7 (Anthropic), versão de abril de 2026. Janela de 8.000 tokens de saída por página. Custo total da tradução: aproximadamente US$ 200, financiado pelo curador. O prompt incluiu regras explícitas para evitar erros sistemáticos detectados em rodada anterior com Sonnet (preservar advérbios latinos, conferir números duas vezes, manter transliteração grega politônica completa, declarar incerteza em flags).</p>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Limitações conhecidas</h2>
<ul style="margin-left: 1.5rem; line-height: 1.8;">
<li>Páginas em árabe (~p.798, p.802), siríaco (parcial) e hebraico (parcial) têm cobertura limitada</li>
<li>Tabelas densas podem ter erros em valores numéricos individuais que requerem auditoria manual</li>
<li>Citações gregas em ligaduras tipográficas de 1629 podem estar normalizadas para grego clássico padrão (declarado em flags)</li>
<li>Conversões de calendário antigo (Olimpíada, era de Augusto, era de Nabonassar) usam tabelas modernas consensuais — uma divergência detectada na auditoria pode refletir erro da nossa conversão, não de Scaliger</li>
</ul>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Reprodutibilidade</h2>
<p>Todos os scripts de geração estão no <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}" target="_blank">repositório GitHub</a>. Os JSONs estruturados de cada página, os datasets de eventos astronômicos, e os resultados da auditoria estão disponíveis em formato JSONL e CSV. A auditoria astronômica é totalmente reproduzível com Python + Skyfield + canons NASA.</p>

</main>
{render_footer()}
</body>
</html>"""


def render_audit_summary(audit_summary):
    s = audit_summary or {}
    total = s.get("total_events", 0)
    auditable = s.get("auditable_total", 0)
    by_verdict = s.get("by_verdict") or {}

    by_verdict_html = "<table><tr><th>Veredicto</th><th>Contagem</th><th>Significado</th></tr>"
    explanations = {
        "MATCH_DATE": "Ano + mês + dia confirmados pela NASA",
        "MATCH_MONTH": "Ano + mês confirmados; dia ambíguo ou não fornecido",
        "MATCH_YEAR_ONLY": "Apenas ano coincide (fraco para eclipses lunares — múltiplos por ano)",
        "DATA_OFF": "Eclipse existe na janela mas em ano diferente do citado por Scaliger",
        "NO_MATCH": "Nenhum eclipse na janela ±2 anos",
        "era_mention_excluded": "Texto descreve era cronológica, não evento específico (excluído da auditoria)",
        "no_year": "Sem âncora temporal extraível",
        "trivially_correct": "Equinócio ou solstício (recorrente todo ano)",
        "skipped_non_eclipse": "Tipo não auditável astronomicamente",
        "needs_manual_review": "Ocultação ou conjunção que requer análise específica",
        "no_year_or_no_eph": "Sem ano e sem efeméride disponível",
    }
    for v, n in sorted(by_verdict.items(), key=lambda x: -x[1]):
        expl = explanations.get(v, "")
        by_verdict_html += f'<tr><td><code>{escape(v)}</code></td><td>{n}</td><td>{escape(expl)}</td></tr>'
    by_verdict_html += "</table>"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auditoria — De Emendatione Temporum</title>
<link rel="stylesheet" href="assets/style.css">
{GOOGLE_FONTS}
{HYPOTHESIS_SCRIPT}
</head>
<body>
{HEADER_TEMPLATE.format(base="")}

<main>
<h1 class="display">Auditoria astronômica — sumário técnico</h1>

<p style="margin-top: 1rem; font-size: 1.1rem; color: var(--ink-soft); font-style: italic;">
Esta página apresenta os números agregados da auditoria. Para a apresentação narrativa dos casos mais sólidos, veja <a href="audit_highlights.html"><strong>Núcleo Sólido</strong></a>.
</p>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Números gerais</h2>
<ul style="margin-left: 1.5rem; line-height: 1.8;">
<li>Total de eventos extraídos: <strong>{total}</strong></li>
<li>Auditáveis (com data derivável): <strong>{auditable}</strong></li>
<li>Confirmados com data exata (MATCH_DATE): <strong>{by_verdict.get("MATCH_DATE", 0)}</strong></li>
<li>Confirmados com mês (MATCH_MONTH): <strong>{by_verdict.get("MATCH_MONTH", 0)}</strong></li>
<li>Confirmados apenas com ano (MATCH_YEAR_ONLY): <strong>{by_verdict.get("MATCH_YEAR_ONLY", 0)}</strong></li>
</ul>

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Distribuição por veredicto</h2>
{by_verdict_html}

<h2 style="margin-top: 2rem; font-family: 'Cormorant Garamond', serif;">Como interpretar</h2>
<p>A auditoria é <strong>computacional preliminar</strong>, não substitui análise filológica. Para discussão dos critérios e dos casos sólidos com narrativa, fontes primárias e bibliografia secundária, veja a página <a href="audit_highlights.html">Núcleo Sólido</a>.</p>

<p>Limitações:</p>
<ul style="margin-left: 1.5rem; line-height: 1.8;">
<li>Conversões de calendário antigo usam tabelas modernas — divergências podem ser nossas, não de Scaliger</li>
<li>Eventos extraídos por NLP podem perder contexto — Scaliger às vezes <em>discute</em> um evento sem afirmá-lo, e o extrator não distingue</li>
<li>ΔT (correção de rotação da Terra) tem incerteza ±15-20 min para eventos pré-1000 a.C., afetando localidade do path of totality (não a data)</li>
</ul>

<div class="contribute-block">
  <h4>Datasets disponíveis</h4>
  <p>Os datasets brutos da auditoria estão no repositório GitHub para análise crítica:</p>
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/data/audit_dataset.csv" target="_blank">CSV completo (planilha)</a>
  <a href="https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/data/audit_final.jsonl" target="_blank" class="secondary">JSONL (estruturado)</a>
</div>

</main>
{render_footer()}
</body>
</html>"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="../translated_opus",
                   help="Pasta com page-XXXX.json")
    p.add_argument("--out", default="../docs",
                   help="Pasta destino (será o GitHub Pages)")
    p.add_argument("--audit-summary", default="../audit_summary.json")
    p.add_argument("--audit-highlights", default="audit_highlights.html",
                   help="Caminho pro audit_highlights.html já pronto")
    args = p.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    pages_dir = out / "pages"
    assets_dir = out / "assets"
    pages_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # CSS
    (assets_dir / "style.css").write_text(CSS, encoding="utf-8")

    # carrega todas as páginas
    page_jsons = sorted(src.glob("page-*.json"))
    pages_meta = []
    page_nums = []
    for jf in page_jsons:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            pages_meta.append({
                "page": data.get("page", -1),
                "type": data.get("page_type", "?"),
            })
            page_nums.append(data.get("page", -1))
        except json.JSONDecodeError:
            print(f"  ⚠ JSON inválido: {jf}")
            continue

    page_nums.sort()
    pages_meta.sort(key=lambda x: x["page"])

    # gera páginas
    n_generated = 0
    for jf in page_jsons:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        pn = data.get("page", -1)
        idx = page_nums.index(pn) if pn in page_nums else -1
        prev_p = page_nums[idx - 1] if idx > 0 else None
        next_p = page_nums[idx + 1] if 0 <= idx < len(page_nums) - 1 else None
        html = render_page(data, prev_p, next_p, len(page_nums))
        (pages_dir / f"{pn:04d}.html").write_text(html, encoding="utf-8")
        n_generated += 1

    # index, about, methodology, audit
    (out / "index.html").write_text(render_index(pages_meta), encoding="utf-8")
    (out / "about.html").write_text(render_about(), encoding="utf-8")
    (out / "methodology.html").write_text(render_methodology(), encoding="utf-8")

    audit_summary = {}
    if Path(args.audit_summary).exists():
        try:
            audit_summary = json.loads(
                Path(args.audit_summary).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    (out / "audit.html").write_text(
        render_audit_summary(audit_summary), encoding="utf-8")

    # copia audit_highlights.html
    if Path(args.audit_highlights).exists():
        import shutil
        shutil.copy(args.audit_highlights, out / "audit_highlights.html")
        print(f"  ✓ audit_highlights.html copiado")

    # arquivo .nojekyll para evitar processamento Jekyll do GitHub Pages
    (out / ".nojekyll").write_text("", encoding="utf-8")

    print(f"\n✓ Site gerado em {out}/")
    print(f"  {n_generated} páginas geradas")
    print(f"  index.html, about.html, methodology.html, audit.html, audit_highlights.html")
    print()
    print(f"Próximo passo: commit + push para GitHub e ativar Pages.")
    print(f"URL final: {SITE_BASE}")


if __name__ == "__main__":
    main()
