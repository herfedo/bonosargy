import streamlit as st
import altair as alt

import pandas as pd

import matplotlib
import base64

matplotlib.use("Agg")

def download_link(object_to_download, download_filename, download_link_text):

    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=True)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def main():

    bonos = ["AL29", "AL30","AL35","AE38","AL41","AL29D","AL30D","AL35D","AE38D","AL41D",
                  "GD29", "GD30", "GD35", "GD38", "GD41", "GD46", "GD29D", "GD30D", "GD35D", "GD38D", "GD41D","GD46D"]

    st.sidebar.title("Bonos Argy")

    choice = st.sidebar.selectbox("Seleccionar bono 1", bonos)
    choice1 = st.sidebar.selectbox("Seleccionar bono 2", bonos)

    st.sidebar.info('\nEsta app fue creada usando Streamlit y es mantenida por [herfedo]('
                    'https://twitter.com/herfedo).\n\n')

    url = 'http://www.rava.com/empresas/precioshistoricos.php?e='+choice

    df_1 = pd.read_html(url, thousands='.')[0]

    df_1.columns = list(df_1.loc[0, :])
    df_1 = df_1.drop(0, axis=0)
    df_1 = df_1.rename(columns={'Fecha': 'index'}).set_index('index')
    #df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

    df_1 = df_1.replace('\.', '', regex=True)
    df_1 = df_1.replace(',', '.', regex=True)

    df_1[df_1.columns[0:4]] = df_1[df_1.columns[0:4]].apply(pd.to_numeric, errors='coerce').round(2)

    df_1.rename(columns=lambda col: choice+'_'+ col, inplace=True)

    url = 'http://www.rava.com/empresas/precioshistoricos.php?e=' + choice1

    df_2 = pd.read_html(url, thousands='.')[0]

    df_2.columns = list(df_2.loc[0, :])

    df_2 = df_2.drop(0, axis=0)
    df_2 = df_2.rename(columns={'Fecha': 'index'}).set_index('index')
    #df = df.drop(columns=['Apertura', 'Mínimo', 'Volumen', 'Máximo'], axis=1)

    df_2 = df_2.replace('\.', '', regex=True)
    df_2 = df_2.replace(',', '.', regex=True)

    df_2[df_2.columns[0:4]] = df_2[df_2.columns[0:4]].apply(pd.to_numeric, errors='coerce').round(2)

    if choice == choice1:
        choice1 = choice1+'_1'

    df_2.rename(columns=lambda col: choice1 + '_' + col, inplace=True)

    df_ratio = pd.concat([df_1, df_2], axis=1, sort=False)

    #print(df_ratio)

    df_ratio ['Ratio'] = df_ratio[choice+'_'+'Cierre'] / df_ratio[choice1+'_'+'Cierre']

    df_ratio.index = pd.to_datetime (df_ratio.index,format='%d/%m/%y')

    df_ratio.sort_index(ascending=True, inplace=True)

    st.dataframe(df_ratio.style.set_precision(2))

    if st.button("Descargar"):
        #open('bonos.csv', 'w').write(df_ratio.to_csv())
        tmp_download_link = download_link(df_ratio, 'bonos_'+choice+'_'+choice1+'.csv', 'Presione para descargar el archivo')
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
            y=alt.Y('rolling_mean:Q',scale=alt.Scale(zero=False))
        ).properties(title=choice+'/'+choice1).interactive()

        points = alt.Chart(cust_data.reset_index()).mark_line().encode(
            x=alt.X('index',axis=alt.Axis(title='Fecha')),
            y=alt.Y('Ratio:Q',
                    axis=alt.Axis(title='Ratio - Media'),scale=alt.Scale(zero=False))
        ).interactive()

        chart = line+points

        st.altair_chart(chart, use_container_width=True)

        base1 = alt.Chart(df_ratio.reset_index()).encode(
            alt.X('index',axis=alt.Axis(title='Fecha')))

        line_1 = base1.mark_line(
            color='red',
            size=3
        ).encode(
            y=alt.Y(choice+'_'+'Cierre:Q',scale=alt.Scale(zero=False),
                    axis=alt.Axis(title='Cierre', titleColor='red'))
        ).properties(title=choice).interactive()

        area_1 = base1.mark_area(opacity=0.3, color='#57A44C').encode(
            alt.Y(choice+'_'+'Máximo:Q',scale=alt.Scale(zero=False)
                  ),
            alt.Y2(choice+'_'+'Mínimo:Q')
        )

        st.altair_chart(line_1+area_1, use_container_width=True)

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

        st.altair_chart(line_2+area_2, use_container_width=True)

if __name__ == '__main__':
    main()