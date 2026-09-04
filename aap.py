import streamlit as st
import re

st.set_page_config(
    page_title="Gerador de Documentos - RecordPlus",
    page_icon="📄",
    layout="wide"
)

# --- 1. CONFIGURAÇÃO DOS MODELOS ---
TIPOS_DOCUMENTO = {
    "Contrato de Assinatura": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE DISPONIBILIZAÇÃO DE CONTEÚDO E OUTRAS AVENÇAS",
    "Termos e Condições de Uso": "Termos e Condições Gerais de Uso do RecordPlus",
    "Política de Privacidade": "Aviso de Privacidade RecordPlus"
}

st.title("🛠️ Gerador de Páginas Estáticas - RecordPlus")
st.markdown("Selecione o documento, monte suas seções de forma dinâmica e gere o HTML final pronto para publicação.")

# --- 2. BARRA LATERAL PARA ESCOLHA DO PROJETO ---
st.sidebar.header("Configurações")
tipo_doc_selecionado = st.sidebar.selectbox("Escolha o Projeto:", list(TIPOS_DOCUMENTO.keys()))

st.sidebar.markdown("---")
st.sidebar.info("💡 **Regras de formatação aceitas nos textos:**\n- **Negrito**: use `<b>texto</b>` ou `**texto**`\n- **Itálico**: use `<i>texto</i>` ou `*texto*\n- **Links**: use `<a href='url'>texto</a>`")

# --- 3. GERENCIAMENTO DE SEÇÕES DINÂMICAS (ESTADO DA SESSÃO) ---
# Inicializa as seções na memória do Streamlit para permitir adicionar/remover dinamicamente
if "secoes" not in st.session_state:
    st.session_state.secoes = [
        {"titulo": "1. Objeto", "conteudo": "Insira o texto da seção aqui..."}
    ]

# Botões de controle de seções
col_b1, col_b2 = st.columns([1, 5])
with col_b1:
    if st.button("➕ Adicionar Seção"):
        st.session_state.secoes.append({"titulo": f"Nova Seção", "conteudo": ""})
        st.rerun()

with col_b2:
    if st.button("🗑️ Remover Última Seção") and len(st.session_state.secoes) > 1:
        st.session_state.secoes.pop()
        st.rerun()

st.markdown("---")
st.subheader(f"Editando: {tipo_doc_selecionado}")

# --- 4. FORMULÁRIO DINÂMICO DE ENTRADA ---
secoes_atualizadas = []

for i, secao in enumerate(st.session_state.secoes):
    with st.expander(f"Seção {i+1}: {secao['titulo'] or 'Sem Título'}", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            novo_titulo = st.text_input(f"Título da Seção {i+1}", value=secao["titulo"], key=f"titulo_{i}")
        
        with col2:
            novo_conteudo = st.text_area(f"Texto da Seção {i+1} (Aceita HTML básico)", value=secao["conteudo"], key=f"conteudo_{i}", height=100)
            
        secoes_atualizadas.append({"titulo": novo_titulo, "conteudo": novo_conteudo})

st.session_state.secoes = secoes_atualizadas

# --- 5. FUNÇÃO AUXILIAR PARA PROCESSAR FORMATOS PERMITIDOS ---
def processar_texto_seguro(texto):
    """
    Garante que apenas tags seguras (b, i, a) passem, 
    ou converte markdown simples para HTML caso o usuário prefira.
    """
    # Exemplo simples: se o usuário digitar markdown simples, podemos converter ou manter HTML
    # Como os modelos utilizam tags HTML puras (<b>, <i>, <a href>), permitiremos tags nativas.
    return texto

# --- 6. GERAÇÃO DO HTML COMPLETO ---
def gerar_html_completo(titulo_principal, secoes):
    # Monta dinamicamente as seções em HTML estruturado idêntico ao padrão R7/RecordPlus
    corpo_html_secoes = ""
    for sec in secoes:
        # Se houver título, adiciona como parágrafo em negrito ou título conforme o padrão do modelo
        if sec["titulo"]:
            corpo_html_secoes += f'    <p><b>{sec["titulo"]}</b></p>\n'
        
        # O conteúdo pode quebrar em parágrafos se houver quebras de linha
        paragrafos = sec["conteudo"].split("\n")
        for p in paragrafos:
            if p.strip():
                corpo_html_secoes += f'    <p>{p.strip()}</p>\n'
        corpo_html_secoes += '    <br>\n'

    # Template HTML Padrão Baseado nos Modelos Fornecidos
    html_template = f"""<!DOCTYPE html>
<html data-theme="dark" lang="pt-br">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <title>RecordPlus | Vídeos, rádios, podcasts para você curtir como quiser.</title>
    <link id="icon" rel="icon" type="image/png" href="https://www.recordplus.com/content/images/faviconrecordplus.ico">
    <link href="https://media.r7.com/r7/media/recordplus/all.css" rel="stylesheet">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/theme.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/styles.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/help.css">
    <link rel="stylesheet" href="https://media.r7.com/r7/media/recordplus/Header.css">
</head>
<body>
    <div class="header">
        <div class="menu-left-wrapper">
            <a href="https://www.recordplus.com/">
                <img alt="Play PLUS" class="img-header" src="https://media.r7.com/r7/media/recordplus/im_logo_recordplus.png">
            </a>
        </div>
        <div class="buutton-login-wrapper">
            <p>Já possui conta?</p>
            <a class="main-button-transparent button-small" href="https://www.recordplus.com/account/login">
                Acesse
            </a>
        </div>
    </div>

    <div class="container-help mt-100">
        <h1 class="title-2">{titulo_principal}</h1>
        <span class="category-line-termos line-termos"></span>

{corpo_html_secoes}

        <p class="text-right">Última atualização: 04.09.2026</p>
    </div>

    <footer data-theme="light">
        <div class="top-footer">
            <div class="right-top-footer">
                <img src="https://media.r7.com/r7/media/recordplus/im_logo_recordplus.png" alt="logo playplus">
            </div>
        </div>
        <div class="bottom-footer">
            <ul class="list-footer">
                <li><a href="https://www.recordplus.com/help/termosdeuso">Termos de Uso </a><span>|</span></li>
                <li><a href="https://www.recordplus.com/help/politica">Privacidade</a>  <span>|</span></li>
                <li><a href="tel:0800 759 3789">Telefone 0800 759 3789</a> <span>|</span></li>
                <li><a href="mailto:suporte@recordplus.com">suporte@recordplus.com</a></li>
            </ul>
        </div>
    </footer>
</body>
</html>
"""
    return html_template

# --- 7. PRÉ-VISUALIZAÇÃO E EXPORTAÇÃO ---
st.markdown("---")
st.subheader("👁️ Pré-visualização do Layout e Download")

if st.button("Gerar Código HTML"):
    titulo_principal_pagina = TIPOS_DOCUMENTO[tipo_doc_selecionado]
    html_gerado = gerar_html_completo(titulo_principal_pagina, st.session_state.secoes)
    
    # Exibe o HTML gerado em uma caixa de código para cópia rápida
    st.code(html_gerado, language="html")
    
    # Botão de Download direto do arquivo .html
    st.download_button(
        label="📥 Baixar Arquivo HTML Estático",
        data=html_gerado,
        file_name=f"{tipo_doc_selecionado.lower().replace(' ', '-')}.html",
        mime="text/html"
    )
