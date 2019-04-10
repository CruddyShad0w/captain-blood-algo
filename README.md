# captain-blood-algo
Heroku worker for Captain Blood's algorithm

## Setup
First you will need to set up a heroku app and install a few buildpacks.
Navigate to https://dashboard.heroku.com/apps and create a new application using the python buildpack.

Next set your environment variables in heroku.
Navigate to https://dashboard.heroku.com/apps

From there go to settings and Reveal Config Vars.
In this section you will set your base_url, key, and secret for alpaca.
use the string before the `=` for the KEY and the string after as the VALUE.
```sh
export APCA_API_BASE_URL=bbb
export APCA_API_KEY_ID=xxx
export APCA_API_SECRET_KEY=yyy
```
Now you can choose to deploy from the heroku tab.
Navigate to Deploy and link your github repo.
Choose to deploy from the master branch and click deploy.

After deployment navigate over to the Resources tab.
Here you will see a line that states 
`worker pylivetrader run -f algo.py` followed by a switch, dollar amount, and pen.
Click the pen and move the slider. Click confirm to activate the worker.

## Verify
You can verify the app is running by navigating to the logs in your dashboard. 
To do this click the More drop down and select logs.
You should see output similar to:
```
Apr 10 16:22:33 captain-blood-algo heroku/worker.1: Starting process with command `pylivetrader run -f algo.py` 
Apr 10 16:22:34 captain-blood-algo heroku/worker.1: State changed from starting to up 
Apr 10 16:22:42 captain-blood-algo app/worker.1: [2019-04-10 23:22:41.803070] INFO: Algorithm: livetrader start running with backend = alpaca data-frequency = minute 
```

You can also verify the logs through an ssh tunnel.
You will need the Heroku CLI at https://devcenter.heroku.com/articles/heroku-cli#download-and-install

launch a powershell and enter the following commands.
```
heroku login
heroku logs -a <app_name>
```
You will see a prompt 
```
heroku: Press any key to open up the browser to login or q to exit:
```
press any key besides q when prompted.

## Maintenance
All trading algorithms need routine maintenance.
Most algorithms need to run continuously without interruption to save variables accrued on the heap during its runtime.
We must make sure the algorithm is running cleanly to ensure we don't have to re-deploy (restart) the algorithm and lose the heap variables. 

After first trading day:
- verify successful run
- verify program did not exit

weekly:
- check for web_socket errors
- verify successful run
- verify program is trading at proper time intervals

