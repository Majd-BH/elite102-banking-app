import sqlite3

def get_connection(db_name="banking_app.db"):
    return sqlite3.connect(db_name)


def init_db(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        balance REAL
    )
    """)
    conn.commit()

    cursor.execute("PRAGMA table_info(accounts)")
    columns = [column[1] for column in cursor.fetchall()]

    if "password" not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN password TEXT")
        conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        amount REAL NOT NULL,
        balance_after REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )
    """)
    conn.commit()


def record_transaction(conn, account_id, transaction_type, amount, balance_after):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (account_id, transaction_type, amount, balance_after)
        VALUES (?, ?, ?, ?)
        """,
        (account_id, transaction_type, amount, balance_after)
    )
    conn.commit()


def get_transactions(conn, account_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT transaction_type, amount, balance_after, created_at
        FROM transactions
        WHERE account_id = ?
        ORDER BY id
        """,
        (account_id,)
    )
    return cursor.fetchall()


def show_transactions(conn, account_id):
    transactions = get_transactions(conn, account_id)

    if not transactions:
        print("No transactions found.")
        return

    print("\nTransaction History:")
    for transaction_type, amount, balance_after, created_at in transactions:
        print(
            f"{created_at} | {transaction_type} | "
            f"Amount: ${amount:.2f} | Balance After: ${balance_after:.2f}"
        )


def create_account_db(conn, name, password, deposit):
    if deposit < 0:
        raise ValueError("Deposit cannot be negative.")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO accounts (name, password, balance) VALUES (?, ?, ?)",
        (name.capitalize(), password, deposit)
    )
    conn.commit()

    account_id = cursor.lastrowid
    record_transaction(conn, account_id, "account_created", deposit, deposit)

    return account_id


def authenticate_account(conn, account_id, password):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM accounts WHERE id = ? AND password = ?",
        (account_id, password)
    )
    return cursor.fetchone() is not None


def get_account_name(conn, account_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM accounts WHERE id = ?", (account_id,))
    row = cursor.fetchone()

    if row is None:
        raise ValueError("Account not found.")

    return row[0]


def get_balance(conn, account_id):
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    row = cursor.fetchone()

    if row is None:
        raise ValueError("Account not found.")

    return row[0]


def deposit_money(conn, account_id, amount):
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?",
        (amount, account_id)
    )
    conn.commit()

    new_balance = get_balance(conn, account_id)
    record_transaction(conn, account_id, "deposit", amount, new_balance)

    return new_balance


def withdraw_money(conn, account_id, amount):
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    balance = get_balance(conn, account_id)

    if amount > balance:
        raise ValueError("You do not have enough money.")

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        (amount, account_id)
    )
    conn.commit()

    new_balance = get_balance(conn, account_id)
    record_transaction(conn, account_id, "withdrawal", amount, new_balance)

    return new_balance


def create_account(conn):
    name = input("Enter your name: ").capitalize()
    password = input("Create a password: ")

    while True:
        try:
            deposit = float(input("How much would you like to deposit to start the account? $"))
            account_id = create_account_db(conn, name, password, deposit)
            print("Account created successfully.")
            print(f"Name: {name}")
            print(f"Account ID: {account_id}")
            print(f"Starting balance: ${deposit:.2f}")
            return account_id
        except ValueError as e:
            print(e)


def find_account(conn):
    while True:
        try:
            account_id = int(input("Enter account ID: "))
            break
        except ValueError:
            print("Please enter a valid integer.")

    password = input("Enter your password: ")

    if authenticate_account(conn, account_id, password):
        name = get_account_name(conn, account_id)
        print(f"Welcome back, {name}!")
        return account_id

    print("Incorrect account ID or password.")
    return None


def show_balance(conn, account_id):
    balance = get_balance(conn, account_id)
    print(f"Your current balance is ${balance:.2f}")


def add_money(conn, account_id):
    while True:
        try:
            amount = float(input("How much money would you like to add? $"))
            new_balance = deposit_money(conn, account_id, amount)
            print(f"${amount:.2f} was added to your account.")
            print(f"Your new balance is ${new_balance:.2f}")
            break
        except ValueError as e:
            print(e)


def take_money_out(conn, account_id):
    while True:
        try:
            amount = float(input("How much money would you like to take out? $"))
            new_balance = withdraw_money(conn, account_id, amount)
            print(f"${amount:.2f} was taken out of your account.")
            print(f"Your new balance is ${new_balance:.2f}")
            break
        except ValueError as e:
            print(e)


def main():
    print("Hello and welcome to the banking app")

    conn = get_connection()
    init_db(conn)

    current_account = None

    while True:
        if current_account is None:
            print("\n1. Create account")
            print("2. Access account by ID")
            print("3. Exit")

            choice = input("Pick an option: ")

            if choice == "1":
                current_account = create_account(conn)

            elif choice == "2":
                current_account = find_account(conn)

            elif choice == "3":
                print("Goodbye!")
                break

            else:
                print("That is not a valid choice.")

        else:
            try:
                name = get_account_name(conn, current_account)
            except ValueError:
                print("That account no longer exists.")
                current_account = None
                continue

            print(f"\nYou are in {name}'s account")
            print("1. Add money")
            print("2. Take money out")
            print("3. Check balance")
            print("4. View transaction history")
            print("5. Switch accounts")
            print("6. Create another account")
            print("7. Log out")

            choice = input("Pick an option: ")

            if choice == "1":
                add_money(conn, current_account)

            elif choice == "2":
                take_money_out(conn, current_account)

            elif choice == "3":
                show_balance(conn, current_account)

            elif choice == "4":
                show_transactions(conn, current_account)

            elif choice == "5":
                current_account = find_account(conn)

            elif choice == "6":
                current_account = create_account(conn)

            elif choice == "7":
                print("Logged out.")
                current_account = None

            else:
                print("That is not a valid choice.")

    conn.close()


if __name__ == "__main__":
    main()