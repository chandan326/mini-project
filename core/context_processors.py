from django.conf import settings
from django.utils import translation

def platform_context(request):
    """Global context processor providing platform metadata and UI translations."""
    # Check active language
    lang = translation.get_language() or request.COOKIES.get('django_language') or request.session.get('_language') or 'en'
    is_hi = str(lang).startswith('hi')

    ui_text = {
        'is_hi': is_hi,
        'current_lang': 'hi' if is_hi else 'en',
        'NOTICE': 'सूचना' if is_hi else 'Notice',
        'LOG_IN': 'लॉग इन' if is_hi else 'Log In',
        'CHECK_PLANT': 'पौधे की जांच करें' if is_hi else 'Check Plant Health',
        'HERO_TITLE_1': 'अपनी फसलों की रक्षा करें।' if is_hi else 'Protect Your Crops.',
        'HERO_TITLE_2': 'पौधे की बीमारियों का जल्दी पता लगाएं।' if is_hi else 'Detect Plant Diseases Early.',
        'HERO_SUB': 'पौधे की तस्वीरें अपलोड करें, कुछ आसान प्रश्नों के उत्तर दें, और व्यावहारिक फसल देखभाल मार्गदर्शन के साथ AI-सहायता प्राप्त रोग मूल्यांकन प्राप्त करें।' if is_hi else 'Upload plant images, answer a few simple questions, and get an AI-assisted disease assessment with practical crop-care guidance.',
        'HOW_IT_WORKS': 'यह कैसे काम करता है' if is_hi else 'How It Works',
        'SUPPORTED_CROPS': 'समर्थित फसलें' if is_hi else 'Supported Crops',
        'WHY_USE': 'इस प्लेटफॉर्म का उपयोग क्यों करें?' if is_hi else 'Why Use This Platform?',
        'IMPORTANT_NOTICE_TITLE': 'AI सहायता पर महत्वपूर्ण सूचना' if is_hi else 'Important Notice on AI Assistance',
        'IMPORTANT_NOTICE_DESC': 'यह प्लेटफॉर्म केवल शुरुआती लक्षणों की पहचान में सहायता के लिए AI-आधारित कृषि जानकारी प्रदान करता है। यह प्रयोगशाला परीक्षण या कृषि विशेषज्ञ की सलाह का स्थान नहीं लेता है।' if is_hi else 'This platform provides AI-assisted agricultural information designed to assist farmers in early symptom identification. It does not replace professional agricultural extension services, soil lab testing, or expert field verification.',
        'DASHBOARD': 'डैशबोर्ड' if is_hi else 'Dashboard',
        'STEP_1_CROP': '1. फसल चुनें' if is_hi else '1. Select Crop',
        'STEP_2_PHOTOS': '2. 5 तस्वीरें अपलोड करें' if is_hi else '2. Upload 5 Photos',
        'STEP_3_QUESTIONS': '3. प्रश्नों के उत्तर दें' if is_hi else '3. Answer Questions',
        'STEP_4_RESULT': '4. AI परिणाम प्राप्त करें' if is_hi else '4. Get AI Result',
        'LABEL_CROP': 'फसल' if is_hi else 'Crop',
        'LABEL_PHOTOS': 'तस्वीरें' if is_hi else 'Photos',
        'LABEL_QUESTIONS': 'प्रश्न' if is_hi else 'Questions',
        'LABEL_ANALYSIS': 'विश्लेषण' if is_hi else 'Analysis',
        'CONTINUE': 'आगे बढ़ें' if is_hi else 'Continue',
        'PREVIOUS': 'पीछे' if is_hi else 'Previous',
        'ANALYZE_NOW': 'पौधे का विश्लेषण करें' if is_hi else 'Analyze Plant Now',
        'DOWNLOAD_PDF': 'रिपोर्ट डाउनलोड करें (PDF)' if is_hi else 'Download Report (PDF)',
        'ASSESSMENT_RESULT': 'पौधे के स्वास्थ्य का मूल्यांकन परिणाम' if is_hi else 'Plant Health Assessment Result',
        'ASSESSED_CONDITION': 'अनुमानित बीमारी / स्थिति' if is_hi else 'Assessed Condition',
        'WHY_DETECTED': 'यह परिणाम क्यों आया?' if is_hi else 'Why This Was Detected',
        'COMMON_SYMPTOMS': 'मुख्य लक्षण' if is_hi else 'Common Symptoms',
        'RECOMMENDED_MANAGEMENT': 'अनुशंसित उपचार और प्रबंधन' if is_hi else 'Recommended Management',
        'PREVENTION_GUIDANCE': 'बचाव के उपाय' if is_hi else 'Prevention Guidance',
        'EXPERT_REFERRAL': 'कृषि विशेषज्ञ से सलाह कब लें' if is_hi else 'When to Seek Agricultural Expert Assistance',
        'WAS_HELPFUL': 'क्या यह परिणाम उपयोगी था?' if is_hi else 'Was this result helpful?',
        'YES_HELPFUL': 'हाँ, उपयोगी था' if is_hi else 'Yes, Helpful',
        'NO_IMPROVE': 'नहीं, सुधार की आवश्यकता है' if is_hi else 'No, Needs Improvement',
    }

    return {
        'PLATFORM_NAME': 'AgriHealth AI',
        'PLATFORM_TAGLINE': 'AI-Powered Plant Disease Detection & Farmer Assistance',
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', True),
        'CONFIDENCE_THRESHOLD_PCT': int(getattr(settings, 'CONFIDENCE_THRESHOLD', 0.60) * 100),
        'UI': ui_text,
    }
