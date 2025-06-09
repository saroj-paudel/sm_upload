from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.image as img
import random
app = Flask(__name__)

app.secret_key = 'keepItSecrete'  # Required for sessions


# Translations
TRANSLATIONS = {
    'en': {
        'title': 'SmartKishan',
        'subtitle': 'AI-Powered Plant Disease Detection System',
        'description': 'Upload an image of your plant to detect diseases and get treatment recommendations',
        'select_category': 'Select Plant Category',
        'detect_diseases': 'Detect Diseases',
        'how_it_works': 'How It Works',
        'upload_image': '1. Upload Image',
        'upload_desc': 'Take a clear photo of the affected plant part and upload it',
        'ai_analysis': '2. AI Analysis',
        'ai_desc': 'Our AI models analyze the image to detect diseases',
        'get_treatment': '3. Get Treatment',
        'treatment_desc': 'Receive detailed treatment recommendations and care tips',
        'home': 'Home',
        'contribute': 'Contribute',
        'ai_chat': 'AI Chat',
        'plants': 'Plants',
        'about': 'About',
        'footer_text': 'Empowering farmers with AI-powered disease detection.',
        'language': 'Language',
        'disease_detection': 'Disease Detection',
        'upload_plant_image': 'Upload Plant Image',
        'supported_formats': 'Supported formats: JPG, PNG, GIF (Max: 16MB)',
        'analyze_image': 'Analyze Image',
        'soil_crops': 'Soil Crops',
        'soil_crops_desc': 'Crops that grow in soil like tomato, potato, etc.',
        'tree_fruits': 'Tree Fruits',
        'tree_fruits_desc': 'Fruits that grow on trees like apple, citrus, etc.',
        'leafy_vegetables': 'Leafy Vegetables',
        'leafy_vegetables_desc': 'Leafy crops like lettuce, spinach, etc.',
        'cereals': 'Cereals',
        'cereals_desc': 'Grain crops like wheat, rice, corn, etc.',

        # About page translations
        'about_title': 'About SmartKishan',
        'about_mission': 'Our Mission',
        'about_mission_text': 'To empower farmers worldwide with AI-powered plant disease detection technology, helping improve crop yields and food security.',
        'about_technology': 'Technology',
        'about_technology_text': 'We use advanced machine learning models trained on thousands of plant images to accurately identify diseases and provide treatment recommendations.',
        'about_team': 'Our Team',
        'about_team_text': 'A dedicated team of agricultural experts, data scientists, and software engineers working together to revolutionize farming practices.',

        # Contribute page translations
        'contribute_title': 'Contribute to SmartKishan',
        'contribute_description': 'Help us improve our disease detection system by contributing your plant images',
        'contribute_why': 'Why Contribute?',
        'contribute_why_text': 'Your contributions help train our AI models to become more accurate and comprehensive.',
        'contribute_guidelines': 'Contribution Guidelines',
        'contribute_guideline_1': '• Take clear, high-quality photos',
        'contribute_guideline_2': '• Include multiple angles of the affected area',
        'contribute_guideline_3': '• Provide accurate disease identification',
        'contribute_guideline_4': '• Add detailed notes about symptoms',
        'plant_category': 'Plant Category',
        'disease_name': 'Disease Name',
        'contributor_name': 'Your Name (Optional)',
        'additional_notes': 'Additional Notes',
        'submit_contribution': 'Submit Contribution',
        'select_plant_category': 'Select plant category',
        'enter_disease_name': 'Enter the disease name',
        'enter_your_name': 'Enter your name',
        'additional_notes_placeholder': 'Any additional information about the plant condition, symptoms, etc.',
        'required_field': 'Required field',
        'be_specific': 'Be as specific as possible (e.g., "Early Blight", "Powdery Mildew")',

        # Chat page translations
        'chat_title': 'AI Agricultural Assistant',
        'chat_description': 'Ask questions about plant diseases, treatment, and farming practices',
        'ask_question': 'Ask a question...',
        'send': 'Send',
        'coming_soon': 'Coming Soon',
        'feature_development': 'This feature is currently under development. Check back soon!',

        # Category page translations
        'back_to_categories': 'Back to Categories',
        'drag_drop': 'Drag and drop your image here or click to browse',
        'file_selected': 'File selected:',
        'analyzing': 'Analyzing...',
        'analysis_results': 'Analysis Results',
        'detected_disease': 'Detected Disease',
        'confidence': 'Confidence',
        'severity': 'Severity',
        'treatment_recommendations': 'Treatment Recommendations',
        'try_another': 'Try Another Image',
        'image_preview': 'Image Preview',

        # Disease names
        'Early Blight': 'Early Blight',
        'Late Blight': 'Late Blight',
        'Leaf Mold': 'Leaf Mold',
        'Bacterial Spot': 'Bacterial Spot',
        'Apple Scab': 'Apple Scab',
        'Fire Blight': 'Fire Blight',
        'Citrus Canker': 'Citrus Canker',
        'Brown Rot': 'Brown Rot',
        'Downy Mildew': 'Downy Mildew',
        'Powdery Mildew': 'Powdery Mildew',
        'Bacterial Leaf Spot': 'Bacterial Leaf Spot',
        'Rust': 'Rust',
        'Smut': 'Smut',
        'Blight': 'Blight',
        'Leaf Spot': 'Leaf Spot',

        # Severity levels
        'Mild': 'Mild',
        'Moderate': 'Moderate',
        'Severe': 'Severe'
    },
    'ne': {
        'title': 'स्मार्टकिशान',
        'subtitle': 'कृत्रिम बुद्धिमत्ता द्वारा बिरुवाको रोग पहिचान प्रणाली',
        'description': 'आफ्नो बिरुवाको तस्विर अपलोड गर्नुहोस् र रोग पहिचान गरी उपचारका सुझावहरू पाउनुहोस्',
        'select_category': 'बिरुवाको श्रेणी छान्नुहोस्',
        'detect_diseases': 'रोग पहिचान गर्नुहोस्',
        'how_it_works': 'यो कसरी काम गर्छ',
        'upload_image': '१. तस्विर अपलोड गर्नुहोस्',
        'upload_desc': 'प्रभावित बिरुवाको भागको स्पष्ट तस्विर खिच्नुहोस् र अपलोड गर्नुहोस्',
        'ai_analysis': '२. कृत्रिम बुद्धिमत्ता विश्लेषण',
        'ai_desc': 'हाम्रो कृत्रिम बुद्धिमत्ता मोडेलले तस्विरको विश्लेषण गरी रोग पहिचान गर्छ',
        'get_treatment': '३. उपचार पाउनुहोस्',
        'treatment_desc': 'विस्तृत उपचार सिफारिस र हेरचाहका सुझावहरू प्राप्त गर्नुहोस्',
        'home': 'घर',
        'contribute': 'योगदान',
        'ai_chat': 'कृत्रिम बुद्धिमत्ता च्याट',
        'plants': 'बिरुवाहरू',
        'about': 'बारेमा',
        'footer_text': 'कृत्रिम बुद्धिमत्ता संचालित रोग पहिचानको साथ किसानहरूलाई सशक्त बनाउँदै।',
        'language': 'भाषा',
        'disease_detection': 'रोग पहिचान',
        'upload_plant_image': 'बिरुवाको तस्विर अपलोड गर्नुहोस्',
        'supported_formats': 'समर्थित ढाँचाहरू: JPG, PNG, GIF (अधिकतम: १६MB)',
        'analyze_image': 'तस्विर विश्लेषण गर्नुहोस्',
        'soil_crops': 'माटोका बालीहरू',
        'soil_crops_desc': 'माटोमा उम्रने बालीहरू जस्तै गोलभेडा, आलु, आदि।',
        'tree_fruits': 'रुखका फलफूलहरू',
        'tree_fruits_desc': 'रुखमा फल्ने फलफूलहरू जस्तै स्याउ, सुन्तला, आदि।',
        'leafy_vegetables': 'पातेदार तरकारीहरू',
        'leafy_vegetables_desc': 'पातेदार बालीहरू जस्तै सलाद, पालुंगो, आदि।',
        'cereals': 'अनाजहरू',
        'cereals_desc': 'अनाजका बालीहरू जस्तै गहुँ, चामल, मकै, आदि।',

        # About page translations
        'about_title': 'स्मार्टकिशानको बारेमा',
        'about_mission': 'हाम्रो मिशन',
        'about_mission_text': 'कृत्रिम बुद्धिमत्ता संचालित बिरुवा रोग पहिचान प्रविधिको साथ विश्वभरका किसानहरूलाई सशक्त बनाउनु, बाली उत्पादन र खाद्य सुरक्षा सुधार गर्न मद्दत गर्नु।',
        'about_technology': 'प्रविधि',
        'about_technology_text': 'हामी रोगहरूलाई सही रूपमा पहिचान गर्न र उपचार सिफारिसहरू प्रदान गर्न हजारौं बिरुवाका तस्विरहरूमा प्रशिक्षित उन्नत मेसिन लर्निङ मोडेलहरू प्रयोग गर्छौं।',
        'about_team': 'हाम्रो टिम',
        'about_team_text': 'कृषि विशेषज्ञहरू, डेटा वैज्ञानिकहरू, र सफ्टवेयर इन्जिनियरहरूको समर्पित टिम जसले कृषि अभ्यासहरूमा क्रान्ति ल्याउन सँगै काम गर्छ।',

        # Contribute page translations
        'contribute_title': 'स्मार्टकिशानमा योगदान गर्नुहोस्',
        'contribute_description': 'तपाईंका बिरुवाका तस्विरहरू योगदान गरेर हाम्रो रोग पहिचान प्रणाली सुधार गर्न मद्दत गर्नुहोस्',
        'contribute_why': 'किन योगदान गर्ने?',
        'contribute_why_text': 'तपाईंका योगदानहरूले हाम्रो कृत्रिम बुद्धिमत्ता मोडेलहरूलाई अझ सटीक र व्यापक बनाउन मद्दत गर्छ।',
        'contribute_guidelines': 'योगदानका दिशानिर्देशहरू',
        'contribute_guideline_1': '• स्पष्ट, उच्च गुणस्तरका तस्विरहरू खिच्नुहोस्',
        'contribute_guideline_2': '• प्रभावित क्षेत्रका धेरै कोणहरू समावेश गर्नुहोस्',
        'contribute_guideline_3': '• सही रोग पहिचान प्रदान गर्नुहोस्',
        'contribute_guideline_4': '• लक्षणहरूका बारेमा विस्तृत टिप्पणीहरू थप्नुहोस्',
        'plant_category': 'बिरुवाको श्रेणी',
        'disease_name': 'रोगको नाम',
        'contributor_name': 'तपाईंको नाम (वैकल्पिक)',
        'additional_notes': 'थप टिप्पणीहरू',
        'submit_contribution': 'योगदान पेश गर्नुहोस्',
        'select_plant_category': 'बिरुवाको श्रेणी चयन गर्नुहोस्',
        'enter_disease_name': 'रोगको नाम प्रविष्ट गर्नुहोस्',
        'enter_your_name': 'तपाईंको नाम प्रविष्ट गर्नुहोस्',
        'additional_notes_placeholder': 'बिरुवाको अवस्था, लक्षणहरू, आदिका बारेमा कुनै थप जानकारी।',
        'required_field': 'आवश्यक क्षेत्र',
        'be_specific': 'यथासम्भव विशिष्ट हुनुहोस् (जस्तै, "प्रारम्भिक झुलसाउने", "पाउडरी फफूंदी")',

        # Chat page translations
        'chat_title': 'कृत्रिम बुद्धिमत्ता कृषि सहायक',
        'chat_description': 'बिरुवाका रोगहरू, उपचार, र कृषि अभ्यासहरूका बारेमा प्रश्नहरू सोध्नुहोस्',
        'ask_question': 'प्रश्न सोध्नुहोस्...',
        'send': 'पठाउनुहोस्',
        'coming_soon': 'छिट्टै आउँदै',
        'feature_development': 'यो सुविधा हाल विकासाधीन छ। छिट्टै फिर्ता जाँच गर्नुहोस्!',

        # Category page translations
        'back_to_categories': 'श्रेणीहरूमा फिर्ता',
        'drag_drop': 'तपाईंको तस्विर यहाँ तान्नुहोस् र छोड्नुहोस् वा ब्राउज गर्न क्लिक गर्नुहोस्',
        'file_selected': 'फाइल चयन गरिएको:',
        'analyzing': 'विश्लेषण गर्दै...',
        'analysis_results': 'विश्लेषण परिणामहरू',
        'detected_disease': 'पत्ता लगाइएको रोग',
        'confidence': 'विश्वास',
        'severity': 'गम्भीरता',
        'treatment_recommendations': 'उपचार सिफारिसहरू',
        'try_another': 'अर्को तस्विर प्रयास गर्नुहोस्',
        'image_preview': 'Image Preview',

        # Disease names in Nepali
        'Early Blight': 'प्रारम्भिक झुलसाउने',
        'Late Blight': 'ढिलो झुलसाउने',
        'Leaf Mold': 'पातको ढुसी',
        'Bacterial Spot': 'ब्याक्टेरियल दाग',
        'Apple Scab': 'स्याउको खुर्चो',
        'Fire Blight': 'आगो झुलसाउने',
        'Citrus Canker': 'सुन्तलाको क्यान्कर',
        'Brown Rot': 'खैरो सड्ने',
        'Downy Mildew': 'डाउनी फफूंदी',
        'Powdery Mildew': 'पाउडरी फफूंदी',
        'Bacterial Leaf Spot': 'ब्याक्टेरियल पातको दाग',
        'Rust': 'खिया',
        'Smut': 'कालो धूलो',
        'Blight': 'झुलसाउने',
        'Leaf Spot': 'पातको दाग',

        # Severity levels in Nepali
        'Mild': 'हल्का',
        'Moderate': 'मध्यम',
        'Severe': 'गम्भीर'
    }
}

def get_language():
    return session.get('language', 'en')

def get_translation(key):
    lang = get_language()
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))

# Plant categories and their models
PLANT_CATEGORIES = {
    'soil_crops': {
        'name_key': 'soil_crops',
        'desc_key': 'soil_crops_desc',
        'diseases': ['Early Blight', 'Late Blight', 'Leaf Mold', 'Bacterial Spot']
    },
    'tree_fruits': {
        'name_key': 'tree_fruits',
        'desc_key': 'tree_fruits_desc',
        'diseases': ['Apple Scab', 'Fire Blight', 'Citrus Canker', 'Brown Rot']
    },
    'leafy_vegetables': {
        'name_key': 'leafy_vegetables',
        'desc_key': 'leafy_vegetables_desc',
        'diseases': ['Downy Mildew', 'Powdery Mildew', 'Bacterial Leaf Spot']
    },
    'cereals': {
        'name_key': 'cereals',
        'desc_key': 'cereals_desc',
        'diseases': ['Rust', 'Smut', 'Blight', 'Leaf Spot']
    }
}

@app.route('/set_language/<language>')
def set_language(language):
    if language in ['en', 'ne']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', categories=PLANT_CATEGORIES, get_translation=get_translation)








@app.route('/category/<category_name>')
def category_page(category_name):
    if category_name not in PLANT_CATEGORIES:
        return redirect(url_for('index'))
    lng = get_language()
    category_info = PLANT_CATEGORIES[category_name]
    return render_template('category.html', 
                         category_name=category_name, 
                         category_info=category_info,
                         get_translation=get_translation,
                         lang=lng)


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.route('/detect', methods=['POST'])
def detect_disease():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        category = request.form.get('category')

        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if category not in PLANT_CATEGORIES:
            return jsonify({'error': 'Invalid category'}), 400

        # Process the image
        img_bytes = file.read()
        img_loaded = read_file_as_image(img_bytes)
        # img_resized = Image.fromarray(img_loaded).resize((256, 256))  # Adjust size as per your model input
        # img_array = np.array(img_resized) / 255.0  # Normalize if model expects normalized input
        img_array = np.expand_dims(img_loaded, axis=0)
        # image = img.imread(file.read())

        # Mock disease detection (replace with your actual model inference)
        prediction = mock_disease_detection(img_array, category)

        return jsonify({
            'success': True,
            'category': get_translation(PLANT_CATEGORIES[category]['name_key']),
            'prediction': prediction
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def mock_disease_detection(image, category):
    """
    Mock function for disease detection. Replace this with your actual model inference.
    """
    # import random

    # if category == "soil_crops":
        # load my model here
    model = load_model('models/soil_crops.keras')

    clss= ['Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___healthy']


    if category == "cereals":
        model = load_model('models/cereals_crops.keras')
        clss = ['Corn___Common_Rust',
 'Corn___Gray_Leaf_Spot',
 'Corn___Healthy',
 'Corn___Northern_Leaf_Blight',
 'Rice___Brown_Spot',
 'Rice___Healthy',
 'Rice___Leaf_Blast',
 'Wheat___Brown_Rust',
 'Wheat___Healthy',
 'Wheat___Yellow_Rust']
        
    elif category == "tree_fruits":
        model = load_model('models/tree_crops.keras')
        clss = ['Apple___Apple_scab',
 'Apple___Black_rot',
 'Apple___Cedar_apple_rust',
 'Apple___healthy']
    elif category == "leafy_vegetables":
        model = load_model('models/leafy_crops.keras')
        clss = ['Bacterial',
 'Downy_mildew_on_lettuce',
 'Healthy',
 'Powdery_mildew_on_lettuce',
 'Septoria_blight_on_lettuce',
 'Shepherd_purse_weeds',
 'Viral',
 'Wilt_and_leaf_blight_on_lettuce']


    diseases = PLANT_CATEGORIES[category]['diseases']
    prediction = model.predict(image)
    detected_disease = clss[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    # Mock treatment suggestions in both languages
    treatments_en = {
        'Early Blight': 'Apply fungicide containing chlorothalonil. Remove affected leaves.',
        'Late Blight': 'Use copper-based fungicides. Improve air circulation.',
        'Apple Scab': 'Apply preventive fungicide sprays. Rake and destroy fallen leaves.',
        'Downy Mildew': 'Reduce humidity. Apply systemic fungicides.',
        'Rust': 'Use resistant varieties. Apply fungicides if severe.',
        'Fire Blight': 'Prune affected branches. Apply copper sprays.',
        'Leaf Mold': 'Improve ventilation. Reduce humidity levels.',
        'Bacterial Spot': 'Use copper-based bactericides. Avoid overhead watering.',
        'Citrus Canker': 'Remove infected plant parts. Apply copper sprays.',
        'Brown Rot': 'Remove mummified fruits. Apply fungicides during bloom.',
        'Powdery Mildew': 'Apply sulfur-based fungicides. Improve air circulation.',
        'Bacterial Leaf Spot': 'Use certified disease-free seeds. Apply copper treatments.',
        'Smut': 'Use resistant varieties. Apply seed treatments.',
        'Blight': 'Improve drainage. Apply appropriate fungicides.',
        'Leaf Spot': 'Remove infected leaves. Apply preventive fungicides.'
    }

    treatments_ne = {
        'Early Blight': 'क्लोरोथालोनिल भएको फफूंदी नाशक प्रयोग गर्नुहोस्। प्रभावित पातहरू हटाउनुहोस्।',
        'Late Blight': 'तामा आधारित ففूंदी नाशकहरू प्रयोग गर्नुहोस्। हावा चलाचल सुधार गर्नुहोस्।',
        'Apple Scab': 'रोकथाम फफूंदी नाशक स्प्रे गर्नुहोस्। झरेका पातहरू जम्मा गरेर नष्ट गर्नुहोस्।',
        'Downy Mildew': 'आर्द्रता कम गर्नुहोस्। प्रणालीगत फफूंदी नाशकहरू प्रयोग गर्नुहोस्।',
        'Rust': 'प्रतिरोधी किस्महरू प्रयोग गर्नुहोस्। गम्भीर भएमा फफूंदी नाशक प्रयोग गर्नुहोस्।',
        'Fire Blight': 'प्रभावित हाँगाहरू काट्नुहोस्। तामाको स्प्रे गर्नुहोस्।',
        'Leaf Mold': 'भेन्टिलेसन सुधार गर्नुहोस्। आर्द्रताको स्तर कम गर्नुहोस्।',
        'Bacterial Spot': 'तामा आधारित ब्याक्टेरिया नाशकहरू प्रयोग गर्नुहोस्। माथिबाट पानी दिनु नहुन्छ।',
        'Citrus Canker': 'संक्रमित बिरुवाका भागहरू हटाउनुहोस्। तामाको स्प्रे गर्नुहोस्।',
        'Brown Rot': 'ममी बनेका फलहरू हटाउनुहोस्। फूल फुल्ने समयमा फफूंदी नाशक गर्नुहोस्।',
        'Powdery Mildew': 'गन्धक आधारित फफूंदी नाशकहरू प्रयोग गर्नुहोस्। हावा चलाचल सुधार गर्नुहोस्।',
        'Bacterial Leaf Spot': 'प्रमाणित रोगमुक्त बीउ प्रयोग गर्नुहोस्। तामाको उपचार गर्नुहोस्।',
        'Smut': 'प्रतिरोधी किस्महरू प्रयोग गर्नुहोस्। बीउ उपचार गर्नुहोस्।',
        'Blight': 'निकासी सुधार गर्नुहोस्। उपयुक्त फफूंदी नाशकहरू प्रयोग गर्नुहोस्।',
        'Leaf Spot': 'संक्रमित पातहरू हटाउनुहोस्। रोकथाम फफूंदी नाशकहरू प्रयोग गर्नुहोस्।'
    }

    lang = get_language()
    treatment_dict = treatments_ne if lang == 'ne' else treatments_en
    severity_options = ['Mild', 'Moderate', 'Severe']

    return {
        'disease': get_translation(detected_disease),
        'disease_original': detected_disease,
        'confidence': confidence,
        'treatment': treatment_dict.get(detected_disease, 'कृषि विशेषज्ञसँग उपचार विकल्पहरूको लागि सल्लाह लिनुहोस्।' if lang == 'ne' else 'Consult with agricultural expert for treatment options.'),
        'severity': get_translation(random.choice(severity_options))
    }






@app.route('/chat')
def chat():
    return render_template('chat.html', get_translation=get_translation)


@app.route('/about')
def about():
    return render_template('about.html', get_translation=get_translation)



@app.route('/contribute')
def contribute():
    return render_template('contribute.html', categories=PLANT_CATEGORIES, get_translation=get_translation)

@app.route('/submit_contribution', methods=['POST'])
def submit_contribution():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        category = request.form.get('category')
        disease = request.form.get('disease')
        contributor_name = request.form.get('contributor_name', 'Anonymous')
        notes = request.form.get('notes', '')

        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400

        if category not in PLANT_CATEGORIES:
            return jsonify({'error': 'Invalid category'}), 400

        if not disease:
            return jsonify({'error': 'Disease name is required'}), 400

        # Process and save the contribution
        image = Image.open(file.stream)

        # Here you would typically save the image and metadata to your dataset
        # For now, we'll just simulate the process
        contribution_data = {
            'category': category,
            'disease': disease,
            'contributor': contributor_name,
            'notes': notes,
            'filename': file.filename,
            'status': 'pending_review'
        }

        

        return jsonify({
            'success': True,
            'message': 'Thank you for your contribution! Your submission is pending review.',
            'contribution_id': f"CONTRIB_{hash(str(contribution_data)) % 10000:04d}"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(port=8080, debug=True)
