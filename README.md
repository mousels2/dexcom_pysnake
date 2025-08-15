# dexcom_pysnake
Simple python script, incorporating pygame elements, and username/password storage in external .env file. Requires live Dexcom Account that receives readings.

**#Before using this script**
Ensure that the .env file is updated with your dexcom login details
Ensure the required python libaries are installed (see requirements.txt)
Update the region in the code (see below)

**Region Update**
The script will not work if the incorrect region is set in the code.

Update the region (line 187) to match your region:
  USA - "us"
  Japan - "jp"
  Everywhere else - "ous"
