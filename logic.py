import regex
import datetime as dt



### extrair informação relevante da CPU ###

def get_codigo_do_local(text):
    distrito = regex.findall('(?<=DISTRITO: )\d+', text)
    concelho = regex.findall('(?<=CONCELHO: )\d+', text)
    freguesia = regex.findall('(?<=FREGUESIA: )\d+', text)
    distrito_concelho = distrito[0] + concelho[0]
    distrito_concelho_freguesia = distrito_concelho + freguesia[0]
    return distrito_concelho, distrito_concelho_freguesia

def get_ano_inscricao(text):
    ano_inscricao = regex.findall('(?<=Ano de inscrição na matriz: )(.*)(?= Valor patrimonial actual)', text)
    ano_inscricao = int(ano_inscricao[0])
    return ano_inscricao

def get_data_avaliacao(text):
    data_avaliacao = regex.findall('(?<=Avaliada em : )(.*)', text)
    data_avaliacao = data_avaliacao[0].split()[0]
    data_avaliacao = dt.datetime.strptime(data_avaliacao, '%Y/%m/%d')
    data_avaliacao = data_avaliacao.date()
    return data_avaliacao

def get_param_calc(text, ano_inscricao):
    ext_vpt = regex.findall('Valor patrimonial actual \(CIMI\):\s*€([\d,.]+)', text)
    VPT_existente = float(ext_vpt[0].replace('.', '').replace(',', '.'))

    ext_calc = regex.findall('(?<=Vc x A x Ca x Cl x Cq x Cv )(.*)(?= Vt = valor patrimonial tributário)', text)
    ext_calc = ext_calc[0].split()

    # valor de construção em 26-07-2024 (última actualização deste código)

    Vc = 665.00 # Valor em 2022: 640; actualizado em 2023, mantido em 2024

    # extrair coeficientes da CPU

    A = float(ext_calc[4].replace('.', '').replace(',', '.'))
    Ca = float(ext_calc[6].replace('.', '').replace(',', '.'))
    Cl = float(ext_calc[8].replace('.', '').replace(',', '.'))
    Cq = float(ext_calc[10].replace('.', '').replace(',', '.'))

    # calcular o coeficiente de vetustez

    idade = dt.date.today().year - ano_inscricao

    if idade < 2:
        Cv = 1.0
    elif idade >= 2 and idade <= 8:
        Cv = 0.9
    elif idade >= 9 and idade <= 15:
        Cv = 0.85
    elif idade >= 16 and idade <= 25:
        Cv = 0.8
    elif idade >= 26 and idade <= 40:
        Cv = 0.75
    elif idade >= 41 and idade <= 50:
        Cv = 0.65
    elif idade >= 51 and idade <= 60:
        Cv = 0.55
    elif idade > 60:
        Cv = 0.4

    return VPT_existente, Vc, A, Ca, Cl, Cq, Cv
