# Virtual Crypto Trading
#### Video Demo:  <https://youtu.be/vcH0rPcqB9k>
#### Description: This project lets someone to try buying and selling cryptocurrency using virtual money with the use of CoinMarketCap API
**This is a project that lets someone to try buying and selling cryptocurrency using virtual cash and CoinMarketCap API.**

# CS50 Final Project - Virtual Crypto Trading

The project is a webpage where one can try buying and selling cryptocurrency with virtual cash using data from CoinMarketCap API

Technologies used:

- Python
- HTML
- CSS
- JavaScript
- SQL
- Flask
- other small libraries or packages

## How the webpage works?

The idea is simple. The user can register. During registration you need to enter these fields:

- Username
- Password: it is checked to match, must be at least 15 symbols long and is hashed after checks are done

### Routing

Each route checks if the user is authenticated.

### Sessions

The webpage uses sessions to confirm that user is registered.

### Databases

There are two databases.
- Users database contains user id as primary key, username, password hash and virtual cash with default value of 100 000 USD.
- Transactions database contains transaction id as primary key, user_id, cryptocurrency name, cryptocurrency symbol, shares (coins), price, time and type (buy or sell).

## Possible improvements

As all applications this one can also be improved. Possible improvements:

- Add donut chart on index.html to see percent share of each coin in portfolio.
- Ability buy or sell crypto directly from index page.

## How to launch application

1. Run command `flask run` to run flask application in VS Code
3. In your browser go to `localhost:5000`
4. You are ready to go!

## HTML page explanation

- On login page one can log in.

- On register page one can register using username and password. The password must be at least 15 character or apology page will render saying that password is too short.

- On index page your portfolio is displayed with cryptocurrency symbol, cryptocurrency name, number of coins, price of purchase, cash and total amount of portfolio. As a new user you will have 100 000 USD.

- On quote page one can get latest price and name of cryptocurrency by using cryptocurrency ticker and data provided by CoinMarketCap API.

- On buy page one can buy cryptocurrency using cryptocurrency ticker and entering number of coins.

- On sell page one can sell already purchased cryptocurrency by choosing it in drop down menu and entering number of coins one wishes to sell. If one enter more coins that one has, an apology page will be rendered.

- On history page there are all transactions with cryptocurrency ticker, type, number of coins, price and time.

- On add cash page one can add cash to one's account entering amount and pressing green add cash button.

- On change password page on can change one's password. Here password must not have minimum 15 symbols.

- When there is some bug an apology page will render displaying a sad man with sand meme with some words about happened bug.

- The project uses data from free version of CoinMarketCap API.

