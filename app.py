with st.sidebar:
    st.header("Configurações")
    
    # Indicador de status visual
    st.info(st.session_state.status_salvamento)
    
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
    st.session_state.rascunhos[tipo_pagina]["titulo"] = titulo_principal
    
    st.divider()

    # Botão de Salvamento Manual/Garantido (Evita conflitos de renderização)
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary"):
        sucesso, novo_sha = salvar_rascunhos_github(st.session_state.rascunhos, st.session_state.github_sha)
        if sucesso:
            st.session_state.github_sha = novo_sha
            st.session_state.status_salvamento = "Salvo na nuvem com sucesso! ☁️"
            st.success("Salvo!")
            st.rerun()
        else:
            st.session_state.status_salvamento = "Erro ao salvar ⚠️"
