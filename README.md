# Python-I-Final-Project
Final Project

requirements.txt - packages required to run TravelStarterKit.py

Enter the following command to install require packages
	pip3 install -r requirements.txt

To run TravelStarterKit.py open a terminal window and go to directory where file is located. Enter the following command
	python3 TravelStarterKit.py

You will be prompted to enter the following
	Enter destination city: <input city>
	Enter destination country: <input country>
	Enter home IATA airport code: <input airport code>
	Enter number of days for trip: <input number of days>
	Enter file type for travel report (csv,html,json): <input file type>

TravelStartKit.py will begin executing and will output
	Searching for best months to travel to <city>, <country>...	Complete!
	Collecting avg hi and low temperatures for best months to travel to <city>, <country>...	Complete!
	Opening google flights for best months with available flight prices to <city>, <country>...	Complete!
	Generating travel report...	Complete!