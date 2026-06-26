USE nexus_intelligence;

-- ====================================
-- CUSTOMER SEGMENTS
-- ====================================

INSERT IGNORE INTO customer_segments
(segment_id, segment_name, description, discount_eligibility)
VALUES
(1, 'Consumer',   'Retail customers',        TRUE),
(2, 'Corporate',  'Business customers',      TRUE),
(3, 'Enterprise', 'Large enterprises',       TRUE),
(4, 'Government', 'Government sector',       FALSE),
(5, 'Education',  'Universities and schools',TRUE);

-- ====================================
-- REGIONS
-- ====================================

INSERT IGNORE INTO regions
(region_id, region_name, country, manager_id, created_at)
VALUES
(1, 'North India',   'India', NULL, NOW()),
(2, 'South India',   'India', NULL, NOW()),
(3, 'East India',    'India', NULL, NOW()),
(4, 'West India',    'India', NULL, NOW()),
(5, 'Central India', 'India', NULL, NOW());

-- ====================================
-- PRODUCT CATEGORIES
-- ====================================

INSERT IGNORE INTO product_categories
(category_id, category_name, parent_category_id, description)
VALUES
(1, 'Electronics',    NULL, 'Electronic products'),
(2, 'Furniture',      NULL, 'Furniture products'),
(3, 'Office Supplies',NULL, 'Office items'),
(4, 'Software',       NULL, 'Software licenses'),
(5, 'Accessories',    NULL, 'Accessories');

-- ====================================
-- WAREHOUSES
-- ====================================

INSERT IGNORE INTO warehouses
(warehouse_id, warehouse_name, location, capacity, manager_name)
VALUES
(1, 'Central Fulfillment',    'Mumbai',    50000, 'Arjun Singh'),
(2, 'Northern Hub',           'Delhi',     35000, 'Priya Sharma'),
(3, 'Southern Distribution',  'Bangalore', 40000, 'Rahul Kumar');
