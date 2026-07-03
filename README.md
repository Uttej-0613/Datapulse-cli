 DataPulse - Data Validation & ML CLI

**DataPulse** is a lightweight CLI tool that validates messy CSV data and trains a Linear Regression model to predict salaries based on age.

 Features
-  Validates CSV rows (age must be > 0, salary must be >= 0)
-  Automatically filters out invalid rows
-  Trains a Scikit-Learn Linear Regression model
-  Saves trained model as `salary_predictor.pkl`
-  Achieves R² score of ~0.998 on test data

 Installation
bash
git clone https://github.com/Uttej-0613/Datapulse-cli.git
cd Datapulse-cli
pip install -e .
