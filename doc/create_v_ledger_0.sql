DROP VIEW IF EXISTS v_ledger_0;
CREATE VIEW v_ledger_0 AS
    SELECT
        trans.date,
		trans.enter_date,
        trans.check_num,
        COALESCE(display_name.display_name, payee.name) as "payee",
        payee.name as "downloaded_payee",
		label.name AS "label",
        category.name AS "category", -- # TODO: Python Maps this instead?
		trans.memo,
        trans.amount
    FROM
        transaction_0 AS trans
        LEFT OUTER JOIN payee
            ON trans.payee_id = payee.id
        LEFT OUTER JOIN category
            ON trans.category_id = category.id
        LEFT OUTER JOIN label
            ON trans.label_id = label.id
        LEFT OUTER JOIN display_name
            ON payee.display_name_id = display_name.id