import unittest
import sqlite3
from Main import (
    init_db,
    create_account_db,
    authenticate_account,
    get_balance,
    deposit_money,
    withdraw_money,
    get_account_name
)

class TestBankingApp(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_db(self.conn)
        self.account_id = create_account_db(self.conn, "Rayyan", "pass123", 100.0)

    def tearDown(self):
        self.conn.close()

    def test_create_account(self):
        balance = get_balance(self.conn, self.account_id)
        self.assertEqual(balance, 100.0)

    def test_get_account_name(self):
        name = get_account_name(self.conn, self.account_id)
        self.assertEqual(name, "Rayyan")

    def test_authenticate_account_correct_password(self):
        self.assertTrue(authenticate_account(self.conn, self.account_id, "pass123"))

    def test_authenticate_account_wrong_password(self):
        self.assertFalse(authenticate_account(self.conn, self.account_id, "wrongpass"))

    def test_deposit_money(self):
        new_balance = deposit_money(self.conn, self.account_id, 50.0)
        self.assertEqual(new_balance, 150.0)

    def test_withdraw_money(self):
        new_balance = withdraw_money(self.conn, self.account_id, 40.0)
        self.assertEqual(new_balance, 60.0)

    def test_withdraw_too_much(self):
        with self.assertRaises(ValueError):
            withdraw_money(self.conn, self.account_id, 200.0)

    def test_negative_starting_balance(self):
        with self.assertRaises(ValueError):
            create_account_db(self.conn, "Maria", "abc123", -10.0)

    def test_negative_deposit(self):
        with self.assertRaises(ValueError):
            deposit_money(self.conn, self.account_id, -5.0)

    def test_zero_withdrawal(self):
        with self.assertRaises(ValueError):
            withdraw_money(self.conn, self.account_id, 0)

if __name__ == "__main__":
    unittest.main()