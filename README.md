# School Library System API Demo

## Introduction
This API is built using Graphene Django and exposes a single GraphQL endpoint for frontend apps to consume and query.
This API also implements JWT for handling of Authentication.

This API simulates a Library System which tracks the movement of borrowed books from students.

## How to Get Up & Running
To test this API out on your local environment, follow the steps below:

### 1. Create a python virtual environment
```
python -m venv school-lib
```

### 2. Activate the virtual env
cd into the directory that was created when we ran the last command and activate the virtual env.
```cd school-lib```
```source bin/activate```

### 3. Install requirements

We'll install all app dependancies in the requirements.txt file
*You may have noticed that we're using DJango 3.2. That's because some 3rd-party packages are still not updated to use Django >= 4.0, so we'll use Django 3.2 instead.*

```pip install -r requirements.txt```

### 4. Load some data for testing
Some test data has already been provided so we can use those straight out of the box for testing.
*If the test data is insufficient, you can always add more from the shell by running ```python manage.py shell```.*

In order to load the test data, run the command below in the terminal:
```python manage.py loaddata users_seed.json```
```python manage.py loaddata books_seed.json```

You should get the same two outputs as below:
```$ Installed 4 object(s) from 1 fixture(s)```

### 5. Start the development server
Start the development server by running ```python manage.py runserver```

### 6. Play around with the GraphQL API
Now we're ready for the fun stuff. We can start querying the GraphQL API by navigating to ```http://localhost:8000/graphql/```. This will open up the Graph*i*QL interface.

On the left hand-side of the screen will be where we'll type our GraphQL query, and the output will be displayed to us on the right=hand side of the screen.

*You might have also noticed the **Docs** tab on the upper right-hand corner of the screen. This is where all of the available API queries and mutations documentation lives. If you want to know more about what data you can actually query or mutate, click on the **Docs** tab and expand the types you want to look up.* 

Let's start with some queries. By the way, there are queries that can be performed without being authenticated, and then there are others which you need to be authenticated to perform the query. We'll start with the former.

#### Query all users
In order to query all the available users, copy the code below. Notice that we're only querying the fields we ask for. This is great for solving under-fetching or over-fetching issues.

```
query allUsers {
  users {
    edges {
      node {
        id
        username
        firstName
        lastName
        role
        isStaff
        isActive
        email
      }
    }
  }
}
```

Run the query by either hitting **Ctrl + Enter** on the keyboard or by clicking the **Play** icon on the top left corner of the Graph*i*QL interface. 
You should get a response something like this:

```
{
  "data": {
    "users": {
      "edges": [
        {
          "node": {
            "id": "VXNlck5vZGU6MQ==",
            "username": "student1",
            "firstName": "Matt",
            "lastName": "Bellamy",
            "role": "STUDENT",
            "isStaff": false,
            "isActive": true,
            "email": "matt.bellamy@example.com"
          }
        },
        {
          "node": {
            "id": "VXNlck5vZGU6Mg==",
            "username": "student2",
            "firstName": "Lisa",
            "lastName": "Goodward",
            "role": "STUDENT",
            "isStaff": false,
            "isActive": true,
            "email": "lisa.goodward@example.com"
          }
        },
        {
          "node": {
            "id": "VXNlck5vZGU6Mw==",
            "username": "student3",
            "firstName": "Tony",
            "lastName": "Streak",
            "role": "STUDENT",
            "isStaff": false,
            "isActive": true,
            "email": "tony.streak@example.com"
          }
        },
        {
          "node": {
            "id": "VXNlck5vZGU6NA==",
            "username": "librarian1",
            "firstName": "Misty",
            "lastName": "Paige",
            "role": "LIBRARIAN",
            "isStaff": true,
            "isActive": true,
            "email": "misty.page@example.com"
          }
        }
      ]
    }
  }
}
```

#### Query all available books
Now let's query some of the available books data that we've loaded from the previous steps:
```
query allBooks {
  books {
    edges {
      node {
        id
        name
        qty
        availableQty
        borrowedbookSet {
          edges {
            node {
              book {
                name
              }
              student {
                firstName
                lastName
              }
              borrowDate
              dueDate
              returnDate
              isRenewed
            }
          }
        }
      }
    }
  }
}
```
Run the query and you should get back the books data that we previously loaded as a result.

#### Perform protected actions
Ok, let's perform some protected actions which requires a user to be logged-in. We're going to start with the *Librarian* role.
In order to authenticate the user we'll use the *getAuthToken* mutation to obtain a JSON Web Token (JWT).

```
mutation logInAsLibrarian {
  tokenAuth(input: {username: "librarian1", password: "$Password123$"}) {
    token
  }
}
```

We should have received the token in our response (something like below although your token string will differ)
```
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InN0dWRlbnQxIiwiZXhwIjoxNjU4MzkxNTA0LCJvcmlnSWF0IjoxNjU4MzkxMjA0fQ.hyW1Vxrda5ac1WRWFBKkntyy9auwzU-lhwZjNVFAoZY"
    }
  }
}
```

##### Use the token in the *Request Headers*
Now that we have our JWT token we need to pass it into the *Request Headers* to perform protected actions. Luckily, Graph*i*QL now has a pane for us to insert this.
On the bottom left corner of the Graph*i*QL interface, click on the **REQUEST HEADERS** tab.

Paste in the following code and replace *<token>* with the JWT token obtained from the last step.

```
{
  "Authorization": "JWT <token>"
}
```

Whenever we want to perform a protected action, we must provde the JWT token in the Request Headers before running a query or mutation. 

##### Perform a mutation
Let's pretend a student wants to borrow a book. We'll run the *borrowBook* mutation to perform this action. Remember, the JWT token must be provided as explained in the last step. If not provided, the server will respond with an appropriate error.

```
mutation borrowABook {
  borrowBook(input: {
    bookId: 1,
    studentId: 1,
  }) {
    borrowedBook {
      student {
        firstName
        lastName
      }
      book {
        name
        qty
        availableQty
      }
      borrowDate
      dueDate
      returnDate
      isRenewed
    }
    success
  }
}
```

When you run this, you should get back a response of the student who borred the book, what book was borrowed, it's due date, as well as a success response.
*Run a few more **borrowBook** mutations (changing the bookId and studentId) to simulate multiple students borrowing multiple books.

##### Renew a borrowed book
To renew a borrowed book, simply add `renew: true` as one of the input arguments in the previous mutation.

```
mutation borrowABook {
  borrowBook(input: {
    bookId: 1,
    studentId: 1,
    renew: true
  }) {
    borrowedBook {
      student {
        firstName
        lastName
      }
      book {
        name
        qty
        availableQty
      }
      borrowDate
      dueDate
      returnDate
      isRenewed
    }
    success
  }
}
```

##### Return a borrowed book
Now let's say a student wants to return a borrowed book. All we need to do is run the `returnBook` mutation.

```
mutation returnABook {
  returnBook(input: {
    bookId: 1,
    studentId: 1
  }) {
    borrowedBook {
      book {
        name
        qty
        availableQty
      }
      student {
        firstName
        lastName
      }
      borrowDate
      dueDate
      returnDate
    }
    success
  }
}
```

Now the system has captured that the book has been returned and the available quantity of books that can be borrowed should have increased by 1.
*Try returning a few more books as we did with the `borrowBook` mutation.*

##### Switch roles
Ok, let's now log-in as a student so we can see the information of the books that we've borrowed.

```
mutation logInAsStudent {
  tokenAuth(input: {username: "student1", password: "$Password123$"}) {
    token
  }
}
```

Again, we'll copy the token returned by the response and insert it into our `Request Headers`.

```
{
  "Authorization": "JWT <token>"
}
```

Alright, now let's query the books that we've borrowed.

```
query myBorrowedBooks {
  myBooks {
    edges {
      node {
        book {
          name
        }
        borrowDate
        dueDate
        returnDate
        isRenewed
      }
    }
  }
}
```

You should now get a response depending on the number of times you've ran the `borrowBook` mutation for this student. Here's an example.

```
{
  "data": {
    "myBooks": {
      "edges": [
        {
          "node": {
            "book": {
              "name": "The Journey Into Computer Engineering"
            },
            "borrowDate": "2022-07-21T06:30:40.739867+00:00",
            "dueDate": "2022-08-20T06:30:40.739870+00:00",
            "returnDate": "2022-07-21T06:33:30.805485+00:00",
            "isRenewed": false
          }
        },
        {
          "node": {
            "book": {
              "name": "Physics for Dummies"
            },
            "borrowDate": "2022-07-21T06:33:37.309049+00:00",
            "dueDate": "2022-08-20T06:33:37.309052+00:00",
            "returnDate": "2022-07-21T06:33:40.044406+00:00",
            "isRenewed": false
          }
        },
        {
          "node": {
            "book": {
              "name": "The Chemistry Between Us"
            },
            "borrowDate": "2022-07-21T06:33:42.594380+00:00",
            "dueDate": "2022-08-20T06:33:42.594383+00:00",
            "returnDate": "2022-07-21T06:33:44.877904+00:00",
            "isRenewed": false
          }
        }
      ]
    }
  }
}
```