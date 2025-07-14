-- Empêche "Vanille de Tahiti" x2
ALTER TABLE products 
ADD CONSTRAINT unique_product_per_origin 
UNIQUE (name, origin_country);
