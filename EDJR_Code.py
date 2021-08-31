#!/usr/bin/env python
# coding: utf-8

# In[1]:


# importando as bibliotecas necessárias para fazer o web scraping:

from bs4 import BeautifulSoup
from splinter import Browser
import time
import pandas as pd
import requests
import re


# In[2]:


# função que armazena os links de cada resolução para a extração de dados:

def get_urls():

#SUGESTÃO: Colocar um input para o usuário digitar o mês em que deseja extrair os dados

    lista_urls = []

# usando o splinter para pesquisar no site do diário oficial pelas páginas com os dados a serem capturados:
    
    with Browser() as browser:
        url = "https://www.in.gov.br/leiturajornal"
        browser.visit(url)
        time.sleep(3)
        browser.fill('search-bar', 'deferir os registros e as petições dos produtos saneantes')
        advsearch_button = browser.find_by_id('toggle-search-advanced')
        advsearch_button.click()
        tipo_pesquisa_button = browser.find_by_id('tipo-pesquisa-1')
        tipo_pesquisa_button.click()
        ano_button = browser.find_by_id('ano')
        ano_button.click()
        pesquisa_button = browser.find_by_text('PESQUISAR')
        pesquisa_button.click()
        
        time.sleep(3)

# filtrando os links desejados na página de resultados da pesquisa:
        
        links_maio = browser.links.find_by_partial_href("maio")
        for i in links_maio:
            lista_urls.append(i["href"])    
        links_junho = browser.links.find_by_partial_href("junho")
        for i in links_junho:
            lista_urls.append(i["href"])  
            
    return lista_urls


# In[5]:


# função que separa os dados e os armazena corretamente:

def get_data():
    
    urls = get_urls()
    titulos = ['RESOLUÇÃO', 'NOME DA EMPRESA:', 'AUTORIZAÇÃO:', 'NOME DO PRODUTO E MARCA:', 'NUMERO DE PROCESSO:', 'NUMERO DE REGISTRO:', 'VENDA E EMPREGO:', 'VENCIMENTO:', 'APRESENTAÇÃO:', 'VALIDADE DO PRODUTO:', 'CATEGORIA:', 'ASSUNTO DA PETIÇÃO:', 'EXPEDIENTE DA PETIÇÃO:', 'VERSÃO:']
    df = pd.DataFrame(columns=['RESOLUÇÃO', 'EMPRESA', 'AUTORIZAÇÃO', 'MARCA', 'PROCESSO', 'REGISTRO', 'VENDA E EMPREGO', 'VENCIMENTO', 'APRESENTAÇÃO', 'VALIDADE PRODUTO', 'CATEGORIA', 'ASSUNTO PETIÇÃO', 'EXPEDIENTE PETIÇÃO', 'VERSÃO'])
    
# separação dos dados de cada empresa por parágrafos:    
    
    for url in urls:
        soup = BeautifulSoup(requests.get(url).text)
        paragraphs_joined = " ".join([data.text for data in soup.find_all(class_="dou-paragraph")])
        resolucao = soup.find(class_="identifica")
        splitted_paragraphs = paragraphs_joined.split("_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
        
# quebra de cada string em substrings e formatação individual de cada informação: 

        for paragrafo in splitted_paragraphs:
            for titulo in titulos:
                paragrafo = paragrafo.replace(titulo, '@' + titulo)
                paragrafo = paragrafo + '@'
                
            empresa = re.search("NOME DA EMPRESA: (.+?) @", paragrafo)
            empresa_string = (empresa.group(1))
            autoriz = re.search("AUTORIZAÇÃO: (.+?) @", paragrafo)
            autoriz_string = (autoriz.group(1))
            marca =  re.findall("NOME DO PRODUTO E MARCA: (.+?) @", paragrafo)
            process =  re.findall("NUMERO DE PROCESSO: (.+?) @", paragrafo)
            registro =  re.findall("NUMERO DE REGISTRO: (.+?) @", paragrafo)
            venda =  re.findall("VENDA E EMPREGO: (.+?) @", paragrafo)
            vencim =  re.findall("VENCIMENTO: (.+?) @", paragrafo)
            apresen =  re.findall("APRESENTAÇÃO: (.+?) @", paragrafo)
            valid =  re.findall("VALIDADE DO PRODUTO: (.+?) @", paragrafo)
            categ =  re.findall("CATEGORIA: (.+?) @", paragrafo)
            assunt =  re.findall("ASSUNTO DA PETIÇÃO: (.+?) @", paragrafo)
                                     
            test_exp = bool(re.search("EXPEDIENTE DA PETIÇÃO:", paragrafo))
            if test_exp is True:
                expedi =  re.findall("EXPEDIENTE DA PETIÇÃO:(.+?) @", paragrafo)                         
                                     
            test_ver = bool(re.search("VERSÃO: ", paragrafo))
            if test_ver is True:
                versao =  re.findall("VERSÃO: (.+?) @", paragrafo)                         
    
# formatação de cada substring em um dataframe:        
        
            indices = 0     
            for product in marca:
                row_list = []
                row_list.append(resolucao.text)
                row_list.append(empresa_string)
                row_list.append(autoriz_string)
                row_list.append(product)
                row_list.append(process[indices])
                row_list.append(registro[indices])
                row_list.append(venda[indices])
                try:
                    row_list.append(vencim[indices])
                except:
                    row_list.append('-')
                row_list.append(apresen[indices])
                row_list.append(valid[indices])
                row_list.append(categ[indices])
                try:
                    row_list.append(assunt[indices])
                except:
                    row_list.append('-')
                try:
                    if test_exp is True:
                        row_list.append(expedi[indices])
                    else:
                        row_list.append('-')
                except:
                    row_list.append('-')
                try:
                    if test_ver is True:
                        row_list.append(versao[indices])
                    else:
                        row_list.append('-')
                except:
                    row_list.append('-')
        
                indices = indices + 1
                    
                df.loc[-1] = row_list
                df.index = df.index + 1                      
        
    df.to_excel("dados_do_cliente.xlsx")    
    print("Dados do cliente salvos com sucesso")
    


# In[6]:


get_data()


# In[ ]:




