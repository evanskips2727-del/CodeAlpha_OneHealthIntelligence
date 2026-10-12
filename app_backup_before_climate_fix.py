import os
import re
import pandas as pd
import streamlit as st
import plotly.express as px

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

st.set_page_config(
    page_title="One Health Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

who = load_csv("who_don_processed.csv")
climate = load_csv("nairobi_climate_processed.csv")
climate_flags = load_csv("climate_2025_anomaly_screen.csv")
articles = load_csv("who_html_article_samples.csv")

# Standardize dates.
if not who.empty and "publication_date" in who.columns:
    who["publication_date"] = pd.to_datetime(
        who["publication_date"], errors="coerce"
    )

if not climate.empty and "date" in climate.columns:
    climate["date"] = pd.to_datetime(climate["date"], errors="coerce")

if not climate_flags.empty:
    for col in ["date", "evaluation_date"]:
        if col in climate_flags.columns:
            climate_flags[col] = pd.to_datetime(
                climate_flags[col], errors="coerce"
            )

if not articles.empty and "scraped_publication_date" in articles.columns:
    articles["scraped_publication_date"] = pd.to_datetime(
        articles["scraped_publication_date"], errors="coerce"
    )

st.title("🌍 One Health Intelligence Platform")
st.caption(
    "Multisource disease surveillance, climate exploration, "
    "and evidence-informed public-health intelligence"
)

st.markdown("""
This portfolio dashboard brings together WHO Disease Outbreak News
announcements, daily Nairobi climate observations, exploratory climate
anomaly flags, and a sample of scraped WHO article text.

**Scope:** These datasets support exploratory monitoring. WHO announcements
are not a complete disease-case surveillance series, and the Nairobi climate
data do not establish a causal relationship with any outbreak.
""")

# Sidebar navigation and filters.
st.sidebar.title("Dashboard Controls")
page = st.sidebar.radio(
    "Select a view",
    [
        "Executive Overview",
        "Disease Surveillance",
        "Climate Explorer",
        "Climate Anomaly Screen",
        "WHO Article Explorer",
        "Data Quality & Limitations"
    ]
)

# Optional date filter for WHO announcements.
who_filtered = who.copy()

if not who.empty and "publication_date" in who.columns:
    valid_dates = who["publication_date"].dropna()

    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        selected_dates = st.sidebar.date_input(
            "WHO publication date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            who_filtered = who[
                who["publication_date"].dt.date.between(
                    start_date, end_date
                )
            ]

# Overview
if page == "Executive Overview":
    st.header("Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("WHO announcements", f"{len(who_filtered):,}")
    c2.metric("Scraped article pages", f"{len(articles):,}")
    c3.metric("Climate observations", f"{len(climate):,}")

    flagged_days = 0
    if not climate_flags.empty:
        flag_col = next(
            (
                col for col in [
                    "any_anomaly",
                    "either_flag",
                    "anomaly_flag",
                    "is_anomaly"
                ]
                if col in climate_flags.columns
            ),
            None
        )

        if flag_col:
            flagged_days = int(
                climate_flags[flag_col].fillna(False).astype(bool).sum()
            )
        else:
            flagged_days = len(climate_flags)

    c4.metric("Climate-screen records", f"{len(climate_flags):,}")

    st.subheader("WHO Announcements Over Time")

    if not who_filtered.empty:
        annual = (
            who_filtered.dropna(subset=["publication_date"])
            .assign(
                year=lambda d: d["publication_date"].dt.year
            )
            .groupby("year")
            .size()
            .reset_index(name="announcement_count")
        )

        fig = px.line(
            annual,
            x="year",
            y="announcement_count",
            markers=True,
            title="Annual WHO Disease Outbreak News announcements",
            labels={
                "year": "Publication year",
                "announcement_count": "Number of announcements"
            }
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Most Mentioned Disease Terms")
        if not who_filtered.empty:
            titles = who_filtered["title"].fillna("").astype(str)

            disease_terms = [
                "influenza", "avian influenza", "ebola", "cholera",
                "polio", "yellow fever", "marburg", "meningitis",
                "measles", "plague", "dengue", "monkeypox", "mpox",
                "hepatitis", "anthrax", "malaria", "covid-19"
            ]

            counts = []
            for term in disease_terms:
                count = int(
                    titles.str.contains(re.escape(term), case=False).sum()
                )
                if count:
                    counts.append({
                        "disease_term": term.title(),
                        "announcement_mentions": count
                    })

            disease_df = pd.DataFrame(counts)
            if not disease_df.empty:
                disease_df = disease_df.sort_values(
                    "announcement_mentions", ascending=False
                ).head(10)

                fig = px.bar(
                    disease_df.sort_values("announcement_mentions"),
                    x="announcement_mentions",
                    y="disease_term",
                    orientation="h",
                    title="Disease terms appearing in announcement titles",
                    labels={
                        "announcement_mentions": "Title mentions",
                        "disease_term": "Disease term"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    "Terms can overlap. Monkeypox and mpox are alternative "
                    "names; counts are title mentions, not unique outbreaks."
                )

    with right:
        st.subheader("Nairobi Climate Snapshot")
        if not climate.empty:
            climate_plot = climate.copy()

            fig = px.line(
                climate_plot,
                x="date",
                y="temperature_2m_c",
                title="Daily temperature in Nairobi",
                labels={
                    "date": "Date",
                    "temperature_2m_c": "Temperature (°C)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            st.metric(
                "Mean recorded temperature",
                f"{climate['temperature_2m_c'].mean():.2f} °C"
            )

    st.info(
        "Interpretation: announcement volume reflects published WHO "
        "communications and reporting practices, not the total incidence "
        "of disease."
    )

# Disease Surveillance
elif page == "Disease Surveillance":
    st.header("Disease Surveillance Explorer")

    if who_filtered.empty:
        st.warning("No WHO announcements match the selected date range.")
    else:
        search_term = st.text_input(
            "Search announcement titles and summaries",
            placeholder="e.g. cholera, Ebola, influenza"
        )

        disease_df = who_filtered.copy()

        if search_term.strip():
            search_cols = [
                c for c in ["title", "overview", "summary", "epidemiology"]
                if c in disease_df.columns
            ]

            mask = pd.Series(False, index=disease_df.index)
            for col in search_cols:
                mask |= disease_df[col].fillna("").astype(str).str.contains(
                    search_term, case=False, regex=False
                )
            disease_df = disease_df[mask]

        st.metric("Matching announcements", f"{len(disease_df):,}")

        if not disease_df.empty:
            annual = (
                disease_df.dropna(subset=["publication_date"])
                .assign(year=lambda d: d["publication_date"].dt.year)
                .groupby("year")
                .size()
                .reset_index(name="announcements")
            )

            fig = px.bar(
                annual,
                x="year",
                y="announcements",
                title="Matching announcements by publication year",
                labels={
                    "year": "Publication year",
                    "announcements": "Announcements"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            display_cols = [
                c for c in [
                    "publication_date", "title", "overview",
                    "source_url"
                ]
                if c in disease_df.columns
            ]

            st.dataframe(
                disease_df[display_cols].sort_values(
                    "publication_date", ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

# Climate Explorer
elif page == "Climate Explorer":
    st.header("Nairobi Climate Explorer")

    if climate.empty:
        st.warning("Climate dataset is unavailable.")
    else:
        min_climate_date = climate["date"].min().date()
        max_climate_date = climate["date"].max().date()

        climate_dates = st.date_input(
            "Climate date range",
            value=(min_climate_date, max_climate_date),
            min_value=min_climate_date,
            max_value=max_climate_date,
            key="climate_date_range"
        )

        climate_view = climate.copy()

        if isinstance(climate_dates, (tuple, list)) and len(climate_dates) == 2:
            climate_view = climate_view[
                climate_view["date"].dt.date.between(
                    climate_dates[0], climate_dates[1]
                )
            ]

        if climate_view.empty:
            st.warning("No observations fall within this date range.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Mean temperature",
                f"{climate_view['temperature_2m_c'].mean():.2f} °C"
            )
            c2.metric(
                "Mean daily precipitation",
                f"{climate_view['precipitation_corrected_mm'].mean():.2f} mm"
            )
            c3.metric("Days observed", f"{len(climate_view):,}")

            variable = st.selectbox(
                "Select climate variable",
                {
                    "Temperature (°C)": "temperature_2m_c",
                    "Daily precipitation (mm)": "precipitation_corrected_mm"
                }
            )

            fig = px.line(
                climate_view,
                x="date",
                y=variable,
                title=f"{variable.replace('_', ' ').title()} over time",
                labels={"date": "Date", variable: variable.replace("_", " ").title()}
            )
            st.plotly_chart(fig, use_container_width=True)

            monthly = (
                climate_view.assign(
                    month=climate_view["date"].dt.to_period("M").dt.to_timestamp()
                )
                .groupby("month")
                .agg(
                    mean_temperature=("temperature_2m_c", "mean"),
                    total_precipitation=("precipitation_corrected_mm", "sum")
                )
                .reset_index()
            )

            fig = px.bar(
                monthly,
                x="month",
                y="total_precipitation",
                title="Monthly accumulated precipitation",
                labels={
                    "month": "Month",
                    "total_precipitation": "Total precipitation (mm)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "Climate observations represent the specified Nairobi "
                "coordinate, not all of Kenya."
            )

# Climate anomaly screen
elif page == "Climate Anomaly Screen":
    st.header("Exploratory Climate Anomaly Screen")

    if climate_flags.empty:
        st.warning("Climate anomaly dataset is unavailable.")
    else:
        st.markdown(
            "The anomaly screen compares 2025 observations with a "
            "2020–2024 baseline using the project's monthly-baseline/IQR "
            "rule. A flagged value is a statistical outlier candidate, "
            "not evidence of an outbreak or climate-change attribution."
        )

        st.metric("Records in anomaly-screen file", f"{len(climate_flags):,}")

        st.write("Available fields:", ", ".join(climate_flags.columns))

        numeric_cols = climate_flags.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:
            variable = st.selectbox(
                "Choose a numeric field",
                numeric_cols
            )

            date_col = next(
                (
                    col for col in ["date", "evaluation_date"]
                    if col in climate_flags.columns
                ),
                None
            )

            if date_col:
                fig = px.scatter(
                    climate_flags,
                    x=date_col,
                    y=variable,
                    title=f"Climate anomaly-screen field: {variable}",
                    labels={date_col: "Date", variable: variable}
                )
                st.plotly_chart(fig, use_container_width=True)

        st.dataframe(climate_flags, use_container_width=True, hide_index=True)

        csv_bytes = climate_flags.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download climate anomaly data",
            data=csv_bytes,
            file_name="climate_2025_anomaly_screen.csv",
            mime="text/csv"
        )

# WHO article explorer
elif page == "WHO Article Explorer":
    st.header("WHO Article Explorer")

    if articles.empty:
        st.warning("Scraped article dataset is unavailable.")
    else:
        query = st.text_input(
            "Search scraped titles and article text",
            placeholder="Search disease, country, or phrase"
        )

        article_view = articles.copy()

        if query.strip():
            mask = (
                article_view["scraped_title"].fillna("").astype(str)
                .str.contains(query, case=False, regex=False)
            )

            if "paragraph_text" in article_view.columns:
                mask |= (
                    article_view["paragraph_text"].fillna("").astype(str)
                    .str.contains(query, case=False, regex=False)
                )

            article_view = article_view[mask]

        st.metric("Matching scraped pages", f"{len(article_view):,}")

        for _, row in article_view.iterrows():
            title = str(row.get("scraped_title") or "Untitled WHO article")
            date = row.get("scraped_publication_date")
            url = row.get("source_url", "")

            with st.expander(f"{title} — {date if pd.notna(date) else 'Date unavailable'}"):
                st.write(f"Source: {url}")
                st.write(
                    str(row.get("paragraph_text", ""))[:12000]
                    or "No paragraph text was extracted."
                )

# Data quality and limitations
elif page == "Data Quality & Limitations":
    st.header("Data Quality, Provenance & Limitations")

    quality_rows = [
        {
            "Dataset": "WHO Disease Outbreak News",
            "Records": len(who),
            "Scope": "Published outbreak announcements",
            "Key limitation": "Not a complete case-count surveillance dataset"
        },
        {
            "Dataset": "Nairobi climate",
            "Records": len(climate),
            "Scope": "Daily observations, 2020–2025",
            "Key limitation": "One geographic coordinate; no causal inference"
        },
        {
            "Dataset": "WHO HTML articles",
            "Records": len(articles),
            "Scope": "Scraped article sample",
            "Key limitation": "Sample of pages, not the entire WHO archive"
        },
        {
            "Dataset": "Climate anomaly screen",
            "Records": len(climate_flags),
            "Scope": "Exploratory 2025 statistical screening",
            "Key limitation": "Flags do not establish disease risk or causality"
        }
    ]

    st.dataframe(
        pd.DataFrame(quality_rows),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Interpretation safeguards")
    st.markdown("""
    - WHO announcement counts represent published communications, not disease incidence.
    - Article title keyword counts can overlap and are not unique outbreak counts.
    - Missing text fields mean information was not populated in the dataset; they do not mean zero events.
    - Climate anomaly flags are exploratory statistical indicators.
    - This dashboard does not issue outbreak alerts or clinical advice.
    - The project is independent and is not affiliated with or endorsed by WHO.
    """)

    st.subheader("Sources")
    st.markdown("""
    - WHO Disease Outbreak News: https://www.who.int/emergencies/disease-outbreak-news
    - NASA POWER: https://power.larc.nasa.gov/
    """)

st.divider()
st.caption(
    "CodeAlpha One Health Intelligence Platform | "
    "Exploratory portfolio project | Interpret results in context."
)
