## Step 1

Create the scaffoldiong for a application, that uses python with fastapi for the back end, with a postgres database. The application will be a simple interval timer app, that allows customization of the various steps and timers. It also allows users to import and export timers.

For now, don't worry about adding features, simply scaffold thee back-end of the application. Use modern design principles and adhere to python coding guidelines.

Place the python back-end in a folder titled "i_timer"

Place any deployment files in a folder titled "deployment"

For the scaffolding:
- This app will be deployed via docker containers and a docker compose file. That is to say, postgres will be run in one container, the python back-end in another, and the front end (to be completed later) will be in a third container
- Create a basic test structure for the python back end
- The initial scaffold should be minimal, but should include basic fastapi endpoints for timers and import/export functionality. it should also include a simple authentication scaffold as user accounts will be a key part of the app
- include a .env file for basic configuration - keep this simple and adhere to general standards for maintanable docker apps when creating env variables.


## Step 2

Now we will create the scaffolding for the UI, try to touch the back-end code that we already created as little as possible. The front end will be in React. Note that I have 0 experience in React or web development in general, so try to keep things very simple, we can add complexiity later.

For the scaffolding:
- create a VERY simple front-end with 2 pages. Page 1 features a list of all timers. 
- when a timer is clicked, open the timer to reveal the steps, and have a "play button", a "pause button", and a "stop button"
- thee front end does not need to activate timers or anything yet, this is just to have a simple ui up and running.