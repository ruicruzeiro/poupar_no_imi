from PyPDF2 import PdfReader
import os
import datetime as dt
from dateutil.relativedelta import relativedelta
import logic as l
from taxas_imi import portugal, gondomar
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

    st.write('Carregue aqui a sua Caderneta Predial e descubra se pode \
        poupar no IMI do seu imóvel pedindo a sua reavaliação à Autoridade \
        Tributária. Esta deverá ser em formato PDF e ter boa qualidade (deve \
        conseguir seleccionar palavras com um duplo clique). Pode obter o PDF \
        no Portal das Finanças.')
    st.text('')

with col2:
    st.text('')
    st.image(image)


# carregar PDF

st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.file_uploader("Carregue aqui a sua Caderneta Predial:", type="pdf")

# disclaimer

st.markdown("""
<style>
.small-font {
    font-size:12px !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<p class="small-font">Não guardaremos qualquer ficheiro. Esta \
        ferramenta foi criada para ajudar os proprietários de imóveis \
        urbanos em Portugal perceber se podem baixar o valor do seu Imposto \
        Municipal sobre Imóveis (IMI). É uma ferramenta experimental e alheia \
        à Autoridade Tributária (AT), não sendo eventuais diferenças da \
        responsabilidade do seu criador e não está dispensada a consulta do \
        <a href="https://zonamentopf.portaldasfinancas.gov.pt/simulador/default.jsp">Simulador de IMI</a> \
        oficial. </p>', unsafe_allow_html=True)

st.markdown('<p class="small-font">As eventuais diferenças poderão ter origem \
        na revisão de alguns parâmetros de cálculo pela AT, como o Coeficiente \
        de Localização, pelo que poderá haver diferenças entre os parâmetros \
        reais e os registados na sua Caderneta Predial. Exemplos disso \
        são alguns regimes especiais de municípios para determinadas zonas \
        e o número de dependentes do agregado familiar. </p>', unsafe_allow_html=True)

st.markdown('<p class="small-font">Não obstante, os resultados aqui \
        obtidos são uma análise preliminar importante, que podem encaminhar o \
        cidadão para uma poupança significativa. Ao seleccionar esta caixa, \
        declaro que tomei conhecimento destes alertas. </p>', unsafe_allow_html=True)


condicoes = 0

if st.checkbox('Concordo com as condições acima.') and uploaded_file is not None:
    condicoes = 1


if st.button('Saiba se pode poupar!'):

    if condicoes == 0:
        st.write('Por favor, carregue um PDF e aceite as condições.')

    else:

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
                VPT_existente, VPT_novo = l.get_param_calc(text, ano_inscricao)


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

                    # Gondomar é o único concelho com taxas diferentes em algumas
                    # freguesias

                    if distrito_concelho == '1304':
                        taxa_concelho = gondomar[distrito_concelho_freguesia]
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
