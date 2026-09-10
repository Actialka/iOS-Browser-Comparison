import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Page setup
st.set_page_config(
    page_title="iOS Browser Performance Benchmark",
    page_icon="⚡",
    layout="wide"
)

st.markdown(
    """
    <style>
        /* 1. Float the collapse button to the top-right corner */
        [data-testid="stSidebarHeader"] {
            position: absolute !important;
            top: 0.5rem !important;
            right: 0.5rem !important;
            z-index: 999999 !important;
            background: transparent !important;
            padding: 0 !important;
            height: auto !important;
            min-height: auto !important;
        }

        /* 2. Start the sidebar content near the top with room on the right */
        [data-testid="stSidebarContent"] {
            padding-top: 1rem !important;
        }

        [data-testid="stSidebarUserContent"] {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }

        /* 3. Ensure heading does not collide with the floating button */
        [data-testid="stSidebarUserContent"] h1:first-child,
        [data-testid="stSidebarUserContent"] h2:first-child,
        [data-testid="stSidebarUserContent"] h3:first-child {
            margin-top: 0.25rem !important;
            padding-right: 2.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function to run SQL queries against SQLite
def run_query(query: str) -> pd.DataFrame:
    conn = sqlite3.connect("browser_benchmarks.db")
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

# Header & Overview
st.header("⚡ iOS Browser Performance Benchmark")
st.markdown("""
A benchmarking study comparing Nadir, a minimalist iOS web browser
against **Apple Safari** and **Brave**. All tests were conducted under identical
hardware and network conditions on iOS with ad-blocking disabled across all runs.
""")

with st.expander("📱 Watch Nadir in Action (Screen Recording)"):
    st.video("nadir_demo.mp4")
    st.caption("Native iOS client executing baseline tests under iOS 26.4.2.")

with st.sidebar:
    st.title("Navigation")
    st.markdown("""
    * [1. Overall Summary](#summary)
    * [2. Safari Baseline Delta](#delta)
    * [3. Category Breakdown](#categories)
    * [4. Methodology & Glossary](#methodology)
    """)
    st.divider()



# Optional context or links
    st.markdown("### Links")
    st.markdown("""
    * [GitHub Repository](https://github.com/Actialka/iOS-Browser-Comparison)
    * [LinkedIn Profile](http://linkedin.com/in/sophiafanpsu/)
    """)

st.divider()

# -------------------------------------------------------------
# Section 1: Executive Overview
# -------------------------------------------------------------
st.header("1. Overall Benchmark Summary", anchor="summary")
st.caption("Aggregated mean performance metrics across all benchmarked domains.")

summary_query = """
SELECT
    b.browser_name,
    COUNT(m.site_id) AS total_runs,
    ROUND(AVG(m.load_time_ms), 1) AS avg_load_time_ms,
    ROUND(AVG(m.fcp_ms), 1) AS avg_fcp_ms,
    ROUND(AVG(m.memory_mb), 1) AS avg_memory_mb,
    ROUND(AVG(m.request_count), 0) AS avg_requests,
    ROUND(AVG(m.transfer_size_kb), 1) AS avg_transfer_kb
FROM performance_metrics m
JOIN browsers b ON m.browser_id = b.browser_id
GROUP BY b.browser_name
ORDER BY avg_load_time_ms ASC;
"""
df_summary = run_query(summary_query)

# Display Key Performance Indicators (KPIs)
cols = st.columns(len(df_summary))
for idx, row in df_summary.iterrows():
    with cols[idx]:
        st.metric(
            label=f"{row['browser_name']} (Avg Load)",
            value=f"{row['avg_load_time_ms']} ms",
            delta=f"{row['avg_memory_mb']} MB RAM",
            delta_color="off"
        )

st.dataframe(df_summary, use_container_width=True, hide_index=True)

with st.expander("View SQL Query for Summary Table"):
    st.code(summary_query, language="sql")

st.markdown("""
### Key Takeaways: Baseline comparison
**Key Findings:**
* **Nadir led the benchmark** with an average load time of **1,800 ms (1.80 s)**, outperforming Safari's **1,960 ms (1.96 s)** by approximately **8%**.
* **Brave exhibited the highest latency**, averaging **3,300 ms (3.30 s)**, representing an **59% increase** in total page completion time compared to Nadir.

**Analytical Takeaway**

Because ad-blocking was disabled across all three environments, this delta highlights the impact of browser architecture and background processes on page load time. Nadir has no other background processes, and background telemetry is negligible. Safari had a similar lean setup as there were no extensions installed, but there still could have been telemetry collected by Apple. Brave’s background features (such as the crypto wallet, built-in AI, and browser-level telemetry)
all could delay load times even when they're disabled.

While sub-2-second loads provide a responsive experience, crossing the 3-second threshold in Brave represents a measurable difference that directly affects user experience.
""")

st.markdown("""
    ### Supporting Diagnostic Metrics
**Key Findings:**
   * **Initial Display Speed (FCP):** Nadir showed the first visible parts of a page fastest **(611.2 ms)**, while Brave took the longest **(992.2 ms)**, a **47.5%** difference. This closely matches our overall load time findings, confirming that Nadir gets content in front of users quicker from start to finish.

   * **Memory Footprint (RAM):** Nadir maintained lower memory usage across tests. While Safari and Brave run extra services like reading list sync, partner services, and heavy user-interface layers, Nadir keeps system resources dedicated strictly to rendering websites.

   * **The Data Transfer Anomaly:** Nadir downloaded significantly more data per page **(5,467 KB)** compared to Safari **(1,907 KB)** and Brave **(1,822 KB).

**Analytical Takeaway**

Commercial browsers like Safari and Brave store large libraries, common fonts, and website files long-term across the entire phone. Because Nadir doesn't have built-in shared caching, it had to download more assets from scratch rather than pulling them from storage.

""")

st.divider()

# -------------------------------------------------------------
# Section 2: Relative Performance vs. Safari Baseline (CTE)
# -------------------------------------------------------------
st.header("2. Performance Delta vs. Safari Baseline", anchor="delta")
st.caption("""Common Table Expression (CTE) calculating percentage difference relative to Safari.

Tip: press the autoscale button in the graphs for the best view. Hover over the bars to get exact numbers.""")

delta_query = """
WITH browser_summary AS (
    SELECT
        b.browser_name,
        AVG(m.load_time_ms) AS avg_load,
        AVG(m.memory_mb) AS avg_ram
    FROM performance_metrics m
    JOIN browsers b ON m.browser_id = b.browser_id
    GROUP BY b.browser_name
),
safari_baseline AS (
    SELECT avg_load, avg_ram
    FROM browser_summary
    WHERE browser_name = 'Safari'
)
SELECT
    bs.browser_name,
    ROUND(bs.avg_load, 1) AS avg_load_ms,
    ROUND(((bs.avg_load - sb.avg_load) / sb.avg_load) * 100.0, 2) AS load_pct_vs_safari,
    ROUND(bs.avg_ram, 1) AS avg_ram_mb,
    ROUND(((bs.avg_ram - sb.avg_ram) / sb.avg_ram) * 100.0, 2) AS ram_pct_vs_safari
FROM browser_summary bs
CROSS JOIN safari_baseline sb;
"""
df_delta = run_query(delta_query)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_load = px.bar(
        df_delta,
        x="browser_name",
        y="load_pct_vs_safari",
        title="Load Time Delta vs Safari (%)",
        labels={"load_pct_vs_safari": "% Difference", "browser_name": "Browser"},
        color="browser_name"
    )
    st.plotly_chart(fig_load, use_container_width=True)

with col_chart2:
    fig_ram = px.bar(
        df_delta,
        x="browser_name",
        y="ram_pct_vs_safari",
        title="Memory Footprint Delta vs Safari (%)",
        labels={"ram_pct_vs_safari": "% Difference", "browser_name": "Browser"},
        color="browser_name"
    )
    st.plotly_chart(fig_ram, use_container_width=True)

with st.expander("View SQL Query for Baseline Delta"):
    st.code(delta_query, language="sql")

st.markdown("""
    ### Key Insights: Relative Efficiency & Architectural Trade-Offs

    * **Nadir’s Resource Advantage:** Nadir operated at **57.77% lower memory consumption** than Safari while simultaneously reducing total page load time by **7.77%**. On constrained mobile hardware, cutting physical memory usage by more than half without degrading render speed demonstrates the efficiency gains of running a stripped-down web view without native browser shell overhead.
    * **The Brave Latency Penalty:** While Brave reduced memory overhead by **22.96%** compared to Safari, it incurred a severe **68.45% latency penalty** in total load time. With ad-blocking disabled across all runs, this indicates that Brave’s background processes throttle network and script execution.
    * **Safari’s System-Level Memory Footprint:** Safari functioned as the performance control group at 0%. It was significantly faster than Brave, but carrying a heavy memory baseline. This reflects the background footprint of native iOS integration that third-party browsers can bypass.
""")

st.divider()

# -------------------------------------------------------------
# Section 3: Category Breakdown & Window Functions
# -------------------------------------------------------------
st.header("3. Category Breakdown & Efficiency Ranking", anchor="categories")
st.caption("Content-type segmentation using SQL Window Functions.")

# Fetch unique categories dynamically from the database
categories_df = run_query("SELECT DISTINCT category FROM websites ORDER BY category;")
category_options = ["All Categories"] + categories_df["category"].tolist()

# Place the filter selector directly above the table
selected_cat = st.pills(
    "Filter by Category:",
    options=category_options,
    default="All Categories"
)

# Apply filter condition to your SQL query
filter_clause = ""
if selected_cat != "All Categories":
    filter_clause = f"WHERE w.category = '{selected_cat}'"

rank_query = f"""
WITH category_metrics AS (
    SELECT
        w.category,
        b.browser_name,
        ROUND(AVG(m.load_time_ms), 1) AS avg_load_ms,
        ROUND(AVG(m.memory_mb), 1) AS avg_memory_mb
    FROM performance_metrics m
    JOIN browsers b ON m.browser_id = b.browser_id
    JOIN websites w ON m.site_id = w.site_id
    {filter_clause}
    GROUP BY w.category, b.browser_name
)
SELECT
    category,
    browser_name,
    avg_load_ms,
    RANK() OVER (PARTITION BY category ORDER BY avg_load_ms ASC) AS speed_rank,
    avg_memory_mb,
    RANK() OVER (PARTITION BY category ORDER BY avg_memory_mb ASC) AS memory_rank
FROM category_metrics
ORDER BY category, speed_rank;
"""

df_rank = run_query(rank_query)
st.dataframe(df_rank, use_container_width=True, hide_index=True)

with st.expander("View SQL Query with Window Functions"):
    st.code(rank_query, language="sql")

st.markdown("""
    ### Key Takeaways by Website Type

    * **Consistent Memory Winner:** Nadir used the least memory across all 5 categories, hovering around 100–145 MB. Safari consistently used more than double that amount (235–276 MB), showing the memory cost of Apple's background features.
    * **The News Site Gap:** News websites had the biggest performance split. Nadir finished loading in about 3 seconds, Safari in 3.5 seconds, while Brave took nearly 6.7 seconds. When sites are packed with tracking scripts and unblocked ads, Brave struggles significantly to finish loading.
    * **Fast on Shopping and Text Sites:** Nadir was the fastest browser on E-Commerce and Reference pages, loading both types of sites in under a second while using half the memory of the competition.
    * **Safari and Brave Win on Social Media:** On interactive social platforms, Brave and Safari were roughly 200 ms faster than Nadir. Full-featured commercial browsers are better optimized for heavy interactive feeds, though they still consume far more memory to achieve that small speed edge.
""")

st.divider()
st.header("4. Methodology & Metric Definitions", anchor="methodology")
with st.expander("🛠️ Methodology & Testing Setup"):
    st.markdown("""
    * **Hardware:** iPhone 13 Pro running iOS 26.4.2.
    * **Network:** Stable high-speed residential Wi-Fi under identical, unmetered network conditions.
    * **Ad-Blocking:** Explicitly disabled across all three browsers to ensure a similar baselines.
    * **Data Collection:** Automated through Safari Web Inspector and Xcode Instruments over USB, measuring multiple runs per site to calculate stable averages.
    """)

with st.expander("📖 Metric Definitions"):
    st.markdown("""
    * **Load Time:** How long you wait before the entire webpage is completely finished loading.
    * **First Contentful Paint (FCP):** The moment content first appears on screen.
    * **Time to First Byte (TTFB):** Initial server response delay.
    * **Memory Use (RAM):** Working memory consumed by the browser while viewing the page.
    * **Network Requests:** Total individual files requested from the server.
    * **Data Transferred:** Total compressed size of downloaded files (mobile data use).
    """)
