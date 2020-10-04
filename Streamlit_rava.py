import streamlit as st
import altair as alt

import pandas as pd

import matplotlib

matplotlib.use("Agg")

def main():

    bonos = ["AL29", "AL30","AL35","AE38","AL41","AL29D","AL30D","AL35D","AE38D","AL41D",
                  "GD29", "GD30", "GD35", "GD38", "GD41", "GD46", "GD29D", "GD30D", "GD35D", "GD38D", "GD41D","GD46D"]

    choice = st.sidebar.selectbox("Seleccionar bono 1", bonos)
    choice1 = st.sidebar.selectbox("Seleccionar bono 2", bonos)

    url = 'http://www.rava.com/empresas/precioshistoricos.php?e='+choice

    df = pd.read_html(url, thousands='.')[0]

    df.columns = list(df.loc[0, :])
    df = df.drop(0, axis=0)
    df = df.rename(columns={'Fecha': 'index'}).set_index('index')
    df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

    df = df.replace('\.', '', regex=True)
    df = df.replace(',', '.', regex=True)

    df[df.columns[0]] = df[df.columns[0]].apply(pd.to_numeric, errors='coerce').round(2)

    df_ratio = df

    url = 'http://www.rava.com/empresas/precioshistoricos.php?e=' + choice1

    df = pd.read_html(url, thousands='.')[0]

    df.columns = list(df.loc[0, :])

    df = df.drop(0, axis=0)
    df = df.rename(columns={'Fecha': 'index'}).set_index('index')
    df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

    df = df.replace('\.', '', regex=True)
    df = df.replace(',', '.', regex=True)

    df[df.columns[0]] = df[df.columns[0]].apply(pd.to_numeric, errors='coerce').round(2)

    df_ratio ['Cierre1'] = df ['Cierre']

    df_ratio ['Ratio'] = df_ratio.Cierre / df_ratio.Cierre1

    df_ratio.index = pd.to_datetime (df_ratio.index,format='%d/%m/%y')

    df_ratio.sort_index(ascending=True, inplace=True)

    st.dataframe(df_ratio)

    if st.button("Graficar"):
        cust_data = df_ratio["Ratio"]

        line = alt.Chart(cust_data.reset_index()).mark_line(
            color='red',
            size=3
        ).transform_window(
            rolling_mean='mean(Ratio)'
        ).encode(
            x=alt.X('index'),
            y=alt.Y('rolling_mean:Q',scale=alt.Scale(zero=False))
        ).interactive()

        points = alt.Chart(cust_data.reset_index()).mark_line().encode(
            x=alt.X('index'),
            y=alt.Y('Ratio:Q',
                    axis=alt.Axis(title='Ratio'),scale=alt.Scale(zero=False))
        ).interactive()

        st.altair_chart(line+points, use_container_width=True)


if __name__ == '__main__':
    main()