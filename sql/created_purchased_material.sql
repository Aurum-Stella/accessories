INSERT INTO material_purchased
(created_on_record, material_id, date_by, count, price)
VALUES ((now() at time zone 'Europe/Kiev'), %s, %s, %s, %s) RETURNING id, material_id;
