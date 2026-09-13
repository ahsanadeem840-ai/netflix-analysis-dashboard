"""
Netflix Content Analysis Dashboard
Bana raha hai: [Aapka Naam]
Tools: Streamlit, Pandas, NumPy, Matplotlib, Seaborn
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# PAGE CONFIG (yeh sabse pehle likhna hota hai)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Netflix Analysis Dashboard",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------------------------------------
# DATA LOAD KARNA (function bana rahe hain taake baar baar
# load na ho, cache ho jaye -> app fast chalay)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")

    # ---- DATA CLEANING ----
    # Missing values ko "Unknown" se fill karo (columns jo text hain)
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')

    # date_added ko proper date format mein convert karo
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month_name()

    # duration ko number mein convert karo (e.g. "90 min" -> 90)
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)

    # Multiple countries wale rows mein sirf pehla country lo (simplicity ke liye)
    df['main_country'] = df['country'].apply(lambda x: x.split(',')[0].strip())

    return df

df = load_data()

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("🎬 Netflix Content Analysis Dashboard")
st.write("Yeh dashboard Netflix ke dataset ka interactive analysis dikhata hai.")

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Filters")

# Filter 1: Type (Movie / TV Show)
type_options = ["All"] + sorted(df['type'].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Content Type Chunein", type_options)

# Filter 2: Release Year Range
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
selected_year_range = st.sidebar.slider(
    "Release Year Range",
    min_year, max_year, (2010, max_year)
)

# Filter 3: Top N Countries (kitne countries ka data dekhna hai charts mein)
top_n = st.sidebar.slider("Top N Countries/Genres Dikhayein", 5, 20, 10)

# ---------------------------------------------------------
# FILTERS APPLY KARNA
# ---------------------------------------------------------
filtered_df = df.copy()

if selected_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == selected_type]

filtered_df = filtered_df[
    (filtered_df['release_year'] >= selected_year_range[0]) &
    (filtered_df['release_year'] <= selected_year_range[1])
]

# ---------------------------------------------------------
# KEY METRICS (top pe numbers)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
col3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
col4.metric("Countries", filtered_df['main_country'].nunique())

st.markdown("---")

# ---------------------------------------------------------
# CHART 1: Movies vs TV Shows (Pie Chart)
# ---------------------------------------------------------
st.subheader("1. Movies vs TV Shows Ka Ratio")
col1, col2 = st.columns([1, 2])

with col1:
    fig1, ax1 = plt.subplots(figsize=(4, 4))
    type_counts = filtered_df['type'].value_counts()
    ax1.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%',
            colors=['#E50914', '#221f1f'], startangle=90)
    ax1.set_title("Content Type Distribution")
    st.pyplot(fig1)

with col2:
    st.write("**Insight:** Yahan aap dekh sakte hain ke total content mein Movies "
             "aur TV Shows ka kitna percentage hai. Netflix agar zyada TV Shows "
             "add kar raha hai, to iska matlab hai wo binge-watching strategy "
             "par focus kar raha hai.")

st.markdown("---")

# ---------------------------------------------------------
# CHART 2: Year-wise Content Growth (Line Chart)
# ---------------------------------------------------------
st.subheader("2. Saal Ke Hisaab Se Content Growth")

yearly_content = filtered_df.groupby('year_added').size()

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(yearly_content.index, yearly_content.values, marker='o', color='#E50914')
ax2.set_xlabel("Year")
ax2.set_ylabel("Number of Titles Added")
ax2.set_title("Netflix Par Har Saal Kitna Content Add Hua")
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)

st.write("**Insight:** Yeh chart batata hai ke kis saal Netflix ne sabse zyada "
         "content add kiya. Aam tor par 2018-2020 mein growth sabse tez dikhti hai.")

st.markdown("---")

# ---------------------------------------------------------
# CHART 3: Top Countries (Bar Chart)
# ---------------------------------------------------------
st.subheader(f"3. Top {top_n} Content-Producing Countries")

top_countries = filtered_df[filtered_df['main_country'] != 'Unknown']['main_country'] \
    .value_counts().head(top_n)

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_countries.values, y=top_countries.index, ax=ax3, palette='Reds_r')
ax3.set_xlabel("Number of Titles")
ax3.set_ylabel("Country")
st.pyplot(fig3)

st.write("**Insight:** Yeh dikhata hai ke Netflix ka zyada tar content kis "
         "country se banaya/liya gaya hai — aam tor par USA aur India top mein hote hain.")

st.markdown("---")

# ---------------------------------------------------------
# CHART 4: Top Genres (Horizontal Bar)
# ---------------------------------------------------------
st.subheader(f"4. Top {top_n} Genres")

# genre column mein multiple genres comma se separated hain, isliye split kar rahe hain
all_genres = filtered_df['listed_in'].str.split(', ').explode()
top_genres = all_genres.value_counts().head(top_n)

fig4, ax4 = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_genres.values, y=top_genres.index, ax=ax4, palette='mako')
ax4.set_xlabel("Number of Titles")
ax4.set_ylabel("Genre")
st.pyplot(fig4)

st.write("**Insight:** Sabse popular genres kaunse hain yeh yahan se pata chalta "
         "hai — Netflix content strategy samajhne mein madad milti hai.")

st.markdown("---")

# ---------------------------------------------------------
# CHART 5: Rating Distribution (Count Plot)
# ---------------------------------------------------------
st.subheader("5. Content Rating Distribution")

fig5, ax5 = plt.subplots(figsize=(10, 4))
sns.countplot(data=filtered_df, x='rating',
              order=filtered_df['rating'].value_counts().index,
              ax=ax5, palette='rocket')
plt.xticks(rotation=45)
ax5.set_xlabel("Rating")
ax5.set_ylabel("Count")
st.pyplot(fig5)

st.write("**Insight:** Yeh batata hai ke kitna content kis age-group ke liye "
         "bana hai (TV-MA = adults, TV-Y = bachon ke liye, waghera).")

st.markdown("---")

# ---------------------------------------------------------
# CHART 6: Month-wise Heatmap (Seasonal Pattern) - Bonus/Advanced
# ---------------------------------------------------------
st.subheader("6. Month vs Year Heatmap (Kab Zyada Content Add Hota Hai)")

heatmap_data = filtered_df.groupby(['year_added', 'month_added']).size().unstack(fill_value=0)

# months ko sahi order mein rakho
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']
heatmap_data = heatmap_data.reindex(columns=month_order, fill_value=0)

fig6, ax6 = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap='Reds', ax=ax6, linewidths=0.5)
ax6.set_xlabel("Month")
ax6.set_ylabel("Year")
st.pyplot(fig6)

st.write("**Insight:** Yeh heatmap dikhata hai ke Netflix kis mahine mein "
         "zyada content release/add karta hai — koi seasonal pattern hai ya nahi.")

st.markdown("---")

# ---------------------------------------------------------
# RAW DATA TABLE (optional - end mein)
# ---------------------------------------------------------
st.subheader("📋 Filtered Data (Raw)")
show_data = st.checkbox("Data Table Dikhayein")
if show_data:
    st.dataframe(filtered_df[['title', 'type', 'release_year', 'main_country',
                                'rating', 'listed_in', 'duration']])

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("Dashboard bani hai Streamlit, Pandas, NumPy, Matplotlib aur Seaborn se.")
