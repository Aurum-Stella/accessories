WITH placeholder AS (
  SELECT %s::INTEGER AS val
)

SELECT * FROM material
WHERE id = (SELECT val FROM placeholder) OR (SELECT val FROM placeholder) = -1
