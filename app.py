import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout='wide')
st.title("📊 Продажи менеджеров — сумма или количество")

# 📥 Автозагрузка CSV
csv_path = '_SELECT_CONCAT_u_username_u_first_name_AS_Менеджер_s_status_name_202505220912.csv'
df = pd.read_csv(csv_path)

# 🔍 Фильтрация по товарам и дате
df = df[df['Товар'].isin(['Теназол Супер', 'РИЧ 350'])]
df['Дата договора'] = pd.to_datetime(df['Дата договора'])
df = df[(df['Дата договора'] > '2025-05-08') & (df['Дата договора'] < '2025-05-21')]
df['Цена'] = pd.to_numeric(df['Цена'], errors='coerce')

# ▶️ Выбор режима отображения
metric_type = st.radio("Что отобразить?", ["Количество", "Сумма продаж"])

# ▶️ Выбор статуса менеджера
available_statuses = df['Статус менеджера'].dropna().unique().tolist()
selected_statuses = st.multiselect("Выберите статус менеджера", available_statuses, default=available_statuses)
df = df[df['Статус менеджера'].isin(selected_statuses)]

# 🔢 Расчёт
if metric_type == "Сумма продаж":
    df['Метрика'] = df['Количество'] * df['Цена']
    y_title = 'Сумма продаж (тенге)'
    group_title = 'Общая сумма продаж'
    bins = [0, 1e5, 1e6, 1e9]
    labels = ['— до 100K —', '— до 1M —', '— до 10M+ —']
    chart_title = '💰 Суммарные продажи менеджеров'
else:
    df['Метрика'] = df['Количество']
    y_title = 'Количество проданных упаковок'
    group_title = 'Общее количество'
    bins = [0, 10, 100, 10000]
    labels = ['— до 10 —', '— до 100 —', '— до 1000+ —']
    chart_title = '📦 Количество продаж менеджеров'

# 📊 Pivot
pivot_df = df.pivot_table(index='Менеджер',
                          columns='Товар',
                          values='Метрика',
                          aggfunc='sum',
                          fill_value=0)
pivot_df[group_title] = pivot_df.sum(axis=1)
pivot_df = pivot_df.sort_values(by=group_title, ascending=True)

# 🧱 Группировка по уровням
low = pivot_df[pivot_df[group_title] <= bins[1]]
mid = pivot_df[(pivot_df[group_title] > bins[1]) & (pivot_df[group_title] <= bins[2])]
high = pivot_df[pivot_df[group_title] > bins[2]]

gap_low = pd.DataFrame({col: [None] for col in pivot_df.columns}, index=[labels[0]])
gap_mid = pd.DataFrame({col: [None] for col in pivot_df.columns}, index=[labels[1]])
gap_high = pd.DataFrame({col: [None] for col in pivot_df.columns}, index=[labels[2]])

pivot_df_spaced = pd.concat([low, gap_low, mid, gap_mid, high, gap_high])
plot_df = pivot_df_spaced.fillna(0)

# 📎 Подписи
def label_or_blank(series):
    return series.apply(lambda x: "" if pd.isna(x) else f"{x:,.0f}")

# 📈 График
fig = go.Figure()

# for товар in ['Теназол Супер', 'РИЧ 350']:
#     if товар in plot_df.columns:
#         fig.add_trace(go.Bar(
#             x=plot_df.index,
#             y=plot_df[товар],
#             name=товар,
#             text=label_or_blank(pivot_df_spaced[товар]),
#             textposition='outside',
#             textfont=dict(size=12, color='black')
#         ))

fig.add_trace(go.Bar(
    x=plot_df.index,
    y=plot_df[group_title],
    name=group_title,
    text=label_or_blank(pivot_df_spaced[group_title]),
    textposition='outside',
    textfont=dict(size=12, color='black')
))

# 🎨 Оформление
fig.update_layout(
    title=dict(text=chart_title, font=dict(size=20, color='black')),
    xaxis_title='Менеджер / Группа',
    yaxis_title=y_title,
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
        title=dict(font=dict(size=14, color='black'))
    ),
    yaxis=dict(
        tickfont=dict(size=12, color='black'),
        title=dict(font=dict(size=14, color='black')),
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
