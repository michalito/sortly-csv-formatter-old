from flask import Flask, render_template, request, send_file, flash
import csv
from io import StringIO
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def transform_csv(input_csv, config):
    # Remove BOM if present
    if input_csv.startswith('\ufeff'):
        input_csv = input_csv[1:]

    # Detect the delimiter
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(input_csv[:1024])
    app.logger.info(f"Detected delimiter: {dialect.delimiter}")

    reader = csv.DictReader(StringIO(input_csv), dialect=dialect)
    input_rows = list(reader)
    
    if not input_rows:
        app.logger.error("The input CSV file is empty.")
        raise ValueError("The input CSV file is empty.")
    
    # Log column names for debugging
    app.logger.info(f"Input CSV columns: {reader.fieldnames}")
    
    # Check if required columns exist
    required_columns = ['Product SKU', 'Product Name', 'Stock', 'MPN', 'GTIN', 'Price', 'Status']
    missing_columns = [col for col in required_columns if col not in reader.fieldnames]
    
    if missing_columns:
        app.logger.error(f"Missing required columns: {', '.join(missing_columns)}")
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Group items by base SKU
    grouped_items = {}
    for row in input_rows:
        base_sku = row['Product SKU'].split('-')[0]
        if base_sku not in grouped_items:
            grouped_items[base_sku] = []
        grouped_items[base_sku].append(row)

    # Prepare output data
    output_rows = []
    for base_sku, items in grouped_items.items():
        main_item = items[0]
        for item in items[1:]:  # Skip the first item as it's the main one
            output_row = {
                'Entry Type': 'Item',
                'Entry Name': main_item['Product Name'],
                'Item Group Name': main_item['Product Name'],
                'Attribute 1 Name': 'Size',
                'Attribute 1 Option': extract_size(item['Product Name']),
                'Attribute 2 Name': 'Color',
                'Attribute 2 Option': 'Not Specified',
                'Quantity': item['Stock'],
                'Unit': 'Unit',
                'Min Level': config['min_level'],
                'Price': main_item['Price'].replace('€ ', ''),
                'Notes': item['Status'],
                'Tags': config['tags'],
                'Primary Folder': config['primary_folder'],
                'Subfolder-level1': config['subfolder_level1'],
                'Subfolder-level2': config['subfolder_level2'],
                'Serial Number': item['MPN'],
                'Barcode/QR2-Data': item['GTIN'],
                'Barcode/QR2-Type': 'org.iso.Code128'
            }
            output_rows.append(output_row)

    # Create output CSV
    output = StringIO()
    fieldnames = ['Entry Type', 'Entry Name', 'Item Group Name', 'Attribute 1 Name', 'Attribute 1 Option',
                  'Attribute 2 Name', 'Attribute 2 Option', 'Quantity', 'Unit', 'Min Level', 'Price',
                  'Notes', 'Tags', 'Primary Folder', 'Subfolder-level1', 'Subfolder-level2',
                  'Serial Number', 'Barcode/QR2-Data', 'Barcode/QR2-Type']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

    return output.getvalue()

def extract_size(name):
    if 'XSmall' in name:
        return 'XS'
    elif 'Small' in name:
        return 'SM'
    elif 'Medium' in name:
        return 'ME'
    elif 'Large' in name:
        return 'LA'
    elif 'X Large' in name:
        return 'XL'
    else:
        return 'OS'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        app.logger.info("POST request received")
        if 'file' not in request.files:
            app.logger.warning("No file part in the request")
            flash('No file part')
            return render_template('index.html')
        file = request.files['file']
        if file.filename == '':
            app.logger.warning("No selected file")
            flash('No selected file')
            return render_template('index.html')
        if file and file.filename.endswith('.csv'):
            try:
                app.logger.info(f"Processing file: {file.filename}")
                input_csv = file.read().decode('utf-8-sig')
                
                config = {
                    'min_level': request.form.get('min_level', '1'),
                    'tags': request.form.get('tags', 'Kallithea'),
                    'primary_folder': request.form.get('primary_folder', 'Apparel'),
                    'subfolder_level1': request.form.get('subfolder_level1', 'Socks'),
                    'subfolder_level2': request.form.get('subfolder_level2', 'Grip Socks'),
                }
                
                app.logger.debug(f"Configuration: {config}")
                transformed_csv = transform_csv(input_csv, config)
                
                # Save the transformed CSV
                with open('transformed_data.csv', 'w', newline='') as f:
                    f.write(transformed_csv)
                
                app.logger.info("File processed successfully")
                return send_file('transformed_data.csv', as_attachment=True)
            except Exception as e:
                app.logger.error(f"Error processing file: {str(e)}", exc_info=True)
                flash(f"Error processing file: {str(e)}")
                return render_template('index.html')
        else:
            app.logger.warning("Invalid file type")
            flash('Invalid file type. Please upload a CSV file.')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')