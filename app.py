from flask import Flask, render_template, request
import pandas as pd
import joblib
import folium
import json

app = Flask(__name__)

# Load model
model = joblib.load('model_new_file.pkl')

print('model',model)

# Load crop dataset (fixing potential issues)
try:
    crop_df = pd.read_csv('final_clean_crop.csv')

    # Clean column names
    crop_df.columns = crop_df.columns.str.strip()

    # Debug: Print column names to terminal
    print("Available columns in dataset:", crop_df.columns.tolist())

    # Optionally rename if needed
    if 'Crop Name' in crop_df.columns and 'Crop' not in crop_df.columns:
        crop_df.rename(columns={'Crop Name': 'Crop'}, inplace=True)

except Exception as e:
    print("Error reading crop dataset:", e)
    crop_df = pd.DataFrame()  # empty to avoid further errors

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Step 1: Collect input
    input_data = {
        'Nitrogen___High': int(request.form['n_high']),
        'Nitrogen_Medium': int(request.form['n_med']),
        'Nitrogen_Low': int(request.form['n_low']),
        'Phosphorous_High': int(request.form['p_high']),
        'Phosphorous_Medium': int(request.form['p_med']),
        'Phosphorous_Low': int(request.form['p_low']),
        'Potassium_High': int(request.form['k_high']),
        'Potassium_Medium': int(request.form['k_med']),
        'Potassium_Low': int(request.form['k_low']),
        'OC_High': int(request.form['oc_high']),
        'OC_Medium': int(request.form['oc_med']),
        'OC_Low': int(request.form['oc_low']),
        'EC_Saline': int(request.form['ec_saline']),
        'EC__Non_Saline': int(request.form['ec_nonsaline']),
        'pH_Acidic': int(request.form['ph_acidic']),
        'pH_Neutral': int(request.form['ph_neutral']),
        'pH_Alkaline': int(request.form['ph_alkaline'])
    }

    df = pd.DataFrame([input_data])
    print('dfdfdf',df)

    # Step 2: Predict crop
    prediction = model.predict(df)[0]
    print('prediction',prediction)

    # Step 3: Filter dataset for districts with this crop
    if 'Crop' in crop_df.columns:
        filtered_df = crop_df[crop_df['Crop'].str.lower() == prediction.lower()]
        district_list = filtered_df['District'].unique() if 'District' in filtered_df.columns else ["District data not found"]
    else:
        filtered_df = pd.DataFrame()
        district_list = ["Crop column missing in dataset"]

    # Step 4: Create a Folium map
    m = folium.Map(location=[22.9734, 78.6569], zoom_start=5)

    popup_text = "<b>Districts suitable for {}:</b><br>{}".format(
        prediction, "<br>".join(district_list)
    )
    folium.Marker(
        location=[22.9734, 78.6569],
        popup=popup_text,
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(m)

    map_html = m._repr_html_()

    return render_template('index.html', prediction=prediction, map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
