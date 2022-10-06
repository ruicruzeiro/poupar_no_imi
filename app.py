from PyPDF2 import PdfReader
import os
import datetime as dt
from dateutil.relativedelta import relativedelta
import logic as l
from taxas_imi import portugal, gondomar
import streamlit as st


st.markdown("""
    # POUPAR NO IMI

    ### Se eu pedir uma reavaliação às Finanças, passo a pagar menos IMI?

""")

st.text('')
st.write('Carregue aqui a sua Caderneta Predial Urbana (CPU) e descubra se é \
    possível poupar no IMI do seu imóvel urbano pedindo a sua reavaliação à \
    Autoridade Tributária. Os ficheiros carregados deverão ser em formato \
    PDF de boa qualidade (deve conseguir seleccionar palavras individuais \
    com um duplo clique). Pode obter o documento certo no Portal das \
    Finanças. Não guardaremos qualquer ficheiro.')
st.text('')

# carregar PDF

st.set_option('deprecation.showfileUploaderEncoding', False)
uploaded_file = st.file_uploader("Carregue aqui a sua CPU:", type="pdf")

# disclaimer

st.markdown("""
<style>
.big-font {
    font-size:12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Esta ferramenta foi criada para ajudar os \
        proprietários de imóveis \
        urbanos em Portugal perceber se podem baixar o valor do seu Imposto \
        Municipal sobre Imóveis (IMI). É uma ferramenta experimental e alheia \
        à Autoridade Tributária (AT), não sendo eventuais diferenças da \
        responsabilidade do seu criador e não está dispensa a consulta do \
        [Simulador de IMI](https://zonamentopf.portaldasfinancas.gov.pt/simulador/default.jsp) \
        oficial. Não obstante, os resultados aqui obtidos são uma análise \
        preliminar importante, que podem encaminhar os cidadãos para uma \
        poupança significativa. Ao seleccionar esta caixa, declaro que \
        tomei conhecimento deste alerta.</p>', unsafe_allow_html=True)


condicoes = 0

if st.checkbox('Concordo com as condições acima.') and uploaded_file is not None:
    condicoes = 1


if st.button('Saiba se pode poupar!'):

    if condicoes == 0:
        st.write('Por favor, carregue um ficheiro válido e aceite as condições.')

    else:

        reader = PdfReader(uploaded_file)

        # extrair conteúdo do PDF com PyPDF2

        text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
        text = ' '.join(text)
        text = text.replace('\n','')

        # extrair parâmetros individuais do conteúdo

        distrito_concelho, distrito_concelho_freguesia = l.get_codigo_do_local(text)
        ano_inscricao = l.get_ano_inscricao(text)
        data_avaliacao = l.get_data_avaliacao(text)
        VPT_existente, VPT_novo = l.get_param_calc(text, ano_inscricao)


        ### analisar resultados ###

        # ainda não passaram 3 anos após a última avaliação

        if data_avaliacao + relativedelta(years=3) > dt.date.today():

            st.info('Ainda não é possível pedir uma reavaliação.')
            st.write('A última reavaliação deste imóvel foi feita em ' + str(data_avaliacao) + '. A Autoridade Tributária impõe um período mínimo de 3 anos entre reavaliações. Para saber se pode poupar no IMI, volte a esta ferramenta no fim desse prazo, uma vez que vários parâmetros de cálculo podem ser alterados pela Autoridade Tributária até lá.')

        # já passaram 3 anos mas o valor patrimonial subiu

        elif VPT_novo > VPT_existente:

            st.warning('Não é aconselhável pedir já uma reavaliação.')
            st.write('Uma reavaliação pedida neste momento irá fazer subir o Valor Patrimonial do imóvel para ' + str(VPT_novo) + ' €. Esta situação poderá dever-se à subida de alguns dos parâmetros de cálculo pela Autoridade Tributária.')

        # já passaram 3 anos e pode haver poupança

        elif VPT_novo <= VPT_existente:

            # Gondomar é o único concelho com taxas diferentes em algumas freguesias

            if distrito_concelho == '1304':
                taxa_concelho = gondomar[distrito_concelho_freguesia]
            else:
                taxa_concelho = portugal[distrito_concelho]

            IMI_existente = round(VPT_existente * taxa_concelho, 2)
            IMI_novo = round(VPT_novo * taxa_concelho, 2)

            st.success('Você pode passar a pagar menos IMI!')
            st.write('Caso peça uma reavaliação à Autoridade Tributária, o Valor Patrimonial do imóvel passará a ser de ' + str(VPT_novo) + ' € e o valor do IMI anual a pagar de ' + str(IMI_novo) + " €.")
            st.write('Com a taxa de ' + str(dt.date.today().year) + ', a poupança anual é de ' + str(IMI_existente - IMI_novo) + ' €!')
