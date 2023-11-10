WITH write_product AS (
   INSERT INTO product_sold (type, created_on,  price)
         VALUES (%s,%s, %s ) RETURNING id
),

write_material as(
    INSERT INTO material_sold (material_id, created_on, product_id, count )
         VALUES (%s,%s, %s, (select id from write_product) ) RETURNING id
)
select * from write_product, write_material;

UPDATE product_sold
SET prime_cost = (
    SELECT sum(price_for_one_unit)
    FROM product_sold ps
    LEFT JOIN material_sold ms ON ps.id = ms.product_id
    LEFT JOIN material m ON m.id = ms.material_id
)







