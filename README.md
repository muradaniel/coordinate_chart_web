# Curvas de Proteção ANSI 50/51

Aplicação Streamlit para comparação de curvas de proteção.

A função 51 utiliza a equação:

`t = A + (B / (M**ALFA - 1)) * TDS`, com `M = Icc / Ip`.

`Ip` corresponde a `IMIN_AT` e `Icc` corresponde à corrente `I` avaliada pela curva.`r`n`r`nNa convenção atual, `A` é o termo constante e `B` é o coeficiente da parcela
inversa. As curvas padrão utilizam `A=0`, `B=80` e `ALFA=2`.

A aplicação inicia com as quatro curvas do estudo FASE-FASE: Relé 4, Relé 3,
Relé 2 e Relé 1. A função 50 permanece integrada ao mesmo traço quando
habilitada.

Arquivos JSON da equação anterior são convertidos automaticamente durante a
importação. O formato exportado atualmente utiliza `version=2`.

## Executar

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Toda a implementação está em `app.py`.