import streamlit as st
import pandas as pd
import plotly.express as px

# page configuration
st.set_page_config(
    page_title="Global Cereal Crop Yield Dashboard",
    layout="wide"
)

# custom css
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] * {
        color: #111111 !important;
    }
    div[data-testid="stMetric"] label {
        color: #555555 !important;
        font-size: 13px !important;
    }
    .section-label {
        font-size: 13px;
        color: #888888;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)


# load and cache the data
@st.cache_data
def load_data():
    data = pd.read_csv("cereal_yield.csv", skiprows=4)
    data = data.dropna(axis=1, how='all')

    id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    year_cols = [col for col in data.columns if col.isdigit()]

    data = data[id_cols + year_cols]

    # reshape so each row is one country one year
    data = data.melt(id_vars=id_cols, var_name='Year', value_name='Yield')
    data['Year'] = data['Year'].astype(int)
    data = data.dropna(subset=['Yield'])

    return data

df = load_data()


# shared axis style
axis_style = dict(
    tickfont=dict(color='#333333', size=12),
    titlefont=dict(color='#333333', size=13),
    linecolor='#cccccc',
    gridcolor='#e8e8e8'
)


# sidebar filters
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Use the filters below to explore the data")

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

selected_year = st.sidebar.slider(
    "Select a Year",
    min_value=min_year,
    max_value=max_year,
    value=2020
)

countries_list = sorted(df['Country Name'].unique())

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    options=countries_list,
    default=["United Kingdom", "India", "United States", "China", "Brazil"]
)

top_n = st.sidebar.selectbox(
    "Number of Top/Bottom Countries",
    options=[5, 10, 15, 20],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** World Bank — Cereal Yield (kg per hectare) 1961–2024")


# dashboard title banner
st.markdown("""
<div style="background-color:#2e7d32; padding:24px 28px; border-radius:10px; margin-bottom:20px;">
    <h1 style="color:#ffffff; margin:0; font-size:28px;">Global Cereal Crop Yield Dashboard</h1>
    <p style="color:#c8e6c9; margin:6px 0 0 0; font-size:15px;">
        Exploring cereal crop yield trends across 266 countries from 1961 to 2024 — 
        providing insights into global agricultural sustainability.
    </p>
</div>
""", unsafe_allow_html=True)

# filter data for selected year
df_year = df[df['Year'] == selected_year]

# kpi metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Selected Year", value=str(selected_year))
col2.metric(label="Countries with Data", value=str(df_year['Country Name'].nunique()))
col3.metric(label="Global Avg Yield (kg/ha)", value=f"{df_year['Yield'].mean():,.0f}")
col4.metric(label="Highest Yield (kg/ha)", value=f"{df_year['Yield'].max():,.0f}")


# ── Visualisation 1 — World Map ──────────────────────────────
st.markdown("---")
st.markdown('<p class="section-label">Visualisation 1 — Choropleth World Map</p>', unsafe_allow_html=True)
st.header("Cereal Yield by Country")
st.markdown(f"The map below shows cereal yield across the world for **{selected_year}**. Darker green indicates higher yield.")

fig_map = px.choropleth(
    df_year,
    locations='Country Code',
    color='Yield',
    hover_name='Country Name',
    hover_data={'Yield': ':,.0f', 'Country Code': False},
    color_continuous_scale='YlGn',
    labels={'Yield': 'kg per hectare'},
    title=f'Cereal Yield by Country ({selected_year})'
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    paper_bgcolor='#f9f9f9',
    geo=dict(showframe=False, showcoastlines=True),
    title_font=dict(color='#333333', size=15),
    coloraxis_colorbar=dict(
        tickfont=dict(color='#333333'),
        titlefont=dict(color='#333333')
    )
)
st.plotly_chart(fig_map, use_container_width=True)


# ── Visualisation 2 — Line Chart ─────────────────────────────
st.markdown("---")
st.markdown('<p class="section-label">Visualisation 2 — Line Chart</p>', unsafe_allow_html=True)
st.header("Yield Trend Over Time")
st.markdown("Compare how cereal yield has changed over the years for selected countries.")

if len(selected_countries) == 0:
    st.warning("Please select at least one country from the sidebar to see the trend.")
else:
    df_line = df[df['Country Name'].isin(selected_countries)]
    fig_line = px.line(
        df_line,
        x='Year',
        y='Yield',
        color='Country Name',
        markers=True,
        labels={'Yield': 'kg per hectare', 'Country Name': 'Country'},
        title='Cereal Yield Trend by Selected Countries'
    )
    fig_line.update_layout(
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#ffffff',
        hovermode='x unified',
        title_font=dict(color='#333333', size=15),
        xaxis=axis_style,
        yaxis=axis_style,
        legend=dict(font=dict(color='#333333'), bgcolor='#f9f9f9')
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ── Visualisation 3 — Bar Charts ─────────────────────────────
st.markdown("---")
st.markdown('<p class="section-label">Visualisation 3 — Bar Charts</p>', unsafe_allow_html=True)
st.header(f"Top and Bottom {top_n} Countries in {selected_year}")
st.markdown(f"Countries with the highest and lowest cereal yield in **{selected_year}**.")

df_sorted = df_year.sort_values('Yield', ascending=False).dropna(subset=['Yield'])
col_left, col_right = st.columns(2)

with col_left:
    top_df = df_sorted.head(top_n)
    fig_top = px.bar(
        top_df,
        x='Yield',
        y='Country Name',
        orientation='h',
        color='Yield',
        color_continuous_scale='Greens',
        labels={'Yield': 'kg per hectare'},
        title=f'Top {top_n} Countries'
    )
    fig_top.update_layout(
        yaxis=dict(autorange='reversed', **axis_style),
        xaxis=axis_style,
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#ffffff',
        showlegend=False,
        title_font=dict(color='#333333', size=15),
        coloraxis_colorbar=dict(tickfont=dict(color='#333333'), titlefont=dict(color='#333333'))
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col_right:
    bot_df = df_sorted.tail(top_n).sort_values('Yield')
    fig_bot = px.bar(
        bot_df,
        x='Yield',
        y='Country Name',
        orientation='h',
        color='Yield',
        color_continuous_scale='Reds',
        labels={'Yield': 'kg per hectare'},
        title=f'Bottom {top_n} Countries'
    )
    fig_bot.update_layout(
        yaxis=axis_style,
        xaxis=axis_style,
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#ffffff',
        showlegend=False,
        title_font=dict(color='#333333', size=15),
        coloraxis_colorbar=dict(tickfont=dict(color='#333333'), titlefont=dict(color='#333333'))
    )
    st.plotly_chart(fig_bot, use_container_width=True)


# ── Key Insights ─────────────────────────────────────────────
st.markdown("---")
st.header("Key Insights")
st.markdown(f"Summary of findings for **{selected_year}**")

top_country = df_sorted.iloc[0]
bot_country = df_sorted.iloc[-1]
avg_yield = df_year['Yield'].mean()

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(f"""
    <div style="background-color:#d4edda; padding:15px; border-radius:8px; border:1px solid #c3e6cb;">
        <p style="color:#155724; font-size:14px; margin:0;"><strong>Highest Yield</strong></p>
        <p style="color:#155724; font-size:16px; margin:5px 0 0 0;">{top_country['Country Name']}<br>{top_country['Yield']:,.0f} kg/ha</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div style="background-color:#f8d7da; padding:15px; border-radius:8px; border:1px solid #f5c6cb;">
        <p style="color:#721c24; font-size:14px; margin:0;"><strong>Lowest Yield</strong></p>
        <p style="color:#721c24; font-size:16px; margin:5px 0 0 0;">{bot_country['Country Name']}<br>{bot_country['Yield']:,.0f} kg/ha</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown(f"""
    <div style="background-color:#d1ecf1; padding:15px; border-radius:8px; border:1px solid #bee5eb;">
        <p style="color:#0c5460; font-size:14px; margin:0;"><strong>Global Average</strong></p>
        <p style="color:#0c5460; font-size:16px; margin:5px 0 0 0;">{avg_yield:,.0f} kg/ha</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Data Source: World Bank — Cereal Yield (kg per hectare) | Dashboard created for 5DATA004C Coursework")
