INSERT INTO material 
(created_on_record, name, size, is_natural, quantity_in_stock, photo, price_for_one_unit, zodiac_sign, total_cost)
VALUES ((now() at time zone 'Europe/Kiev'), %s, %s, %s, round(%s, 2), %s, 0, %s, %s);

UPDATE material m
SET price_for_one_unit =
    case when (quantity_in_stock is null or total_cost is null)
         then 0
    else
    round((total_cost::numeric / quantity_in_stock::numeric), 2)
    end
