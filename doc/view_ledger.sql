CREATE VIEW `view_ledger` AS
    SELECT 
        `transaction`.transaction_id,
        `transaction`.date,
        `transaction`.account_id,
        account.name AS 'AccountName',
        `transaction`.enter_date,
        `transaction`.check_num,
        COALESCE(display_name.name, payee.name) AS 'Payee',
        payee.name AS 'DownloadedPayee',
        transaction_label.value AS 'TransactionLabel',
        category.name AS 'Category',
        memo.text AS 'Memo',
        `transaction`.amount AS 'Amount'
    FROM
        `transaction`
            LEFT OUTER JOIN
        payee ON payee.payee_id = `transaction`.payee_id
            LEFT OUTER JOIN
        category ON category.category_id = `transaction`.category_id
            LEFT OUTER JOIN
        transaction_label ON transaction_label.transaction_label_id = `transaction`.transaction_label_id
            LEFT OUTER JOIN
        display_name ON display_name.display_name_id = payee.display_name_id
            LEFT OUTER JOIN
        account ON account.account_id = `transaction`.account_id
            LEFT OUTER JOIN
        memo ON memo.memo_id = `transaction`.memo_id