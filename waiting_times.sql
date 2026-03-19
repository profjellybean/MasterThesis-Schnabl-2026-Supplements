
CREATE OR REPLACE VIEW v_dspace_workflow_bottlenecks AS
WITH TargetItems AS (
    -- Step 1: Identify ONLY the items that were actually submitted in our target timeframe
    SELECT DISTINCT mv.resource_id
    FROM metadatavalue mv
             JOIN item i ON i.item_id = mv.resource_id
    WHERE mv.metadata_field_id = 30
      AND mv.resource_type_id = 2
      AND (mv.text_value LIKE 'Submitted by % on 2023-%'
      OR
          mv.text_value LIKE 'Submitted by % on 2024-%'
    OR mv.text_value LIKE 'Submitted by % on 2025-%')
      AND mv.text_value NOT LIKE 'Submitted by %(katharina.kaiser@tuwien.ac.at)%'
      AND i.in_archive = 1
),
     RawEvents AS (
         -- Step 2: Get ALL workflow events, but ONLY for the items identified above
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
                  INNER JOIN TargetItems t ON m.resource_id = t.resource_id
         WHERE m.metadata_field_id = 30
           AND i.owning_collection IS NOT NULL
           AND i.owning_collection NOT IN (4, 7)
           AND i.in_archive = 1
           AND LOWER(TO_CHAR(m.text_value)) NOT LIKE '%katharina.kaiser@tuwien.ac.at%'
     ),
     FilteredEvents AS (
         SELECT * FROM RawEvents WHERE event_type != 'Other' AND event_time IS NOT NULL
     ),
     OrderedEvents AS (
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
         SELECT
             resource_id,
             event_time AS start_time,
             next_event_time AS end_time,
             event_type AS start_stage,
             next_event_type AS end_stage,
             approval_step_num,
             GREATEST(0,
                      ((CAST(next_event_time AS DATE) - CAST(event_time AS DATE)) * 24)
                          -
                      (
                          ((TRUNC(CAST(next_event_time AS DATE), 'IW') - TRUNC(CAST(event_time AS DATE), 'IW')) / 7) * 48
                          )
             ) AS business_hours_in_queue
         FROM OrderedEvents
         WHERE next_event_time IS NOT NULL
     )
SELECT
    resource_id,
    start_time,
    end_time,
    CASE
        WHEN start_stage = 'Submitted' AND end_stage = 'Approved' THEN '1. Submit -> FIS Check'
        WHEN start_stage = 'Approved' AND approval_step_num = 1 AND end_stage = 'Approved' THEN '2. FIS -> Library'
        WHEN start_stage = 'Approved' AND approval_step_num = 2 AND (end_stage = 'Approved' OR end_stage = 'Archived') THEN '3. Library -> Faculty'
        WHEN start_stage = 'Rejected' AND end_stage = 'Submitted' THEN '4. Rejected -> Resubmitted (User)'
        ELSE 'Other Transitions'
        END AS workflow_stage,
    ROUND(business_hours_in_queue, 2) AS wait_time_hours
FROM QueueTimes
WHERE CASE
          WHEN start_stage = 'Submitted' AND end_stage = 'Approved' THEN '1. Submit -> FIS Check'
          WHEN start_stage = 'Approved' AND approval_step_num = 1 AND end_stage = 'Approved' THEN '2. FIS -> Library'
          WHEN start_stage = 'Approved' AND approval_step_num = 2 AND (end_stage = 'Approved' OR end_stage = 'Archived') THEN '3. Library -> Faculty'
          WHEN start_stage = 'Rejected' AND end_stage = 'Submitted' THEN '4. Rejected -> Resubmitted (User)'
          ELSE 'Other Transitions'
          END != 'Other Transitions';
