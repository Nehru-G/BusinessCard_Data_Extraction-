import re
import easyocr
import streamlit as st
import mysql.connector
from PIL import Image
import base64
from io import BytesIO

# Create a MySQL connection
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@7890sql",
    database="business_db"
)
cursor = cnx.cursor()

def extract_information(image_path):
    # Extract text from image using EasyOCR
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(image_path)
    extracted_text = ''
    for result in results:
        extracted_text += result[1] + ' '

    # Extract card_holder name
    card_holder_name = extracted_text.split()[0]
    extracted_text = re.sub(card_holder_name, '', extracted_text)

    # Extract designation
    designation_pattern = r'\b(CEO|FOUNDER|Technical|General|Data|Chief Executive Officer|President|Managing Director|Owner|Partner|Vice|President|Director|Manager|Supervisor|Team|Leader|Department|Head|Sales|Account|Executive|Business|Development|Marketing|Sales|Representative|Brand)\b'
    designation_matches = re.findall(designation_pattern, extracted_text, re.IGNORECASE)
    designation_parts = ["".join(designation_match).strip() for designation_match in designation_matches]
    designation = " ".join(designation_parts)
    for designations in designation_parts:
        extracted_text = re.sub(re.escape(designations), '', extracted_text, flags=re.IGNORECASE)

    # Extract phone numbers
    phone_pattern = r"\+?\d{3}-?\d{3}-?\d{4}"
    matches = re.findall(phone_pattern, extracted_text)
    if matches:
        if len(matches) >= 2:
            mobile_number1 = matches[0]
            extracted_text = re.sub(re.escape(mobile_number1), '', extracted_text)
            mobile_number2 = matches[1]
            extracted_text = re.sub(re.escape(mobile_number2), '', extracted_text)
        else:
            mobile_number1 = matches[0]
            extracted_text = re.sub(re.escape(mobile_number1), '', extracted_text)
            mobile_number2 = None
    else:
        mobile_number1 = "check the number"
        mobile_number2 = "check the number"

    # Extract email address
    email_pattern = r'\b([A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+\.[A-Za-z]{2,6})\b'
    email_matches = re.findall(email_pattern, extracted_text)
    email_addresses = ' '.join(email_matches)
    extracted_text = re.sub(email_addresses, '', extracted_text)

    # Extract website URL
    website_url_pattern = r'(?<!\S)(?:WWW\s)?([a-zA-Z0-9_.-]+\.[a-zA-Z]{2,6}|xn--[a-zA-Z0-9]+)\b'
    matched_website_url = re.findall(website_url_pattern, extracted_text)
    website_url = ' '.join(matched_website_url)
    extracted_text = re.sub(website_url, '', extracted_text)

    pattern = r'www'
    matches = re.findall(pattern, extracted_text, re.IGNORECASE)
    match = ' '.join(matches)
    extracted_text = re.sub(match, '', extracted_text)

    # Extract state
    state_names = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
                   "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
                   "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
                   "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
    # Create the pattern dynamically using the state names
    state_pattern = r"\b(" + "|".join([name.replace(" ", r"\s*") for name in state_names]) + r")\b"
    state_matches = re.findall(state_pattern, extracted_text, flags=re.IGNORECASE)
    state = ' '.join(state_matches)
    extracted_text = re.sub(state, '', extracted_text)

    # Extract Pincode
    pincode_pattern = r'\b\d{5,7}\b'
    pincode_matches = re.findall(pincode_pattern, extracted_text)
    if pincode_matches:
        if len(pincode_matches[0]) != 6:
            pin_code = f"pincode is not in correct format '{pincode_matches[0]}'"
            extracted_text = re.sub(pincode_matches[0], '', extracted_text)
        else:
            pin_code = pincode_matches[0]
            extracted_text = re.sub(pin_code, '', extracted_text)
    else:
        pin_code = None

    # Extract address information
    address_pattern = r'\b\d{1,3}+\s+[A-Za-z]+\s+|(?:St|street)\b'
    address_matches = re.findall(address_pattern, extracted_text)
    address_parts = ["".join(address_match).strip() for address_match in address_matches]
    address = " ".join(address_parts)
    for addres in address_parts:
        extracted_text = re.sub(re.escape(addres), '', extracted_text, flags=re.IGNORECASE)

    # Extract city
    city_pattern = r"[A-Z][a-zA-Z\s]+(?=,|;)"
    city_match = re.search(city_pattern, extracted_text)
    if city_match:
        city = city_match.group()
    else:
        city = ""
    extracted_text = re.sub(city, '', extracted_text)

    # Extract company name
    extracted_text = re.sub(r'[^a-zA-Z\s]', '', extracted_text)
    extracted_text = re.sub(r'\s+', ' ', extracted_text)
    company_name = extracted_text.strip()

    return card_holder_name, designation, company_name, mobile_number1, mobile_number2, email_addresses, website_url, address, city, state, pin_code

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS card_information (
        id INT AUTO_INCREMENT PRIMARY KEY,
        image LONGBLOB NOT NULL,
        card_holder_name VARCHAR(255),
        designation VARCHAR(255),
        company_name VARCHAR(255),
        mobile_number1 VARCHAR(15),
        mobile_number2 VARCHAR(15),
        email_addresses VARCHAR(255),
        website_url VARCHAR(255),
        address VARCHAR(255),
        city VARCHAR(255),
        state VARCHAR(255),
        pin_code VARCHAR(10)
    )
    """
    cursor.execute(create_table_query)

def upload_to_database(image, card_holder_name, designation, company_name, mobile_number1, mobile_number2, email_addresses, website_url, address, city, state, pin_code):
    insert_query = """
    INSERT INTO card_information (image, card_holder_name, designation, company_name, mobile_number1, mobile_number2, email_addresses, website_url, address, city, state, pin_code)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (image, card_holder_name, designation, company_name, mobile_number1, mobile_number2, email_addresses, website_url, address, city, state, pin_code)
    cursor.execute(insert_query, data)
    cnx.commit()

def retrieve_image(image_id):
    query = "SELECT image FROM card_information WHERE id = %s"
    cursor.execute(query, (image_id,))
    result = cursor.fetchone()

    if result is not None:
        image_data = result[0]
        return image_data
    else:
        return None

def main():
    st.title("Image Text Extraction and Database Upload")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image_path = "./temp_image.png"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        with open(image_path, "rb") as f:
            encoded_image = f.read()
        card_holder_name, designation, company_name, mobile_number1, mobile_number2, email_addresses, website_url, address, city, state, pin_code = extract_information(
            image_path)
        st.success("Text extraction completed.")

        # Display the extracted information in individual text boxes
        st.subheader("Extracted Information")
        card_holder = st.text_input("Card Holder Name", value=card_holder_name)
        designation = st.text_input("Designation", value=designation)
        company = st.text_input("Company Name", value=company_name)
        mobile_1= st.text_input("Mobile Number 1", value=mobile_number1)
        mobile_2 = st.text_input("Mobile Number 2", value=mobile_number2)
        email = st.text_input("Email Addresses", value=email_addresses)
        url = st.text_input("Website URL", value=website_url)
        address = st.text_input("Address", value=address)
        city = st.text_input("City", value=city)
        state = st.text_input("State", value=state)
        pincode = st.text_input("Pincode", value=pin_code)

        if st.button("Upload to Database"):
            upload_to_database(encoded_image, card_holder, designation, company, mobile_1, mobile_2, email, url,
                               address, city, state, pincode)
            st.success("Data uploaded to the database.")

def image_retrival():
    st.title("Image Retrieval")
    image_id = st.number_input("Enter the ID of the image", min_value=1, value=1, step=1)
    if st.button("Retrieve Image"):
        image = retrieve_image(image_id)

        if image is not None:
            st.image(image, caption="Retrieved Image", use_column_width=True)
        else:
            st.warning("Image not found in the database.")


if __name__ == "__main__":
    create_table()
    main()
    image_retrival()