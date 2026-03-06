# Appendix: SQL Analytics for ReposiTUm Workflow Validation

This appendix contains the Oracle SQL scripts used to extract empirical performance metrics from the ReposiTUm (DSpace-based) repository. 
These queries analyze provenance metadata (Metadata Field ID 30) to quantify workflow latency and rejection frequencies for the period 2023–2025.

---

## 1. Rejection Frequency per Workflow Step

This script quantifies the "Hidden Factory" of rework loops. 
It maps rejection events to specific steps in the 3-step validation chain by counting successful approvals within a specific submission cycle.

```sql
WITH RawEvents AS (
    -- Aggregate all provenance events for target items
    SELECT m.resource_id, m.metadata_value_id, TO_CHAR(m.text_value) as txt
    FROM metadatavalue m
             INNER JOIN item i ON m.resource_id = i.item_id
    WHERE m.metadata_field_id = 30
      AND i.owning_collection IS NOT NULL 
      AND i.owning_collection != 4 
      AND i.in_archive = 1
      AND (m.text_value LIKE '%2023%' 
           OR m.text_value LIKE '%2024%' 
           OR m.text_value LIKE '%2025%')
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
         -- Baseline count of unique submitted items
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

```

## 2. Workflow Queue Time Analysis

This script calculates the end-to-end "Lead Time" for publications by measuring the duration between workflow states. 
It utilizes Regex to extract ISO 8601 timestamps from the free-text provenance logs and calculates the time difference in hours.

```sql
WITH RawEvents AS (
    -- Extract provenance events and timestamps using Oracle Regex
    SELECT
        m.resource_id,
        LOWER(TO_CHAR(m.text_value)) as txt,
        TO_TIMESTAMP(
                REGEXP_SUBSTR(TO_CHAR(m.text_value), '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z'),
                'YYYY-MM-DD"T"HH24:MI:SS"Z"'
        ) AS event_time,
        CASE
            WHEN LOWER(TO_CHAR(m.text_value)) LIKE 'submitted by%' THEN 'Submitted'
            WHEN LOWER(TO_CHAR(m.text_value)) LIKE 'approved for entry into archive by%' THEN 'Approved'
            WHEN LOWER(TO_CHAR(m.text_value)) LIKE 'rejected by%' THEN 'Rejected'
            WHEN LOWER(TO_CHAR(m.text_value)) LIKE 'made available in dspace%' THEN 'Archived'
            ELSE 'Other'
            END AS event_type
    FROM metadatavalue m
             INNER JOIN item i ON m.resource_id = i.item_id
    WHERE m.metadata_field_id = 30
      AND i.owning_collection IS NOT NULL 
      AND i.owning_collection != 4 
      AND i.in_archive = 1
      AND (TO_CHAR(m.text_value) LIKE '%2023%' 
           OR TO_CHAR(m.text_value) LIKE '%2024%' 
           OR TO_CHAR(m.text_value) LIKE '%2025%')
),
     FilteredEvents AS (
         -- Exclude maintenance updates and malformed dates
         SELECT * FROM RawEvents WHERE event_type != 'Other' AND event_time IS NOT NULL
     ),
     OrderedEvents AS (
         -- Partition by item and order chronologically to calculate transitions
         SELECT
             resource_id,
             event_time,
             event_type,
             CASE
                 WHEN event_type = 'Approved' THEN
                     ROW_NUMBER() OVER (PARTITION BY resource_id, event_type ORDER BY event_time)
                 ELSE 0
                 END as approval_step_num,
             LEAD(event_time) OVER (PARTITION BY resource_id ORDER BY event_time) AS next_event_time,
             LEAD(event_type) OVER (PARTITION BY resource_id ORDER BY event_time) AS next_event_type
         FROM FilteredEvents
     ),
     QueueTimes AS (
         -- Calculate duration in hours
         SELECT
             resource_id,
             event_type AS start_stage,
             next_event_type AS end_stage,
             approval_step_num,
             (CAST(next_event_time AS DATE) - CAST(event_time AS DATE)) * 24 AS hours_in_queue
         FROM OrderedEvents
         WHERE next_event_time IS NOT NULL
     )
-- Aggregate statistical distributions per workflow stage
SELECT
    CASE
        WHEN start_stage = 'Submitted' AND end_stage = 'Approved' THEN '1. Queue: Submit -> FIS Check (Step 1)'
        WHEN start_stage = 'Approved' AND approval_step_num = 1 AND end_stage = 'Approved' THEN '2. Queue: FIS -> Library (Step 2)'
        WHEN start_stage = 'Approved' AND approval_step_num = 2 AND (end_stage = 'Approved' OR end_stage = 'Archived') THEN '3. Queue: Library -> Faculty (Step 3)'
        WHEN start_stage = 'Rejected' AND end_stage = 'Submitted' THEN '4. User Rework Time: Rejected -> Resubmitted'
        ELSE 'Other Transitions'
        END AS workflow_stage,
    COUNT(*) AS total_transitions,
    ROUND(AVG(hours_in_queue), 2) AS mean_wait_time_hours,
    ROUND(MEDIAN(hours_in_queue), 2) AS median_wait_time_hours,
    ROUND(MIN(hours_in_queue), 2) AS min_wait_hours,
    ROUND(MAX(hours_in_queue), 2) AS max_wait_hours
FROM QueueTimes
WHERE hours_in_queue >= 0 -- Filter out out-of-order ID anomalies
GROUP BY
    CASE
        WHEN start_stage = 'Submitted' AND end_stage = 'Approved' THEN '1. Queue: Submit -> FIS Check (Step 1)'
        WHEN start_stage = 'Approved' AND approval_step_num = 1 AND end_stage = 'Approved' THEN '2. Queue: FIS -> Library (Step 2)'
        WHEN start_stage = 'Approved' AND approval_step_num = 2 AND (end_stage = 'Approved' OR end_stage = 'Archived') THEN '3. Queue: Library -> Faculty (Step 3)'
        WHEN start_stage = 'Rejected' AND end_stage = 'Submitted' THEN '4. User Rework Time: Rejected -> Resubmitted'
        ELSE 'Other Transitions'
        END
HAVING COUNT(*) > 100
ORDER BY workflow_stage;

```

---
