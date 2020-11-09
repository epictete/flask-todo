# Flask Todo App

<p align="center" margin-top="30">
  <img width="320" src="flask-logo.png" alt="Flask Logo">
</p>

### Project

This is my first full stack Python (Flask) app :tada:  
It is a simple todo list manager based on a time management technique called [The Eisenhower Method](https://en.wikipedia.org/wiki/Time_management#The_Eisenhower_Method) :memo:  

The app will keep track of all your todos and organize them based on the 2 axis of the method's matrix :
-   Important
-   Urgent  

You will optionally be able to set a due date.
In that case, the app will automatically flag as "urgent" every todo that is due in a day or less.  

It will behave similarly with items that are overdue, by adding the "important" flag  as well as highlighting the due date, so you can deal with these in priority.  

There is a sort button on top of each column and the lists are sorted by creation date by default.  

The history section keeps track of all the tasks that are either done or deleted, and allows you to restore elements if needed.
You can also clear the history if it gets too long.  

The user section allows you to change your password, reset your todo list and delete your account. 

Feel free to leave a comment! 
Tips and suggestions are more than welcome, the goal is to learn and improve :rocket:

### Features

-   Frontend with HTML5 and [Bootstrap](https://getbootstrap.com/)
-   Backend with [Python](https://www.python.org/) using the [Flask](https://flask.palletsprojects.com/en/1.1.x/) microframework
-   [SQLite](https://sqlite.org/index.html) database using the [SQLAlchemy](https://www.sqlalchemy.org/) ORM
-   Password hashing using [Werkzeug Security Helpers](https://werkzeug.palletsprojects.com/en/1.0.x/utils/#module-werkzeug.security)
-   Use of the built-in [Login Required Decorator](https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/) to protect the routes
-   Hosting on [Heroku](https://www.heroku.com/home)

### Link

If you'd like, you can [try it here](http://todo-matrix.herokuapp.com/)
