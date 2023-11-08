INSERT INTO material 
(name, size, is_natural, quantity_in_stock, total_cost, price_for_one_unit)
VALUES (%s, %s, %s, round(%s, 2), %s, 0);

UPDATE material m
SET price_for_one_unit =
    case when (quantity_in_stock is null or total_cost is null)
         then 0
    else
    round((total_cost::numeric / quantity_in_stock::numeric), 2)
    end
