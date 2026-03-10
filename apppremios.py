import streamlit as st
import datetime

# --- CONFIGURAÇÃO DA PÁGINA E ÍCONE DO NAVEGADOR ---
# O parâmetro page_icon puxa o arquivo icone.png
st.set_page_config(page_title="Calculadora de Prêmios", page_icon="icone.png", layout="wide")


# --- SISTEMA DE LOGIN ---
def verificar_senha():
    """Retorna True se o usuário inseriu a senha correta."""
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Centralizando a tela de login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image("logo.png", use_column_width=True)
            except:
                st.warning("Salve o arquivo do logotipo como 'logo.png' na mesma pasta.")

            st.subheader("Acesso Restrito")
            senha_digitada = st.text_input("Senha", type="password")

            if st.button("Entrar"):
                if senha_digitada == "royal2024":
                    st.session_state["autenticado"] = True
                    st.rerun()  # Atualiza a página para mostrar o app
                else:
                    st.error("Senha incorreta. Tente novamente.")
        return False
    return True


# --- SE O LOGIN FOR BEM SUCEDIDO, RODA O APP ---
if verificar_senha():

    # Exibe o logo no topo do app (menor)
    try:
        st.image("logo.png", width=250)
    except:
        pass

    st.title("Calculadora de Prêmios")

    # --- 1. CAMPOS DO ADMINISTRADOR (Barra Lateral) ---
    st.sidebar.header("⚙️ Parâmetros (Administrador)")

    curva_dolar_input = st.sidebar.number_input("Curva Dólar (%)", value=8.60, format="%.2f")
    juros_aa_input = st.sidebar.number_input("Juros a.a. (%)", value=7.20, format="%.2f")

    fobbings = st.sidebar.number_input("Fobbings", value=9.00, format="%.2f")
    retencao_quebra = st.sidebar.number_input("Retenção/Quebra Rod (Multiplicador)", value=1.0015, format="%.4f")
    desagio_financeiro = st.sidebar.selectbox("Deságio Financeiro?", ["SIM", "NÃO"])

    st.sidebar.markdown("---")
    st.sidebar.info("As taxas em (%) são automaticamente convertidas para as fórmulas.")

    # Botão para sair (Logout) na barra lateral
    if st.sidebar.button("Sair (Logout)"):
        st.session_state["autenticado"] = False
        st.rerun()

    # --- 2. CAMPOS DO VENDEDOR ---
    st.header("Dados da Negociação")

    col1, col2, col3 = st.columns(3)

    with col1:
        cliente = st.text_input("Cliente")
        dolar_spot = st.number_input("Dólar Spot", value=5.1783, format="%.4f")
        cbot = st.number_input("Cotação Cbot", value=1199.5000, format="%.4f")
        r_sc = st.number_input("R$/SC", value=123.00, format="%.2f")

    with col2:
        inicio_entrega = st.date_input("Início da Entrega", format="DD/MM/YYYY")
        final_entrega = st.date_input("Final da Entrega", format="DD/MM/YYYY")
        data_pagamento = st.date_input("Data Pagamento", format="DD/MM/YYYY")

    with col3:
        destino = st.text_input("Destino")
        frete_destino = st.number_input("Frete Destino", value=120.00, format="%.4f")
        frete_pgua = st.number_input("Frete Pgua", value=260.00, format="%.4f")

    # --- 3. CONVERSÃO DE TAXAS E CÁLCULOS ---
    curva_dolar = curva_dolar_input / 100
    juros_aa = juros_aa_input / 100

    hoje = datetime.date.today()
    qtd_dias = (data_pagamento - hoje).days

    dolar_futuro = dolar_spot
    if qtd_dias > 0:
        dolar_futuro = ((1 + curva_dolar) ** (qtd_dias / 360)) * dolar_spot

    dias_entrega_total = (final_entrega - inicio_entrega).days
    med_dias_entrega = inicio_entrega + datetime.timedelta(days=(dias_entrega_total // 2))

    entrega_x_pagamento = (data_pagamento - med_dias_entrega).days
    qtd_desagio = entrega_x_pagamento - 30
    desagio_meses = qtd_desagio / 30

    if desagio_financeiro == "SIM":
        preco_c_desagio = r_sc - ((juros_aa / 12) * desagio_meses * r_sc)
    else:
        preco_c_desagio = r_sc

    premio = 0.0
    if dolar_futuro > 0:
        premio = ((((((preco_c_desagio * retencao_quebra) - (frete_destino * 0.06)) + (
                    frete_pgua * 0.06)) / 0.06) / dolar_futuro) + fobbings) / 0.367454 - cbot

    # --- 4. RESULTADOS ---
    st.markdown("---")
    st.header("Resultado Final")

    # Arredondamento idêntico ao Excel
    premio_arredondado = round(premio)

    st.metric(label="Prêmio Calculado (cents/bushel)", value=f"{premio_arredondado}")

    texto_para_copiar = f"""Cliente: {cliente}
Início da Entrega: {inicio_entrega.strftime('%d/%m/%Y')}
Final da Entrega: {final_entrega.strftime('%d/%m/%Y')}
Data de Pagamento: {data_pagamento.strftime('%d/%m/%Y')}
R$/SC: {r_sc:.2f}
Prêmio: {premio_arredondado}"""

    st.subheader("Copiar Dados")
    st.code(texto_para_copiar, language="text")

    with st.expander("Ver cálculos intermediários (Auditoria)"):
        st.write(f"- **Hoje:** {hoje.strftime('%d/%m/%Y')}")
        st.write(f"- **Quantidade de Dias:** {qtd_dias}")
        st.write(f"- **Dólar Futuro:** {dolar_futuro:.4f}")
        st.write(f"- **Med. Dias de Entrega:** {med_dias_entrega.strftime('%d/%m/%Y')}")
        st.write(f"- **Entrega x Pagamento:** {entrega_x_pagamento} dias")
        st.write(f"- **Quantidade Deságio:** {qtd_desagio}")
        st.write(f"- **Deságio em Meses:** {desagio_meses:.4f}")
        st.write(f"- **Preço C Deságio:** {preco_c_desagio:.4f}")
