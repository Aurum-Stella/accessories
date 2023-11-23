
UPDATE material m
SET quantity_in_stock = quantity_in_stock - ms.count
FROM product_sold ps
LEFT JOIN material_sold ms ON ps.id = ms.product_id
WHERE ps.id = %s AND m.id = ms.material_id;


UPDATE material m
SET total_cost = price_for_one_unit * quantity_in_stock
FROM product_sold ps
LEFT JOIN material_sold ms ON ps.id = ms.product_id
WHERE ps.id = %s AND m.id = ms.material_id;
