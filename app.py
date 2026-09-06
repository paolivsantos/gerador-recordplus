import streamlit as st
import re

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Crie e ajuste o conteúdo da página estruturando seções, listas e tabelas de forma simples.")

# ---------------------------------------------------------
# FUNÇÃO DE CONVERSÃO COM SUPORTE A SUB-LISTAS
# ---------------------------------------------------------
def converter_texto_para_html(texto):
    if not texto:
        return ""
    
    linhas = texto.split('\n')
    html_linhas = []
    nivel_lista = 0  # 0: fora, 1: lista principal, 2: sub-lista

    for linha in linhas:
        # Conta espaços à esquerda para identificar sub-níveis (ex: 2 ou 4 espaços)
        espacos_liderantes = len(linha) - len(linha.lstrip(' '))
        linha_strip = linha.strip()

        # Verifica se é item de lista (começa com - ou * seguido de espaço)
        is_item = linha_strip.startswith('- ') or linha_strip.startswith('* ')

        if is_item:
            item_texto = linha_strip[2:]
            # Formatações internas
            item_texto = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', item_texto)
            item_texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_texto)
            item_texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', item_texto)

            # Define se é sub-lista baseado na indentação
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

        # Formatações de parágrafo normal
        linha_fmt = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', linha)
        linha_fmt = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linha_fmt)
        linha_fmt = re.sub(r'\*(.*?)\*', r'<i>\1</i>', linha_fmt)
        
        html_linhas.append(f'<p>{linha_fmt}</p>')

    if nivel_lista > 0:
        if nivel_lista == 2:
            html_linhas.append('</ul></ul>')
        else:
            html_linhas.append('</ul>')

    return '\n'.join(html_linhas)

# ---------------------------------------------------------
# BARRA LATERAL (FIXA: CONFIGURAÇÕES, GUIA E BOTÕES DE AÇÃO)
# ---------------------------------------------------------
with st.sidebar:
    st.header("Configurações")
    titulo_principal = st.text_input("Título Principal da Página", "Aviso de Privacidade RecordPlus")
    
    st.divider()
    
    st.subheader("➕ Adicionar Seções")
    add_texto_sidebar = st.button("Adicionar Texto/Lista", use_container_width=True)
    add_tabela_sidebar = st.button("Adicionar Tabela", use_container_width=True)

    st.divider()

    with st.expander("💡 Guia Rápido de Formatação", expanded=True):
        st.markdown("""
        * **Negrito**: `**texto**`
        * **Itálico**: `*texto*`
        * **Links**: `[Texto](https://url.com)`
        * **Listas**: Inicie com `- ` ou `* ` (**com espaço** após o símbolo).
        * **Sub-listas**: Dê 2 espaços antes do `- ` ou `* `.
        * **Tabelas**: Cabeçalho por vírgula e linhas abaixo.
        """)

# Inicializa estado das seções
if 'secoes' not in st.session_state:
    st.session_state.secoes = []

# Processa cliques dos botões da barra lateral
if add_texto_sidebar:
    st.session_state.secoes.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
    st.rerun()

if add_tabela_sidebar:
    st.session_state.secoes.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
    st.rerun()

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL (ÁREA DE EDIÇÃO)
# ---------------------------------------------------------
st.subheader("Conteúdo e Seções da Página")

if not st.session_state.secoes:
    st.info("Nenhuma seção adicionada ainda. Use os botões na barra lateral para começar.")

html_secoes_geradas = ""

for i, secao in enumerate(st.session_state.secoes):
    tipo_atual = secao.get('tipo', 'texto')
    num_secao = i + 1
    titulo_exibicao = secao['titulo'].strip() if secao['titulo'] else "Nova Seção"
    
    if tipo_atual == 'texto':
        with st.expander(f"Seção {num_secao} [Texto/Lista]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.secoes[i]['titulo'] = st.text_input(f"Título da Seção {num_secao}", value=secao['titulo'], key=f"tit_{i}")
                st.session_state.secoes[i]['conteudo'] = st.text_area(f"Conteúdo (Aceita formatações e sub-listas com recuo)", value=secao['conteudo'], key=f"cont_{i}", height=120)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{i}"):
                    st.session_state.secoes.pop(i)
                    st.rerun()
            
            t_sec = st.session_state.secoes[i]['titulo']
            c_sec = converter_texto_para_html(st.session_state.secoes[i]['conteudo'])
            
            if t_sec:
                html_secoes_geradas += f"\n    <h3>{t_sec}</h3>"
            if c_sec:
                html_secoes_geradas += f"\n    {c_sec}\n"

    elif tipo_atual == 'tabela':
        with st.expander(f"Seção {num_secao} [Tabela]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.secoes[i]['titulo'] = st.text_input(f"Título da Tabela {num_secao}", value=secao['titulo'], key=f"ttab_{i}")
                st.session_state.secoes[i]['cabecalho'] = st.text_input(f"Cabeçalho da Tabela (separado por vírgula)", value=secao.get('cabecalho', ''), key=f"cab_{i}")
                st.session_state.secoes[i]['linhas'] = st.text_area(f"Linhas da Tabela (cada linha em uma quebra, colunas separadas por vírgula)", value=secao.get('linhas', ''), key=f"lin_{i}", height=100)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{i}"):
                    st.session_state.secoes.pop(i)
                    st.rerun()
            
            t_tab = st.session_state.secoes[i]['titulo']
            cab_tab = [c.strip() for c in st.session_state.secoes[i]['cabecalho'].split(',')] if st.session_state.secoes[i]['cabecalho'] else []
            linhas_raw = st.session_state.secoes[i]['linhas'].split('\n') if st.session_state.secoes[i]['linhas'] else []
            
            html_tabela = ""
            if cab_tab or linhas_raw:
                html_tabela += '\n    <div class="table-container">\n        <table>'
                if cab_tab:
                    html_tabela += '\n            <thead>\n                <tr>'
                    for th in cab_tab:
                        html_tabela += f'\n                    <th>{th}</th>'
                    html_tabela += '\n                </tr>\n            </thead>'
                
                html_tabela += '\n            <tbody>'
                for l in linhas_raw:
                    if l.strip():
                        colunas = [col.strip() for col in l.split(',')]
                        html_tabela += '\n                <tr>'
                        for idx, td in enumerate(colunas):
                            if idx == 0:
                                html_tabela += f'\n                    <td class="cookie-type">{td}</td>'
                            else:
                                html_tabela += f'\n                    <td class="cookie-description">{td}</td>'
                        html_tabela += '\n                </tr>'
                html_tabela += '\n            </tbody>\n        </table>\n    </div>\n'

            if t_tab:
                html_secoes_geradas += f"\n    <h3>{t_tab}</h3>"
            html_secoes_geradas += html_tabela

# Botões inferiores para adicionar seção sem precisar subir a página
st.divider()
col_bot1, col_bot2 = st.columns(2)
with col_bot1:
    if st.button("➕ Adicionar Seção de Texto/Lista (Inferior)", use_container_width=True):
        st.session_state.secoes.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
        st.rerun()
with col_bot2:
    if st.button("📊 Adicionar Tabela (Inferior)", use_container_width=True):
        st.session_state.secoes.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})
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
    <link id="icon" rel="icon" type="image/png" href="http://media.r7.com/r7/media/recordplus/images/faviconrecordplus.ico">
    <link href="http://media.r7.com/r7/media/recordplus/css/all.css" rel="stylesheet">
    <link rel="stylesheet" href="http://media.r7.com/r7/media/recordplus/css/theme.css">
    <link rel="stylesheet" href="http://media.r7.com/r7/media/recordplus/css/styles.css">
    <link rel="stylesheet" href="http://media.r7.com/r7/media/recordplus/css/help.css">
    <link rel="stylesheet" href="http://media.r7.com/r7/media/recordplus/css/Header.css">
    <link rel="stylesheet" href="http://media.r7.com/r7/media/recordplus/css/footer.css">
</head>
<body>
    <div id="modal_container"></div>
    <div class="menu-overlay"></div>
    
    <div class="header">
        <div class="menu-left-wrapper">
            <a href="https://www.recordplus.com/">
                <img alt="Play PLUS" class="img-header" src="http://media.r7.com/r7/media/recordplus/images/im_logo_recordplus.png">
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
        <h1 class="home-section-termos-title">{titulo_principal}</h1>
        <span class="category-line-termos line-termos"></span>
        {html_secoes_geradas}
    </div>

    <footer data-theme="light">
        <div class="bottom-footer">
            <ul class="list-footer">
                <li><a href="https://www.recordplus.com/help/termosdeuso">Termos de Uso </a><span>|</span></li>
                <li><a href="https://www.recordplus.com/help/politica">Privacidade</a>  <span>|</span></li>
            </ul>
        </div>
    </footer>
</body>
</html>"""

st.divider()
if st.button("🚀 Gerar Código e Opção de PDF", type="primary", use_container_width=True):
    st.success("HTML gerado com sucesso!")
    st.subheader("Código HTML final para cópia:")
    st.code(html_gerado, language="html")

    # PLUS: Opção para exportar PDF utilizando componentes de impressão do navegador via st.markdown / HTML embutido
    st.subheader("📄 Visualização e Exportação para PDF")
    st.write("Para salvar como PDF, clique no botão abaixo para abrir a página gerada em uma nova aba e utilize o comando de impressão do seu navegador (`Ctrl+P` / `Cmd+P` -> Salvar como PDF):")
    
    # Cria um data URI para visualização rápida do HTML gerado
    import urllib.parse
    html_bytes = html_gerado.encode("utf-8")
    b64_html = urllib.parse.quote(html_gerado)
    data_url = f"data:text/html;charset=utf-8,{b64_html}"
    
    st.markdown(f'<a href="{data_url}" target="_blank" style="padding: 0.5rem 1rem; background-color: #f63366; color: white; border-radius: 4px; text-decoration: none; font-weight: bold;">🔗 Abrir Página em Nova Aba para Salvar em PDF</a>', unsafe_allow_html=True)
