UPDATE material m
SET quantity_in_stock = quantity_in_stock + mp.count,
    total_cost = total_cost + mp.price
    from material_purchased mp
    WHERE mp.id = %s
    and m.id = %s;


UPDATE material m
SET price_for_one_unit =
    case when (quantity_in_stock is null or total_cost is null)
         then 0
    else
    round((total_cost::numeric / quantity_in_stock::numeric), 2)
    end