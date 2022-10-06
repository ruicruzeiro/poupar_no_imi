from PyPDF2 import PdfReader
import os
import logic as l

# abrir PDF

file = 'test_pdfs/CPU.pdf'
filepath = os.path.abspath(os.path.join(os.getcwd(), file))



# extrair conteúdo do PDF com PyPDF2

reader = PdfReader(filepath)
text = [reader.pages[page].extract_text() for page in range(len(reader.pages))]
text = ' '.join(text)
text = text.replace('\n','')



# extrair parâmetros individuais do conteúdo

distrito_concelho, distrito_concelho_freguesia = l.get_codigo_do_local(text)
ano_inscricao = l.get_ano_inscricao(text)
data_avaliacao = l.get_data_avaliacao(text)
VPT_existente, VPT_novo = l.get_param_calc(text, ano_inscricao)
