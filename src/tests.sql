WITH signal_table AS (
    SELECT
        DISTINCT(segment_index) AS segment_index
      , signal  AS signal_segment
    FROM
        ecg_000000_test06c
    ORDER BY
        segment_index
)
SELECT
    0.001 * ((ROW_NUMBER() OVER ()) -1) as time_s
  , signal
FROM (
	SELECT
		UNNEST(signal_segment) AS signal
	FROM signal_table
) AS tmp



