import logging
import json
import datetime
import mysql.connector
import time
import crypt
from fints.client import FinTS3PinTanClient


mydb = None


def get_accounts():
    with open('accounts.json') as j:
        data = json.load(j)
    return data


def get_conf():
    with open('config.json') as k:
        data = json.load(k)
    global mydb
    mydb = mysql.connector.connect(
        host=data['host'],
        user=data['user'],
        passwd=data['passwd'],
        database=data['database']

    )


def get_userid(f):
    mycursor = mydb.cursor()

    sql = "Select id from user where username = %s and bankcode = %s"
    val = (f.user_id, f.bank_identifier.bank_code)
    mycursor.execute(sql, val)
    id = mycursor.fetchone()
    if id is None:
        id = create_user(f)
    else:
        id = id[0]
    return id


def create_user(f):
    mycursor = mydb.cursor()
    password = crypt.crypt(str(f.pin))
    sql = "Insert into user (username, bankcode, password) VALUES (%s, %s, %s)"
    val = (f.user_id,f.bank_identifier.bank_code, password)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid


def get_last_Date(account, userid):
    mycursor = mydb.cursor()
    sql = "Select MAX(date) as max from transactions where accountNumber = "+account.accountnumber+" and userid = "+str(userid)
    mycursor.execute(sql)
    date = mycursor.fetchone()
    if date[0] is None:
        datetime_object = datetime.datetime.strptime('JAN 1 1919  1:33PM', '%b %d %Y %I:%M%p')
        date = datetime_object.date();
    else:
        date = date[0]
        date = date + datetime.timedelta(days=1)
    return date


def get_balance(account, f):
    balance = f.get_balance(account)
    balance_double = balance.amount.amount
    print("Balance is ", balance_double)
    return balance_double


def get_transactions(account, f, userid):
    startdate = get_last_Date(account, userid)
    transactions = f.get_transactions(account, startdate, datetime.datetime.now().date())
    save_transactions(transactions, account, userid)


def save_balance(balance_double, account, userid):
    mycursor = mydb.cursor()
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    month = time.strftime('%m')
    year = time.strftime('%Y')

    sql = "SELECT id from balance where userid = %s and accountNumber = %s and month(date) = %s and year(date) = %s"
    val = (userid, account.accountnumber, int(month), int(year))

    mycursor.execute(sql, val)
    id = mycursor.fetchone()
    if id is None:
        sql = "INSERT INTO balance (userid, accountNumber, balance, date) VALUES (%s, %s, %s, %s)"
        val = (int(userid), account.accountnumber, balance_double, date)

        mycursor.execute(sql, val)
        mydb.commit()
        print("Balance inserted")
    else:
        id = id[0];
        sql = "UPDATE balance set balance = %s, date = %s where id = %s"
        val = (balance_double, date, id)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Balance updated")




def save_transactions(transactions,account, userid):
    mycursor = mydb.cursor()
    mytransactions = generate_transaction_ids(transactions, userid)
    for transactionid in mytransactions:

        try:
            transaction = mytransactions[transactionid]
            purpose = transaction.data['purpose'] or "";
            applicant = transaction.data['applicant_name'] or "";
            sql = "INSERT INTO transactions (id,userid,accountNumber,amount,purpose,applicant,date,entryDate) " \
                  "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (transactionid,userid, account.accountnumber, transaction.data['amount'].amount, purpose, applicant,
                   transaction.data['date'], transaction.data['entry_date'])
            mycursor.execute(sql, val)
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

    mydb.commit()
    print("Transactions inserted")


def generate_transaction_ids(transcations, userid):
    count = 1
    lastday = ""
    mytransactions = dict()
    for transaction in transcations:
        if str(transaction.data['date']) != lastday:
            count = 1;
        key = str(count)+'_'+str(userid)+'_'+str(transaction.data['date'])
        mytransactions[key] = transaction
        lastday = str(transaction.data['date'])
        count += 1

    return mytransactions


def main():
    print("Start BalanceFetcher ", datetime.datetime.now())
    print("==============================================")
    logging.basicConfig()
    get_conf()
    loginAccounts = get_accounts()
    for login in loginAccounts:
        f = FinTS3PinTanClient(login['bankcode'], login['banklogin'], login['bankpin'], login['bankurl'])
        userid = get_userid(f)
        accounts = f.get_sepa_accounts()
        for account in accounts:
            get_transactions(account, f, userid)
            balance = get_balance(account, f)
            save_balance(balance, account, userid)
    print("==============================================")


main()
