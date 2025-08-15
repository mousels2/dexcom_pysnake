# dexcom_pysnake
Simple python script, incorporating pygame elements, and username/password storage in external .env file. Requires live Dexcom Account that receives readings.

# Script Features
Displays current BM reading, and refreshes every 5 min. Prints the readings to the console, and to the bottom of the pygame screen. Projects a line graph behind the current reading. The line graph and displayed readings are colour coded, green for OK, red for high/low, grey for no readings.

# Readings
Readings are presented in mmol/l

# Before using this script
Ensure that the .env file is updated with your dexcom login details.
Ensure the required python libaries are installed (see requirements.txt).
Update the region in the code (see below).

# Account Username/Password
Your username and password is stored inside the .env file. Ensure this is updated before using the script.

# Region Select
The script will not work if the incorrect region is set in the code.

Update the region (line 190) to match your region:
  USA - "us".
  Japan - "jp".
  Everywhere else - "ous".

# Running the script
In your console, type: py bm_dexcom.py

# Ending the script
Press ESC within the pygame window to close the script, or use the CTRL+C command in the console.

# Args
-t or -test: Run the script using a short series of simulated readings.
