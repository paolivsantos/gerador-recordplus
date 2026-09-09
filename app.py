import streamlit as st
import re
from html.parser import HTMLParser

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Crie e ajuste o conteúdo da página estruturando seções, listas, tabelas e FAQs de forma simples.")

# ---------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO GLOBAL DE RASCUNHOS
# ---------------------------------------------------------
if 'rascunhos' not in st.session_state:
    st.session_state.rascunhos = {
        "Aviso de Privacidade": {
            "titulo": "Aviso de Privacidade RecordPlus", 
            "secoes": []
        },
        "Termos de Uso": {
            "titulo": "Termos de Uso RecordPlus", 
            "secoes": []
        },
        "Contrato de Assinatura": {
            "titulo": "Contrato de Assinatura RecordPlus", 
            "secoes": []
        },
        "F.A.Q.": {
            "titulo": "F.A.Q.", 
            "secoes": []
        }
    }

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
        self._current_data = []

    def handle_endtag(self, tag):
        conteudo_tag = "".join(self._current_data).strip()
        if tag == 'h1':
            self._em_h1 = False
            self.titulo_principal = conteudo_tag
        elif tag == 'h3':
            self._em_h3 = False
            self._titulo_secao_atual = conteudo_tag
        elif tag == 'p' and not self._em_h3 and not self._em_h1:
            if conteudo_tag:
                self._conteudo_secao_atual.append(conteudo_tag)
        elif tag == 'li':
            if conteudo_tag:
                self._conteudo_secao_atual.append(f"- {conteudo_tag}")
        self._current_data = []
        self._current_tag = None

    def handle_data(self, data):
        if data:
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
# FUNÇÃO DE CONVERSÃO DE TEXTO (COM LINKS CLICÁVEIS)
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
# BARRA LATERAL (CONFIGURAÇÕES, GUIA E BOTÕES)
# ---------------------------------------------------------
with st.sidebar:
    st.header("Configurações")
    
    tipo_pagina = st.selectbox(
        "Selecione o Modelo de Página",
        ["Aviso de Privacidade", "Termos de Uso", "Contrato de Assinatura", "F.A.Q."],
        key="tipo_pagina_select"
    )
    
    dados_atuais = st.session_state.rascunhos[tipo_pagina]

    # Atualização direta do título principal vinculado ao rascunho da aba ativa
    titulo_principal = st.text_input(
        "Título Principal da Página", 
        value=dados_atuais["titulo"], 
        key=f"tit_principal_{tipo_pagina}"
    )
    st.session_state.rascunhos[tipo_pagina]["titulo"] = titulo_principal
    
    st.divider()
    
    if tipo_pagina != "F.A.Q.":
        with st.expander("📥 Importar HTML Existente"):
            html_importado_input = st.text_area("Cole o código HTML anterior aqui", key=f"imp_{tipo_pagina}", height=100)
            if st.button("Carregar Dados do HTML", key=f"btn_imp_{tipo_pagina}", use_container_width=True):
                if html_importado_input:
                    novo_tit, novas_sec = importar_html_para_estado(html_importado_input)
                    st.session_state.rascunhos[tipo_pagina]["titulo"] = novo_tit
                    if novas_sec:
                        st.session_state.rascunhos[tipo_pagina]["secoes"] = novas_sec
                    st.success("HTML importado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Cole o HTML no campo acima.")

        st.divider()
        st.subheader("➕ Adicionar Seções")
        add_texto_sidebar = st.button("Adicionar Texto/Lista", use_container_width=True)
        add_tabela_sidebar = st.button("Adicionar Tabela", use_container_width=True)
    else:
        st.subheader("➕ Adicionar Categoria na FAQ")
        add_cat_sidebar = st.button("Adicionar Categoria", use_container_width=True)

    st.divider()

    with st.expander("💡 Guia Rápido de Formatação", expanded=True):
        st.markdown("""
        * **Negrito**: `**texto**`
        * **Itálico**: `*texto*`
        * **Sublinhado**: `_texto_`
        * **Links**: `[Texto do Link](url)`
        * **Listas**: Inicie com `- ` ou `* ` (**com espaço**).
        """)

secoes_ativas = st.session_state.rascunhos[tipo_pagina]["secoes"]

if tipo_pagina != "F.A.Q.":
    if 'add_texto_sidebar' in locals() and add_texto_sidebar:
        secoes_ativas.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
        st.rerun()
    if 'add_tabela_sidebar' in locals() and add_tabela_sidebar:
        secoes_ativas.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
        st.rerun()
else:
    if 'add_cat_sidebar' in locals() and add_cat_sidebar:
        secoes_ativas.append({'tipo': 'categoria_faq', 'nome_categoria': '', 'perguntas': []})
        st.rerun()

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL
# ---------------------------------------------------------
st.subheader(f"Conteúdo: {tipo_pagina}")

if not secoes_ativas:
    st.info(f"Nenhuma seção adicionada para **{tipo_pagina}** ainda. Use os botões na barra lateral.")

html_secoes_geradas = ""

if tipo_pagina != "F.A.Q.":
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
                            colunas = [c.strip() for c in l.split(',')]
                            html_tabela += '\n                <tr>'
                            for td in colunas:
                                html_tabela += f'\n                    <td style="border: 1px solid #ddd; padding: 8px;">{td}</td>'
                            html_tabela += '\n                </tr>'
                    html_tabela += '\n            </tbody>\n        </table>\n    </div>\n'

                if t_tab:
                    html_secoes_geradas += f"\n    <h3>{t_tab}</h3>"
                html_secoes_geradas += html_tabela

else:
    html_faq_gerado = ""
    for i, cat in enumerate(secoes_ativas):
        cat_nome_atual = cat.get('nome_categoria', '')
        with st.expander(f"📂 Categoria: {cat_nome_atual.strip() or f'Categoria {i+1}'}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                cat_nome_input = st.text_input(f"Nome da Categoria {i+1}", value=cat_nome_atual, key=f"cat_nome_{tipo_pagina}_{i}")
                secoes_ativas[i]['nome_categoria'] = cat_nome_input
            with col2:
                st.write("")
                if st.button("🗑️ Remover Categoria", key=f"del_cat_{tipo_pagina}_{i}"):
                    secoes_ativas.pop(i)
                    st.rerun()

            st.markdown("##### Perguntas desta Categoria")
            if 'perguntas' not in secoes_ativas[i]:
                secoes_ativas[i]['perguntas'] = []
            
            perguntas_cat = secoes_ativas[i]['perguntas']
            
            for p_idx, pergunta_obj in enumerate(perguntas_cat):
                cols_p = st.columns([10, 1])
                with cols_p[0]:
                    p_val = pergunta_obj.get('pergunta', '')
                    r_val = pergunta_obj.get('resposta', '')
                    
                    perguntas_cat[p_idx]['pergunta'] = st.text_input(f"Pergunta {p_idx+1}", value=p_val, key=f"p_{tipo_pagina}_{i}_{p_idx}")
                    perguntas_cat[p_idx]['resposta'] = st.text_area(f"Resposta {p_idx+1}", value=r_val, key=f"r_{tipo_pagina}_{i}_{p_idx}", height=80)
                with cols_p[1]:
                    st.write("")
                    st.write("")
                    if st.button("❌", key=f"del_p_{tipo_pagina}_{i}_{p_idx}", help="Remover pergunta"):
                        perguntas_cat.pop(p_idx)
                        st.rerun()
                st.divider()

            if st.button(f"➕ Adicionar Pergunta em '{cat_nome_input or f'Categoria {i+1}'}'", key=f"add_p_btn_{tipo_pagina}_{i}"):
                perguntas_cat.append({'pergunta': '', 'resposta': ''})
                st.rerun()

        # Montagem do HTML da FAQ
        if cat_nome_atual.strip():
            html_faq_gerado += f"""
    <div class="faq-category-wrapper">
        <details class="faq-category-accordion">
            <summary class="faq-category-title">{cat_nome_atual}</summary>
            <div class="faq-items-box">
                <div class="faq-items-container">"""
            
            for p_obj in perguntas_cat:
                p_text = p_obj.get('pergunta', '').strip()
                r_text = converter_texto_para_html(p_obj.get('resposta', ''))
                if p_text:
                    html_faq_gerado += f"""
                    <details class="faq-item-accordion">
                        <summary class="faq-question">{p_text}</summary>
                        <div class="faq-answer">{r_text}</div>
                    </details>"""
            
            html_faq_gerado += """
                </div>
            </div>
        </details>
    </div>"""

    html_secoes_geradas = html_faq_gerado

st.divider()
if tipo_pagina != "F.A.Q.":
    col_bot1, col_bot2 = st.columns(2)
    with col_bot1:
        if st.button("➕ Adicionar Seção de Texto/Lista (Inferior)", use_container_width=True):
            secoes_ativas.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
            st.rerun()
    with col_bot2:
        if st.button("📊 Adicionar Tabela (Inferior)", use_container_width=True):
            secoes_ativas.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
            st.rerun()
else:
    if st.button("➕ Adicionar Nova Categoria (Inferior)", use_container_width=True):
        secoes_ativas.append({'tipo': 'categoria_faq', 'nome_categoria': '', 'perguntas': []})
        st.rerun()

# ---------------------------------------------------------
# MONTAGEM DO HTML COMPLETO COM SETAS E SANFONA NAS SUBCATEGORIAS
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
        
        /* Estilização da FAQ conforme especificações */
        .faq-category-wrapper {{ margin-bottom: 16px; }}
        
        /* Remove marcadores padrão */
        details.faq-category-accordion summary::-webkit-details-marker,
        details.faq-item-accordion summary::-webkit-details-marker {{ display: none; }}
        details.faq-category-accordion > summary,
        details.faq-item-accordion > summary {{ list-style: none; }}

        /* Categoria principal com 20px e Seta Indicativa */
        .faq-category-accordion > summary.faq-category-title {{
            font-size: 20px;
            font-weight: 700;
            padding: 12px 24px 12px 0;
            cursor: pointer;
            position: relative;
        }}
        .faq-category-accordion > summary.faq-category-title::after {{
            content: '';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%) rotate(0deg);
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid currentColor;
            transition: transform 0.3s ease;
        }}
        .faq-category-accordion[open] > summary.faq-category-title::after {{
            transform: translateY(-50%) rotate(180deg);
        }}

        /* Caixa de fundo para as subcategorias */
        .faq-items-box {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 12px;
            margin-top: 8px;
            margin-bottom: 12px;
        }}

        /* Subcategorias (Perguntas) e Respostas com 16px e Seta Indicativa */
        details.faq-item-accordion {{
            margin-bottom: 8px;
            border-radius: 6px;
            background-color: rgba(255, 255, 255, 0.04);
        }}
        details.faq-item-accordion:last-child {{
            margin-bottom: 0;
        }}
        summary.faq-question {{
            font-size: 16px;
            font-weight: 600;
            padding: 12px 40px 12px 16px;
            cursor: pointer;
            position: relative;
        }}
        summary.faq-question::after {{
            content: '';
            position: absolute;
            right: 16px;
            top: 50%;
            transform: translateY(-50%) rotate(0deg);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid currentColor;
            transition: transform 0.3s ease;
        }}
        details.faq-item-accordion[open] > summary.faq-question::after {{
            transform: translateY(-50%) rotate(180deg);
        }}

        .faq-answer {{
            font-size: 16px;
            padding: 0 16px 14px 16px;
            line-height: 1.6;
        }}
        .faq-answer a {{
            color: inherit;
            text-decoration: underline;
        }}
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

    <script>
        // Script para fechar as outras subcategorias ao abrir uma nova dentro da mesma caixa
        document.addEventListener('DOMContentLoaded', () => {{
            const itemAccordions = document.querySelectorAll('details.faq-item-accordion');
            itemAccordions.forEach((item) => {{
                item.addEventListener('toggle', (e) => {{
                    if (item.open) {{
                        itemAccordions.forEach((other) => {{
                            if (other !== item && other.open) {{
                                other.open = false;
                            }}
                        }});
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""

st.divider()
if st.button("🚀 Gerar Código HTML", type="primary", use_container_width=True):
    st.success("HTML gerado com sucesso!")
    st.subheader("Código HTML final para cópia:")
    st.code(html_gerado, language="html")
