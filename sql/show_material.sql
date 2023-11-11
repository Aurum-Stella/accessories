WITH placeholder AS (
  SELECT %s::INTEGER AS val
)

SELECT id,
       name,
       size,
       is_natural,
       quantity_in_stock,
       total_cost,
       price_for_one_unit

FROM material
WHERE id = (SELECT val FROM placeholder) OR (SELECT val FROM placeholder) = -1
group by id