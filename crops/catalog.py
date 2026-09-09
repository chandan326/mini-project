"""Thirty widely grown Indian field and horticultural crops shown in the scanner."""

INDIA_MAJOR_CROPS = [
    {'name': 'Rice', 'name_hi': 'धान', 'scientific_name': 'Oryza sativa', 'icon_class': 'fa-bowl-rice'},
    {'name': 'Wheat', 'name_hi': 'गेहूं', 'scientific_name': 'Triticum aestivum', 'icon_class': 'fa-wheat-awn'},
    {'name': 'Maize', 'name_hi': 'मक्का', 'scientific_name': 'Zea mays', 'icon_class': 'fa-plant-wilt'},
    {'name': 'Pearl Millet', 'name_hi': 'बाजरा', 'scientific_name': 'Cenchrus americanus', 'icon_class': 'fa-wheat-awn'},
    {'name': 'Sorghum', 'name_hi': 'ज्वार', 'scientific_name': 'Sorghum bicolor', 'icon_class': 'fa-wheat-awn'},
    {'name': 'Barley', 'name_hi': 'जौ', 'scientific_name': 'Hordeum vulgare', 'icon_class': 'fa-wheat-awn'},
    {'name': 'Chickpea', 'name_hi': 'चना', 'scientific_name': 'Cicer arietinum', 'icon_class': 'fa-seedling'},
    {'name': 'Pigeon Pea', 'name_hi': 'अरहर', 'scientific_name': 'Cajanus cajan', 'icon_class': 'fa-seedling'},
    {'name': 'Green Gram', 'name_hi': 'मूंग', 'scientific_name': 'Vigna radiata', 'icon_class': 'fa-seedling'},
    {'name': 'Black Gram', 'name_hi': 'उड़द', 'scientific_name': 'Vigna mungo', 'icon_class': 'fa-seedling'},
    {'name': 'Lentil', 'name_hi': 'मसूर', 'scientific_name': 'Lens culinaris', 'icon_class': 'fa-seedling'},
    {'name': 'Groundnut', 'name_hi': 'मूंगफली', 'scientific_name': 'Arachis hypogaea', 'icon_class': 'fa-seedling'},
    {'name': 'Mustard', 'name_hi': 'सरसों', 'scientific_name': 'Brassica juncea', 'icon_class': 'fa-leaf'},
    {'name': 'Soybean', 'name_hi': 'सोयाबीन', 'scientific_name': 'Glycine max', 'icon_class': 'fa-seedling'},
    {'name': 'Sesame', 'name_hi': 'तिल', 'scientific_name': 'Sesamum indicum', 'icon_class': 'fa-seedling'},
    {'name': 'Cotton', 'name_hi': 'कपास', 'scientific_name': 'Gossypium spp.', 'icon_class': 'fa-feather-alt'},
    {'name': 'Sugarcane', 'name_hi': 'गन्ना', 'scientific_name': 'Saccharum officinarum', 'icon_class': 'fa-wheat-awn'},
    {'name': 'Jute', 'name_hi': 'जूट', 'scientific_name': 'Corchorus spp.', 'icon_class': 'fa-leaf'},
    {'name': 'Tea', 'name_hi': 'चाय', 'scientific_name': 'Camellia sinensis', 'icon_class': 'fa-leaf'},
    {'name': 'Coffee', 'name_hi': 'कॉफी', 'scientific_name': 'Coffea spp.', 'icon_class': 'fa-mug-hot'},
    {'name': 'Potato', 'name_hi': 'आलू', 'scientific_name': 'Solanum tuberosum', 'icon_class': 'fa-seedling'},
    {'name': 'Tomato', 'name_hi': 'टमाटर', 'scientific_name': 'Solanum lycopersicum', 'icon_class': 'fa-apple-whole'},
    {'name': 'Onion', 'name_hi': 'प्याज', 'scientific_name': 'Allium cepa', 'icon_class': 'fa-seedling'},
    {'name': 'Chilli', 'name_hi': 'मिर्च', 'scientific_name': 'Capsicum annuum', 'icon_class': 'fa-pepper-hot'},
    {'name': 'Brinjal', 'name_hi': 'बैंगन', 'scientific_name': 'Solanum melongena', 'icon_class': 'fa-seedling'},
    {'name': 'Okra', 'name_hi': 'भिंडी', 'scientific_name': 'Abelmoschus esculentus', 'icon_class': 'fa-seedling'},
    {'name': 'Mango', 'name_hi': 'आम', 'scientific_name': 'Mangifera indica', 'icon_class': 'fa-tree'},
    {'name': 'Banana', 'name_hi': 'केला', 'scientific_name': 'Musa spp.', 'icon_class': 'fa-seedling'},
    {'name': 'Apple', 'name_hi': 'सेब', 'scientific_name': 'Malus domestica', 'icon_class': 'fa-apple-whole'},
    {'name': 'Grapes', 'name_hi': 'अंगूर', 'scientific_name': 'Vitis vinifera', 'icon_class': 'fa-seedling'},
]

for crop in INDIA_MAJOR_CROPS:
    crop.setdefault('description', 'Supported by live multi-photo Gemini plant-health assessment.')
