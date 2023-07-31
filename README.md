# CryptXSpace
#### Video Demo:  https://youtu.be/vh6twRuFBo0
#### Description:
Think of CrptxSpace as a platform of index funds created for the modern digital age, Cryptocurrencies.
As you may have probably seen, the rise in popularity of currencies outside of the fiat exchange system has become wildy apparent.
With the growth and popularity of something so new and unfamiliar, the need for a less risky approach of investing has become much needed.
Think of S&P 500 for example, this index fund / ETF has grown at a staggering rate of about 10 to 15% per year, as the stocks within this
ETF (exchange trade fund) sparadically fluctuate each and every year. Investing in a ETF is essiential for beginner
investors and investors that can't neccesarily afford to risk half of their life savings on a company that might not even
exist a few years from now. Investing in cryptocurrencies can be just as risky if not more than stocks can be. Therefore
creating an ETF cryptocurrency platform has become a topic and idea that was begging for me to take action upon.

In this project I focused on using **Python** and **Flask** as a _framework_, **SQLite** for _data storage_, **html5**, **Javascript** and **TailwindCSS** for _styling_. The color theme behind the site was a Synthwave based color palette that brings an element of older 1970's vibrancy but new and modern.
Implementation was fairly tricky seeing as though Crypto ETF's have never been done before. So correctly storing multiple cryptocurrencies
into a dictionary was quite the challenge, especially when incorporating api calls that where specifically tailored to coins presented in one or multiple packages.
Aligning and setting up the websites layout was fairly difficult with using a new framework like tailwind, but the customization it alloted was
completely worh the initial struggles I faced.

## Instalation
1. Create a project folder and a .venv folder within:
```
$ mkdir cryptxspace
$ cd cryptxspace
$ python3 -m venv .venv
```
2. Activate environment with `. .venv/bin/activate`
3. Install Pip `pip3 install Flask`
4. Ensure that all your packages are up to date with `npm i`
5. Install all dependencies
```
$ pip install -r requirements.txt
```
6. `flask run` to start application

## Instructions
- Make an account through the Register page. Full name is not required
- Locate Log in page and log in to interact with the website
- You will now be brought to the Homepage (Dashboard) where you can purchase and sell any of the 3 custom made ETF's by clicking on the ETF that you would like to purchase
- To Buy and sell from the application you must click an ETF and you will find a list of the currencies that will be included in your purchase from there you can enter an amount to buy and you will be alerted of your purchase.
- To see items that you have purchased locate to the Portfolio page where you will find your transaction history at the bottom of the page.
- The Portfolio page will display the following:
  * Your display name, which if you provided a full name will display your name else the display name will be your username
  * Alongside your name will be the cash amount that you have available to spend
  * The middle-left coloumn you will find the Balance section where your total account balance will be displayed
  * The middle-right section will display a list of 10 trending ETF's that are randomly generated and selected on each refresh. These ETF's are not tradable at the moment, but will be in the future development of the app.
  * Last but not least we have your transaction history that stacks on the x-axis.
    + If you have not made any purchases yet. You will see a prompt that guides you to make a purchase.
    + All of your purchases and sells will show up in this row, with purple being your purchases and red being your sells.
    + Each transaction will appear with the ETF that you interacted with, the dollar amount in which you interacted at the time, and how many shares you interacted.
- From the Portfolio page we can locate to Settings where you can edit your profile and change your ***name, username, email,*** and ***password***.
  * Any changes made to your name and username will appear on your Portfolio immediately.
  * Changing your password will direct you to a seperate page where you must first enter your old password. Then you will be sent to a page where you can create your new password.
- Also in settings you can Validate your debit / credit to ensure valid purchases in future implementations. To ensure your safety we do not allow your card information to be saved or used on the site. The application is for paper trading ONLY at the moment for you to getting accustom to interacting with the future of trading and investment.
- Moving now onto Cash where you can add more money to your account to increase volume of trading.
- Located at the navbar, you'll find **Credit** which is the same link for validating your debit / credit card in _Settings_

***And there you have it. CryptxSpace! Very much in it's Beta form, but look forward to more interactable ETF's, graphs, times, features, and stats in the very nearing future. Thank you.***


