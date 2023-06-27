# BusinessCard_Data_Extraction-

# Image Text Extraction and Database Upload

This is a Python program that allows you to extract text from images, upload the extracted information to a MySQL database, and retrieve and display images from the database.

## Prerequisites

Before running the program, ensure you have the following:

- Python 3.x installed on your system
- Required Python libraries: `re`, `easyocr`, `streamlit`, and `mysql.connector`
- A MySQL database with the necessary credentials

## Installation

1. Clone the repository or download the script to your local machine.

2. Install the required Python libraries using the following command:
   ```
   pip install re easyocr streamlit mysql-connector-python
   ```

## Usage

1. Set up the MySQL database with the correct credentials. Update the following lines in the script with your database details:

   ```python
   cnx = mysql.connector.connect(
       host="localhost",
       user="root",
       password="your_password",
       database="business_db"
   )
   ```

2. Execute the script using the following command:

   ```
   streamlit run your_script_name.py
   ```

3. The program will launch a Streamlit web application in your browser.

4. Use the "Upload an image" section to select an image file (PNG, JPG, or JPEG) for text extraction.

5. Once the text extraction is completed, the extracted information will be displayed in individual text input boxes.

6. Modify any information if required.

7. Click the "Upload to Database" button to upload the extracted information along with the image to the MySQL database.

8. To retrieve and display images from the database, use the "Image Retrieval" section and enter the ID of the image.

## Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - For providing an easy-to-use OCR library.
- [Streamlit](https://streamlit.io/) - For creating interactive web applications with Python.
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/) - For connecting to and interacting with MySQL databases.
