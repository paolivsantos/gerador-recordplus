import streamlit as st
import re

st.set_page_config(
    page_title="Editor RecordPlus",
    page_icon="📄",
    layout="wide"
)

# --- 1. CONFIGURAÇÃO DOS MODELOS ---
TIPOS_DOCUMENTO = {
    "Contrato de Assinatura": "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE DISPONIBILIZAÇÃO DE CONTEÚDO E OUTRAS AVENÇAS",
    "Termos e Condições de Uso": "Termos e Condições Gerais de Uso do RecordPlus",
    "Política de Privacidade": "Aviso de Privacidade RecordPlus"
}

st.title("🛠️ Editor de Documentos - RecordPlus")
st.markdown("Escreva o conteúdo do documento utilizando formatação simples (sem códigos HTML).")

# --- 2. BARRA LATERAL ---
st.sidebar.header("Configurações")
tipo_doc_selecionado = st.sidebar.selectbox("Escolha o Documento:", list(TIPOS_DOCUMENTO.keys()))

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Guia Rápido de Formatação:**\n\n"
    "- **Negrito:** `**texto**`\n"
    "- **Itálico:** `*texto*`\n"
    "- **Link:** `[Nome do Botão](https://link.com)`\n"
    "- **Títulos:** `# Título` ou `## Subtítulo`"
)

# --- 3. EDITOR DE TEXTO ÚNICO ---
st.markdown(f"### Editando: {tipo_doc_selecionado}")
st.markdown("Cole ou digite todo o texto do documento abaixo:")

# Texto padrão de exemplo para orientar o usuário
texto_padrao = """## 1. Objeto do Serviço
Este documento estabelece os **Termos e Condições** para utilização da plataforma **RecordPlus**. 

Para mais informações, consulte a nossa [Central de Ajuda](https://www.recordplus.com/help).

## 2. Condições de Uso
O acesso aos conteúdos implica na aceitação integral das regras descritas neste instrumento. *Qualquer dúvida, entre em contato.*"""

conteudo_usuario = st.text_area("Conteúdo do Documento", value=texto_padrao, height=350)

# --- 4. FUNÇÃO DE CONVERSÃO INTELIGENTE ---
def markdown_para_html_seguro(texto_md):
    """
    Converte marcações simples de Markdown (negrito, itálico, links, títulos) 
    diretamente para o HTML padrão compatível com o layout R7/RecordPlus.
    """
    linhas = texto_md.split("\n")
    html_final = ""
    
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            html_final += "    <br>\n"
            continue
            
        # Converte Títulos (## ou #)
        if linha_limpa.startswith("## "):
            titulo_texto = linha_limpa.replace("## ", "")
            html_final += f'    <p><b>{titulo_texto}</b></p>\n'
            continue
        elif linha_limpa.startswith("# "):
            titulo_texto = linha_limpa.replace("# ", "")
            html_final += f'    <p><b>{titulo_texto}</b></p>\n'
            continue

        # Processa Negrito (**texto**)
        linha_limpa = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linha_limpa)
        
        # Processa Itálico (*texto*)
        linha_limpa = re.sub(r'\*(.*?)\*', r'<i>\1</i>', linha_limpa)
        
        # Processa Links ([Texto](url))
        linha_limpa = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', linha_limpa)
        
        html_final += f'    <p>{linha_limpa}</p>\n'
        
    return html_final

# --- 5. GERAÇÃO DO HTML COMPLETO ---
def gerar_html_completo(titulo_principal, corpo_convertido):
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

{corpo_convertido}

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

# --- 6. PRÉ-VISUALIZAÇÃO E EXPORTAÇÃO ---
st.markdown("---")
st.subheader("👁️ Visualização e Exportação")

col_prev, col_cod = st.columns(2)

with col_prev:
    st.markdown("**Como o texto vai parecer (Visualização):**")
    st.markdown(conteudo_usuario)

if st.button("Gerar e Baixar HTML Final", type="primary"):
    titulo_principal_pagina = TIPOS_DOCUMENTO[tipo_doc_selecionado]
    corpo_html = markdown_para_html_seguro(conteudo_usuario)
    html_gerado = gerar_html_completo(titulo_principal_pagina, corpo_html)
    
    st.success("Arquivo gerado com sucesso!")
    st.download_button(
        label="📥 Baixar Arquivo .html",
        data=html_gerado,
        file_name=f"{tipo_doc_selecionado.lower().replace(' ', '-')}.html",
        mime="text/html"
    )
