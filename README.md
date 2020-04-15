# Final Project

Setting up Flask:

"source ./flaskrunner.sh"

"flask run"

Pulling and Pushing to Git:

make sure you have pull from the github repository "git pull <url>"
            
git add .

git commit -m "[COMMIT MESSAGE]"

git push origin master



ENGO 551 Project 1
Sebastian Mcgonigle *[Student ID]*
Jeffrey Thompson 30021871

The project is contained in the following folders:

application.py - main python script handling the creation of the flask server, the contents of the webpages, and the interactions between the webpage and the SQL database

templates - a folder of .html files used alongside application.py to provide formats to the website

            layouts.html - base .html files that extends to all other files, providing formatting and styling specifications.

            index.html - The introductory webpage, handles logging in and registering to the website, as well as provides an Welcome page after logging in

            search.html - after entering a query into the searchbar, this page shows the results of the query, i.e. all books in the database matching the query

            book.html - after a book is selected from the search page, the book webpage opens to show information and reviews on the selected book, as well as providing space for a user to input their own review of the book

            error.html - The error page handled all situations that may have proved problematic for the nature of the script. It redirects to the welcome page.

HEROKU DATABASE: 

Host: ec2-3-223-21-106.compute-1.amazonaws.com

Database: dbl2cg6nng3q61

User: nrzfbmbyrfuiiv 

Port: 5432

Password:bcf70f112a5c78fda0451689f2228006e08b08f976780950d889a94fd2737e5b

URI: postgres://nrzfbmbyrfuiiv:bcf70f112a5c78fda0451689f2228006e08b08f976780950d889a94fd2737e5b@ec2-3-223-21-106.compute-1.amazonaws.com:5432/dbl2cg6nng3q61 

Heroku CLI: heroku pg:psql postgresql-encircled-05629 --app map-project-551 



