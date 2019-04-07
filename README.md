# BootBankJS-PY
Backend script for BootBankJS frontend

## Install
1. clone repository
```shell
git clone https://github.com/Ezak91/BootBankJS-PY.git
```  
2. rename config files
```shell
cd BootBankJS-PY
mv config.json.example config.json
mv accounts.json.example accounts.json
```
3. edit config files see
```shell
nano config.json
nano accounts.json
```

## Edit config files
**config.json**
```json
{
    "host": "localhost",
    "user": "root",
    "passwd": "password",
    "database": "bootbankjs"
}
```
* **host**: your mysql host
* **user**: your mysql username
* **passwd**: your mysql passwd
* **database**: the bootbankjs database name

**accounts.json**
```json
[
  {
    "bankcode": "59350110",
    "banklogin": "bankuser",
    "bankpin": "bankpassword",
    "bankurl": "https://banking-sl2.s-fints-pt-sl.de/fints30"
  }
]
```
* **bankcode**: the bankcode of your bank
* **banklogin**: your banking user for online banking
* **bankpin**: your banking password for online banking
* **bankurl**: hbci/fints url of your bank

You can add multiple accounts separate by , like
```json
[
  {
    "bankcode": "59350110",
    "banklogin": "bankuser",
    "bankpin": "bankpassword",
    "bankurl": "https://banking-sl2.s-fints-pt-sl.de/fints30"
  },
  {
    "bankcode": "59350110",
    "banklogin": "bankuse2r",
    "bankpin": "bankpassword2",
    "bankurl": "https://banking-sl2.s-fints-pt-sl.de/fints30"
  }  
]
```
