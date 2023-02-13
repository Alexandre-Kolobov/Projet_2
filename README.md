Project:
Use the python basics for market analysis

Project Description:
This program makes a scraping of a bookstore website and gets essential information.
Information is saved in /scraping_result as an CSV file and all cover images are saved in /scraping_result/img

How to install and run:
This document will help you to set up the virtual environment and to execute the program.

	1) To set up the virtual environment, please make sure that you have a python version higher that 3.3 (in prompt: python --version)
	because you need to have the pip installer.
	
	2)You have to create a folder ( /YOUR_FOLDER) and go in with the command line. In command line plese make "python -m venv venv"
	to create the virtual envrinment named "venv".
	
	3)To activate venv, via command line:
		For Windows: venv/Scripts/Activate.ps1 (with powershell) or go to /Scripts and do ". activate" (if you use bash)
		For Linux: venv/bin/activate
	
	
	4)Place your command line in /YOUR_FOLDER and Make "git init" and then "git clone https://github.com/Alexandre-Kolobov/Projet_2.git"
	
	5)Go to Projet_2 folder and make "pip install -r requirements.txt"
	
	6)Now you are ready to execute the program. In the commande line make "python books_scraping.py". Wait untill the end of execution (can take some minutes)
	
Attention:
Extracted files are removed on each execution, so if you need to keep it, please move it in another folder.