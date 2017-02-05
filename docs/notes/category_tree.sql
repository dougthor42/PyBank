SELECT t1.name AS level1, t2.name as level2, t3.name as level3, t4.name as level4, t5.name as level5, t6.name as level6, t7.name as level7
FROM category AS t1
LEFT JOIN category AS t2 ON t2.parent = t1.id
LEFT JOIN category AS t3 ON t3.parent = t2.id
LEFT JOIN category AS t4 ON t4.parent = t3.id
LEFT JOIN category AS t5 ON t5.parent = t4.id
LEFT JOIN category AS t6 ON t6.parent = t5.id
LEFT JOIN category AS t7 ON t7.parent = t6.id
WHERE t1.name = 'Category'