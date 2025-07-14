-- Fusionner les doublons
UPDATE orders SET supplier_id = 101 WHERE supplier_id = 102;
DELETE FROM suppliers WHERE id = 102;
