DROP VIEW temp_view_3;
CREATE VIEW temp_view_3 AS
    SELECT
        payee.id,
		payee.name,
		payee.display_name_id,
		display_name.display_name,
		coalesce(display_name.display_name, payee.name) as 'col'
    FROM
	    payee
        LEFT OUTER JOIN display_name
            ON payee.display_name_id = display_name.id
