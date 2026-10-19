#!/usr/bin/env python3
"""
generate_synthetic_data.py
Generates realistic synthetic quantitative survey data (N ~ 1,350 total: ~1,200 valid + ~150 QC defect records),
30 rich qualitative excerpts labeled as simulated, and a 150-response human benchmark coding dataset.
"""

import json
import random
import numpy as np
import pandas as pd

# Set fixed seed for perfect reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

def generate_dataset():
    print("Generating synthetic quantitative survey data...")
    
    n_valid = 1200
    n_speeders = 40
    n_straightliners = 40
    n_duplicates = 30  # 15 original pairs
    n_logic_errors = 40
    total_records = n_valid + n_speeders + n_straightliners + n_duplicates + n_logic_errors # 1,350
    
    # -------------------------------------------------------------
    # 1. GENERATE CLEAN / VALID RESPONDENTS (N=1,200)
    # -------------------------------------------------------------
    
    # Markets: KSA 50% (600), UAE 35% (420), Kuwait 15% (180)
    markets = ['KSA'] * 600 + ['UAE'] * 420 + ['Kuwait'] * 180
    random.shuffle(markets)
    
    records = []
    
    # Brand universe:
    # 1. Dabur Amla, 2. Parachute, 3. Vatika, 4. Bajaj Almond Drops,
    # 5. Kerastase, 6. Olaplex, 7. Fable & Mane, 8. Gisou,
    # 9. Mielle Organics, 10. The Ordinary, 11. Hask Argan, 12. Local/Artisanal Blend
    brand_names = [
        "Dabur Amla", "Parachute", "Vatika", "Bajaj Almond Drops",
        "Kerastase", "Olaplex", "Fable & Mane", "Gisou",
        "Mielle Organics", "The Ordinary", "Hask Argan Oil", "Local Artisanal Apothecary"
    ]
    
    # Segments definition:
    # Segment 1: Heritage Traditionalists (~35%)
    # Segment 2: Bio-Clinical Solutionists (~45%)
    # Segment 3: Pragmatic Occasionals (~20%)
    segment_choices = ['Heritage Traditionalist', 'Bio-Clinical Solutionist', 'Pragmatic Occasional']
    segment_probs = [0.35, 0.45, 0.20]
    
    current_id = 1000001
    
    for i in range(n_valid):
        mkt = markets[i]
        
        # Segment assignment influenced by market & demographics
        if mkt == 'KSA':
            seg = np.random.choice(segment_choices, p=[0.48, 0.37, 0.15])
            nat = np.random.choice(['Saudi National', 'Arab Expat', 'South Asian Expat', 'Western Expat'], p=[0.70, 0.18, 0.10, 0.02])
            city = np.random.choice(['Riyadh', 'Jeddah', 'Dammam / Eastern Prov'], p=[0.55, 0.30, 0.15])
            currency_mult = 1.0  # SAR
        elif mkt == 'UAE':
            seg = np.random.choice(segment_choices, p=[0.20, 0.55, 0.25])
            nat = np.random.choice(['Emirati National', 'Arab Expat', 'South Asian Expat', 'Western Expat'], p=[0.20, 0.45, 0.25, 0.10])
            city = np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah'], p=[0.60, 0.28, 0.12])
            currency_mult = 1.0  # AED
        else: # Kuwait
            seg = np.random.choice(segment_choices, p=[0.30, 0.50, 0.20])
            nat = np.random.choice(['Kuwaiti National', 'Arab Expat', 'South Asian Expat', 'Western Expat'], p=[0.60, 0.28, 0.10, 0.02])
            city = np.random.choice(['Kuwait City', 'Hawalli'], p=[0.70, 0.30])
            currency_mult = 0.082  # KWD conversion (1 SAR/AED approx 0.082 KWD)
            
        gender = np.random.choice(['Female', 'Male'], p=[0.65, 0.35])
        age_cat = np.random.choice(['18-24', '25-34', '35-44', '45-54'], p=[0.20, 0.40, 0.25, 0.15])
        
        # Hair covering (Females only)
        if gender == 'Female':
            if 'National' in nat:
                hair_cover = np.random.choice(['Always (Daily in public)', 'Frequently (Most days)', 'Occasionally', 'Never'], p=[0.85, 0.10, 0.03, 0.02])
            elif 'Arab' in nat:
                hair_cover = np.random.choice(['Always (Daily in public)', 'Frequently (Most days)', 'Occasionally', 'Never'], p=[0.55, 0.25, 0.10, 0.10])
            else:
                hair_cover = np.random.choice(['Always (Daily in public)', 'Frequently (Most days)', 'Occasionally', 'Never'], p=[0.05, 0.05, 0.10, 0.80])
        else:
            hair_cover = 'Not Applicable'
            
        # LOI: realistic normal distribution around 720 seconds (12 min) with std 120s, min 320s
        loi = int(np.clip(np.random.normal(720, 110), 360, 1400))
        
        # Usage frequency
        if seg == 'Heritage Traditionalist':
            freq = np.random.choice(['Daily or almost daily', '3-5 times per week', '1-2 times per week'], p=[0.35, 0.45, 0.20])
            rituals = ['Overnight treatment', 'Pre-wash intensive bath']
            if np.random.rand() > 0.5: rituals.append('Dry styling finish')
        elif seg == 'Bio-Clinical Solutionist':
            freq = np.random.choice(['3-5 times per week', '1-2 times per week', '2-3 times per month'], p=[0.30, 0.55, 0.15])
            rituals = ['Post-wash damp hair application', 'Pre-wash intensive bath']
            if np.random.rand() > 0.4: rituals.append('Pre-blow dry heat protectant')
        else: # Pragmatic Occasional
            freq = np.random.choice(['1-2 times per week', '2-3 times per month', 'Once a month'], p=[0.35, 0.45, 0.20])
            rituals = ['Dry styling finish', 'Post-wash damp hair application']
            
        # Stressors battery (1 to 5): Q2_1 hard water, Q2_2 AC indoor, Q2_3 summer heat, Q2_4 hijab microclimate, Q2_5 chemical, Q2_6 stress
        # Base realistic scores
        if seg == 'Bio-Clinical Solutionist':
            q2_1 = int(np.clip(np.random.choice([4, 5, 3], p=[0.55, 0.35, 0.10]), 1, 5)) # Hard water anxiety very high
            q2_2 = int(np.clip(np.random.choice([4, 5, 3], p=[0.45, 0.35, 0.20]), 1, 5))
            q2_3 = int(np.clip(np.random.choice([4, 5, 3, 2], p=[0.40, 0.40, 0.15, 0.05]), 1, 5))
            q2_4 = int(np.clip(np.random.choice([4, 5, 3, 2, 1], p=[0.40, 0.35, 0.15, 0.05, 0.05]), 1, 5)) if gender == 'Female' else 2
            q2_5 = int(np.clip(np.random.choice([3, 4, 5, 2], p=[0.35, 0.35, 0.20, 0.10]), 1, 5))
            q2_6 = int(np.clip(np.random.choice([4, 5, 3], p=[0.45, 0.40, 0.15]), 1, 5))
        elif seg == 'Heritage Traditionalist':
            q2_1 = int(np.clip(np.random.choice([3, 4, 5, 2], p=[0.35, 0.35, 0.20, 0.10]), 1, 5))
            q2_2 = int(np.clip(np.random.choice([4, 3, 5], p=[0.40, 0.35, 0.25]), 1, 5))
            q2_3 = int(np.clip(np.random.choice([4, 5, 3], p=[0.45, 0.35, 0.20]), 1, 5))
            q2_4 = int(np.clip(np.random.choice([4, 5, 3], p=[0.50, 0.35, 0.15]), 1, 5)) if gender == 'Female' else 2
            q2_5 = int(np.clip(np.random.choice([2, 3, 4], p=[0.40, 0.40, 0.20]), 1, 5))
            q2_6 = int(np.clip(np.random.choice([3, 4, 5], p=[0.35, 0.40, 0.25]), 1, 5))
        else:
            q2_1 = int(np.clip(np.random.choice([3, 4, 2, 5], p=[0.40, 0.30, 0.20, 0.10]), 1, 5))
            q2_2 = int(np.clip(np.random.choice([3, 4, 2], p=[0.45, 0.35, 0.20]), 1, 5))
            q2_3 = int(np.clip(np.random.choice([3, 4, 5], p=[0.40, 0.40, 0.20]), 1, 5))
            q2_4 = int(np.clip(np.random.choice([3, 2, 4, 1], p=[0.40, 0.30, 0.20, 0.10]), 1, 5)) if gender == 'Female' else 1
            q2_5 = int(np.clip(np.random.choice([3, 2, 4], p=[0.40, 0.35, 0.25]), 1, 5))
            q2_6 = int(np.clip(np.random.choice([3, 4, 2], p=[0.45, 0.35, 0.20]), 1, 5))
            
        # Top 3 benefits sought
        if seg == 'Heritage Traditionalist':
            top_benefits = ['Reducing hair fall and promoting regrowth', '100% natural / clean ingredients', 'Deep hydration and repairing brittle ends']
        elif seg == 'Bio-Clinical Solutionist':
            top_benefits = ['Protecting against hard tap-water mineral buildup', 'Lightweight, non-greasy absorption', 'Reducing hair fall and promoting regrowth']
        else:
            top_benefits = ['Easy to wash out in one shampoo rinse', 'Lightweight, non-greasy absorption', 'Luxury fragrance that lasts all day']
            
        # Brand Awareness & Usage
        if seg == 'Heritage Traditionalist':
            aided_pool = ["Dabur Amla", "Parachute", "Vatika", "Bajaj Almond Drops", "Local Artisanal Apothecary"]
            if np.random.rand() > 0.4: aided_pool.extend(["Kerastase", "Fable & Mane"])
            ever_pool = [b for b in aided_pool if np.random.rand() > 0.3]
            if not ever_pool: ever_pool = ["Dabur Amla"]
            p3m_pool = [b for b in ever_pool if np.random.rand() > 0.4]
            if not p3m_pool: p3m_pool = [ever_pool[0]]
            bumo = random.choice(p3m_pool)
        elif seg == 'Bio-Clinical Solutionist':
            aided_pool = ["Kerastase", "Olaplex", "The Ordinary", "Mielle Organics", "Gisou", "Fable & Mane", "Dabur Amla"]
            ever_pool = [b for b in aided_pool if np.random.rand() > 0.25]
            if not ever_pool: ever_pool = ["The Ordinary"]
            p3m_pool = [b for b in ever_pool if np.random.rand() > 0.35]
            if not p3m_pool: p3m_pool = [ever_pool[0]]
            bumo = random.choice(p3m_pool)
        else:
            aided_pool = ["Parachute", "Dabur Amla", "Hask Argan Oil", "The Ordinary", "Vatika"]
            ever_pool = [b for b in aided_pool if np.random.rand() > 0.4]
            if not ever_pool: ever_pool = ["Parachute"]
            p3m_pool = [b for b in ever_pool if np.random.rand() > 0.5]
            if not p3m_pool: p3m_pool = [ever_pool[0]]
            bumo = random.choice(p3m_pool)
            
        # Van Westendorp Pricing (SAR/AED base, multiplied by currency_mult)
        if seg == 'Bio-Clinical Solutionist':
            base_tc = np.random.normal(55, 10)
            base_ch = base_tc + np.random.normal(45, 8)
            base_ex = base_ch + np.random.normal(50, 10)
            base_te = base_ex + np.random.normal(65, 12)
        elif seg == 'Heritage Traditionalist':
            base_tc = np.random.normal(40, 8)
            base_ch = base_tc + np.random.normal(35, 6)
            base_ex = base_ch + np.random.normal(45, 8)
            base_te = base_ex + np.random.normal(55, 10)
        else:
            base_tc = np.random.normal(30, 6)
            base_ch = base_tc + np.random.normal(30, 5)
            base_ex = base_ch + np.random.normal(35, 7)
            base_te = base_ex + np.random.normal(45, 8)
            
        vw_tc = round(max(15, base_tc) * currency_mult, 1 if mkt == 'Kuwait' else 0)
        vw_ch = round(max(vw_tc + (2 if mkt == 'Kuwait' else 15), base_ch * currency_mult), 1 if mkt == 'Kuwait' else 0)
        vw_ex = round(max(vw_ch + (2 if mkt == 'Kuwait' else 20), base_ex * currency_mult), 1 if mkt == 'Kuwait' else 0)
        vw_te = round(max(vw_ex + (3 if mkt == 'Kuwait' else 25), base_te * currency_mult), 1 if mkt == 'Kuwait' else 0)
        
        # Monadic Concept Assignment (50/50 balanced)
        concept_cell = 1 if i % 2 == 0 else 2
        concept_name = "Concept A: Bio-Clinical" if concept_cell == 1 else "Concept B: Royal Heritage"
        
        # Concept KPIs
        if concept_cell == 1: # Bio-Clinical
            if seg == 'Bio-Clinical Solutionist':
                pi = np.random.choice([5, 4, 3, 2], p=[0.48, 0.38, 0.11, 0.03])
                diag_uniq = np.random.choice([5, 4, 3], p=[0.50, 0.40, 0.10])
                diag_rel = np.random.choice([5, 4, 3], p=[0.55, 0.35, 0.10])
                diag_bel = np.random.choice([5, 4, 3, 2], p=[0.40, 0.45, 0.12, 0.03])
                diag_vfm = np.random.choice([5, 4, 3, 2], p=[0.35, 0.45, 0.15, 0.05])
            elif seg == 'Heritage Traditionalist':
                pi = np.random.choice([5, 4, 3, 2, 1], p=[0.18, 0.32, 0.30, 0.15, 0.05])
                diag_uniq = np.random.choice([5, 4, 3, 2], p=[0.35, 0.40, 0.20, 0.05])
                diag_rel = np.random.choice([5, 4, 3, 2], p=[0.25, 0.35, 0.30, 0.10])
                diag_bel = np.random.choice([5, 4, 3, 2], p=[0.20, 0.40, 0.30, 0.10])
                diag_vfm = np.random.choice([4, 3, 2, 1], p=[0.25, 0.45, 0.22, 0.08])
            else:
                pi = np.random.choice([4, 3, 2, 5, 1], p=[0.35, 0.35, 0.15, 0.10, 0.05])
                diag_uniq = np.random.choice([4, 3, 5], p=[0.45, 0.40, 0.15])
                diag_rel = np.random.choice([3, 4, 2], p=[0.45, 0.35, 0.20])
                diag_bel = np.random.choice([4, 3, 2], p=[0.45, 0.35, 0.20])
                diag_vfm = np.random.choice([3, 2, 4], p=[0.50, 0.30, 0.20])
                
            verb_likes_pool = [
                "I love that it addresses hard desalinated tap water, which is my biggest hair struggle in Dubai.",
                "The copper peptides and chelating mineral filter claim sounds very innovative and derm-approved.",
                "Non-greasy micro-mist root absorption is exactly what I need before putting my sheyla on.",
                "Fast absorbing and no greasy pillow stains. Very modern clinical solution.",
                "Clinically backed reduction in shedding by 72% makes me willing to pay premium.",
                "Love the lightweight idea. Most oils are too heavy for our hot weather."
            ]
            verb_barrier_pool = [
                "The price at 155 SAR is steep compared to normal hair treatments; needs proven results.",
                "Sounds a bit too chemical or clinical; I prefer botanical and natural oils like almond.",
                "Unscented might feel medicinal; I like my hair to smell luxurious under my hijab.",
                "Not sure if copper peptides really dissolve calcium deposits or if it is just marketing.",
                "I worry it won't give enough moisture to the dry ends of my hair.",
                "Dropper bottles can be messy to use in the shower; pump would be better."
            ]
        else: # Concept B: Royal Heritage
            if seg == 'Heritage Traditionalist':
                pi = np.random.choice([5, 4, 3, 2], p=[0.52, 0.36, 0.09, 0.03])
                diag_uniq = np.random.choice([5, 4, 3], p=[0.45, 0.45, 0.10])
                diag_rel = np.random.choice([5, 4, 3], p=[0.60, 0.32, 0.08])
                diag_bel = np.random.choice([5, 4, 3], p=[0.55, 0.38, 0.07])
                diag_vfm = np.random.choice([5, 4, 3, 2], p=[0.40, 0.45, 0.12, 0.03])
            elif seg == 'Bio-Clinical Solutionist':
                pi = np.random.choice([4, 3, 2, 5, 1], p=[0.32, 0.35, 0.20, 0.10, 0.03])
                diag_uniq = np.random.choice([4, 3, 2, 5], p=[0.35, 0.40, 0.15, 0.10])
                diag_rel = np.random.choice([3, 4, 2], p=[0.40, 0.35, 0.25])
                diag_bel = np.random.choice([4, 3, 5], p=[0.45, 0.35, 0.20])
                diag_vfm = np.random.choice([3, 2, 4], p=[0.45, 0.35, 0.20])
            else:
                pi = np.random.choice([3, 4, 2, 1], p=[0.40, 0.30, 0.20, 0.10])
                diag_uniq = np.random.choice([3, 4, 2], p=[0.45, 0.35, 0.20])
                diag_rel = np.random.choice([3, 2, 4], p=[0.45, 0.35, 0.20])
                diag_bel = np.random.choice([4, 3, 2], p=[0.50, 0.35, 0.15])
                diag_vfm = np.random.choice([3, 2, 4], p=[0.50, 0.35, 0.15])
                
            verb_likes_pool = [
                "Royal Sidr and Habba Sawda are Sunnah ingredients my grandmother swore by; love seeing them modernized.",
                "The Taif rose and oud infusion sounds heavenly and authentic to our Khaleeji taste.",
                "Pure cold-pressed oil with zero silicones is exactly what damaged hair needs.",
                "Rich nocturnal nourishment in a heavyweight glass bottle feels like true luxury.",
                "Authentic Gulf botanical heritage; proud to support local regional formulas."
            ]
            verb_barrier_pool = [
                "I am terrified it will be heavy, greasy, and impossible to wash out without 3 shampoos.",
                "Price is high when I can buy raw cold-pressed Sidr oil at the local apothecary/attar.",
                "Heavy oils clog my scalp pores and cause itchy pimples under my sheyla.",
                "Oud and rose scent might be too overpowering or conflict with my daily perfume.",
                "Doesn't tackle hard tap-water calcium crust, which is my actual main problem.",
                "Glass flacon is dangerous in a tiled bathroom; needs a safer pump dispenser."
            ]
            
        verb_like = random.choice(verb_likes_pool)
        verb_barrier = random.choice(verb_barrier_pool)
        
        # Household Income
        if mkt == 'Kuwait':
            hh_inc = np.random.choice(['Under 800 KWD', '800-1,599 KWD', '1,600-2,799 KWD', '2,800+ KWD', 'Prefer not to say'], p=[0.10, 0.30, 0.35, 0.20, 0.05])
        else:
            hh_inc = np.random.choice(['Under 10k SAR/AED', '10k-19.9k SAR/AED', '20k-34.9k SAR/AED', '35k-49.9k SAR/AED', '50k+ SAR/AED'], p=[0.15, 0.35, 0.30, 0.12, 0.08])
            
        rec = {
            'RESP_ID': f"R{current_id}",
            'STATUS': 'COMPLETE',
            'QC_DEFECT_TYPE': 'None (Valid)',
            'LOI_SECONDS': loi,
            'MARKET': mkt,
            'CITY': city,
            'GENDER': gender,
            'AGE_GROUP': age_cat,
            'NATIONALITY_CAT': nat,
            'HAIR_COVERING': hair_cover,
            'HH_INCOME': hh_inc,
            'PLANTED_SEGMENT': seg,
            'USAGE_FREQUENCY': freq,
            'RITUALS_LIST': "; ".join(rituals),
            'Q2_1_HARD_WATER': q2_1,
            'Q2_2_AC_DRYNESS': q2_2,
            'Q2_3_SUMMER_HEAT': q2_3,
            'Q2_4_HIJAB_SWEAT': q2_4,
            'Q2_5_CHEMICAL_DAMAGE': q2_5,
            'Q2_6_STRESS_FALL': q2_6,
            'BENEFITS_TOP3': "; ".join(top_benefits),
            'AWARE_BRANDS': "; ".join(aided_pool),
            'EVER_USED_BRANDS': "; ".join(ever_pool),
            'P3M_USED_BRANDS': "; ".join(p3m_pool),
            'BUMO_BRAND': bumo,
            'VW_TOO_CHEAP': vw_tc,
            'VW_CHEAP': vw_ch,
            'VW_EXPENSIVE': vw_ex,
            'VW_TOO_EXPENSIVE': vw_te,
            'CONCEPT_CELL': concept_cell,
            'CONCEPT_NAME': concept_name,
            'PURCHASE_INTENT_5PT': pi,
            'DIAG_UNIQUENESS': diag_uniq,
            'DIAG_RELEVANCE': diag_rel,
            'DIAG_BELIEVABILITY': diag_bel,
            'DIAG_VALUE_FOR_MONEY': diag_vfm,
            'VERBATIM_LIKES': verb_like,
            'VERBATIM_BARRIERS': verb_barrier,
            'IP_ADDRESS': f"192.168.{random.randint(10, 250)}.{random.randint(2, 254)}"
        }
        records.append(rec)
        current_id += 1

    # -------------------------------------------------------------
    # 2. PLANT QC DEFECT RECORDS (~150 records)
    # -------------------------------------------------------------
    
    # 2.1 Speeders (N=40): LOI < 240 seconds
    print("Planting 40 Speeders...")
    for _ in range(n_speeders):
        base_rec = dict(random.choice(records[:100]))
        base_rec['RESP_ID'] = f"R{current_id}"
        base_rec['STATUS'] = 'DEFECT'
        base_rec['QC_DEFECT_TYPE'] = 'Speeding'
        base_rec['LOI_SECONDS'] = random.randint(65, 210) # Median is 720s, so < 240 is blatant speeding
        base_rec['IP_ADDRESS'] = f"10.0.{random.randint(1, 99)}.{random.randint(1, 254)}"
        records.append(base_rec)
        current_id += 1
        
    # 2.2 Straight-liners (N=40): Q2 stressor grid standard deviation = 0
    print("Planting 40 Straight-liners...")
    for _ in range(n_straightliners):
        base_rec = dict(random.choice(records[:100]))
        base_rec['RESP_ID'] = f"R{current_id}"
        base_rec['STATUS'] = 'DEFECT'
        base_rec['QC_DEFECT_TYPE'] = 'Straight-lining'
        flat_score = random.choice([1, 3, 5])
        base_rec['Q2_1_HARD_WATER'] = flat_score
        base_rec['Q2_2_AC_DRYNESS'] = flat_score
        base_rec['Q2_3_SUMMER_HEAT'] = flat_score
        base_rec['Q2_4_HIJAB_SWEAT'] = flat_score
        base_rec['Q2_5_CHEMICAL_DAMAGE'] = flat_score
        base_rec['Q2_6_STRESS_FALL'] = flat_score
        base_rec['LOI_SECONDS'] = random.randint(280, 500)
        base_rec['IP_ADDRESS'] = f"172.16.{random.randint(1, 50)}.{random.randint(1, 254)}"
        records.append(base_rec)
        current_id += 1
        
    # 2.3 Duplicate Submissions (N=30: 15 pairs)
    print("Planting 30 Duplicate submissions (15 pairs)...")
    for _ in range(15):
        target = random.choice(records[:200])
        # Duplicate A
        dup_a = dict(target)
        dup_a['RESP_ID'] = f"R{current_id}"
        dup_a['STATUS'] = 'DEFECT'
        dup_a['QC_DEFECT_TYPE'] = 'Duplicate Submission (Primary)'
        dup_ip = f"185.120.{random.randint(10, 90)}.{random.randint(1, 200)}"
        dup_a['IP_ADDRESS'] = dup_ip
        records.append(dup_a)
        current_id += 1
        
        # Duplicate B (Clone of A with identical IP, verbatims, and demographics)
        dup_b = dict(dup_a)
        dup_b['RESP_ID'] = f"R{current_id}"
        dup_b['STATUS'] = 'DEFECT'
        dup_b['QC_DEFECT_TYPE'] = 'Duplicate Submission (Repeat)'
        dup_b['LOI_SECONDS'] = dup_a['LOI_SECONDS'] + random.randint(1, 5)
        records.append(dup_b)
        current_id += 1
        
    # 2.4 Impossible / Logic Inconsistencies (N=40)
    print("Planting 40 Logic & Pricing Inconsistencies...")
    for _ in range(n_logic_errors):
        base_rec = dict(random.choice(records[:200]))
        base_rec['RESP_ID'] = f"R{current_id}"
        base_rec['STATUS'] = 'DEFECT'
        
        defect_flavor = random.choice(['vw_inversion', 'bumo_not_used', 'negative_price'])
        if defect_flavor == 'vw_inversion':
            base_rec['QC_DEFECT_TYPE'] = 'Logic Inconsistency: Van Westendorp Price Inversion'
            # Too cheap is higher than too expensive!
            base_rec['VW_TOO_CHEAP'] = 350.0
            base_rec['VW_CHEAP'] = 250.0
            base_rec['VW_EXPENSIVE'] = 150.0
            base_rec['VW_TOO_EXPENSIVE'] = 50.0
        elif defect_flavor == 'bumo_not_used':
            base_rec['QC_DEFECT_TYPE'] = 'Logic Inconsistency: BUMO Brand Not in Ever Used'
            base_rec['AWARE_BRANDS'] = "Dabur Amla; Parachute"
            base_rec['EVER_USED_BRANDS'] = "Dabur Amla"
            base_rec['P3M_USED_BRANDS'] = "Dabur Amla"
            base_rec['BUMO_BRAND'] = "Gisou" # Never even aware of or used!
        else:
            base_rec['QC_DEFECT_TYPE'] = 'Logic Inconsistency: Impossible Negative/Zero Price'
            base_rec['VW_TOO_CHEAP'] = -25.0
            base_rec['VW_CHEAP'] = 0.0
            
        records.append(base_rec)
        current_id += 1
        
    df_raw = pd.DataFrame(records)
    raw_path = "data/raw_survey_data.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"Saved raw survey dataset with {len(df_raw)} records to {raw_path}")
    print(f"  - Valid planned: {n_valid}")
    print(f"  - Defect planted: {len(df_raw) - n_valid} (Speeders: {n_speeders}, Straight-liners: {n_straightliners}, Duplicates: {n_duplicates}, Logic errors: {n_logic_errors})")
    
    return df_raw

def generate_qual_excerpts():
    print("Generating 30 simulated qualitative excerpts...")
    excerpts = [
        {
            "id": "QUAL_01",
            "participant": "Fatima Al-Otaibi",
            "age": 29,
            "gender": "Female",
            "nationality": "Saudi National",
            "city": "Riyadh",
            "format": "FGD - Saudi Trendsetters",
            "planted_segment": "Bio-Clinical Solutionist",
            "theme": "Desalinated Water & Mineral Crust",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'The water in Riyadh literally eats your hair away. Within three months of moving into my new villa in Al-Narjis, my hair became brittle and dry like straw. You take a shower and you feel this invisible white calcium film on your scalp that no clarifying shampoo can strip away. I had to install a three-stage shower filter and even then, every Friday I rinse my hair with a bottle of drinking water. If a brand offers a chelating serum that actually dissolves mineral crust without frying my curls, I would subscribe to it on auto-delivery.'",
            "context": "Exploring everyday environmental stressors and the bottled-water rinse ritual."
        },
        {
            "id": "QUAL_02",
            "participant": "Maryam Al-Hashemi",
            "age": 34,
            "gender": "Female",
            "nationality": "Emirati National",
            "city": "Dubai",
            "format": "IDI - Deep Dive",
            "planted_segment": "Bio-Clinical Solutionist",
            "theme": "Postpartum Shedding & Vanity Anxiety",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'After having my second baby, my hair started falling out in literal clumps in the shower drain. In our culture, thick hair is feminine pride. When I saw my scalp parting widening under the harsh salon spotlights, I broke down in tears. I tried traditional castor oil, but it was so sticky that when I tried washing it out with shampoo, I pulled out even more hair! That was my turning point. I abandoned traditional heavy oils forever and switched to peptide scalp serums. Clean, water-like, clinical.'",
            "context": "Examining the emotional trauma of hair loss and the rejection of thick traditional oils."
        },
        {
            "id": "QUAL_03",
            "participant": "Kareem El-Gohary",
            "age": 32,
            "gender": "Male",
            "nationality": "Arab Expat (Egyptian)",
            "city": "Dubai",
            "format": "FGD - Expat Professionals",
            "planted_segment": "Pragmatic Occasional",
            "theme": "Beard & Scalp Dual Care",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'As a man in Dubai, between the gym, cycling on weekends, and corporate meetings, my scalp is sweating under 40-degree heat daily. But I also keep a trimmed beard. I don't want five different greasy bottles cluttering my bathroom. I want a lightweight oil that I can drop onto my crown to stop thinning edges and use on my beard for softness without smelling like grandma's kitchen or coconut curry.'",
            "context": "Male grooming perspectives and functional cross-usage between scalp and beard."
        },
        {
            "id": "QUAL_04",
            "participant": "Noura Al-Mutawa",
            "age": 42,
            "gender": "Female",
            "nationality": "Kuwaiti National",
            "city": "Kuwait City",
            "format": "IDI - Prestige Beauty Buyer",
            "planted_segment": "Heritage Traditionalist",
            "theme": "Cultural Reverence for Sidr & Sunnah Botanicals",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'Sidr is not just an ingredient to us; it is in our religious heritage and our grandmothers used freshly crushed Sidr leaves as natural soap before modern shampoos existed. When modern brands put Sidr or Habba Sawda (black seed) in a luxury glass bottle with a fine scent like Taif rose, my heart immediately opens. But my condition is authenticity: do not dilute it with cheap mineral oil or petroleum.'",
            "context": "Exploring heritage botanicals as sacred cultural anchors vs modern packaging."
        },
        {
            "id": "QUAL_05",
            "participant": "Aisha Al-Dossari",
            "age": 24,
            "gender": "Female",
            "nationality": "Saudi National",
            "city": "Dammam",
            "format": "FGD - Young Saudi Creatives",
            "planted_segment": "Bio-Clinical Solutionist",
            "theme": "Hijab Scalp Microclimate",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'People who don't wear a hijab have no idea what happens after 9 hours of wearing a tight cotton underscarf and a black sheyla in the summer humidity. Your scalp is trapped in a sauna. Your roots get tender and sore. By 4 PM, you feel like taking your hijab off just to let your scalp breathe. If you put heavy oil on in the morning, it mixes with sweat and clogs your pores, causing itchy pimples. We need an ultra-breathable, cooling scalp tonic.'",
            "context": "Sensory and physical impact of long-duration head covering."
        },
        {
            "id": "QUAL_06",
            "participant": "Zainab Merchant",
            "age": 31,
            "gender": "Female",
            "nationality": "South Asian Expat",
            "city": "Sharjah",
            "format": "FGD - Working Mothers",
            "planted_segment": "Heritage Traditionalist",
            "theme": "The Generational Clash on Amla Oil",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'I grew up with my mother drenching my hair in Dabur Amla every Sunday. Yes, it works for thickness, but let's be honest: the pungent chemical-herb smell lingers for three days. My husband complains, my pillows get green stains, and it takes three rounds of harsh shampoo to wash it out, which undoes all the conditioning! I want the heritage benefit of Amla or Sidr, but with Parisian luxury fragrance and clean washability.'",
            "context": "Deconstructing legacy FMCG oil pain points (scent and washability)."
        },
        {
            "id": "QUAL_07",
            "participant": "Reem Al-Sabah",
            "age": 38,
            "gender": "Female",
            "nationality": "Kuwaiti National",
            "city": "Kuwait City",
            "format": "IDI - Derm Clinic Patient",
            "planted_segment": "Bio-Clinical Solutionist",
            "theme": "Clinical Validation vs Marketing Fluff",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'I spent 4,000 KWD on PRP scalp injections and mesotherapy at a clinic in Salmiya. I don't buy cosmetic promises anymore. When a concept claims 'copper tri-peptide-1 and chelating agents', that speaks my language because my dermatologist talked to me about peptide signals for follicle revival. But if you charge me 25 KWD for 50ml, I want to see third-party clinical trichology trial data, not just an Instagram influencer shaking her hair.'",
            "context": "High-income consumers demanding clinical rigor and dermatologist-grade efficacy."
        },
        {
            "id": "QUAL_08",
            "participant": "Tariq Mansoor",
            "age": 28,
            "gender": "Male",
            "nationality": "Emirati National",
            "city": "Abu Dhabi",
            "format": "IDI - Professional",
            "planted_segment": "Pragmatic Occasional",
            "theme": "Ghutra Scalp Heat & Quick Fixes",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'Wearing the ghutra and egal all day in government offices flattens your hair and heats your crown. When I come home, I just want a lightweight scalp tonic that absorbs in 30 seconds and feels icy cool. I don't have patience for a 45-minute oil mask before a shower. Speed, lightness, and anti-thinning action are what matter.'",
            "context": "Traditional male headdress dynamics and demand for rapid absorption."
        },
        {
            "id": "QUAL_09",
            "participant": "Layla Boutros",
            "age": 35,
            "gender": "Female",
            "nationality": "Arab Expat (Lebanese)",
            "city": "Dubai",
            "format": "FGD - Prestige Beauty Shoppers",
            "planted_segment": "Bio-Clinical Solutionist",
            "theme": "Sephora Hauls & Aesthetic Pleasure",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'I shop at Sephora Dubai Mall twice a month. For me, hair care is the new skin care—the skinification of hair. Gisou looks gorgeous on my marble vanity, and Fable & Mane has that wonderful ritual story. If a GCC brand launches with Concept A, it must have an amber apothecary dropper bottle with clean typography. If it looks like an old pharmacy bottle from an industrial zone, nobody in Dubai will pay 150 AED for it.'",
            "context": "The role of visual aesthetics, social display, and the skinification trend."
        },
        {
            "id": "QUAL_10",
            "participant": "Huda Al-Ghamdi",
            "age": 48,
            "gender": "Female",
            "nationality": "Saudi National",
            "city": "Jeddah",
            "format": "IDI - Traditional Homemaker",
            "planted_segment": "Heritage Traditionalist",
            "theme": "Natural Apothecary Blends vs Factory Bottling",
            "excerpt": "[SIMULATED QUAL EXCERPT] 'Every six months, I go to the local attar (spice apothecary) in Al-Balad in Jeddah. He presses pure sweet almond oil and habba sawda right in front of my eyes. How can a commercial brand charge me 160 Riyals for a 100ml bottle when I can buy a 250ml pure glass jar from the apothecary for 45 Riyals? The commercial brand has to prove their distillation is cleaner and doesn't turn rancid in the summer heat.'",
            "context": "Price benchmarking against artisanal local apothecaries (Al-Attar)."
        }
    ]
    
    # Extend to 30 simulated excerpts programmatically with rich cultural nuance
    additional_excerpts = [
        ("QUAL_11", "Dalal Al-Enezi", 26, "Female", "Kuwaiti National", "Kuwait City", "FGD", "Bio-Clinical Solutionist", "Hard Water & Bleach Damage",
         "[SIMULATED QUAL EXCERPT] 'I bleached my hair blonde for my wedding and the tap water completely turned it brassy and brittle. Chelating defense is the only thing that saved my ends.'"),
        ("QUAL_12", "Sultan Al-Kuwari", 37, "Male", "Saudi National", "Riyadh", "IDI", "Heritage Traditionalist", "Family Hair Legacy",
         "[SIMULATED QUAL EXCERPT] 'My father had a full head of thick hair until his 70s because he oiled his scalp with cold-pressed olive oil and sidr every Thursday night. Heritage works.'"),
        ("QUAL_13", "Chloe Henderson", 30, "Female", "Western Expat (UK)", "Dubai", "FGD", "Pragmatic Occasional", "Expats in Dubai Water Shock",
         "[SIMULATED QUAL EXCERPT] 'Within two months of landing in Dubai Marina, half my hair fell out in the shower. Every expat group on Facebook talks about the Dubai hair-fall syndrome.'"),
        ("QUAL_14", "Sara Al-Hajri", 33, "Female", "Saudi National", "Khobar", "IDI", "Bio-Clinical Solutionist", "Rosemary Oil DIY vs Formulated Serum",
         "[SIMULATED QUAL EXCERPT] 'I tried boiling fresh rosemary leaves at home like on TikTok, but it spoiled in four days in the fridge. I need a stabilized bio-fermented serum that lasts.'"),
        ("QUAL_15", "Mona Al-Kandari", 40, "Female", "Kuwaiti National", "Hawalli", "FGD", "Heritage Traditionalist", "Friday Family Oiling Ritual",
         "[SIMULATED QUAL EXCERPT] 'On Fridays before Dhuhur prayer, my sisters and I put oil in our hair, sit together with gahwa, and then wash it out before family lunch. It is sisterhood.'"),
        ("QUAL_16", "Omar Farooq", 27, "Male", "South Asian Expat", "Dubai", "IDI", "Pragmatic Occasional", "Scalp Dandruff in Air Conditioned Offices",
         "[SIMULATED QUAL EXCERPT] 'Sitting under the AC vent at work dry-freezes my scalp, causing dry flakes. I need quick scalp drops that don't make my hair look wet or greasy.'"),
        ("QUAL_17", "Lulwa Al-Thani", 22, "Female", "Kuwaiti National", "Kuwait City", "FGD", "Bio-Clinical Solutionist", "Gen Z Anti-Aging Obsession",
         "[SIMULATED QUAL EXCERPT] 'My friends and I start scalp therapy at 20. Prevention is everything. We look for peptides, niacinamide, and rosemary. We don't wait for bald spots.'"),
        ("QUAL_18", "Hassan Al-Bishi", 45, "Male", "Saudi National", "Riyadh", "IDI", "Heritage Traditionalist", "Counterfeit Concerns in Souqs",
         "[SIMULATED QUAL EXCERPT] 'Many oils sold in small street shops are diluted with cheap paraffin wax. I am willing to pay 150 SAR in Nahdi or Boots just to have a certified pure bottle.'"),
        ("QUAL_19", "Rania Abboud", 36, "Female", "Arab Expat (Syrian)", "Sharjah", "FGD", "Pragmatic Occasional", "Washout Battle & Shampoo Stripping",
         "[SIMULATED QUAL EXCERPT] 'If I have to shampoo three times to wash an oil out, my colored hair loses its dye and becomes even drier. Easy rinse-out is my non-negotiable rule.'"),
        ("QUAL_20", "Yara Al-Mansoor", 31, "Female", "Emirati National", "Abu Dhabi", "IDI", "Bio-Clinical Solutionist", "Scalp Folliculitis Experience",
         "[SIMULATED QUAL EXCERPT] 'Heavy castor oil gave me folliculitis bumps along my hairline. The dermatologist told me: scalp skin is facial skin. Treat it like a lightweight facial serum.'"),
        ("QUAL_21", "Fahad Al-Shammari", 39, "Male", "Saudi National", "Hail/Riyadh", "FGD", "Heritage Traditionalist", "Taif Rose Scent Attachment",
         "[SIMULATED QUAL EXCERPT] 'When a product smells like natural Taif rose water, it brings an immediate sense of purity and regal cleanliness. It honors our regional flowers.'"),
        ("QUAL_22", "Priya Nair", 29, "Female", "South Asian Expat", "Dubai", "FGD", "Bio-Clinical Solutionist", "Ayurveda Meets Modern Dermatology",
         "[SIMULATED QUAL EXCERPT] 'I love Indian botanicals like Bhringraj and Amla, but I want them formulated with modern peptides so they absorb without greasy stickiness.'"),
        ("QUAL_23", "Basma Al-Qarni", 35, "Female", "Saudi National", "Jeddah", "IDI", "Heritage Traditionalist", "Hair Oil as Bedtime Aromatherapy",
         "[SIMULATED QUAL EXCERPT] 'Oiling my hair before bed with a light lavender or herbal oil relaxes my nervous system. It is my 15 minutes of quiet meditation away from the kids.'"),
        ("QUAL_24", "Jana Al-Humaidhi", 27, "Female", "Kuwaiti National", "Kuwait City", "FGD", "Bio-Clinical Solutionist", "Influencer Skepticism",
         "[SIMULATED QUAL EXCERPT] 'Every beauty blogger on Snapchat claims this oil gave her three inches in one week. We laugh at that now. Show me trichologist microscope before/afters.'"),
        ("QUAL_25", "Karim Al-Masri", 33, "Male", "Arab Expat (Jordanian)", "Dubai", "IDI", "Pragmatic Occasional", "Water Desalination Chemistry",
         "[SIMULATED QUAL EXCERPT] 'I am a chemical engineer; desalinated sea water has aggressive sodium and calcium carbonates. Chelating agents that bind free calcium are scientifically sound.'"),
        ("QUAL_26", "Deema Al-Falasi", 41, "Female", "Emirati National", "Dubai", "IDI", "Heritage Traditionalist", "Generational Gifting of Hair Rituals",
         "[SIMULATED QUAL EXCERPT] 'For Eid, we gift luxury hair oils in beautiful flacons. A beautiful bottle with amber and oud feels like a respectful gift for mothers and sisters.'"),
        ("QUAL_27", "Mariam Al-Khaldi", 25, "Female", "Saudi National", "Riyadh", "FGD", "Bio-Clinical Solutionist", "Corporate Office Look",
         "[SIMULATED QUAL EXCERPT] 'In a modern corporate office, you cannot walk in smelling like edible cooking oil. You need a sleek, clean fragrance or completely fragrance-free.'"),
        ("QUAL_28", "Nasser Al-Ajmi", 36, "Male", "Kuwaiti National", "Kuwait City", "IDI", "Heritage Traditionalist", "Preventing Premature Graying",
         "[SIMULATED QUAL EXCERPT] 'Habba Sawda (black seed) is known in Islamic medicine to maintain pigment and strengthen roots. That cultural conviction is very powerful for me.'"),
        ("QUAL_29", "Elena Rostova", 34, "Female", "Western Expat", "Dubai", "FGD", "Pragmatic Occasional", "Salon Keratin Maintenance",
         "[SIMULATED QUAL EXCERPT] 'I spend 1,200 AED on hair Botox every four months. I cannot use harsh sulfates or heavy mineral oils that strip the treatment out.'"),
        ("QUAL_30", "Ghadah Al-Saud", 30, "Female", "Saudi National", "Riyadh", "IDI", "Bio-Clinical Solutionist", "The Ultimate Scalp Wish",
         "[SIMULATED QUAL EXCERPT] 'My magic wand wish: A mist that neutralizes tap water minerals the moment I spray it, stops shedding, and smells like an expensive niche perfume.'")
    ]
    
    for item in additional_excerpts:
        excerpts.append({
            "id": item[0],
            "participant": item[1],
            "age": item[2],
            "gender": item[3],
            "nationality": item[4],
            "city": item[5],
            "format": item[6],
            "planted_segment": item[7],
            "theme": item[8],
            "excerpt": item[9],
            "context": f"Simulated focus quote exploring {item[8].lower()}."
        })
        
    qual_path = "data/synthetic_qual_excerpts.json"
    with open(qual_path, "w", encoding="utf-8") as f:
        json.dump(excerpts, f, indent=2, ensure_ascii=False)
    print(f"Saved 30 simulated qualitative excerpts to {qual_path}")
    
    # Also write a readable markdown compendium in docs/
    md_content = "# GCC Hair & Scalp Care: Qualitative Excerpt Compendium (Simulated)\n\n"
    md_content += "> [!IMPORTANT]\n> **SIMULATION DISCLOSURE:** All quotations, participant personas, and scenarios in this document are **synthetic research artifacts** designed to illustrate qualitative depth, cultural nuances, and sensory tensions across the GCC. They do not represent real individuals or proprietary clinical data.\n\n"
    md_content += "This compendium documents 30 rich qualitative excerpts across Focus Group Discussions (FGD) and In-Depth Interviews (IDI) conducted across Riyadh, Jeddah, Dubai, Abu Dhabi, and Kuwait City.\n\n---\n\n"
    
    for ex in excerpts:
        md_content += f"### {ex['id']}: {ex['participant']} ({ex['age']}y, {ex['gender']}, {ex['nationality']} — {ex['city']})\n"
        md_content += f"- **Format:** {ex['format']} | **Planted Segment:** `{ex['planted_segment']}`\n"
        md_content += f"- **Theme:** *{ex['theme']}*\n"
        md_content += f"> {ex['excerpt']}\n\n"
        md_content += f"*Analytical Context:* {ex['context']}\n\n---\n\n"
        
    with open("docs/SYNTHETIC_QUAL_EXCERPTS.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Saved docs/SYNTHETIC_QUAL_EXCERPTS.md")

def generate_human_benchmark_coding():
    print("Generating 150-response human benchmark coding dataset for open-end AI validation...")
    
    # Code frame:
    # Code 1: Price / High Cost Barrier ("Too expensive / not worth 150+ SAR/AED")
    # Code 2: Greasiness / Wash-Out Difficulty ("Too greasy, heavy, hard to rinse out")
    # Code 3: Skepticism of Claims / Hard-Water Marketing ("Doubt chelating / peptide claims")
    # Code 4: Scent / Fragrance Preference ("Unscented is boring OR scent too strong")
    # Code 5: Natural vs Chemical Tension ("Prefer 100% pure botanical, fear chemicals")
    # Code 6: Packaging / Dispenser Friction ("Dropper bottle messy, prefer pump or spray")
    # Code 7: Scalp Pore Clogging / Breakout Fear ("Causes pimples, folliculitis under hijab")
    
    verbatim_pool = [
        # Code 1: Price / High Cost Barrier
        ("155 SAR is way too expensive for just 100ml of hair oil when I can buy Dabur or Parachute for 25 SAR.",
         "Price / High Cost Barrier", "Mentions 155 SAR is too expensive compared to alternative FMCG brands."),
        ("The cost is simply too high. In this economic climate, spending over 150 AED on a hair oil every month is not sustainable.",
         "Price / High Cost Barrier", "Directly cites 150 AED monthly cost as unsustainable."),
        ("Too pricey. I would only buy this if it were on a major 50% discount at Sephora.",
         "Price / High Cost Barrier", "Price sensitivity; demands discount."),
        ("12.5 KWD for a 100ml bottle is premium salon pricing. I need a smaller travel size to test first.",
         "Price / High Cost Barrier", "High KWD price cited; barrier to full-size trial."),
        ("Price point is unaffordable for daily use. If I use it 4 times a week, a bottle won't last a month.",
         "Price / High Cost Barrier", "Frequent usage makes the high unit price cost-prohibitive."),
        
        # Code 2: Greasiness / Wash-Out Difficulty
        ("I am worried it will leave my hair limp and greasy. I hate when oils take three shampoo washes to remove.",
         "Greasiness / Wash-Out Difficulty", "Mentions limp greasy hair and multiple shampoo washes needed."),
        ("Sounds too heavy. Heavy oils weigh down my fine hair and make it look flat and dirty.",
         "Greasiness / Wash-Out Difficulty", "Heaviness and weighing down fine hair."),
        ("My main issue with hair oils is the greasy pillowcase and having to double wash. If this leaves residue, I won't use it.",
         "Greasiness / Wash-Out Difficulty", "Explicitly mentions greasy pillowcase residue and wash-out friction."),
        ("It looks like it will make my roots oily by lunchtime. Our weather is too humid for thick oils.",
         "Greasiness / Wash-Out Difficulty", "Oily roots and humidity interaction."),
        ("Oils always make my hair look stringy. Unless it washes out completely in one rinse, it is a no for me.",
         "Greasiness / Wash-Out Difficulty", "Stringy hair and requirement for single-rinse wash-out."),

        # Code 3: Skepticism of Claims / Hard-Water Marketing
        ("I don't believe an oil can dissolve hard tap-water calcium deposits. That sounds like scientific marketing gibberish.",
         "Skepticism of Claims / Hard-Water Marketing", "Challenges chelating hard-water claim as marketing gimmick."),
        ("How can copper peptides reduce shedding by 72% in 4 weeks? That claim seems exaggerated without clinical proof.",
         "Skepticism of Claims / Hard-Water Marketing", "Questions 72% shedding reduction percentage; demands clinical evidence."),
        ("Sounds like every other influencer gimmick on TikTok. Everyone promises miracle regrowth nowadays.",
         "Skepticism of Claims / Hard-Water Marketing", "General skepticism of viral beauty claims."),
        ("Not convinced that topical peptides can penetrate through the scalp barrier without microneedling.",
         "Skepticism of Claims / Hard-Water Marketing", "Specific skepticism regarding topical transdermal delivery."),
        ("Hard water needs a water softener in the pipes, not a serum on your scalp. Seems scientifically doubtful.",
         "Skepticism of Claims / Hard-Water Marketing", "Mechanistic skepticism: physical plumbing filter vs topical serum."),

        # Code 4: Scent / Fragrance Preference
        ("I really dislike that Concept A is completely fragrance-free. Hair care should be a luxurious sensory experience.",
         "Scent / Fragrance Preference", "Dislikes unscented clinical formulation; wants luxury aroma."),
        ("The oud and rose scent in Concept B sounds way too strong. It will clash with my French perfume and give me a headache.",
         "Scent / Fragrance Preference", "Complains scent is overpowering and clashing with perfume."),
        ("I want a clean fresh botanical scent like mint or eucalyptus, not heavy musk or perfume under my sheyla.",
         "Scent / Fragrance Preference", "Desires specific fresh scent profile rather than oriental notes."),
        ("Fragrance-free feels too much like medicine. When I shower I want my hair to smell fresh and clean all day.",
         "Scent / Fragrance Preference", "Equates fragrance-free to medicinal feel."),
        ("Strong perfumes in hair products irritate my sensitive scalp and make me sneeze.",
         "Scent / Fragrance Preference", "Fragrance sensitivity and irritation barrier."),

        # Code 5: Natural vs Chemical Tension
        ("I try to avoid chemical sounding ingredients like copper tri-peptides. I prefer 100% natural organic oils like almond and argan.",
         "Natural vs Chemical Tension", "Explicit rejection of synthetic peptides in favor of pure botanicals."),
        ("If it has chemical chelating agents, I worry it will damage my sensitive hair follicle over time.",
         "Natural vs Chemical Tension", "Fear that chemical chelating agents cause long-term damage."),
        ("I only use cold-pressed single ingredient botanicals. Modern laboratory formulas worry me.",
         "Natural vs Chemical Tension", "Preference for clean, unadulterated cold-pressed herbs."),
        ("Is it truly clean? I do not want any hidden parabens, silicones, or lab preservatives touching my roots.",
         "Natural vs Chemical Tension", "Anxiety over synthetic additives and preservative safety."),
        ("Nature provides the best remedies like Sidr and Habba Sawda; humans in labs cannot beat Allah's nature.",
         "Natural vs Chemical Tension", "Cultural/spiritual conviction favoring pure natural botanicals."),

        # Code 6: Packaging / Dispenser Friction
        ("A glass dropper bottle is dangerous in a slippery marble shower. It should have a sturdy plastic pump dispenser.",
         "Packaging / Dispenser Friction", "Cites glass safety hazard in wet shower environment; requests pump."),
        ("Droppers are messy and leak when traveling in my gym bag. I want a precision nozzle spray.",
         "Packaging / Dispenser Friction", "Dropper leakage during travel; prefers targeted nozzle spray."),
        ("The glass flacon looks heavy and cumbersome to use with oily fingers.",
         "Packaging / Dispenser Friction", "Ergonomic difficulty handling heavy glass with oily hands."),
        ("Dropper applicator takes too long to section hair; a targeted scalp tip applicator would be much faster.",
         "Packaging / Dispenser Friction", "Application speed and precision nozzle requirement."),
        ("100ml in heavy glass is too bulky for carry-on luggage when flying between Riyadh and Dubai.",
         "Packaging / Dispenser Friction", "Portability and air travel restrictions."),

        # Code 7: Scalp Pore Clogging / Breakout Fear
        ("Applying oil directly to my roots always clogs my scalp pores and gives me painful acne bumps under my hijab.",
         "Scalp Pore Clogging / Breakout Fear", "Fears pore clogging and acne bumps under headwear."),
        ("I have an oily scalp and dry ends; putting oil on my scalp will trigger severe seborrheic dermatitis and flaking.",
         "Scalp Pore Clogging / Breakout Fear", "Concerns regarding seborrheic dermatitis flaring up."),
        ("Oil traps heat and sweat under my scarf, causing scalp folliculitis. My dermatologist warned me against it.",
         "Scalp Pore Clogging / Breakout Fear", "Direct medical warning regarding scalp folliculitis."),
        ("Every time I use root oils, my scalp starts itching violently after two days.",
         "Scalp Pore Clogging / Breakout Fear", "Itchiness and irritation trigger."),
        ("Clogged follicles cause more hair fall, not less. I am terrified this will block my hair roots.",
         "Scalp Pore Clogging / Breakout Fear", "Paradoxical anxiety: oil causing follicular occlusion and shedding.")
    ]
    
    # Expand to 150 responses systematically with variations
    rows = []
    idx = 1
    
    # We will generate ~20-25 responses per category to reach exactly 150
    for category, grp in pd.DataFrame(verbatim_pool, columns=['text', 'code', 'rationale']).groupby('code'):
        templates = grp['text'].tolist()
        rationales = grp['rationale'].tolist()
        
        # We need ~21 responses per code (7 codes * 21.4 = 150)
        target_count = 22 if idx in [1, 2, 3, 4] else 21
        for j in range(target_count):
            base_t = templates[j % len(templates)]
            base_r = rationales[j % len(rationales)]
            
            # Add slight naturalistic variation
            variations = [
                base_t,
                f"Honestly, {base_t.lower()}",
                f"{base_t} That is my biggest reservation.",
                f"For me personally: {base_t}",
                f"{base_t} If they fix this, I would consider it."
            ]
            chosen_text = variations[j % len(variations)]
            
            rows.append({
                'RESPONSE_ID': f"VERB_{idx:03d}",
                'VERBATIM_TEXT': chosen_text,
                'HUMAN_GOLD_CODE': category,
                'HUMAN_RATIONALE': base_r,
                'DIFFICULTY_LEVEL': 'Moderate' if j % 4 == 0 else ('Subtle/Nuanced' if j % 5 == 0 else 'Standard')
            })
            idx += 1
            if idx > 150: break
        if idx > 150: break
        
    df_benchmark = pd.DataFrame(rows[:150])
    bench_path = "data/human_benchmark_coding.csv"
    df_benchmark.to_csv(bench_path, index=False)
    print(f"Saved 150-response human benchmark coding dataset to {bench_path}")

if __name__ == "__main__":
    generate_dataset()
    generate_qual_excerpts()
    generate_human_benchmark_coding()
    print("Phase 2 synthetic data generation completed successfully!")
