WITH write_product AS (
   INSERT INTO product_sold (type, created_on,  price)
         VALUES (%s,%s, %s ) RETURNING id
),

write_material as(
    INSERT INTO material_sold (material_id, created_on, product_id, count )
         VALUES (%s,%s, %s, (select id from write_product) ) RETURNING id
)
select * from write_product, write_material;









