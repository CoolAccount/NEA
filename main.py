import sqlite3

db = sqlite3.connect("records.db")

def get_id(name: str,lastname:str):
    user_id = db.execute("SELECT p_id FROM details WHERE p_name = ? AND p_lastname = ?", (name,lastname,))
    user_id = user_id.fetchone()
    if user_id is None:
        return -1
    return user_id[0]

def intiliase_tables():
    db.execute("""CREATE TABLE IF NOT EXISTS details(
    p_id INTEGER PRIMARY KEY AUTOINCREMENT,
    p_name text,
    p_lastname text,
    p_address text,
    p_number int
  )""")
    db.execute("""CREATE TABLE IF NOT EXISTS p_order(
    order_id int,
    sweet text,
    quantity int
  )""")
    db.execute("""
  CREATE TABLE IF NOT EXISTS messages(
    p_id int,
    message text
  )
  """)
    db.commit()

def add_message(id:int,message:str):
    db.execute("INSERT OR IGNORE INTO messages(p_id,message) VALUES (?,?)",(id,message))
    db.commit()

def add_details(phone_number: int, name: str,lastname:str, address: str):
    db.execute("INSERT OR IGNORE INTO details(p_name,p_lastname,p_address,p_number) VALUES(?,?,?,?)", (name, lastname,address, phone_number))
    db.commit()

def get_all_orders():
    msg = ""
    data = db.execute("SELECT p_id,p_name,p_lastname FROM details")
    data = data.fetchall()
    for id,name,lastname in data:
        msg += f"{name} {lastname}\n".title()
        order = db.execute("SELECT sweet,quantity FROM p_order WHERE order_id = ?",(id,))
        order = order.fetchall()
        for sweet,quantity in order:
            msg += f"{sweet} {quantity}g\n"
        msg += "\n"

    return msg

def add_order(name: str,lastname:str, item: str, quantity: int):
    user_id = get_id(name,lastname)
    db.execute("INSERT OR IGNORE INTO p_order(order_id,sweet,quantity) VALUES(?,?,?)", (user_id, item, quantity,))
    db.commit()

def get_order(name: str,lastname:str):
    message = ""
    user_id = get_id(name,lastname)
    if user_id == -1:
        return "Order doesn't exist."

    order = db.execute("SELECT sweet,quantity FROM p_order WHERE order_id = ?", (user_id,))
    order = order.fetchall()

    message_db = db.execute("SELECT message FROM messages WHERE p_id = ?",(user_id,))
    message_db = message_db.fetchone()
    for sweet, quantity in order:
        message += f"{sweet} {quantity}g\n"
    if message_db == None:
        message += "Message: Merry Christmas"
    else:
        message += f"Message: Merry Christmas {message_db[0]}"

    return message

def sendinvoice(name:str,lastname:str):
    delivery = 4.99
    sweets = 9.99
    message_length = 0
    message = ""
    user_id = get_id(name,lastname)
    if user_id == -1:
        return f"No record for {name} and {lastname} in database."

    order = db.execute("SELECT sweet,quantity FROM p_order WHERE order_id = ?", (user_id,))
    order = order.fetchall()

    message_db = db.execute("SELECT message FROM messages WHERE p_id = ?", (user_id,))
    message_db = message_db.fetchone()
    for sweet, quantity in order:
        message += f"{sweet} {quantity}g\n"
    if message_db == None:
        message += "Message: Merry Christmas"
    else:
        message_len = message_db[0].replace(" ","")
        message_length += len(message_len)
        message += f"Message: Merry Christmas {message_db[0]}"

    if message_length == 0:
        message += f"\nTotal: £{delivery+sweets}"
    else:
        message += f"\nTotal: £{delivery+sweets+(message_length*0.10)}"


    return message

intiliase_tables()

incremenets = [100,200,300,400,500]

menu = """
1) New order
2) View specific order
3) View all orders
4) Get customer's invoice
"""

def integer(num):
    try:
        return int(num)
    except ValueError:
        return -1

while True:
    choice = input(menu)
    try:
        choice = int(choice)
        if choice in [1,2,3,4]:
            if choice == 1:
                order = [[],[]]
                name = input("What is customers' name? ")
                lastname = input("What is customer's lastname? ")
                number = input("What is customers' number? ")
                address = input("What is customers' address? ")
                int_number = integer(number)
                if int_number == -1:
                    print("Invalid phone number")
                else:
                    add_details(int_number,name,lastname,address)
                    amount = 0
                    itemAmount = 0
                    checker = 0
                    while True:
                        if amount == 1000:
                            if 3 <= itemAmount <= 6:
                                msg = ""
                                for k, v in zip(order[0], order[1]):
                                    msg += f"{k} {v}g\n"
                                print(msg + f"\nThis is your order!({itemAmount})")
                            else:
                                checker += 1
                                print("You need at least 3 items. Retry the order!")
                            break
                        item = input("What item do you want? ")
                        quanity = input("How much grams? ")
                        int_quanity = integer(quanity)
                        if int_quanity == -1:
                            print("Provide an integer.")
                            break
                        else:
                            if int_quanity in incremenets:
                                if amount+int_quanity > 1000 or itemAmount >= 6:
                                    if itemAmount >= 6:
                                        print(f"You have gone over the limit of 6! Retry again.")
                                        checker += 1
                                    else:
                                        print(f"If you add that item you will go over 1000!({amount})")
                                elif amount + int_quanity == 1000 and 3 <= itemAmount+1 <= 6:
                                    order[0].append(item)
                                    order[1].append(int_quanity)
                                    add_order(name,lastname,item,int_quanity)
                                    msg = ""
                                    for k, v in zip(order[0], order[1]):
                                        msg += f"{k} {v}g\n"
                                    print(msg + f"\nThis is your order!({itemAmount+1})")
                                    break
                                else:
                                    itemAmount += 1
                                    order[0].append(item)
                                    order[1].append(int_quanity)
                                    amount += int_quanity
                                    add_order(name,lastname,item,int_quanity)
                            else:
                                print("The items have to be increments of 100 and cannot be over 500!")
                    if checker == 0:
                        message = input("Do you want to add an additional message? Y/N ")
                        validOptions = ["Y"]
                        if message.upper() in validOptions:
                            extra_message = input("What do you want the message to be? ")
                            id = get_id(name,lastname)
                            add_message(id,extra_message)

            elif choice == 2:
                name = input("What is the person's name ? ")
                surname = input("What is the person's surname? ")
                print(get_order(name,surname))
            elif choice == 3:
                print(get_all_orders())
            else:
                name = input("What is the person's name ? ")
                surname = input("What is the person's surname? ")
                print(sendinvoice(name, surname))

    except ValueError:
        print("You need to provide a valid option!")


