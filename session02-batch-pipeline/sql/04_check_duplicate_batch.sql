SELECT source_month, COUNT(*) AS rows
FROM urban_curated.traffic
WHERE source_month = '2026-06'
GROUP BY source_month;
