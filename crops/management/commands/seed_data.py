from django.core.management.base import BaseCommand
from crops.models import Crop
from diseases.models import Disease, Symptom, DiseaseSymptom
from knowledge_base.models import KnowledgeSource

class Command(BaseCommand):
    help = 'Seeds database with default crops, symptoms, diseases, and verified knowledge base records.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding agricultural database...")

        # 1. Seed Symptoms
        symptoms_data = [
            {'name': 'Yellowing', 'name_hi': 'पीलापन', 'code': 'yellowing', 'icon': 'fa-leaf'},
            {'name': 'Brown spots', 'name_hi': 'भूरे धब्बे', 'code': 'brown_spots', 'icon': 'fa-dot-circle'},
            {'name': 'White powder', 'name_hi': 'सफेद पाउडर', 'code': 'white_powder', 'icon': 'fa-snowflake'},
            {'name': 'Wilting', 'name_hi': 'मुरझाना', 'code': 'wilting', 'icon': 'fa-spa'},
            {'name': 'Leaf curling', 'name_hi': 'पत्तियों का मुड़ना', 'code': 'leaf_curling', 'icon': 'fa-compress-alt'},
            {'name': 'Holes', 'name_hi': 'छेद', 'code': 'holes', 'icon': 'fa-adjust'},
            {'name': 'Lesions', 'name_hi': 'घाव / धब्बे', 'code': 'lesions', 'icon': 'fa-disease'},
            {'name': 'Rot', 'name_hi': 'सड़न', 'code': 'rot', 'icon': 'fa-biohazard'},
        ]

        symptom_objs = {}
        for s_data in symptoms_data:
            sym, _ = Symptom.objects.get_or_create(code=s_data['code'], defaults=s_data)
            symptom_objs[s_data['code']] = sym

        # 2. Seed Crops
        crops_data = [
            {'name': 'Tomato', 'name_hi': 'टमाटर', 'scientific_name': 'Solanum lycopersicum', 'icon_class': 'fa-pepper-hot', 'description': 'Trained for Leaf Blight, Leaf Curl Virus, and Bacterial Spot.'},
            {'name': 'Potato', 'name_hi': 'आलू', 'scientific_name': 'Solanum tuberosum', 'icon_class': 'fa-egg', 'description': 'Trained for Early and Late Blight detection.'},
            {'name': 'Rice', 'name_hi': 'चावल', 'scientific_name': 'Oryza sativa', 'icon_class': 'fa-bowl-rice', 'description': 'Trained for Rice Blast and Bacterial Leaf Blight.'},
            {'name': 'Wheat', 'name_hi': 'गेहूं', 'scientific_name': 'Triticum aestivum', 'icon_class': 'fa-wheat-awn', 'description': 'Trained for Yellow Rust and Powdery Mildew.'},
            {'name': 'Maize', 'name_hi': 'मक्का', 'scientific_name': 'Zea mays', 'icon_class': 'fa-plant-wilt', 'description': 'Trained for Northern Leaf Blight and Common Rust.'},
            {'name': 'Cotton', 'name_hi': 'कपास', 'scientific_name': 'Gossypium', 'icon_class': 'fa-feather-alt', 'description': 'Trained for Cotton Leaf Curl Virus and Wilt.'},
            {'name': 'Chilli', 'name_hi': 'मिर्च', 'scientific_name': 'Capsicum annuum', 'icon_class': 'fa-pepper-hot', 'description': 'Trained for Chilli Anthracnose and Leaf Curl.'},
            {'name': 'Apple', 'name_hi': 'सेब', 'scientific_name': 'Malus domestica', 'icon_class': 'fa-apple-whole', 'description': 'Trained for Apple Scab and Black Rot.'},
        ]

        crop_objs = {}
        for c_data in crops_data:
            crop, _ = Crop.objects.get_or_create(name=c_data['name'], defaults=c_data)
            crop_objs[c_data['name']] = crop

        # 3. Seed Diseases & Knowledge Sources
        diseases_seed = [
            {
                'crop': crop_objs['Tomato'],
                'name': 'Early Blight',
                'name_hi': 'अगेती अंगमारी (अर्ली ब्लाइट)',
                'scientific_name': 'Alternaria solani',
                'severity': 'MEDIUM',
                'description': 'Fungal disease producing dark brown spots with concentric ring pattern (target spots) on lower leaves.',
                'symptoms': [symptom_objs['brown_spots'], symptom_objs['yellowing']],
                'knowledge': {
                    'title': 'Tomato Early Blight Field Guidelines',
                    'symptoms_summary': 'Concentric target-like brown lesions starting on mature lower foliage, surrounded by yellow chlorotic halos.',
                    'causes': 'Fungal pathogen Alternaria solani surviving in plant debris or soil.',
                    'favorable_conditions': 'Warm humid weather (24-29°C) with frequent rainfall or heavy dew.',
                    'treatment_immediate': 'Prune affected lower leaves to improve airflow. Avoid overhead leaf wetting during irrigation.',
                    'treatment_management': 'Apply crop sanitation, maintain wider plant spacing (45-60cm), and apply bio-fungicide if spread exceeds threshold.',
                    'prevention_methods': 'Practice 2-year crop rotation with non-solanaceous crops. Use certified resistant seed varieties.',
                    'monitoring_guidance': 'Inspect lower leaf canopy weekly. Consult local agricultural officer if over 20% canopy shows lesions.'
                }
            },
            {
                'crop': crop_objs['Tomato'],
                'name': 'Leaf Curl Virus',
                'name_hi': 'पत्ती मरोड़ रोग (लीफ कर्ल)',
                'scientific_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
                'severity': 'HIGH',
                'description': 'Viral disease transmitted by whiteflies leading to upward curling, stunting, and reduced fruit set.',
                'symptoms': [symptom_objs['leaf_curling'], symptom_objs['yellowing']],
                'knowledge': {
                    'title': 'Tomato Leaf Curl Virus Management',
                    'symptoms_summary': 'Severe upward curling of leaves, yellowing of leaf margins, thick leathery leaf texture, and stunted plant growth.',
                    'causes': 'Begomovirus transmitted primarily by Bemisia tabaci (whitefly) vectors.',
                    'favorable_conditions': 'Hot dry weather favoring high whitefly population density.',
                    'treatment_immediate': 'Remove and safely destroy severely infected young plants to prevent vector transmission.',
                    'treatment_management': 'Use yellow sticky traps (15-20 traps/acre) to monitor and control whitefly vector populations.',
                    'prevention_methods': 'Install 40-mesh insect-proof net nurseries. Plant TYLCV-resistant hybrid tomato varieties.',
                    'monitoring_guidance': 'Monitor undersides of leaves for whiteflies daily during dry warm periods.'
                }
            },
            {
                'crop': crop_objs['Potato'],
                'name': 'Late Blight',
                'name_hi': 'पिछेती अंगमारी (लेट ब्लाइट)',
                'scientific_name': 'Phytophthora infestans',
                'severity': 'HIGH',
                'description': 'Devastating oomycete pathogen causing water-soaked dark lesions and white mildew on leaf undersides.',
                'symptoms': [symptom_objs['lesions'], symptom_objs['white_powder'], symptom_objs['rot']],
                'knowledge': {
                    'title': 'Potato Late Blight Integrated Control',
                    'symptoms_summary': 'Water-soaked irregular dark green/brown spots turning black, with white fuzzy growth on leaf undersides in cool moist conditions.',
                    'causes': 'Phytophthora infestans water mold.',
                    'favorable_conditions': 'Cool temperatures (10-20°C) with continuous high humidity (>90%) for >12 hours.',
                    'treatment_immediate': 'Destroy infected foliage immediately to prevent tuber rot infection during harvest.',
                    'treatment_management': 'Apply protective copper-based or approved contact sprays at first forecast warning.',
                    'prevention_methods': 'Plant disease-free certified seed tubers. Ensure proper hilling up to cover growing tubers.',
                    'monitoring_guidance': 'Monitor local weather blight alerts daily during cool rainy periods.'
                }
            },
            {
                'crop': crop_objs['Rice'],
                'name': 'Rice Blast',
                'name_hi': 'धान का झोंका रोग (ब्लास्ट)',
                'scientific_name': 'Magnaporthe oryzae',
                'severity': 'HIGH',
                'description': 'Diamond/spindle-shaped lesions on leaves with reddish-brown borders and grey centers.',
                'symptoms': [symptom_objs['lesions'], symptom_objs['brown_spots']],
                'knowledge': {
                    'title': 'Rice Blast Management Guide',
                    'symptoms_summary': 'Spindle-shaped spots on leaves, neck rot leading to empty white heads (white ears).',
                    'causes': 'Fungal spores spread by wind and high nitrogen application.',
                    'favorable_conditions': 'High humidity, cloudy weather, high night temperatures, excess nitrogen fertilizer.',
                    'treatment_immediate': 'Drain field water temporarily if feasible and suspend excessive nitrogen application.',
                    'treatment_management': 'Maintain recommended water depth (2-5cm) and apply balanced NPK fertilizers.',
                    'prevention_methods': 'Treat seed with recommended bio-agents before sowing. Use resistant cultivars.',
                    'monitoring_guidance': 'Inspect leaf blades at tillering stage weekly.'
                }
            }
        ]

        for d_info in diseases_seed:
            disease, _ = Disease.objects.get_or_create(
                crop=d_info['crop'],
                name=d_info['name'],
                defaults={
                    'name_hi': d_info['name_hi'],
                    'scientific_name': d_info['scientific_name'],
                    'severity': d_info['severity'],
                    'description': d_info['description'],
                    'source_reference': 'Verified ICAR / Agricultural University Guidelines'
                }
            )

            # Link symptoms
            for sym in d_info['symptoms']:
                DiseaseSymptom.objects.get_or_create(disease=disease, symptom=sym, defaults={'is_primary': True})

            # Create Knowledge Base Source
            k_info = d_info['knowledge']
            KnowledgeSource.objects.update_or_create(
                disease=disease,
                defaults={
                    'title': k_info['title'],
                    'symptoms_summary': k_info['symptoms_summary'],
                    'causes': k_info['causes'],
                    'favorable_conditions': k_info['favorable_conditions'],
                    'treatment_immediate': k_info['treatment_immediate'],
                    'treatment_management': k_info['treatment_management'],
                    'prevention_methods': k_info['prevention_methods'],
                    'monitoring_guidance': k_info['monitoring_guidance'],
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded crops, symptoms, diseases, and knowledge base!"))
