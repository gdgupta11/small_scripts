## small_scripts

These are some small scripts just to get some stuff done quickly or small automations which help us in day to day work

### Commit Password Store

Managing passwords is difficult and remembering different passwords for each website is even more difficult. There is free open source password managing utility available called pass for linux platforms.
It uses GPG keys to encrypt your passwords and keep safe. You also can create a private repository on github or bitbucket and
push you changes there so that you can sync passwords across different devices like andriod, Iphone and linux desktops. 

I have created a small script which downloads your remote password-store repo in /tmp/ compares the changes in your local repo and pushes it if there are changes. 

#### Changes needs to be done: 

1. Add your own working path
2. Add your own remote URL repo (Currently its clones using ssh, for that case you need to have your public keys added to the github)
3. Log file path

#### CRON Entry 

The main usage is with CRON, because now you can keep adding your passwords in pass store and need not worry about pushing them. 
Executing via cron can push it every 4 hours or what ever time you set. 
