INSERT INTO material_sold
(created_on_record, material_id, count, product_id, date_sold)
VALUES ((now() at time zone 'Europe/Kiev'), %s, %s, %s, %s);


UPDATE product_sold ps
SET prime_cost = (
    SELECT round(sum(ms.count::numeric *  m.price_for_one_unit::numeric), 2)
    from product_sold ps1
    left join material_sold ms on ps1.id = ms.product_id
    left join material m on m.id = ms.material_id
    WHERE ps.id = ps1.id
);





