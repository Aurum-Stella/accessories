select
    m.id,
    m.name,
    ms.count
from product_sold ps
left join material_sold ms on ps.id = ms.product_id
left join material m on m.id = ms.material_id
where ps.id = %s