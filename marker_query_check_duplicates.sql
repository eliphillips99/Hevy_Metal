SELECT 
    cd.date AS Date,
    COUNT(hm.common_data_id) AS RowCount
FROM 
    health_markers hm
JOIN 
    common_data cd ON hm.common_data_id = cd.common_data_id
GROUP BY 
    cd.date
HAVING 
    COUNT(hm.common_data_id) > 1
ORDER BY 
    cd.date;
