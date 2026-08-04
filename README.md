<div align="center">

# ⚡ Coordenograma

### Curvas de proteção ANSI 50/51 com Streamlit e Plotly

Uma ferramenta leve para criar, comparar e exportar coordenogramas de proteção
de sobrecorrente conforme as normas **IEC** e **ANSI**.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.1%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Proteção](https://img.shields.io/badge/Protecao-ANSI%2050%2F51-1F77B4?style=flat-square)

</div>

---

## Sobre o projeto

O **Coordenograma** é uma aplicação web para estudos de coordenação de proteção
elétrica. Cada curva é independente, permanece armazenada no
<code>st.session_state</code> e é atualizada automaticamente após qualquer
alteração.

O projeto foi desenhado para ser simples de usar em análises acadêmicas,
relatórios técnicos e ajustes preliminares de relés.

## Principais recursos

- Curvas temporizadas **ANSI 51** em eixos logarítmicos.
- Função instantânea **ANSI 50** opcional e integrada ao mesmo traço.
- Múltiplas curvas simultâneas com nome e cor próprios.
- Bibliotecas normalizadas **IEC** e **ANSI**.
- Preenchimento automático de <code>A</code>, <code>B</code> e <code>ALFA</code>.
- Coeficientes editáveis manualmente após a seleção.
- Formatos **Tela**, **A4 Retrato** e **A4 Paisagem**.
- Controle da transparência do grid diretamente no painel.
- Tema claro ou escuro herdado automaticamente do Streamlit.
- Importação e exportação das configurações em JSON.
- Título externo personalizável e gráfico interativo com Plotly.

## Equação utilizada

A função temporizada é calculada por:

$$
t = A + \left(\frac{B}{M^{\alpha}-1}\right)TDS
$$

com:

$$
M = \frac{I_{cc}}{I_p}
$$

onde <code>Ip</code> é a corrente de pickup (<code>IMIN_AT</code>) e
<code>Icc</code> é a corrente avaliada no eixo horizontal.

## Biblioteca de curvas

### Norma IEC

| Tipo de curva | A | B | α |
|---|---:|---:|---:|
| Inversa | 0,0 | 0,14 | 0,02 |
| Muito inversa | 0,0 | 13,5 | 1 |
| Extremamente inversa | 0,0 | 80 | 2 |
| Tempo longo | 0,0 | 120 | 1 |
| Tempo curto | 0,0 | 0,05 | 0,04 |

### Norma ANSI

| Tipo de curva | A | B | α |
|---|---:|---:|---:|
| Moderadamente inversa | 0,0226 | 0,0104 | 0,02 |
| Inversa | 0,180 | 5,98 | 2 |
| Muito inversa | 0,0963 | 3,88 | 2 |
| Extremamente inversa | 0,02434 | 5,64 | 2 |
| Tempo curto | 0,00262 | 0,00342 | 0,02 |

> A curva inicial utiliza **Norma IEC → Extremamente inversa**, com
> <code>A = 0</code>, <code>B = 80</code> e <code>ALFA = 2</code>.

## Instalação

### 1. Crie um ambiente virtual

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

### 2. Instale as dependências

~~~powershell
python -m pip install -r requirements.txt
~~~

### 3. Execute a aplicação

~~~powershell
streamlit run app.py
~~~

Depois, acesse [http://localhost:8501](http://localhost:8501).

## Uso rápido

1. Escolha a **Norma** e o **Tipo de curva**.
2. Ajuste <code>Ip</code>, <code>TDS</code> e os coeficientes, se necessário.
3. Defina a corrente máxima da curva ou habilite a função 50 e informe
   <code>I50</code>.
4. Adicione outras curvas para realizar a coordenação.
5. Selecione o formato da figura e exporte pelo menu do Plotly.
6. Baixe o JSON para continuar o estudo posteriormente.

## Configurações JSON

O arquivo exportado guarda o título, formato da figura, alpha do grid e parâmetros de todas as
curvas. Na importação, os dados são validados, novos identificadores internos
são gerados para evitar conflitos e as curvas são exibidas inicialmente recolhidas.

<details>
<summary>Exemplo simplificado</summary>

~~~json
{
  "version": 3,
  "graph_title": "Coordenograma de Proteção",
  "figure_format": "Tela (Responsivo)",
  "grid_alpha": 0.28,
  "curves": [
    {
      "NOME": "Curva 1",
      "COR": "#D62728",
      "STANDARD": "Norma IEC",
      "CURVE_TYPE": "Extremamente inversa",
      "IMIN_AT": 100.0,
      "A": 0.0,
      "B": 80.0,
      "ALFA": 2.0,
      "TDS": 1.0,
      "ENABLE_50": false,
      "I50": 1000.0,
      "I_MAX": 20000.0
    }
  ]
}
~~~

</details>

## Estrutura

~~~text
coordenograma_web/
├── app.py              # Aplicação Streamlit
├── requirements.txt    # Dependências
├── README.md           # Documentação
└── .gitignore
~~~

## Observação técnica

Os resultados devem ser comparados com as equações e tolerâncias específicas do
fabricante do relé antes da aplicação em um sistema elétrico real.

---

<div align="center">

Desenvolvido por **Daniel Murad de Freitas**

</div>