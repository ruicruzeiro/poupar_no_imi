from PyPDF2 import PdfReader
import os
import datetime as dt
from dateutil.relativedelta import relativedelta
import logic as l
from taxas_imi import portugal, gondomar, espinho
import streamlit as st
from PIL import Image

image = Image.open('casa.jpg')
icon = Image.open('casa_icon.jpg')

st.set_page_config(
    page_title='Poupar no IMI',
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        # POUPAR NO IMI

        ### Se eu pedir uma reavaliação às Finanças, passo a pagar menos IMI?

    """)

    st.markdown("""
        ### Carregue aqui a sua Caderneta Predial e descubra!
    """)

    st.text('')

with col2:
    st.text('')
    st.image(image)


# disclaimer

st.markdown("""
<style>
.small-font {
    font-size:12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="small-font">A Caderneta Predial a carregar deverá estar \
        em formato PDF e permitir seleccionar palavras com um duplo clique. \
        Pode obter o documento no Portal das das Finanças. Não guardaremos \
        qualquer ficheiro.', unsafe_allow_html=True)

st.markdown('<p class="small-font">Esta aplicação foi criada para indicar \
        possíveis poupanças de Imposto Municipal sobre Imóveis (IMI) aos \
        proprietários de imóveis urbanos em Portugal. É uma ferramenta \
        experimental e alheia à Autoridade Tributária (AT), não sendo o seu \
        criador responsável por eventuais diferenças no resultado. Estas \
        diferenças poderão ter origem em Cadernetas Prediais com informação \
        desatualizada, regimes especiais de alguns municípios para determinadas \
        zonas, ou dependentes do agregado familiar, entre outras. Não dispensa a \
        consulta do <a href="https://zonamentopf.portaldasfinancas.gov.pt/simulador/default.jsp">Simulador de IMI</a> \
        oficial. </p>', unsafe_allow_html=True)

st.markdown('<p class="small-font">Ao carregar a sua Caderneta Predial, \
        está a declar que tomou conhecimento destes alertas. </p>', unsafe_allow_html=True)

st.markdown('<p class="small-font">Última actualização: 26-07-2024: actualizadas \
    as taxas de IMI de 2023 (referentes aos pagamentos de 2024). </p>', unsafe_allow_html=True)

st.text('')
st.text('')

# carregar PDF

st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.file_uploader("Carregue aqui a sua Caderneta Predial:", type="pdf")

st.text('')
st.text('')

if uploaded_file:

    with st.spinner(text="Analisando o ficheiro..."):

        reader = PdfReader(uploaded_file)

        # extrair conteúdo do PDF com PyPDF2

        text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
        text = ' '.join(text)
        text = text.replace('\n','')

        if 'CADERNETA PREDIAL URBANA' and 'SERVIÇO DE FINANÇAS' and \
            'DADOS DE AVALIAÇÃO' in text:

            # extrair parâmetros individuais do conteúdo

            distrito_concelho, distrito_concelho_freguesia = l.get_codigo_do_local(text)
            ano_inscricao = l.get_ano_inscricao(text)
            data_avaliacao = l.get_data_avaliacao(text)
            VPT_existente, Vc, A, Ca, Cl, Cq, Cv = l.get_param_calc(text, ano_inscricao)

            st.markdown('<p class="small-font">O seu documento contém o \
                Coeficiente de localização abaixo. Este é alterado \
                a cada 3 anos. Pode verificar no <a href="https://zonamentopf.portaldasfinancas.gov.pt/simulador/default.jsp"> \
                Simulador da AT</a> se é o atual.</p>', unsafe_allow_html=True)

            Cl_verif = st.number_input('Coeficiente de Localização', min_value=0.4, max_value=3.5, value=Cl, label_visibility="collapsed")

            if st.button('Confirmar Coeficiente de Localização'):

                # calcular VPT novo

                VPT_novo = round(Vc * A * Ca * Cl_verif * Cq * Cv, 2)


                ### analisar resultados ###

                # ainda não passaram 3 anos após a última avaliação

                if data_avaliacao + relativedelta(years=3) > dt.date.today():

                    st.info('Ainda não é possível pedir uma reavaliação.')
                    st.write('A última reavaliação deste imóvel foi feita em ' \
                        + str(data_avaliacao) + '. A Autoridade Tributária impõe um \
                        período mínimo de 3 anos entre reavaliações. Para saber se \
                        pode poupar no IMI, volte a esta ferramenta no fim desse \
                        prazo, uma vez que vários parâmetros de cálculo podem ser \
                        alterados pela Autoridade Tributária até lá.')

                # já passaram 3 anos mas o valor patrimonial subiu

                elif VPT_novo > VPT_existente:

                    st.warning('Não é aconselhável pedir já uma reavaliação.')
                    st.write('Uma reavaliação pedida neste momento irá fazer subir o \
                            Valor Patrimonial do imóvel para ' + str(int(VPT_novo)) + ' €. \
                            Esta situação poderá dever-se à subida de alguns dos \
                            parâmetros de cálculo pela Autoridade Tributária.')

                # já passaram 3 anos e pode haver poupança

                elif VPT_novo <= VPT_existente:

                    # em 2024, Gondomar e Espinho são os únicos concelhos com
                    # taxas diferentes em algumas freguesias

                    if distrito_concelho == '1304':
                        taxa_concelho = gondomar[distrito_concelho_freguesia]
                    elif distrito_concelho == '0107':
                        taxa_concelho = espinho[distrito_concelho_freguesia]
                    else:
                        taxa_concelho = portugal[distrito_concelho]

                    IMI_existente = int(round(VPT_existente * taxa_concelho, 0))
                    IMI_novo = int(round(VPT_novo * taxa_concelho, 0))
                    IMI_poupanca = IMI_existente - IMI_novo

                    if IMI_poupanca >= 10:

                        st.success('Você pode passar a pagar menos IMI!')
                        st.write('Caso peça uma reavaliação à Autoridade Tributária, \
                            o Valor Patrimonial do imóvel passará a ser de ' + \
                            str(int(VPT_novo)) + ' € e o valor do IMI anual a \
                            pagar de ' + str(IMI_novo) + " €.")
                        st.write('Com a taxa de ' + str(dt.date.today().year) + ', \
                            a poupança anual de IMI neste imóvel é de ' + \
                            str(int(round(IMI_poupanca, 0))) + ' €!')

                    # não há poupança ou esta é inferior a 10 €.

                    else:

                        IMI_poupanca_peq = '{:.2f}'.format(round(VPT_existente \
                            * taxa_concelho, 2) - round(VPT_novo * taxa_concelho, 2))
                        st.info('Pode pagar menos, mas pode não compensar.')
                        st.write('Uma reavaliação irá resultar numa poupança anual \
                            no IMI do imóvel de ' + IMI_poupanca_peq + ' €. \
                            Recordamos que as reavaliações só podem ser pedidas \
                            de 3 em 3 anos, pelo que deve analisar se esta é a \
                            melhor opção para si. Consulte o seu Serviço de \
                            Finanças.')

        else:

            st.error('Esta ferramenta só aceita Cadernetas Prediais Urbanas.')
