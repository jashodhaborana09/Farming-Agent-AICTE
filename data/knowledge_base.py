"""
Farming Knowledge Base
Curated agricultural documents loaded into ChromaDB for RAG retrieval.
"""

FARMING_DOCUMENTS = [
    # ── Crop Recommendations ──────────────────────────────────────────────────
    {
        "id": "crop_kharif_001",
        "content": (
            "Kharif crops are sown at the beginning of the rainy season (June–July) and harvested "
            "in September–October. Major kharif crops include Rice, Maize, Bajra (Pearl Millet), "
            "Jowar (Sorghum), Cotton, Groundnut, Sugarcane, Soybean, and Turmeric. "
            "Rice requires waterlogged conditions; ideal temperature 20–35°C. "
            "Cotton prefers deep black soil (regur) with low moisture. "
            "Groundnut thrives in light sandy loam soil with pH 6.0–6.5."
        ),
        "metadata": {"category": "crop_recommendation", "season": "kharif", "language": "en"},
    },
    {
        "id": "crop_rabi_001",
        "content": (
            "Rabi crops are sown in October–November and harvested in March–April. "
            "Key rabi crops: Wheat, Barley, Gram (Chickpea), Mustard, Linseed, and Peas. "
            "Wheat grows best at 10–25°C with well-drained loamy soil; pH 6–7. "
            "Mustard is drought-tolerant and suits sandy loam soil. "
            "Chickpea fixes atmospheric nitrogen and improves soil fertility."
        ),
        "metadata": {"category": "crop_recommendation", "season": "rabi", "language": "en"},
    },
    {
        "id": "crop_zaid_001",
        "content": (
            "Zaid crops are grown between March and June (summer season). "
            "Common zaid crops: Watermelon, Muskmelon, Cucumber, Bitter Gourd, Pumpkin, "
            "Moong (Green Gram), and Urad (Black Gram). "
            "These crops need high temperature, ample sunlight, and irrigation support. "
            "Watermelon and muskmelon are ideal cash crops for small farmers in summer."
        ),
        "metadata": {"category": "crop_recommendation", "season": "zaid", "language": "en"},
    },
    {
        "id": "crop_soil_match_001",
        "content": (
            "Soil-Crop matching guide: "
            "Alluvial soil (Indo-Gangetic plains) → Wheat, Rice, Sugarcane, Pulses. "
            "Black soil (Deccan plateau) → Cotton, Jowar, Linseed, Tobacco. "
            "Red & yellow soil → Groundnut, Potato, Rice. "
            "Laterite soil → Tea, Coffee, Cashew. "
            "Mountain soil → Apple, Peach, Walnut, Saffron. "
            "Sandy/desert soil → Bajra, Guar, Date Palm. "
            "Conduct soil pH test before sowing; ideal range 6.0–7.5 for most crops."
        ),
        "metadata": {"category": "crop_recommendation", "topic": "soil_matching", "language": "en"},
    },
    # ── Soil Health & Fertilizers ─────────────────────────────────────────────
    {
        "id": "soil_health_001",
        "content": (
            "Soil health management for small farmers: "
            "1. Test soil every 2 years via Soil Health Card (Government of India scheme). "
            "2. Maintain organic matter by adding 5–10 tonnes/hectare of FYM (Farm Yard Manure). "
            "3. Use green manure crops like Dhaincha or Sunhemp to fix nitrogen. "
            "4. Avoid over-use of urea; balanced NPK ratio is critical. "
            "5. pH correction: add lime for acidic soil (pH < 6), gypsum for alkaline (pH > 7.5). "
            "6. Vermicompost improves water-holding capacity by up to 30%."
        ),
        "metadata": {"category": "soil_health", "language": "en"},
    },
    {
        "id": "fertilizer_guide_001",
        "content": (
            "Fertilizer recommendations per crop: "
            "Rice: 120 kg N, 60 kg P, 60 kg K per hectare. Apply urea in 3 splits. "
            "Wheat: 120 kg N, 60 kg P, 40 kg K per hectare. "
            "Maize: 180 kg N, 80 kg P, 60 kg K per hectare. "
            "Tomato: 100 kg N, 60 kg P, 80 kg K per hectare, plus micronutrients. "
            "Sugarcane: 250 kg N, 115 kg P, 115 kg K per hectare. "
            "Always apply phosphorus and potassium as basal dose at sowing time. "
            "Use soil test-based fertilizer recommendations to reduce input costs."
        ),
        "metadata": {"category": "soil_health", "topic": "fertilizer", "language": "en"},
    },
    # ── Pest & Disease Management ─────────────────────────────────────────────
    {
        "id": "pest_rice_001",
        "content": (
            "Rice pest management: "
            "1. Brown Plant Hopper (BPH): Apply Imidacloprid 17.8 SL @ 0.25 ml/L water. "
            "   Avoid excessive nitrogen fertilization. Use resistant varieties like IR64. "
            "2. Stem Borer: Use Carbofuran 3G @ 33 kg/ha or Chlorantraniliprole. "
            "3. Blast Disease: Apply Tricyclazole 75 WP @ 0.6 g/L. "
            "4. Sheath Blight: Hexaconazole 5% EC @ 1.5 ml/L. "
            "5. Integrated Pest Management: use pheromone traps, light traps, and bio-pesticides. "
            "Early detection and field scouting twice a week is recommended."
        ),
        "metadata": {"category": "pest_control", "crop": "rice", "language": "en"},
    },
    {
        "id": "pest_wheat_001",
        "content": (
            "Wheat pest and disease management: "
            "1. Yellow/Brown Rust: Apply Propiconazole 25 EC @ 0.1% at first sign. "
            "2. Aphids: Use Dimethoate 30 EC @ 1.7 ml/L or Thiamethoxam. "
            "3. Termites: Soil treatment with Chlorpyrifos 20 EC @ 4 L/ha before sowing. "
            "4. Loose Smut: Seed treatment with Carboxin 75 WP @ 2.5 g/kg seed. "
            "5. Rodent control: use zinc phosphide bait @ 10 g/burrow. "
            "Regular field monitoring during tillering and heading stages is critical."
        ),
        "metadata": {"category": "pest_control", "crop": "wheat", "language": "en"},
    },
    {
        "id": "pest_tomato_001",
        "content": (
            "Tomato pest management: "
            "1. Fruit Borer (Helicoverpa): Spray Spinosad 45 SC @ 0.3 ml/L or Emamectin benzoate. "
            "2. Whitefly (virus vector): Use yellow sticky traps + Imidacloprid 0.3 ml/L. "
            "3. Early Blight: Mancozeb 75 WP @ 2 g/L or Chlorothalonil. "
            "4. Late Blight: Metalaxyl + Mancozeb @ 2 g/L every 7 days. "
            "5. Leaf Curl Virus: Control whitefly vectors; remove infected plants immediately. "
            "6. Nematodes: Apply Carbofuran 3G at transplanting in infested soil. "
            "Use drip irrigation to reduce foliar diseases in tomato."
        ),
        "metadata": {"category": "pest_control", "crop": "tomato", "language": "en"},
    },
    {
        "id": "organic_pest_001",
        "content": (
            "Organic and bio-pesticide options for farmers: "
            "1. Neem-based products (Azadirachtin): Effective against 200+ insect pests. "
            "   Spray 3–5 ml/L every 10–15 days. Safe for beneficial insects. "
            "2. Trichoderma viride: Bio-fungicide for soil-borne diseases. Apply 4 g/kg seed. "
            "3. Pseudomonas fluorescens: Induces systemic resistance. Drench 2.5 kg/ha. "
            "4. Beauveria bassiana: Entomopathogenic fungus for whitefly, thrips, aphids. "
            "5. Yellow sticky traps: Catch whitefly and aphids; 10 traps/acre. "
            "6. Pheromone traps: For fruit borers; 5 traps/acre. "
            "Organic farming increases premium pricing and market access."
        ),
        "metadata": {"category": "pest_control", "topic": "organic", "language": "en"},
    },
    # ── Irrigation ────────────────────────────────────────────────────────────
    {
        "id": "irrigation_001",
        "content": (
            "Efficient irrigation methods for small farmers: "
            "1. Drip Irrigation: Saves 40–60% water; ideal for vegetables, fruits, sugarcane. "
            "   Government subsidy available under PMKSY (Pradhan Mantri Krishi Sinchayee Yojana). "
            "2. Sprinkler irrigation: Suitable for wheat, groundnut, and horticulture. "
            "3. Critical irrigation stages: "
            "   - Rice: Transplanting, tillering, panicle initiation, grain filling. "
            "   - Wheat: Crown root initiation (21 DAS), booting, milk stage. "
            "   - Maize: Knee-high stage, tasseling, silking. "
            "4. Avoid waterlogging; maintain proper drainage channels. "
            "5. Mulching reduces soil water evaporation by 25–30%."
        ),
        "metadata": {"category": "irrigation", "language": "en"},
    },
    # ── Government Schemes ────────────────────────────────────────────────────
    {
        "id": "govt_schemes_001",
        "content": (
            "Key government schemes for Indian farmers (2024): "
            "1. PM-KISAN: ₹6,000/year direct income support; apply at pmkisan.gov.in. "
            "2. PM Fasal Bima Yojana: Crop insurance at low premium (1.5–5%); protects against yield loss. "
            "3. Soil Health Card Scheme: Free soil testing every 2 years from govt labs. "
            "4. eNAM: National Agriculture Market for better mandi prices; register at enam.gov.in. "
            "5. Kisan Credit Card (KCC): Low-interest crop loans at 4–7% pa. "
            "6. PKVY (Paramparagat Krishi Vikas Yojana): Support for organic farming clusters. "
            "7. RKVY (Rashtriya Krishi Vikas Yojana): Infrastructure and allied sector funding. "
            "8. Agri-clinics: Business support for agri-entrepreneurs."
        ),
        "metadata": {"category": "government_schemes", "language": "en"},
    },
    # ── Seasonal Calendar ─────────────────────────────────────────────────────
    {
        "id": "seasonal_calendar_001",
        "content": (
            "Indian farming seasonal calendar: "
            "June–July: Sow kharif crops (rice, maize, cotton, soybean) after first rains. "
            "July–August: Weeding and fertilizer top-dressing for kharif crops. "
            "September–October: Harvest kharif; land preparation for rabi season. "
            "October–November: Sow rabi crops (wheat, mustard, chickpea, barley). "
            "November–February: Manage rabi crops; apply irrigation at critical stages. "
            "March–April: Harvest rabi crops; summer ploughing. "
            "April–May: Sow zaid crops (watermelon, vegetables) with irrigation. "
            "Year-round: Maintain fruit orchards; manage perennials like sugarcane and banana."
        ),
        "metadata": {"category": "seasonal_planning", "language": "en"},
    },
    # ── Market & Post-Harvest ─────────────────────────────────────────────────
    {
        "id": "market_001",
        "content": (
            "Mandi (market) price guidance for farmers: "
            "1. Check prices daily on agmarknet.gov.in before selling produce. "
            "2. eNAM platform lets you sell directly across state mandis online. "
            "3. FPO (Farmer Producer Organizations) aggregate produce for better price. "
            "4. Cold storage use: Onion, potato, apple, tomato prices fluctuate; store for 4–8 weeks. "
            "5. MSP (Minimum Support Price) 2024 key crops: "
            "   Wheat ₹2,275/qtl, Rice ₹2,300/qtl, Maize ₹2,090/qtl, "
            "   Soybean ₹4,600/qtl, Groundnut ₹6,783/qtl, Cotton ₹7,521/qtl. "
            "6. Grading and packaging improve farm-gate price by 15–30%. "
            "7. Direct sale to supermarkets, food processors offers 20–40% premium."
        ),
        "metadata": {"category": "market_prices", "language": "en"},
    },
    # ── Water Conservation ────────────────────────────────────────────────────
    {
        "id": "water_conservation_001",
        "content": (
            "Water conservation techniques: "
            "1. Rainwater harvesting: Farm ponds capture monsoon runoff. "
            "   Ideal size: 20m × 20m × 3m pond for 10-acre farm. "
            "2. Contour bunding: Reduces runoff on slopes; increases percolation. "
            "3. Mulching with crop residue or plastic film conserves soil moisture. "
            "4. SRI (System of Rice Intensification): 30% water saving with higher yield. "
            "5. Alternate Wetting and Drying (AWD) in rice: saves 30% water. "
            "6. Bore-well recharge structures recommended where water table is declining."
        ),
        "metadata": {"category": "water_management", "language": "en"},
    },
    # ── Hindi crop info ───────────────────────────────────────────────────────
    {
        "id": "crop_hindi_001",
        "content": (
            "खरीफ फसलें (Kharif Faslein): "
            "खरीफ मौसम में बोई जाने वाली प्रमुख फसलें: धान, मक्का, बाजरा, कपास, मूंगफली, सोयाबीन। "
            "धान के लिए 20-35°C तापमान और जलभराव वाली मिट्टी उपयुक्त है। "
            "रबी फसलें (Rabi Faslein): अक्टूबर-नवंबर में बोई जाती हैं — गेहूं, सरसों, चना, जौ। "
            "गेहूं के लिए दोमट मिट्टी और 10-25°C तापमान अच्छा है। "
            "सरकारी योजनाएं: PM-KISAN से 6000 रुपये सालाना मिलते हैं। "
            "फसल बीमा के लिए PM Fasal Bima Yojana में पंजीकरण करें।"
        ),
        "metadata": {"category": "crop_recommendation", "language": "hi"},
    },
]

DOCUMENT_IDS = [doc["id"] for doc in FARMING_DOCUMENTS]
DOCUMENT_TEXTS = [doc["content"] for doc in FARMING_DOCUMENTS]
DOCUMENT_METADATAS = [doc["metadata"] for doc in FARMING_DOCUMENTS]
