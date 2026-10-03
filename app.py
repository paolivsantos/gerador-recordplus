import streamlit as st
import re
import json
import base64
import requests
from html.parser import HTMLParser

# 1. Configuração da página DEVE ser a primeira instrução do Streamlit
st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

# 2. Configurações e segredos do GitHub
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "paolivsantos/gerador-recordplus")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
ARQUIVO_JSON_GITHUB = "rascunhos.json"

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Crie e ajuste o conteúdo da página estruturando seções, listas, tabelas e FAQs de forma simples.")

# ---------------------------------------------------------
# FUNÇÕES DE INTEGRAÇÃO COM O GITHUB (Padrão Automático)
# ---------------------------------------------------------
def carregar_do_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return None, None
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{ARQUIVO_JSON_GITHUB}?ref={GITHUB_BRANCH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            file_content = base64.b64decode(file_data["content"]).decode("utf-8")
            return json.loads(file_content), file_data.get("sha")
        elif response.status_code == 404:
            return None, None
        else:
            return None, None
    except Exception:
        return None, None

def salvar_no_github(dados_dict):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.error("Credenciais do GitHub não configuradas.")
        return False
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{ARQUIVO_JSON_GITHUB}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    }
    
    _, sha_atual = carregar_do_github()
    
    json_str = json.dumps(dados_dict, ensure_ascii=False, indent=4)
    content_encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Atualização automática de rascunhos via Gerador RecordPlus [skip ci]",
        "content": content_encoded,
        "branch": GITHUB_BRANCH
    }
    if sha_atual:
        payload["sha"] = sha_atual
        
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True
        else:
            err_msg = response.json().get('message', response.text)
            st.error(f"Erro ao salvar alteração no GitHub: {err_msg}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão com o GitHub: {e}")
        return False

def aplicar_e_sintonizar(novo_dict):
    """Atualiza o estado e sincroniza automaticamente no GitHub com feedback visual"""
    st.session_state.rascunhos = novo_dict
    sucesso_git = salvar_no_github(novo_dict)

    if sucesso_git:
        st.toast("Alteração salva e sincronizada no GitHub com sucesso!", icon="🚀")
    st.rerun()

# ---------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO GLOBAL
# ---------------------------------------------------------
if 'rascunhos' not in st.session_state:
    dados_git, _ = carregar_do_github()
    if dados_git:
        st.session_state.rascunhos = dados_git
    else:
        st.session_state.rascunhos = {
            "Aviso de Privacidade": {"titulo": "Aviso de Privacidade RecordPlus", "secoes": []},
            "Termos de Uso": {"titulo": "Termos de Uso RecordPlus", "secoes": []},
            "Contrato de Assinatura": {"titulo": "Contrato de Assinatura RecordPlus", "secoes": []},
            "F.A.Q.": {"titulo": "F.A.Q.", "secoes": []}
        }

if 'status_salvamento' not in st.session_state:
    st.session_state.status_salvamento = "Sincronizado com a nuvem ☁️"

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
# FUNÇÃO DE CONVERSÃO DE TEXTO
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
# BARRA LATERAL
# ---------------------------------------------------------
with st.sidebar:
    st.header("Configurações")
    
    st.info("☁️ Sincronizado automaticamente com o GitHub!")

    tipo_pagina = st.selectbox(
        "Selecione o Modelo de Página",
        ["Aviso de Privacidade", "Termos de Uso", "Contrato de Assinatura", "F.A.Q."],
        key="unique_tipo_pagina_selectbox"
    )
    
    dados_atuais = st.session_state.rascunhos[tipo_pagina]

    titulo_principal = st.text_input(
        "Título Principal da Página", 
        value=dados_atuais["titulo"], 
        key=f"tit_principal_{tipo_pagina}"
    )
    
    if titulo_principal != dados_atuais["titulo"]:
        st.session_state.rascunhos[tipo_pagina]["titulo"] = titulo_principal
        aplicar_e_sintonizar(st.session_state.rascunhos)
    
    st.divider()

    json_str = json.dumps(st.session_state.rascunhos, ensure_ascii=False, indent=4)
    st.download_button(
        label="📥 Baixar Backup JSON",
        data=json_str,
        file_name="rascunhos_recordplus.json",
        mime="application/json",
        use_container_width=True,
    )

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
                    aplicar_e_sintonizar(st.session_state.rascunhos)
                else:
                    st.warning("Cole o HTML no campo acima.")

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

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL
# ---------------------------------------------------------
st.subheader(f"Conteúdo: {tipo_pagina}")

if not secoes_ativas:
    st.info(f"Nenhuma seção adicionada para **{tipo_pagina}** ainda. Use os botões abaixo para começar.")

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
                    novo_tit_sec = st.text_input(f"Título da Seção {num_secao}", value=secao['titulo'], key=f"tit_{tipo_pagina}_{i}")
                    novo_cont_sec = st.text_area(f"Conteúdo", value=secao['conteudo'], key=f"cont_{tipo_pagina}_{i}", height=120)
                    
                    if novo_tit_sec != secao['titulo'] or novo_cont_sec != secao['conteudo']:
                        secoes_ativas[i]['titulo'] = novo_tit_sec
                        secoes_ativas[i]['conteudo'] = novo_cont_sec
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Remover", key=f"del_{tipo_pagina}_{i}"):
                        secoes_ativas.pop(i)
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                
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
                    novo_ttab = st.text_input(f"Título da Tabela {num_secao}", value=secao['titulo'], key=f"ttab_{tipo_pagina}_{i}")
                    novo_cab = st.text_input(f"Cabeçalho da Tabela (separado por vírgula)", value=secao.get('cabecalho', ''), key=f"cab_{tipo_pagina}_{i}")
                    novo_lin = st.text_area(f"Linhas da Tabela (cada linha em uma quebra, use a 1ª vírgula para separar colunas)", value=secao.get('linhas', ''), key=f"lin_{tipo_pagina}_{i}", height=100)
                    
                    if novo_ttab != secao['titulo'] or novo_cab != secao.get('cabecalho', '') or novo_lin != secao.get('linhas', ''):
                        secoes_ativas[i]['titulo'] = novo_ttab
                        secoes_ativas[i]['cabecalho'] = novo_cab
                        secoes_ativas[i]['linhas'] = novo_lin
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Remover", key=f"del_{tipo_pagina}_{i}"):
                        secoes_ativas.pop(i)
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                
                t_tab = secoes_ativas[i]['titulo']
                cab_raw = secoes_ativas[i]['cabecalho']
                cab_tab = [c.strip() for c in cab_raw.split(',', 1)] if cab_raw else []

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
                            colunas = [c.strip() for c in l.split(',', 1)]
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
                if cat_nome_input != cat_nome_atual:
                    secoes_ativas[i]['nome_categoria'] = cat_nome_input
                    aplicar_e_sintonizar(st.session_state.rascunhos)
            with col2:
                st.write("")
                if st.button("🗑️️ Remover Categoria", key=f"del_cat_{tipo_pagina}_{i}"):
                    secoes_ativas.pop(i)
                    aplicar_e_sintonizar(st.session_state.rascunhos)

            st.markdown("##### Perguntas desta Categoria")
            if 'perguntas' not in secoes_ativas[i]:
                secoes_ativas[i]['perguntas'] = []
            
            perguntas_cat = secoes_ativas[i]['perguntas']
            
            for p_idx, pergunta_obj in enumerate(perguntas_cat):
                cols_p = st.columns([10, 1])
                with cols_p[0]:
                    p_val = pergunta_obj.get('pergunta', '')
                    r_val = pergunta_obj.get('resposta', '')
                    
                    p_input = st.text_input(f"Pergunta {p_idx+1}", value=p_val, key=f"p_{tipo_pagina}_{i}_{p_idx}")
                    r_input = st.text_area(f"Resposta {p_idx+1}", value=r_val, key=f"r_{tipo_pagina}_{i}_{p_idx}", height=80)
                    
                    if p_input != p_val or r_input != r_val:
                        perguntas_cat[p_idx]['pergunta'] = p_input
                        perguntas_cat[p_idx]['resposta'] = r_input
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                with cols_p[1]:
                    st.write("")
                    st.write("")
                    if st.button("❌", key=f"del_p_{tipo_pagina}_{i}_{p_idx}", help="Remover pergunta"):
                        perguntas_cat.pop(p_idx)
                        aplicar_e_sintonizar(st.session_state.rascunhos)
                st.divider()

            if st.button(f"➕ Adicionar Pergunta em '{cat_nome_input or f'Categoria {i+1}'}'", key=f"add_p_btn_{tipo_pagina}_{i}"):
                perguntas_cat.append({'pergunta': '', 'resposta': ''})
                aplicar_e_sintonizar(st.session_state.rascunhos)

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
        if st.button("➕ Adicionar Seção de Texto/Lista", use_container_width=True):
            secoes_ativas.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
            aplicar_e_sintonizar(st.session_state.rascunhos)
    with col_bot2:
        if st.button("📊 Adicionar Tabela", use_container_width=True):
            secoes_ativas.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
            aplicar_e_sintonizar(st.session_state.rascunhos)
else:
    if st.button("➕ Adicionar Nova Categoria de FAQ", use_container_width=True):
        secoes_ativas.append({'tipo': 'categoria_faq', 'nome_categoria': '', 'perguntas': []})
        aplicar_e_sintonizar(st.session_state.rascunhos)

# ---------------------------------------------------------
# MONTAGEM DO HTML COMPLETO (Autossuficiente para CMS)
# ---------------------------------------------------------
html_gerado = f"""<!-- Estilos de segurança embutidos para garantir carregamento no CMS -->
<style>
    .recordplus-container {{
        font-family: Arial, sans-serif;
        color: #e0e0e0;
        background-color: #121212;
        padding: 20px;
        line-height: 1.6;
    }}
    .recordplus-container h1, .recordplus-container h3 {{
        color: #ffffff;
    }}
    .recordplus-container table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }}
    .recordplus-container th, .recordplus-container td {{
        border: 1px solid #444;
        padding: 10px;
        text-align: left;
    }}
    .recordplus-container th {{
        background-color: #5c4a76;
        color: #ffffff;
    }}
    .faq-category-wrapper {{
        margin-bottom: 16px;
    }}
    details.faq-category-accordion summary::-webkit-details-marker,
    details.faq-item-accordion summary::-webkit-details-marker {{
        display: none;
    }}
    details.faq-category-accordion > summary,
    details.faq-item-accordion > summary {{
        list-style: none;
        cursor: pointer;
    }}
    .faq-category-accordion > summary.faq-category-title {{
        font-size: 20px;
        font-weight: 700;
        padding: 12px 24px 12px 0;
        position: relative;
    }}
    .faq-items-box {{
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 12px;
    }}
    details.faq-item-accordion {{
        margin-bottom: 8px;
        border-radius: 6px;
        background-color: rgba(255, 255, 255, 0.04);
    }}
    summary.faq-question {{
        font-size: 16px;
        font-weight: 600;
        padding: 12px 40px 12px 16px;
        position: relative;
    }}
    .faq-answer {{
        font-size: 16px;
        padding: 0 16px 14px 16px;
    }}
    .faq-answer a {{
        color: inherit;
        text-decoration: underline;
    }}
</style>

<div class="recordplus-container">
    <div class="container-help mt-100">
        <h1 class="home-section-termos-title">{titulo_principal}</h1>
        <span class="category-line-termos line-termos"></span>
        {html_secoes_geradas}
    </div>
</div>

<script>
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
</script>"""
# ---------------------------------------------------------
# EXIBIÇÃO DO HTML GERADO
# ---------------------------------------------------------
st.divider()
if st.button("🚀 Gerar Código HTML", type="primary", use_container_width=True):
    st.success("HTML gerado com sucesso!")
    st.subheader("Código HTML final para cópia:")
    st.code(html_gerado, language="html")
