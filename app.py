import streamlit as st
import re
from html.parser import HTMLParser

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Crie e ajuste o conteúdo da página estruturando seções, listas e tabelas de forma simples.")

# ---------------------------------------------------------
# CONVERSÃO REVERSA (HTML -> MARKDOWN DO EDITOR)
# ---------------------------------------------------------
def html_para_markdown(html_fragmento):
    if not html_fragmento:
        return ""
    
    # Links: <a href="url" target="_blank">texto</a> -> [texto](url)
    texto = re.sub(r'<a\s+[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', r'[\2](\1)', html_fragmento, flags=re.IGNORECASE)
    
    # Negrito: <b>texto</b> ou <strong>texto</strong> -> **texto**
    texto = re.sub(r'<(?:b|strong)>(.*?)</(?:b|strong)>', r'**\1**', texto, flags=re.IGNORECASE)
    
    # Itálico: <i>texto</i> ou <em>texto</em> -> *texto*
    texto = re.sub(r'<(?:i|em)>(.*?)</(?:i|em)>', r'*\1*', texto, flags=re.IGNORECASE)
    
    # Sublinhado: <u>texto</u> -> _texto_
    texto = re.sub(r'<u>(.*?)</u>', r'_\1_', texto, flags=re.IGNORECASE)
    
    return texto.strip()

# ---------------------------------------------------------
# PARSER PARA IMPORTAR HTML EXISTENTE
# ---------------------------------------------------------
class HTMLSecaoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titulo_principal = ""
        self.secoes = []
        self._current_tag = None
        self._current_data = []
        self._titulo_secao_atual = ""
        self._conteudo_secao_atual = []
        self._em_h1 = False
        self._em_h3 = False
        self._nivel_ul = 0

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        if tag == 'h1':
            self._em_h1 = True
        elif tag == 'h3':
            self._em_h3 = True
            if self._titulo_secao_atual or self._conteudo_secao_atual:
                self.secoes.append({
                    'tipo': 'texto',
                    'titulo': self._titulo_secao_atual,
                    'conteudo': '\n'.join(self._conteudo_secao_atual).strip()
                })
                self._titulo_secao_atual = ""
                self._conteudo_secao_atual = []
        elif tag == 'ul':
            self._nivel_ul += 1

    def handle_endtag(self, tag):
        if tag == 'h1':
            self._em_h1 = False
        elif tag == 'h3':
            self._em_h3 = False
            self._titulo_secao_atual = "".join(self._current_data).strip()
            self._current_data = []
        elif tag == 'p' and not self._em_h3 and not self._em_h1:
            fragmento = "".join(self._current_data).strip()
            if fragmento:
                self._conteudo_secao_atual.append(html_para_markdown(fragmento))
            self._current_data = []
        elif tag == 'li':
            fragmento = "".join(self._current_data).strip()
            if fragmento:
                md_convertido = html_para_markdown(fragmento)
                # Identifica se é sub-lista baseada na profundidade da tag <ul>
                prefixo = "  - " if self._nivel_ul > 1 else "- "
                self._conteudo_secao_atual.append(f"{prefixo}{md_convertido}")
            self._current_data = []
        elif tag == 'ul':
            self._nivel_ul = max(0, self._nivel_ul - 1)
        self._current_tag = None

    def handle_data(self, data):
        if not data:
            return
        if self._em_h1:
            self.titulo_principal += data
        else:
            self._current_data.append(data)

    def fechar(self):
        if self._titulo_secao_atual or self._conteudo_secao_atual:
            self.secoes.append({
                'tipo': 'texto',
                'titulo': self._titulo_secao_atual,
                'conteudo': '\n'.join(self._conteudo_secao_atual).strip()
            })

def importar_html_para_estado(html_str):
    parser = HTMLSecaoParser()
    parser.feed(html_str)
    parser.fechar()
    
    titulo = parser.titulo_principal.strip() if parser.titulo_principal else "Documento RecordPlus"
    secoes = parser.secoes if parser.secoes else []
    return titulo, secoes

# ---------------------------------------------------------
# FUNÇÃO DE CONVERSÃO DE TEXTO (MARKDOWN -> HTML)
# ---------------------------------------------------------
def converter_texto_para_html(texto):
    if not texto:
        return ""
    
    linhas = texto.split('\n')
    html_linhas = []
    nivel_lista = 0

    for linha in linhas:
        espacos_liderantes = len(linha) - len(linha.lstrip(' '))
        linha_strip = linha.strip()

        is_item = linha_strip.startswith('- ') or linha_strip.startswith('* ')

        if is_item:
            item_texto = linha_strip[2:]
            item_texto = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', item_texto)
            item_texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_texto)
            item_texto = re.sub(r'(?<!\w)_(.+?_)(?!\w)', r'<u>\1</u>', item_texto)
            item_texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', item_texto)

            if espacos_liderantes >= 2:
                if nivel_lista == 1:
                    html_linhas.append('<ul>')
                    nivel_lista = 2
                elif nivel_lista == 0:
                    html_linhas.append('<ul><ul>')
                    nivel_lista = 2
                html_linhas.append(f'    <li>{item_texto}</li>')
            else:
                if nivel_lista == 2:
                    html_linhas.append('</ul></ul>')
                    nivel_lista = 1
                elif nivel_lista == 0:
                    html_linhas.append('<ul>')
                    nivel_lista = 1
                html_linhas.append(f'    <li>{item_texto}</li>')
            continue
        else:
            if nivel_lista > 0:
                if nivel_lista == 2:
                    html_linhas.append('</ul></ul>')
                else:
                    html_linhas.append('</ul>')
                nivel_lista = 0

        if not linha_strip:
            continue

        linha_fmt = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', linha)
        linha_fmt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linha_fmt)
        linha_fmt = re.sub(r'(?<!\w)_(.+?_)(?!\w)', r'<u>\1</u>', linha_fmt)
        linha_fmt = re.sub(r'\*(.*?)\*', r'<i>\1</i>', linha_fmt)
        
        html_linhas.append(f'<p>{linha_fmt}</p>')

    if nivel_lista > 0:
        if nivel_lista == 2:
            html_linhas.append('</ul></ul>')
        else:
            html_linhas.append('</ul>')

    return '\n'.join(html_linhas)

# ---------------------------------------------------------
# BARRA LATERAL (FIXA: CONFIGURAÇÕES, GUIA E BOTÕES)
# ---------------------------------------------------------
with st.sidebar:
    st.header("Configurações")
    
    tipo_pagina = st.selectbox(
        "Selecione o Modelo de Página",
        ["Aviso de Privacidade", "Termos de Uso", "Contrato de Assinatura"],
        key="tipo_pagina_select"
    )
    
    if 'rascunhos' not in st.session_state:
        st.session_state.rascunhos = {
            "Aviso de Privacidade": {"titulo": "Aviso de Privacidade RecordPlus", "secoes": []},
            "Termos de Uso": {"titulo": "Termos de Uso RecordPlus", "secoes": []},
            "Contrato de Assinatura": {"titulo": "Contrato de Assinatura RecordPlus", "secoes": []}
        }

    if 'pagina_anterior' not in st.session_state:
        st.session_state.pagina_anterior = tipo_pagina

    if st.session_state.pagina_anterior != tipo_pagina:
        st.session_state.pagina_anterior = tipo_pagina
        st.rerun()

    dados_atuais = st.session_state.rascunhos[tipo_pagina]

    titulo_principal = st.text_input("Título Principal da Página", value=dados_atuais["titulo"], key=f"tit_principal_{tipo_pagina}")
    st.session_state.rascunhos[tipo_pagina]["titulo"] = titulo_principal
    
    st.divider()
    
    with st.expander("📥 Importar HTML Existente"):
        html_importado_input = st.text_area("Cole o código HTML anterior aqui", key=f"imp_{tipo_pagina}", height=100)
        if st.button("Carregar Dados do HTML", key=f"btn_imp_{tipo_pagina}", use_container_width=True):
            if html_importado_input:
                novo_tit, novas_sec = importar_html_para_estado(html_importado_input)
                st.session_state.rascunhos[tipo_pagina]["titulo"] = novo_tit
                if novas_sec:
                    st.session_state.rascunhos[tipo_pagina]["secoes"] = novas_sec
                st.success("HTML importado e convertido com sucesso!")
                st.rerun()
            else:
                st.warning("Cole o HTML no campo acima.")

    st.divider()
    
    st.subheader("➕ Adicionar Seções")
    add_texto_sidebar = st.button("Adicionar Texto/Lista", use_container_width=True)
    add_tabela_sidebar = st.button("Adicionar Tabela", use_container_width=True)

    st.divider()

    with st.expander("💡 Guia Rápido de Formatação", expanded=True):
        st.markdown("""
        * **Negrito**: `**texto**`
        * **Itálico**: `*texto*`
        * **Sublinhado**: `_texto_`
        * **Links**: `[Texto](https://url.com)`
        * **Listas**: Inicie com `- ` ou `* ` (**com espaço**).
        * **Sub-listas**: 2 espaços antes do `- ` ou `* `.
        * **Tabelas**: Separe colunas por vírgula (a 1ª vírgula divide as colunas).
        """)

secoes_ativas = st.session_state.rascunhos[tipo_pagina]["secoes"]

if add_texto_sidebar:
    secoes_ativas.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
    st.rerun()

if add_tabela_sidebar:
    secoes_ativas.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
    st.rerun()

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL
# ---------------------------------------------------------
st.subheader(f"Conteúdo: {tipo_pagina}")

if not secoes_ativas:
    st.info(f"Nenhuma seção adicionada para **{tipo_pagina}** ainda. Use os botões na barra lateral ou importe um HTML existente.")

html_secoes_geradas = ""

for i, secao in enumerate(secoes_ativas):
    tipo_atual = secao.get('tipo', 'texto')
    num_secao = i + 1
    titulo_exibicao = secao['titulo'].strip() if secao['titulo'] else "Nova Seção"
    
    if tipo_atual == 'texto':
        with st.expander(f"Seção {num_secao} [Texto/Lista]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                secoes_ativas[i]['titulo'] = st.text_input(f"Título da Seção {num_secao}", value=secao['titulo'], key=f"tit_{tipo_pagina}_{i}")
                secoes_ativas[i]['conteudo'] = st.text_area(f"Conteúdo", value=secao['conteudo'], key=f"cont_{tipo_pagina}_{i}", height=120)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{tipo_pagina}_{i}"):
                    secoes_ativas.pop(i)
                    st.rerun()
            
            t_sec = secoes_ativas[i]['titulo']
            c_sec = converter_texto_para_html(secoes_ativas[i]['conteudo'])
            
            if t_sec:
                html_secoes_geradas += f"\n    <h3>{t_sec}</h3>"
            if c_sec:
                html_secoes_geradas += f"\n    {c_sec}\n"

    elif tipo_atual == 'tabela':
        with st.expander(f"Seção {num_secao} [Tabela]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                secoes_ativas[i]['titulo'] = st.text_input(f"Título da Tabela {num_secao}", value=secao['titulo'], key=f"ttab_{tipo_pagina}_{i}")
                secoes_ativas[i]['cabecalho'] = st.text_input(f"Cabeçalho da Tabela (separado por vírgula)", value=secao.get('cabecalho', ''), key=f"cab_{tipo_pagina}_{i}")
                secoes_ativas[i]['linhas'] = st.text_area(f"Linhas da Tabela (cada linha em uma quebra)", value=secao.get('linhas', ''), key=f"lin_{tipo_pagina}_{i}", height=100)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{tipo_pagina}_{i}"):
                    secoes_ativas.pop(i)
                    st.rerun()
            
            t_tab = secoes_ativas[i]['titulo']
            cab_raw = secoes_ativas[i]['cabecalho']
            if ',' in cab_raw and cab_raw.count(',') > 1:
                cab_tab = [c.strip() for c in cab_raw.split(',', 1)]
            else:
                cab_tab = [c.strip() for c in cab_raw.split(',')] if cab_raw else []

            linhas_raw = secoes_ativas[i]['linhas'].split('\n') if secoes_ativas[i]['linhas'] else []
            
            html_tabela = ""
            if cab_tab or linhas_raw:
                html_tabela += '\n    <div class="table-container">\n        <table style="width:100%; border-collapse: collapse; border: 1px solid #ddd;">'
                if cab_tab:
                    html_tabela += '\n            <thead>\n                <tr style="background-color: #5c4a76; color: #ffffff;">'
                    for th in cab_tab:
                        html_tabela += f'\n                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left; color: #ffffff;">{th}</th>'
                    html_tabela += '\n                </tr>\n            </thead>'
                
                html_tabela += '\n            <tbody>'
                for l in linhas_raw:
                    if l.strip():
                        if ',' in l:
                            colunas = [c.strip() for c in l.split(',', 1)]
                        else:
                            colunas = [l.strip()]

                        html_tabela += '\n                <tr>'
                        for idx, td in enumerate(colunas):
                            html_tabela += f'\n                    <td style="border: 1px solid #ddd; padding: 8px;">{td}</td>'
                        html_tabela += '\n                </tr>'
                html_tabela += '\n            </tbody>\n        </table>\n    </div>\n'

            if t_tab:
                html_secoes_geradas += f"\n    <h3>{t_tab}</h3>"
            html_secoes_geradas += html_tabela

st.divider()
col_bot1, col_bot2 = st.columns(2)
with col_bot1:
    if st.button("➕ Adicionar Seção de Texto/Lista (Inferior)", use_container_width=True):
        secoes_ativas.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
        st.rerun()
with col_bot2:
    if st.button("📊 Adicionar Tabela (Inferior)", use_container_width=True):
        secoes_ativas.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
        st.rerun()

# ---------------------------------------------------------
# MONTAGEM DO HTML COMPLETO
# ---------------------------------------------------------
html_gerado = f"""<!DOCTYPE html>
<html data-theme="dark" lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <title>RecordPlus | Vídeos, rádios, podcasts para você curtir como quiser.</title>
    <link id="icon" rel="icon" type="image/png" href="https://media.r7.com/r7/media/recordplus/images/faviconrecordplus.ico">
    <link href="https://media.r7.com/r7/media/recordplus/css/all.css" rel="stylesheet">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/css/theme.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/css/styles.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/css/help.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/css/Header.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/css/footer.css">
    <style>
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
        th {{ background-color: #5c4a76; color: #ffffff; }}
    </style>
</head>
<body>
    <div id="modal_container"></div>
    <div class="menu-overlay"></div>
    
    <div class="header">
        <div class="menu-left-wrapper">
            <a href="https://www.recordplus.com/">
                <img alt="Play PLUS" class="img-header" src="https://media.r7.com/r7/media/recordplus/images/im_logo_recordplus.png">
            </a>
        </div>
    </div>

    <div class="container-help mt-100">
        <h1 class="home-section-termos-title">{titulo_principal}</h1>
        <span class="category-line-termos line-termos"></span>
        {html_secoes_geradas}
    </div>

    <footer data-theme="light">
        <div class="bottom-footer">
            <ul class="list-footer">
                <li><a href="https://descubra.recordplus.com/termosdeuso/">Termos de Uso </a><span>|</span></li>
                <li><a href="https://descubra.recordplus.com/politica/">Privacidade</a>  <span>|</span></li>
            </ul>
        </div>
    </footer>
</body>
</html>"""

st.divider()
if st.button("🚀 Gerar Código HTML", type="primary", use_container_width=True):
    st.success("HTML gerado com sucesso!")
    st.subheader("Código HTML final para cópia:")
    st.st.code(html_gerado, language="html") if hasattr(st, 'st') else st.code(html_gerado, language="html")
