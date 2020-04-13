# Project 1

ENGO 551 Project 1
Jeffrey Thompson 30021871

The project is contained in the following folders:

import.py - python script written to upload the book data from the provided books.csv into the SQL database

application.py - main python script handling the creation of the flask server, the contents of the webpages, and the interactions between the webpage and the SQL database

templates - a folder of .html files used alongside application.py to provide formats to the website

layouts.html - base .html files that extends to all other files, providing formatting and styling specifications.

index.html - The introductory webpage, handles logging in and registering to the website, as well as provides an Welcome page after logging in

search.html - after entering a query into the searchbar, this page shows the results of the query, i.e. all books in the database matching the query

book.html - after a book is selected from the search page, the book webpage opens to show information and reviews on the selected book, as well as providing space for a user to input their own review of the book

error.html - The error page handled all situations that may have proved problematic for the nature of the script. It redirects to the welcome page.

Database Information:
Host        ec2-3-234-109-123.compute-1.amazonaws.com
Database    dcg1phll5jsck3
User        yxglmjgpfdpdds
Port        5432
Password    29d1c599fdb113d5d001ac58da80cd32ffd8870cc98ed67d6
            3d0df1bc9185f60
URI         postgres://     yxglmjgpfdpdds:29d1c599fdb113d5d001ac58da80cd32ffd8870cc98ed67d63d0df1bc9185f60@ec2-3-234-109-123.compute-1.amazonaws.com:5432/dcg1phll5jsck3
Heroku CLI  heroku pg:psql postgresql-graceful-07672 --app engo551lab1jeff

GoodReads Information:
key: 9LYdPW0XgC6gZkiQV8Aevg
secret: AGvPxtEfnjWsPXaBQHPMHrPag2cNGMKFyowZ11xjYU


The REQUIREMENTS section of the Project description was completed, the basic components of which are detailed below:

1. Registration: At the login page, users can register a new account by inputting their email, username, and password. All boxes must be filled, otherwise you will be redirected to the error page. The username must be unique, otherwise the webpage will show an error. The password must be confirmed, otherwise an error will show. Once acceptable information ha been input into the webpage, a new database entry will be created for the new user and they will be automatically logged in, setting the session['user'] and session['user_id'] values appropriately.

2. Login: At the login page, users can input existing login information (username and password) to access the website. If either field is left empty, an error page will show. If the username and password do not correspond to an entry in the database, an error message will show. Once valid credentials have been input, the user will be taken to the rest of the website, setting the session['user'] and session['user_id'] values appropriately.

3. Logout: Every non-error page has a "logout" button at the bottom. This wipes the session['user'] and session['user_id']  values and redirects the user to the login page.

4. Import: As described above, import.py uploaded the values from books.csv into the SQL database.

5. Search: A search bar was included in index.html and search.html. The bar contains space to input information pertaining to a book's ISBN, Title, and/or Author. When activated, a query is performed using the contents of the three search bars simultaneously in LIKE '%__%' queries to find any entries in the books Table containing all entered information.
**Note the search queries are currently case-sensitive, this has not been corrected for.

6. Once selected, the Book Page used the database 'books' Table to show the ISBN, title, author, and publication year of the book. The 'reviews' table is also queried to display any reviews pertaining to this books created on the website

7. At the bottom of books.html, the user is provided room to give a review of the book in question. Both the rating and comments section must be filled in or an error page comes up. If a user tries to give a second review of the same book, the database entry corresponding to their user_id for that book is instead updated to reflect the contents of the new review.

8. The app.route for books.html sends a request to GoodReads using the above API key to display the number of ratings and average rating for the books as seen on the GoodReads website. This is from the json object book.review_counts

9. An API route was created to correspond to every book in the database. It uses the book's ISBN code to query both the 'books' Table and Goodreads to compile a json object containing the book's ISBN, Title, Author, Publication Year, Number of GoodReads Ratings, and Average GoodRead Rating.

