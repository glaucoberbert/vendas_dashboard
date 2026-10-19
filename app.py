# É aquela biblioteca pra poder montar os caminhos dentro do sistema operacional
import os

# Biblioteca pandas que lê a planilha e trabalha com tabelas
import pandas as pd

# Plotly Express (apelido px): desenha os gráficos
import plotly.express as px

# Dash: cria a página web do dashboard.
# Dash = o aplicativo, dcc = componentes interativos (gráfico e lista de opções),
# html = as caixas, títulos e tabela da página,
# Input e Output = ligam um filtro a um gráfico nos callbacks (explicado lá embaixo)
from dash import Dash, dcc, html, Input, Output

# ---------- 1) DADOS ----------

# Garante que o programa acha a planilha ao lado dele, de qualquer lugar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Junta a pasta com o nome REAL da planilha (com underscores, como baixada).
ARQUIVO = os.path.join(BASE_DIR, "1_-_Base_de_Dados.xlsx")

# Lê a planilha e guarda na variável df (DataFrame = tabela na memória).
df = pd.read_excel(ARQUIVO)

# Tira a coluna "Unnamed: 0", que veio vazia na planilha e a gente nunca usa.
df = df.drop(columns=["Unnamed: 0"])

# Tira o espaço sobrando do começo e do fim do nome do produto
# ("Teclado " vira "Teclado"). Só essa coluna tinha esse problema.
df["Nome_Produto"] = df["Nome_Produto"].str.strip()

# Põe inicial maiúscula nos clientes ("amazon" vira "Amazon", "kabum" vira "Kabum").
# O title() deixa maiúscula a primeira letra de cada palavra; os outros nomes
# já estavam assim, então não mudam.
df["Nome_Cliente"] = df["Nome_Cliente"].str.title()

# Troca "MINAS" por "MG", pra ficar igual às siglas dos outros estados.
df["Estado_Cliente"] = df["Estado_Cliente"].replace({"MINAS": "MG"})

# Meses em português, na ordem do calendário.
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Cria a coluna Mes a partir da data do pedido:
# - dt.month pega o número do mês (1 a 12);
# - o map troca o número pelo nome. Usa MESES[m - 1] porque a lista começa
#   na posição 0 (mês 1 = posição 0);
# - o pd.Categorical avisa a ORDEM certa dos meses. Sem ele, os gráficos
#   ficariam em ordem alfabética (Abril, Agosto, Dezembro...).
df["Mes"] = pd.Categorical(df["Data_Pedido"].dt.month.map(lambda m: MESES[m - 1]),
                           categories=MESES, ordered=True)

# ---------- 2) FUNÇÕES QUE A GENTE REUSA ----------

# Nomes bonitos que aparecem nos eixos e quando passa o mouse no gráfico
# (no lugar do nome da coluna, tipo Valor_Total_Venda).
ROTULOS = {"Valor_Total_Venda": "Total vendido (R$)", "Nome_Representante": "Representante",
           "Nome_Produto": "Produto", "Estado_Cliente": "Estado", "Mes": "Mês"}


# Soma o valor vendido agrupando por uma coluna (igual uma tabela dinâmica do Excel).
# Ex.: soma_por(df, "Regional") devolve o total vendido em cada regional.
# O observed=True evita mostrar mês sem nenhuma venda como linha vazia.
def soma_por(dados, coluna):
    return dados.groupby(coluna, as_index=False, observed=True)["Valor_Total_Venda"].sum()


# Aplica um filtro SÓ se a pessoa escolheu algo na lista.
# Se não escolheu nada (None ou lista vazia), devolve a tabela inteira.
def filtrar(dados, coluna, escolhidos):
    if escolhidos:
        return dados[dados[coluna].isin(escolhidos)]
    return dados


# Gráfico de área: vendas por mês (os meses já saem na ordem do calendário).
def grafico_mes(dados, titulo):
    return px.area(soma_por(dados, "Mes"), x="Mes", y="Valor_Total_Venda",
                   markers=True, labels=ROTULOS, title=titulo)


# Gráfico de barras: vendas por representante, do maior pro menor.
def grafico_representante(dados, titulo):
    soma = soma_por(dados, "Nome_Representante").sort_values("Valor_Total_Venda", ascending=False)
    return px.bar(soma, x="Nome_Representante", y="Valor_Total_Venda",
                  labels=ROTULOS, title=titulo)


# Gráfico de barras: vendas por produto, do maior pro menor.
def grafico_produto(dados, titulo):
    soma = soma_por(dados, "Nome_Produto").sort_values("Valor_Total_Venda", ascending=False)
    return px.bar(soma, x="Nome_Produto", y="Valor_Total_Venda",
                  labels=ROTULOS, title=titulo)


# Escreve um número no padrão brasileiro, sem casas decimais.
# O f"{x:,.0f}" põe vírgula no milhar (177,774,816) e o replace troca por ponto.
def br(x):
    return f"{x:,.0f}".replace(",", ".")


# ---------- 3) GRÁFICOS E TABELA FIXOS (item 1 do roteiro) ----------

# Tabela de produtos: quantidade vendida e total, do produto que mais vendeu pro que menos.
tabela_produto = (df.groupby("Nome_Produto", as_index=False)
                  .agg(Quantidade=("Quantidade_Vendida", "sum"), Total=("Valor_Total_Venda", "sum"))
                  .sort_values("Total", ascending=False))

# Estilo das células da tabela (borda fina e um respiro dentro de cada célula).
CELULA = {"border": "1px solid #ccc", "padding": "4px 8px"}


# Transforma a tabela do pandas numa tabela da página (html.Table), linha por linha.
# Tr = linha, Th = célula de título, Td = célula de dado.
def monta_tabela(dados):
    titulos = html.Tr([html.Th(t, style=CELULA) for t in ["Produto", "Quantidade vendida", "Total vendido"]])
    linhas = [html.Tr([html.Td(r.Nome_Produto, style=CELULA),
                       html.Td(br(r.Quantidade), style=CELULA),
                       html.Td("R$ " + br(r.Total), style=CELULA)])
              for r in dados.itertuples()]
    return html.Table([html.Thead(titulos), html.Tbody(linhas)],
                      style={"borderCollapse": "collapse"})


# Pizza: vendas por regional.
fig_regional = px.pie(soma_por(df, "Regional"), names="Regional", values="Valor_Total_Venda",
                      title="Vendas por Regional")

# Barras: vendas por estado, do maior pro menor.
fig_estado = px.bar(soma_por(df, "Estado_Cliente").sort_values("Valor_Total_Venda", ascending=False),
                    x="Estado_Cliente", y="Valor_Total_Venda", labels=ROTULOS,
                    title="Vendas por Estado")

# ---------- 4) LAYOUT (a página) ----------

app = Dash(__name__)
app.title = "Dashboard de Vendas 2020"

# O PythonAnywhere precisa dessa variável: ela é o servidor web (Flask) que o Dash criou.
server = app.server

# Tudo que aparece na página, de cima pra baixo.
# As listas dos filtros usam valores únicos da própria planilha (sorted = ordem alfabética).
app.layout = html.Div(style={"maxWidth": "1100px", "margin": "0 auto", "fontFamily": "Arial"}, children=[
    html.H1("Dashboard de Vendas - 2020"),

    # Item 1: gráficos e tabela fixos (sem filtro)
    html.H2("1) Visão geral"),
    dcc.Graph(figure=grafico_mes(df, "Vendas por Mês")),
    dcc.Graph(figure=grafico_representante(df, "Vendas por Representante")),
    html.H3("Vendas por Produto"),
    monta_tabela(tabela_produto),
    dcc.Graph(figure=fig_regional),
    dcc.Graph(figure=fig_estado),

    # Item 2: três gráficos que mudam quando a pessoa escolhe algo nos filtros.
    # O id é o "nome" do componente; é por ele que o callback encontra o filtro e o gráfico.
    # multi=True deixa escolher vários itens; sem escolher nada, mostra tudo.
    html.H2("2) Gráficos com filtros"),

    html.H3("Vendas por Mês, filtrando por Representante"),
    dcc.Dropdown(id="f-repr", options=sorted(df["Nome_Representante"].unique()),
                 multi=True, placeholder="Todos os representantes"),
    dcc.Graph(id="g-mes-repr"),

    html.H3("Vendas por Produto, filtrando por Regional"),
    dcc.Dropdown(id="f-regional", options=sorted(df["Regional"].unique()),
                 multi=True, placeholder="Todas as regionais"),
    dcc.Graph(id="g-prod-regional"),

    html.H3("Vendas por Representante, filtrando por Mês e Cliente"),
    dcc.Dropdown(id="f-mes", options=MESES, multi=True, placeholder="Todos os meses"),
    dcc.Dropdown(id="f-cliente", options=sorted(df["Nome_Cliente"].unique()),
                 multi=True, placeholder="Todos os clientes"),
    dcc.Graph(id="g-repr-mes-cliente"),

    # Item 3: filtros encadeados. A lista de cidades começa vazia e é preenchida
    # pelo callback quando a pessoa escolhe um estado.
    html.H2("3) Estado e Cidade"),
    dcc.Dropdown(id="f-estado", options=sorted(df["Estado_Cliente"].unique()),
                 placeholder="Escolha um estado"),
    dcc.Dropdown(id="f-cidade", placeholder="Escolha uma cidade"),
    dcc.Graph(id="g-estado-cidade"),
])

# ---------- 5) CALLBACKS (o que faz os filtros funcionarem) ----------
# Callback = função que o Dash chama sozinho quando a pessoa mexe num filtro.
# Input = o filtro que foi mexido; Output = o que vai ser atualizado.
# O que a função devolve (return) vai para o Output.


# Filtro de representante muda o gráfico de vendas por mês.
@app.callback(Output("g-mes-repr", "figure"), Input("f-repr", "value"))
def atualiza_mes_repr(representantes):
    dados = filtrar(df, "Nome_Representante", representantes)
    return grafico_mes(dados, "Vendas por Mês (filtro: Representante)")


# Filtro de regional muda o gráfico de vendas por produto.
@app.callback(Output("g-prod-regional", "figure"), Input("f-regional", "value"))
def atualiza_prod_regional(regionais):
    dados = filtrar(df, "Regional", regionais)
    return grafico_produto(dados, "Vendas por Produto (filtro: Regional)")


# Filtros de mês e de cliente mudam, juntos, o gráfico de vendas por representante.
@app.callback(Output("g-repr-mes-cliente", "figure"),
              Input("f-mes", "value"), Input("f-cliente", "value"))
def atualiza_repr(meses, clientes):
    dados = filtrar(df, "Mes", meses)
    dados = filtrar(dados, "Nome_Cliente", clientes)
    return grafico_representante(dados, "Vendas por Representante (filtros: Mês e Cliente)")


# FILTRO ENCADEADO: quando o estado muda, troca a lista de cidades.
# Devolve dois valores: as opções novas da cidade e o valor escolhido (None = limpa
# a cidade anterior, pra não sobrar uma cidade de outro estado).
# Se nenhum estado foi escolhido, a comparação não acha nada e a lista fica vazia.
@app.callback(Output("f-cidade", "options"), Output("f-cidade", "value"),
              Input("f-estado", "value"))
def atualiza_cidades(estado):
    cidades = sorted(df.loc[df["Estado_Cliente"] == estado, "Cidade_Cliente"].unique())
    return cidades, None


# Estado e cidade escolhidos mudam o gráfico de vendas por produto naquele local.
@app.callback(Output("g-estado-cidade", "figure"),
              Input("f-estado", "value"), Input("f-cidade", "value"))
def atualiza_estado_cidade(estado, cidade):
    dados = df
    if estado:
        dados = dados[dados["Estado_Cliente"] == estado]
    if cidade:
        dados = dados[dados["Cidade_Cliente"] == cidade]
    local = cidade or estado or "todos os estados"
    soma = soma_por(dados, "Nome_Produto").sort_values("Valor_Total_Venda")
    return px.bar(soma, x="Valor_Total_Venda", y="Nome_Produto", orientation="h",
                  labels=ROTULOS, title=f"Vendas por Produto - {local}")

    
# Só liga o servidor no seu computador quando o arquivo é rodado direto (py app.py).
# No PythonAnywhere esse trecho não roda; quem atende o site é o "server" lá de cima.
if __name__ == "__main__":
    app.run(debug=True)