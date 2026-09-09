SELECT
    b.browser_name,
    COUNT(m.site_id) AS total_sites,
    ROUND(AVG(m.load_time_ms), 1) AS avg_load_ms,
    ROUND(AVG(m.fcp_ms), 1) AS avg_fcp_ms,
    ROUND(AVG(m.memory_mb), 1) AS avg_memory_mb,
    ROUND(AVG(m.transfer_size_kb), 1) AS avg_transfer_kb
FROM performance_metrics m
JOIN browsers b ON m.browser_id = b.browser_id
GROUP BY b.browser_name
ORDER BY avg_load_ms ASC;

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
    ROUND(((bs.avg_load - sb.avg_load) / sb.avg_load) * 100.0, 2) AS load_time_pct_vs_safari,
    ROUND(bs.avg_ram, 1) AS avg_ram_mb,
    ROUND(((bs.avg_ram - sb.avg_ram) / sb.avg_ram) * 100.0, 2) AS ram_pct_vs_safari
FROM browser_summary bs
CROSS JOIN safari_baseline sb;

WITH category_metrics AS (
    SELECT
        w.category,
        b.browser_name,
        ROUND(AVG(m.load_time_ms), 1) AS avg_load_ms,
        ROUND(AVG(m.memory_mb), 1) AS avg_memory_mb
    FROM performance_metrics m
    JOIN browsers b ON m.browser_id = b.browser_id
    JOIN websites w ON m.site_id = w.site_id
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

SELECT
    b.browser_name,
    ROUND(AVG(m.request_count), 0) AS avg_requests,
    ROUND(AVG(m.transfer_size_kb), 1) AS avg_transfer_kb,
    ROUND(AVG(m.transfer_size_kb) / NULLIF(AVG(m.request_count), 0), 2) AS kb_per_request,
    ROUND(
        100.0 * SUM(CASE WHEN m.transfer_size_kb > 2048 THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS pct_runs_over_2mb
FROM performance_metrics m
JOIN browsers b ON m.browser_id = b.browser_id
GROUP BY b.browser_name;
