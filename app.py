import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout='wide')
st.title("💼 Продажи менеджеров с разбивкой: до 100K / до–1M / до 10M")

# 📥 Автозагрузка CSV
csv_path = '_SELECT_CONCAT_u_username_u_first_name_AS_Менеджер_s_status_name_202505220912.csv'
df = pd.read_csv(csv_path)

# 🔍 Фильтрация по товарам и дате
df = df[df['Товар'].isin(['Теназол Супер', 'РИЧ 350'])]
df['Дата договора'] = pd.to_datetime(df['Дата договора'])
df = df[(df['Дата договора'] > '2025-05-07') & (df['Дата договора'] < '2025-05-21')]
df['Цена'] = pd.to_numeric(df['Цена'], errors='coerce')
df['Сумма продажи'] = df['Количество'] * df['Цена']

# ▶️ Выбор статуса менеджера
available_statuses = df['Статус менеджера'].dropna().unique().tolist()
selected_statuses = st.multiselect("Выберите статус менеджера", available_statuses, default=available_statuses)

# 🔁 Фильтрация по выбранным статусам
df = df[df['Статус менеджера'].isin(selected_statuses)]

# 📊 Pivot
pivot_df = df.pivot_table(index='Менеджер',
                          columns='Товар',
                          values='Сумма продажи',
                          aggfunc='sum',
                          fill_value=0)
pivot_df['Общая сумма продаж'] = pivot_df.sum(axis=1)
pivot_df = pivot_df.sort_values(by='Общая сумма продаж', ascending=True)

# 🧱 Группировка
low = pivot_df[pivot_df['Общая сумма продаж'] <= 1e5]
mid = pivot_df[(pivot_df['Общая сумма продаж'] > 1e5) & (pivot_df['Общая сумма продаж'] < 1e6)]
high = pivot_df[pivot_df['Общая сумма продаж'] >= 1e6]

gap_low = pd.DataFrame({'Теназол Супер': [None], 'РИЧ 350': [None], 'Общая сумма продаж': [None]}, index=['— до 100K —'])
gap_mid = pd.DataFrame({'Теназол Супер': [None], 'РИЧ 350': [None], 'Общая сумма продаж': [None]}, index=['— до–1M —'])
gap_high = pd.DataFrame({'Теназол Супер': [None], 'РИЧ 350': [None], 'Общая сумма продаж': [None]}, index=['— до 10M —'])

pivot_df_spaced = pd.concat([low, gap_low, mid, gap_mid, high, gap_high])
plot_df = pivot_df_spaced.fillna(0)

# 📎 Подписи
def label_or_blank(series):
    return series.apply(lambda x: "" if pd.isna(x) else f"{x:,.0f}")

# 📈 График
fig = go.Figure()

for товар in ['Теназол Супер', 'РИЧ 350']:
    fig.add_trace(go.Bar(
        x=plot_df.index,
        y=plot_df[товар],
        name=товар,
        text=label_or_blank(pivot_df_spaced[товар]),
        textposition='outside',
        textfont=dict(size=12, color='black')
    ))

fig.add_trace(go.Bar(
    x=plot_df.index,
    y=plot_df['Общая сумма продаж'],
    name='Общая сумма продаж',
    text=label_or_blank(pivot_df_spaced['Общая сумма продаж']),
    textposition='outside',
    textfont=dict(size=12, color='black')
))

# 🎨 Оформление
fig.update_layout(
    title='💼 Продажи менеджеров с разбивкой: до 100K / до 1M / до 10',
    title_font=dict(size=20, color='black'),

    xaxis_title='Менеджер / Группа',
    yaxis_title='Сумма продаж (лог шкала)',

    barmode='group',
    legend_title='Товары и итоги',
    bargap=0.3,
    bargroupgap=0.15,
    width=1800,
    height=800,

    yaxis_type='log',

    plot_bgcolor='white',
    paper_bgcolor='white',

    font=dict(size=14, color='black'),

    xaxis=dict(
        tickangle=-45,
        tickfont=dict(size=12, color='black'),
        titlefont=dict(size=14, color='black')
    ),

    yaxis=dict(
        tickfont=dict(size=12, color='black'),
        titlefont=dict(size=14, color='black'),
        gridcolor='lightgray'
    ),

    legend=dict(
        font=dict(size=13, color='black'),
        bgcolor='white',
        bordercolor='lightgray',
        borderwidth=1
    )
)

fig.update_xaxes(showgrid=False, showline=False, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='lightgray')

st.plotly_chart(fig, use_container_width=True)
