import json
import os

protocols = [
  {
    "protocol_id": "P001",
    "name": "Minor Cut and Superficial Wound",
    "version": "1.0",
    "category": "TRAUMA_FIRST_AID",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["cut", "wound", "scrape", "scratch", "laceration", "cheera", "ghav", "jakhmi", "chot"],
    "required_fields": ["body_part", "bleeding_status", "duration", "pain_level"],
    "questions": [
      {"field": "body_part", "text": "Where is the cut located on your body?", "text_hi": "चोट आपके शरीर के किस हिस्से पर लगी है?", "text_mr": "जखम तुमच्या शरीराच्या कोणत्या भागावर झाली आहे?"},
      {"field": "bleeding_status", "text": "Is the bleeding controlled or is it continuously spurting?", "text_hi": "क्या खून बहना रुक गया है या लगातार बह रहा है?", "text_mr": "रक्तस्त्राव थांबला आहे की सतत वाहत आहे?"},
      {"field": "duration", "text": "How long ago did this cut happen?", "text_hi": "यह चोट कितनी देर पहले लगी थी?", "text_mr": "ही जखम साधारण किती वेळापूर्वी झाली?"},
      {"field": "pain_level", "text": "On a scale of 1 to 10, how severe is the pain?", "text_hi": "1 से 10 के पैमाने पर दर्द कितना तेज है?", "text_mr": "1 ते 10 च्या प्रमाणात वेदना किती तीव्र आहे?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Wash hands and gently rinse the minor cut with clean running water.", "instruction_hi": "डेमो सूचना: हाथ धोएं और साफ पानी से हल्के से घाव को धो लें।", "instruction_mr": "डेमो सूचना: हात स्वच्छ धुवा आणि जखम वाहत्या स्वच्छ पाण्याने धुवा."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Apply gentle direct pressure with a clean cloth or sterile gauze if oozing.", "instruction_hi": "डेमो सूचना: साफ कपड़े या स्टेराइल पट्टी से हल्का दबाव डालें।", "instruction_mr": "डेमो सूचना: स्वच्छ कापडाने किंवा पट्टीने हलका दाब द्या."},
      {"step": 3, "instruction": "DEMO PLACEHOLDER: Keep the area clean and wait for the nursing triage staff to inspect.", "instruction_hi": "डेमो सूचना: घाव को साफ रखें और नर्स/डॉक्टर के आने तक प्रतीक्षा करें।", "instruction_mr": "डेमो सूचना: जखम स्वच्छ ठेवा आणि वैद्यकीय कर्मचारी तपासणी करेपर्यंत थांबा."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["uncontrolled_bleeding", "arterial_spurting", "deep_wound_exposing_tissue", "severe_pain_above_7"]
    }
  },
  {
    "protocol_id": "P002",
    "name": "Minor Bleeding",
    "version": "1.0",
    "category": "TRAUMA_FIRST_AID",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["bleed", "bleeding", "blood", "khoon", "rakt", "rakta"],
    "required_fields": ["body_part", "bleeding_rate", "duration"],
    "questions": [
      {"field": "body_part", "text": "Which body part is bleeding?", "text_hi": "शरीर के किस अंग से खून बह रहा है?", "text_mr": "कोणत्या अवयवातून रक्त येत आहे?"},
      {"field": "bleeding_rate", "text": "Is the bleeding slow oozing or rapid spurting?", "text_hi": "क्या खून धीरे-धीरे रिस रहा है या तेजी से बह रहा है?", "text_mr": "रक्त हळूहळू पाझरत आहे की वेगाने वाहत आहे?"},
      {"field": "duration", "text": "How many minutes has it been bleeding continuously?", "text_hi": "लगातार खून बहते हुए कितने मिनट हो गए हैं?", "text_mr": "सतत रक्तस्त्राव सुरू होऊन किती मिनिटे झाली आहेत?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Apply firm, continuous pressure with a clean cloth or bandage.", "instruction_hi": "डेमो सूचना: साफ कपड़े से लगातार दृढ़ दबाव बनाए रखें।", "instruction_mr": "डेमो सूचना: स्वच्छ कापडाने सतत दाब देऊन धरा."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: If safe to do so, elevate the bleeding limb above heart level.", "instruction_hi": "डेमो सूचना: संभव हो तो प्रभावित अंग को दिल के स्तर से ऊपर उठाएं।", "instruction_mr": "डेमो सूचना: शक्य असल्यास तो अवयव हृदयाच्या पातळीपेक्षा वर ठेवा."}
    ],
    "escalation": {
      "default_priority": "NEEDS_REVIEW",
      "trigger_conditions": ["bleeding_not_stopping_after_10_min", "blood_soaking_through_dressings", "dizziness"]
    }
  },
  {
    "protocol_id": "P003",
    "name": "Minor Burn",
    "version": "1.0",
    "category": "TRAUMA_FIRST_AID",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["burn", "scald", "burned", "jalna", "jal gaya", "bhajla", "pola"],
    "required_fields": ["body_part", "burn_source", "blisters_present"],
    "questions": [
      {"field": "body_part", "text": "Where is the burn located?", "text_hi": "जलने का घाव कहाँ पर है?", "text_mr": "भाजलेली जागा कुठे आहे?"},
      {"field": "burn_source", "text": "What caused the burn (hot liquid, hot object, fire, chemical)?", "text_hi": "जलने का कारण क्या था (गर्म पानी, आग, रसायन)?", "text_mr": "भाजण्याचे कारण काय होते (गरम पाणी, आग, रसायन)?"},
      {"field": "blisters_present", "text": "Are there blisters or blackened skin visible?", "text_hi": "क्या छाले या त्वचा काली पड़ गई है?", "text_mr": "त्वचेवर फोड आले आहेत का किंवा त्वचा काळी पडली आहे का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Immediately cool the burn under cool (not ice cold) running water for 10-20 minutes.", "instruction_hi": "डेमो सूचना: जले हुए हिस्से को 10-20 मिनट के लिए ठंडे बहते पानी के नीचे रखें (बर्फ का उपयोग न करें)।", "instruction_mr": "डेमो सूचना: भाजलेल्या भागावर 10-20 मिनिटे थंड वाहते पाणी टाका (बर्फ वापरू नका)."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Do not pop blisters or apply toothpaste, butter, or ointments.", "instruction_hi": "डेमो सूचना: छालों को न फोड़ें और टूथपेस्ट या तेल न लगाएं।", "instruction_mr": "डेमो सूचना: फोड फोडू नका आणि टूथपेस्ट किंवा मलम लावू नका."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["facial_burn", "chemical_burn", "electrical_burn", "large_surface_area", "charred_skin"]
    }
  },
  {
    "protocol_id": "P004",
    "name": "Minor Injury and Sprain",
    "version": "1.0",
    "category": "TRAUMA_FIRST_AID",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["sprain", "twist", "injury", "swelling", "moch", "mar", "lagli"],
    "required_fields": ["body_part", "weight_bearing", "swelling_observed"],
    "questions": [
      {"field": "body_part", "text": "Which joint or body part is injured?", "text_hi": "किस जोड़ या अंग में चोट/मोच आई है?", "text_mr": "कोणत्या सांध्याला किंवा अवयवाला दुखापत झाली आहे?"},
      {"field": "weight_bearing", "text": "Can you put weight on it or move the joint?", "text_hi": "क्या आप उस पर वजन डाल सकते हैं या हिला सकते हैं?", "text_mr": "तुम्ही त्यावर भार देऊ शकता किंवा तो सांधा हलवू शकता का?"},
      {"field": "swelling_observed", "text": "Is there noticeable rapid swelling or visible deformity?", "text_hi": "क्या कोई असामान्य सूजन या विकृति दिख रही है?", "text_mr": "काही सूज किंवा विकृती दिसत आहे का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Rest the injured joint and avoid unnecessary movement.", "instruction_hi": "डेमो सूचना: प्रभावित अंग को आराम दें और हिलने-डुलने से बचें।", "instruction_mr": "डेमो सूचना: दुखापत झालेल्या भागाला विश्रांती द्या आणि हालचाल टाळा."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Apply a cold compress wrapped in a towel for 15 minutes at a time.", "instruction_hi": "डेमो सूचना: तौलिए में लपेटकर 15 मिनट के लिए बर्फ की सिकाई करें।", "instruction_mr": "डेमो सूचना: टॉवेलमध्ये गुंडाळलेला बर्फ 15 मिनिटांसाठी लावा."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["visible_bone_deformity", "inability_to_bear_weight", "numbness_distal_to_joint"]
    }
  },
  {
    "protocol_id": "P005",
    "name": "Fever Evaluation",
    "version": "1.0",
    "category": "GENERAL_MEDICINE",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["fever", "temperature", "chills", "bukhar", "taap"],
    "required_fields": ["temperature_recorded", "duration", "associated_symptoms"],
    "questions": [
      {"field": "temperature_recorded", "text": "Do you know your measured body temperature, if checked?", "text_hi": "क्या आपने थर्मामीटर से तापमान नापा है? कितना है?", "text_mr": "तुम्ही ताप मोजला आहे का? किती आहे?"},
      {"field": "duration", "text": "How many days have you had the fever?", "text_hi": "बुखार कितने दिनों से आ रहा है?", "text_mr": "ताप किती दिवसांपासून येत आहे?"},
      {"field": "associated_symptoms", "text": "Do you have shivering, neck stiffness, rash, or vomiting?", "text_hi": "क्या कंपकंपी, गर्दन में अकड़न, चकत्ते या उल्टी है?", "text_mr": "थंडी वाजणे, मान आखडणे, पुरळ किंवा उलट्या होत आहेत का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Stay hydrated with small, frequent sips of clean water or oral rehydration.", "instruction_hi": "डेमो सूचना: प्रचुर मात्रा में पानी पिएं और शरीर में पानी की कमी न होने दें।", "instruction_mr": "डेमो सूचना: पुरेसे पाणी प्या आणि विश्रांती घ्या."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Rest in a well-ventilated, comfortable room until staff triage.", "instruction_hi": "डेमो सूचना: हवादार कमरे में आराम करें।", "instruction_mr": "डेमो सूचना: हवेशीर खोलीत विश्रांती घ्या."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["fever_over_104F", "stiff_neck_with_headache", "seizures_convulsions", "severe_lethargy"]
    }
  },
  {
    "protocol_id": "P006",
    "name": "Dizziness and Lightheadedness",
    "version": "1.0",
    "category": "GENERAL_MEDICINE",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["dizzy", "dizziness", "faint", "fainting", "lightheaded", "chakkar", "bhraman"],
    "required_fields": ["duration", "chest_or_neuro_symptoms"],
    "questions": [
      {"field": "duration", "text": "Did you completely lose consciousness or feel faint?", "text_hi": "क्या आप पूरी तरह बेहोश हो गए थे या सिर्फ चक्कर आए?", "text_mr": "तुम्ही पूर्ण बेशुद्ध झालात की फक्त चक्कर आली?"},
      {"field": "chest_or_neuro_symptoms", "text": "Do you feel chest pain, shortness of breath, speech difficulty, or weakness on one side?", "text_hi": "क्या सीने में दर्द, सांस लेने में तकलीफ, या एक तरफ कमजोरी लग रही है?", "text_mr": "छातीत दुखणे, श्वास घेण्यास त्रास किंवा एका बाजूला अशक्तपणा वाटतोय का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Please sit or lie down immediately to prevent falls.", "instruction_hi": "डेमो सूचना: गिरने से बचने के लिए तुरंत बैठ जाएं या लेट जाएं।", "instruction_mr": "डेमो सूचना: पडणे टाळण्यासाठी कृपया ताबडतोब खाली बसा किंवा झोपा."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Loosen any tight clothing around the neck and notify staff if feeling worse.", "instruction_hi": "डेमो सूचना: गले के पास तंग कपड़े ढीले करें।", "instruction_mr": "डेमो सूचना: मानेजवळील घट्ट कपडे सैल करा."}
    ],
    "escalation": {
      "default_priority": "NEEDS_REVIEW",
      "trigger_conditions": ["syncope_loss_of_consciousness", "associated_chest_pain", "focal_neurological_deficit"]
    }
  },
  {
    "protocol_id": "P007",
    "name": "Nosebleed Epistaxis",
    "version": "1.0",
    "category": "TRAUMA_FIRST_AID",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["nosebleed", "nose bleed", "nak se khoon", "nakatun rakt"],
    "required_fields": ["duration", "head_trauma"],
    "questions": [
      {"field": "duration", "text": "How long has your nose been bleeding?", "text_hi": "नाक से कितनी देर से खून बह रहा है?", "text_mr": "नाकातून किती वेळापासून रक्त येत आहे?"},
      {"field": "head_trauma", "text": "Did you have any recent hit or trauma to your head or face?", "text_hi": "क्या सिर या चेहरे पर कोई चोट लगी है?", "text_mr": "डोक्याला किंवा चेहऱ्याला काही मार लागला आहे का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Sit upright and lean slightly FORWARD. Do not lean your head back.", "instruction_hi": "डेमो सूचना: सीधे बैठें और थोड़ा आगे झुकें। सिर पीछे न झुकाएं।", "instruction_mr": "डेमो सूचना: सरळ बसा आणि थोडे पुढे वाका. डोके मागे झुकवू नका."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Firmly pinch the soft part of the nose just below the bridge for 10-15 minutes.", "instruction_hi": "डेमो सूचना: नाक के कोमल हिस्से को 10-15 मिनट तक दबाकर रखें।", "instruction_mr": "डेमो सूचना: नाकाचा मऊ भाग 10-15 मिनिटे घट्ट दाबून धरा."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["bleeding_exceeding_20_minutes", "post_head_trauma", "difficulty_breathing"]
    }
  },
  {
    "protocol_id": "P008",
    "name": "Minor Allergic Symptoms",
    "version": "1.0",
    "category": "GENERAL_MEDICINE",
    "clinical_validation_status": "DEMO / REQUIRES CLINICAL VALIDATION",
    "keywords": ["allergy", "allergic", "rash", "itching", "hives", "khujli"],
    "required_fields": ["breathing_status", "lip_tongue_swelling"],
    "questions": [
      {"field": "breathing_status", "text": "Are you experiencing any difficulty breathing, wheezing, or tightness in the throat?", "text_hi": "क्या सांस लेने में कोई तकलीफ, घरघराहट या गले में कसाव महसूस हो रहा है?", "text_mr": "श्वास घेण्यास त्रास किंवा घशात आवळल्यासारखे वाटत आहे का?"},
      {"field": "lip_tongue_swelling", "text": "Is there any swelling of your lips, face, or tongue?", "text_hi": "क्या आपके होठों, चेहरे या जीभ पर सूजन आ रही है?", "text_mr": "ओठ, चेहरा किंवा जिभेवर सूज आली आहे का?"}
    ],
    "guidance": [
      {"step": 1, "instruction": "DEMO PLACEHOLDER: Avoid any further contact with suspected food, insect sting, or trigger.", "instruction_hi": "डेमो सूचना: संदिग्ध एलर्जी कारक (भोजन, कीड़ा इत्यादि) से दूर रहें।", "instruction_mr": "डेमो सूचना: संशयित ॲलर्जी घटकापासून दूर राहा."},
      {"step": 2, "instruction": "DEMO PLACEHOLDER: Remain seated calmly while staff reviews your allergy assessment.", "instruction_hi": "डेमो सूचना: शांतिपूर्वक बैठे रहें जब तक कर्मचारी समीक्षा न करें।", "instruction_mr": "डेमो सूचना: कर्मचारी तपासणी करेपर्यंत शांतपणे बसून राहा."}
    ],
    "escalation": {
      "default_priority": "NORMAL",
      "trigger_conditions": ["breathing_difficulty_anaphylaxis", "lip_or_tongue_swelling", "throat_constriction", "rapid_progression"]
    }
  }
]

os.makedirs("protocols/examples", exist_ok=True)
for p in protocols:
    fname = f"protocols/examples/{p['protocol_id']}_{p['name'].lower().replace(' ', '_')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)
print(f"Generated {len(protocols)} protocols successfully.")
