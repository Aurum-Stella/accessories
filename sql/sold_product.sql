INSERT INTO product_sold
(created_on_record, type, date_sold, price)
VALUES ((now() at time zone 'Europe/Kiev'), %s, %s, %s)  RETURNING id;

