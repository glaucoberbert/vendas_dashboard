TRABALHO PRÁTICO - DASHBOARD DE VENDAS 2020 (Dash + Plotly Express)

Integrante: Glauco Berbert
Link do dashboard: https://glaucoberbert.pythonanywhere.com

O QUE TEM NO DASHBOARD
1) Visão geral: vendas por mês (área), por representante (barras),
   por produto (tabela), por regional (pizza) e por estado (barras).
2) Três gráficos com filtros: vendas por mês filtrado por representante;
   vendas por produto filtrado por regional; vendas por representante
   filtrado por mês e cliente.
3) Filtros encadeados: ao escolher o estado, a lista de cidades mostra
   só as cidades daquele estado.

ARQUIVOS
app.py ........................ código do dashboard
requirements.txt .............. bibliotecas usadas
1_-_Base_de_Dados.xlsx ........ dados de vendas de 2020
README.txt .................... este arquivo

COMO RODAR NO COMPUTADOR
1. pip install -r requirements.txt
2. python app.py   (no Windows: py app.py)
3. Abrir http://127.0.0.1:8050 no navegador

HOSPEDAGEM
PythonAnywhere (plano gratuito). Foi criado um ambiente virtual com
Python 3.13, as bibliotecas foram instaladas com o requirements.txt e o
arquivo WSGI importa a variável "server" do app.py.