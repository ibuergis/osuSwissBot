# Setup the bot
***
Here I will explain everything needed for the bot

## How to run
first clone the repository with:
```
git clone https://github.com/ibuergis/osuSwissBot.git
```

In the config folder there is config.sample.json. clone it and remove ".sample"

next Add in the values accordingly:
````json
{
  "botToken": "<The token from the bot youre using>",
  "firebase": "<firebase link>",
  "clientId": "<The client ID you that you can get from osu!>",
  "clientSecret": "<The client secret connected to the client ID>",
  "callbackPort": "3914 is the default"
}
````


### Setup firebase
Create a realtime Database. Copypase firebaseRuleset.json into the realtime Database ruleset.

In the config folder there is firebase.sample.json. clone it and remove ".sample".

Replace your firebase.json file with the firebase SDK you downloaded. it should have the same format.


### To get the client ID and secret.
go to your osu! user and click on settings. Scroll down until you find oAuth.
Then click on this.

![img.png](.github/readmeFiles/newoauthappication.png)

After that you can name your client after whatever you want.
The callback url is the localhost and the port you defined:
```
http://localhost:3914/
```

![img.png](.github/readmeFiles/clientDataPutInSmthIdk.png)

After you registered you can see the clientId and the client secret.

![img.png](.github/readmeFiles/clientIdAndSecret.png)


### Install dependencies

Go to the folder where the project is in and open terminal.

If you just want to run it use:
```
    pip install .
```

Lastly you can run it with:
```
    python main.py
```
