select ps.id,
       ps.type,
       date(date_sold),
       prime_cost,
       price
from product_sold ps
where ps.id = %s;


