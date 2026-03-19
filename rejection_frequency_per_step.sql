WITH TargetItems AS (
    -- Step 1: Identify ONLY the items that were actually submitted in our target timeframe
    SELECT DISTINCT mv.resource_id
    FROM metadatavalue mv
             JOIN item i ON i.item_id = mv.resource_id
    WHERE mv.metadata_field_id = 30
      AND mv.resource_type_id = 2
      AND (mv.text_value LIKE 'Submitted by % on 2023-%'
        OR mv.text_value LIKE 'Submitted by % on 2024-%'
        OR mv.text_value LIKE 'Submitted by % on 2025-%')
      AND mv.text_value NOT LIKE 'Submitted by %(katharina.kaiser@tuwien.ac.at)%'
      AND i.in_archive = 1
),
     RawEvents AS (
         -- Aggregate all provenance events ONLY for the target items
         SELECT m.resource_id, m.metadata_value_id, TO_CHAR(m.text_value) as txt
         FROM metadatavalue m
                  INNER JOIN item i ON m.resource_id = i.item_id
                  INNER JOIN TargetItems t ON m.resource_id = t.resource_id
         WHERE m.metadata_field_id = 30
           AND i.owning_collection IS NOT NULL
           AND i.owning_collection != 4
           AND i.in_archive = 1
     ),
     RejectionAnchors AS (
         -- Identify rejection events and their preceding workflow 'Reset' point
         SELECT
             r.resource_id,
             r.metadata_value_id AS current_rej_id,
             (SELECT MAX(s.metadata_value_id)
              FROM RawEvents s
              WHERE s.resource_id = r.resource_id
                AND s.metadata_value_id < r.metadata_value_id
                AND (LOWER(s.txt) LIKE 'submitted by%'
                  OR LOWER(s.txt) LIKE 'rejected by%')) AS last_reset_id
         FROM RawEvents r
         WHERE LOWER(r.txt) LIKE 'rejected by%'
     ),
     StepCounter AS (
         -- Determine step location based on approvals within the current cycle
         SELECT
             ra.resource_id,
             ra.current_rej_id,
             (SELECT COUNT(*)
              FROM RawEvents a
              WHERE a.resource_id = ra.resource_id
                AND LOWER(a.txt) LIKE 'approved for entry into archive by%'
                AND a.metadata_value_id > NVL(ra.last_reset_id, 0)
                AND a.metadata_value_id < ra.current_rej_id) AS approvals_in_current_cycle
         FROM RejectionAnchors ra
     ),
     Categorized AS (
         -- Map numeric counts to human-readable workflow steps
         SELECT DISTINCT
             resource_id,
             current_rej_id,
             CASE approvals_in_current_cycle
                 WHEN 0 THEN 'Step 1 Rejection'
                 WHEN 1 THEN 'Step 2 Rejection'
                 WHEN 2 THEN 'Step 3 Rejection'
                 ELSE 'Step 3 Rejection (Multiple Loops)'
                 END AS rejection_step
         FROM StepCounter
     ),
     TotalSubmissions AS (
         -- Baseline count of unique submitted items from our targeted list
         SELECT COUNT(DISTINCT resource_id) AS total_items
         FROM RawEvents
         WHERE LOWER(txt) LIKE 'submitted by%'
     )
-- Generate final percentage-based frequency report
SELECT
    c.rejection_step,
    COUNT(c.current_rej_id) AS total_rejection_events,
    COUNT(DISTINCT c.resource_id) AS distinct_items_rejected,
    ts.total_items AS total_items_submitted,
    ROUND((COUNT(DISTINCT c.resource_id) / NULLIF(ts.total_items, 0)) * 100, 2) AS percentage_of_total
FROM Categorized c
         CROSS JOIN TotalSubmissions ts
GROUP BY c.rejection_step, ts.total_items
ORDER BY c.rejection_step;