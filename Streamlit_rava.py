import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import seaborn as sns

import base64


def download_link(object_to_download, download_filename, download_link_text):

    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=True)

        b64 = base64.b64encode(object_to_download.encode()).decode()

        return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def main():

    bonos = ["AL29", "AL30","AL35","AE38","AL41","AL29D","AL30D","AL35D","AE38D","AL41D",
                  "GD29", "GD30", "GD35", "GD38", "GD41", "GD46", "GD29D", "GD30D", "GD35D", "GD38D", "GD41D","GD46D"]

    periodos = ["Historico", "Intradiario"]

    st.sidebar.title("Bonos Argy")

    choice = st.sidebar.selectbox("Seleccionar bono 1", bonos)
    choice1 = st.sidebar.selectbox("Seleccionar bono 2", bonos)

    periodo = st.sidebar.selectbox("Seleccionar periodo", periodos)

    if periodo == 'Historico':

        url = 'http://www.rava.com/empresas/precioshistoricos.php?e=' + choice

        df_1 = pd.read_html(url, thousands='.')[0]

        df_1.columns = list(df_1.loc[0, :])
        df_1 = df_1.drop(0, axis=0)
        df_1 = df_1.rename(columns={'Fecha': 'index'}).set_index('index')
        # df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

        df_1 = df_1.replace('\.', '', regex=True)
        df_1 = df_1.replace(',', '.', regex=True)

        df_1[df_1.columns[0:5]] = df_1[df_1.columns[0:5]].apply(pd.to_numeric, errors='coerce').round(2)

        df_1.rename(columns=lambda col: choice + '_' + col, inplace=True)

        url = 'http://www.rava.com/empresas/precioshistoricos.php?e=' + choice1

        df_2 = pd.read_html(url, thousands='.')[0]

        df_2.columns = list(df_2.loc[0, :])

        df_2 = df_2.drop(0, axis=0)
        df_2 = df_2.rename(columns={'Fecha': 'index'}).set_index('index')
        # df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

        df_2 = df_2.replace('\.', '', regex=True)
        df_2 = df_2.replace(',', '.', regex=True)

        df_2[df_2.columns[0:5]] = df_2[df_2.columns[0:5]].apply(pd.to_numeric, errors='coerce').round(2)

        if choice == choice1:
            choice1 = choice1 + '_1'

        df_2.rename(columns=lambda col: choice1 + '_' + col, inplace=True)

        df_ratio = pd.concat([df_1, df_2], axis=1, sort=False)

        # print(df_ratio)

        df_ratio['Ratio'] = df_ratio[choice + '_' + 'Cierre'] / df_ratio[choice1 + '_' + 'Cierre']

        df_ratio.index = pd.to_datetime(df_ratio.index, format='%d/%m/%y')

        df_ratio.sort_index(ascending=True, inplace=True)

        st.dataframe(df_ratio.style.highlight_max(color='green', axis=0).format('{:,.2f}').format({'Ratio': '{:,.5f}'}))
    else:
        df = pd.read_csv("intradiario.csv",sep=';')
        df = df.replace('\.', '', regex=True)
        df = df.replace(',', '.', regex=True)
        df = df.rename(columns={'Fecha': 'index'}).set_index('index')
        df [df.columns[0:22]] = df[df.columns[0:22]].apply(pd.to_numeric, errors='coerce').round(2)
        df = df.replace(0,np.nan)

        if choice == choice1:
            choice1 = choice1 + '_1'
            df_ratio = df.filter([choice + '_' + 'Cierre'], axis=1)
            df_ratio[choice1 + '_' + 'Cierre'] = df_ratio[choice + '_' + 'Cierre']
        else:
            df_ratio = df.filter([choice + '_' + 'Cierre',choice1 + '_' + 'Cierre'], axis=1)


        df_ratio['Ratio'] = (df_ratio[choice + '_' + 'Cierre'] / df_ratio[choice1 + '_' + 'Cierre']).replace(np.inf, np.nan )


        df_ratio.index = pd.to_datetime(df_ratio.index, format='%d/%m/%Y %H:%M')

        df_ratio.sort_index(ascending=True, inplace=True)

        #cm = sns.light_palette("green", as_cmap=True)

        st.dataframe(df_ratio.style.highlight_max(color='green', axis=0).format('{:,.2f}').format({'Ratio':'{:,.5f}'}))


    if st.button("Descargar"):
        # open('bonos.csv', 'w').write(df_ratio.to_csv())
        tmp_download_link = download_link(df_ratio, 'bonos_' + choice + '_' + choice1 + '.csv',
                                          'Presione para descargar el archivo')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

    if st.button("Resumen"):
        st.write(df_ratio.describe())

    if st.button("Graficar"):
        cust_data = df_ratio["Ratio"]

        line = alt.Chart(cust_data.reset_index()).mark_line(
            color='red',
            size=3
        ).transform_window(
            rolling_mean='mean(Ratio)'
        ).encode(
            x=alt.X('index'),
            y=alt.Y('rolling_mean:Q', scale=alt.Scale(zero=False))
        ).properties(title=choice + '/' + choice1).interactive()

        points = alt.Chart(cust_data.reset_index()).mark_line().encode(
            x=alt.X('index', axis=alt.Axis(title='Fecha')),
            y=alt.Y('Ratio:Q',
                    axis=alt.Axis(title='Ratio - Media'), scale=alt.Scale(zero=False))
        ).interactive()

        chart = line + points

        st.altair_chart(chart, use_container_width=True)

        base1 = alt.Chart(df_ratio.reset_index()).encode(
            alt.X('index', axis=alt.Axis(title='Fecha')))

        line_1 = base1.mark_line(
            color='red',
            size=3
        ).encode(
            y=alt.Y(choice + '_' + 'Cierre:Q', scale=alt.Scale(zero=False),
                    axis=alt.Axis(title='Cierre', titleColor='red'))
        ).properties(title=choice).interactive()

        area_1 = base1.mark_area(opacity=0.3, color='#57A44C').encode(
            alt.Y(choice + '_' + 'Máximo:Q', scale=alt.Scale(zero=False)
                  ),
            alt.Y2(choice + '_' + 'Mínimo:Q')
        )

        bar_1 = base1.mark_bar().encode(
            alt.Y(choice + '_' + 'Volumen:Q', axis=alt.Axis(title='Volumen', titleColor='red'))
        )

        layer1 = alt.layer(line_1 + area_1, bar_1).resolve_scale(
            y='independent'
        )

        st.altair_chart(layer1, use_container_width=True)

        base2 = alt.Chart(df_ratio.reset_index()).encode(
            alt.X('index', axis=alt.Axis(title='Fecha')))

        line_2 = base2.mark_line(
            color='red',
            size=3
        ).encode(
            y=alt.Y(choice1 + '_' + 'Cierre:Q', scale=alt.Scale(zero=False),
                    axis=alt.Axis(title='Cierre', titleColor='red'))
        ).properties(title=choice1).interactive()

        area_2 = base2.mark_area(opacity=0.3, color='#57A44C').encode(
            alt.Y(choice1 + '_' + 'Máximo:Q', scale=alt.Scale(zero=False)
                  ),
            alt.Y2(choice1 + '_' + 'Mínimo:Q')
        )

        bar_2 = base2.mark_bar().encode(
            alt.Y(choice1 + '_' + 'Volumen:Q', axis=alt.Axis(title='Volumen', titleColor='red')
                  )
        )

        layer2 = alt.layer(line_2 + area_2, bar_2).resolve_scale(
            y='independent'
        )

        st.altair_chart(layer2, use_container_width=True)


    st.sidebar.info('\nEsta app fue creada usando Streamlit y es mantenida por [herfedo]('
                    'https://twitter.com/herfedo).\n\n'
                    'La informacion historica e intradiaria se actualiza al finalizar la rueda.')




if __name__ == '__main__':
    main()