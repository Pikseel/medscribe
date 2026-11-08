# Rollu / rolsuz SOAP note comparison
## Summary

| Dialogue | Rollu negation flags | Rolsuz negation flags |
|---|---|---|
| aci_001 | 1 | 2 |
| aci_002 | 0 | 0 |
| aci_003 | 4 | 2 |


## aci_001

**Reference note** (2182 chars)

```
CHIEF COMPLAINT

Kidney stones.

HISTORY OF PRESENT ILLNESS

Mason Ward is a pleasant 80-year-old male who presents to the clinic today for the evaluation of kidney stones. The patient was referred from his primary care physician. The onset of his pain began 1 week ago when he was in his barn moving hay when he had a sudden onset of right back pain. The patient initially thought his pain was due to throwing hay; however, he broke out into a sweat and became nauseated. He was seen by his primary care physician, who ordered a CT scan and told him that he had a kidney stone. He denies having kidney stones before, but states that his father has a history of kidney stones in the past. He explains that when he had pain, which has now resolved, it would radiate almost to his groin. The patient describes the pain as intermittent after he found out it was a kidney stone. He explains that he has been straining his urine, but has not seen anything. He denies any hematuria.

REVIEW OF SYSTEMS

Musculoskeletal: Reports right back pain.

VITALS

Vitals look good, blood pressure and hear rate are within normal limits. Temperature is within normal limits.

PHYSICAL EXAM

MSK: Examination of the abdomen: No pain with palpation of the abdomen. No rebound or guarding. There is CVA tenderness on the right side.

RESULTS

The CT scan of the abdomen revealed a stone that is measuring 0.5 cm located in the proximal right ureter. There is no evidence of hydronephrosis.

ASSESSMENT

Right kidney stone.

PLAN

We reviewed the patient's CT results in detail today. I have recommended that we treat the patient conservatively. I have prescribed the patient oxycodone 5 mg every 6 to 8 hours for pain. He may continue to take Tylenol between the oxycodone doses for any breakthrough pain. The patient should continue to use the strainer when he urinates until the stone passes. I have also recommended that we obtain a BMP, urinalysis, and urine culture to evaluate for any signs of infection.

INSTRUCTIONS

The patient will follow up with me in 1 to 2 weeks to check on his progress. If his symptoms have not improved, we will discuss further treatment options including lithotripsy.
```

### With roles (gold_role) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** patient had a sudden onset of pain in the right back about a week ago while working in the barn. The pain radiated to the groin and was accompanied by nausea. Pain comes and goes, and patient has been straining urine but not seeing anything in the cup. No blood in urine. Father had kidney stones in the past, but patient has never had them before. Patient had a CT scan which showed a 0.5 cm stone in the proximal right ureter.

**O.** vital signs looked good, no fever, blood pressure and heart rate were fine. Abdominal examination showed no tenderness, no rebound or guarding, but tenderness on the right side. CT scan showed a 0.5 cm stone in the proximal right ureter, no evidence of hydronephrosis.

**A.** patient has a kidney stone in the proximal right ureter, no evidence of hydronephrosis. Plan includes pushing fluids, oxycodone 5 mg every 6-8 hours for pain, and acetaminophin for breakthrough pain. Urinalysis, BMP, and urine culture ordered. Follow-up in 1-2 weeks to check if stone has passed. Discuss lithotripsy if stone hasn't passed by then.

**P.** patient to continue using the strainer, take prescribed medications, and follow up in 1-2 weeks. Nurse will bring the prescription.

**Negation flags: 1**
- reference has *"no pain with palpation of the abdomen"* → note says: _patient had a sudden onset of pain in the right back about a week ago while working in the barn._

Words absent from the reference (28): abdominal, about, accompanied, acetaminophin, bring, com, cup, fever, fine, fluid, goe, hasn't, heart, includ, looked, medication, nausea, nurse, passed, prescription

### Without roles (None) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** Patient presented with sudden onset of pain in the right back about a week ago while working in the barn. The pain radiated to the groin and was accompanied by nausea. Pain has since subsided, but patient experiences intermittent pain. No blood in urine. Father has had kidney stones in the past, but patient has never had them before. CT scan confirmed a 0.5 cm stone in the proximal right ureter.

**O.** Vitals: good, no fever, blood pressure and heart rate within normal limits. Abdominal examination: no tenderness to palpation, no rebound or guarding, tenderness on the right side. CT scan shows a 0.5 cm stone in the proximal right ureter, no evidence of hydronephrosis.

**A.** Patient has a kidney stone in the proximal right ureter. Plan includes fluid intake to facilitate passage of the stone, oxycodone 5 mg every 6-8 hours for pain, and acetaminophin for breakthrough pain. Urinalysis, BMP, and urine culture ordered to check for infection. Follow-up in one to two weeks to assess stone passage. Lithotripsy may be considered if the stone has not passed by then.

**P.** Patient to continue using a strainer. Schedule follow-up in one to two weeks. Nurse will bring the prescription.

**Negation flags: 2**
- reference has *"denies having kidney stones before"* → note says: _Patient has a kidney stone in the proximal right ureter._
- reference has *"no pain with palpation of the abdomen"* → note says: _Patient presented with sudden onset of pain in the right back about a week ago while working in the barn._

Words absent from the reference (32): abdominal, about, accompanied, acetaminophin, asses, bring, confirmed, considered, experienc, facilitate, fever, fluid, heart, includ, intake, nausea, nurse, one, passage, passed

## aci_002

**Reference note** (1154 chars)

```
CHIEF COMPLAINT

Itchy scalp pain.

REVIEW OF SYSTEMS

Constitutional: Denies fever or weight loss.
HENT: Reports scalp pain Musculoskeletal: Denies joint pain.
Skin: Reports itchy scalp Denies any rashes.

VITALS

BP: 130/68.
HR: 98.
RR:18.
Temperature is 97.7 today.

PHYSICAL EXAM

Integumentary
- Examination: Scalp reveals demarcated scaly, erythematous plaques. They are patchy in format and diffusely present across the back of the skull.

ASSESSMENT AND PLAN

1. Scalp psoriasis.
- Medical Reasoning: The patient presents today with symptoms similar to scalp psoriasis.
- Patient Education and Counseling: Nature of the diagnosis was discussed as well as treatment options. Patient was advised there is no cure for this. Patient was counseled on how to apply clobetasol 0.05%.
- Medical Treatment: Prescription for clobetasol 0.05% solution twice daily provided. Continuing using T/Gel shampoo. Prescription for steroids provided to be used for flare ups.

Patient Agreements: The patient understands and agrees with the recommended medical treatment plan.

INSTRUCTIONS

The patient will follow-up in 3 months or sooner if her conditions worsen.
```

### With roles (gold_role) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** itchy scalp, dandruff, embarrassing, itching, dry scalp, no joint pain, no fever, no weight loss, no rashes elsewhere, no new hair products, no new stressors, family history of similar symptoms in sister, long-standing issue, worsening in past 6 months

**O.** blood pressure 130/68, heart rate 98, respiratory rate 18, temperature 97.7, demarcated scaly erythematous plaques on scalp, diffusely present across back of skull, white dander on clothes

**A.** scalp psoriasis

**P.** prescribed clobetasol 0.05% solution to apply twice daily on affected areas, continue using T-Gel shampoo, follow up in 3 months or sooner if worse, call doctor if worse

No negation flags.

Words absent from the reference (32): affected, area, blood, call, cloth, continue, dander, dandruff, doctor, dry, elsewhere, embarrassing, family, hair, heart, history, issue, itching, long, new

### Without roles (None) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** itchy scalp pain for a while, worsening in the past six months, dandruff, itching, embarrassing, no rashes elsewhere, no joint pain, fever, weight loss, no new stressors, sister has dry scalp, no significant family history of similar symptoms.

**O.** blood pressure 130/68, heart rate 98, respiratory rate 18, temperature 97.7, demarcated scaly erythematous plaques diffusely present across the back of the skull, white dander on clothes.

**A.** scalp psoriasis, clobetasol 0.05% solution twice daily on affected areas, continue to use T-Gel shampoo, no cure, unpredictable flare-ups, use steroids as needed for flare-ups, follow-up in three months or sooner if worse.

**P.** use clobetasol 0.05% solution twice daily, continue to use T-Gel shampoo, follow-up in three months or sooner if worse, call if it gets worse.

No negation flags.

Words absent from the reference (33): affected, area, blood, call, cloth, continue, dander, dandruff, dry, elsewhere, embarrassing, family, get, heart, history, itching, needed, new, past, pressure

## aci_003

**Reference note** (3008 chars)

```
CHIEF COMPLAINT

Left foot pain.

HISTORY OF PRESENT ILLNESS

Jean Martinez is a pleasant 27-year-old female who presents to the clinic today for the evaluation of left foot pain.

The patient sustained an injury to her left foot while playing soccer yesterday. She became entangled with another player, causing the player to fall onto the patient's foot, resulting in immediate pain. After the incident, she required help to get off of the field and was unable to participate for the rest of the game. Her trainer wrapped her foot, and she has tried ice, elevation, and ibuprofen to treat her symptoms. with medication, she rates her pain as 3/10, but without medication her pain is rated as 7-8/10. There is no numbness, tingling, or other abnormal sensations associated with her pain.

Of note, the patient has sustained several injuries in the past while playing soccer, but this is her first left foot injury.

MEDICAL HISTORY

The patient reports that she has sustained several soccer injuries in the past.

SOCIAL HISTORY

The patient has been playing soccer since she was 4 or 5 years old. She is currently playing in a local league.

MEDICATIONS

The patient reports that she has been taking ibuprofen.

REVIEW OF SYSTEMS

Musculoskeletal: Reports left foot pain.
Neurological: Denies left foot numbness or tingling.

VITALS

Blood pressure: 118/72 mmHg
Heart rate: 58 bpm
Respiratory rate: 14
Temperature: Afebrile
Oxygen saturation: 99% on room air

PHYSICAL EXAM

CV: Regular rate and rhythm without clicks, rubs, or murmurs. No ectopic beats noted on auscultation of the heart. Brisk capillary refill, less than 3 seconds. Dorsalis pedis pulse is intact and strong.
RESPIRATORY: Lungs are clear and equal bilaterally.
NEURO: Motor and sensation in the left foot are intact to light touch.
MSK: Examination of the left foot: Ecchymosis on the plantar and dorsal aspects of the foot. Associated swelling. Tenderness to palpation of the midfoot. Positive piano key test.

RESULTS

X-ray images of the left foot were obtained and reviewed today. These reveal subtle dorsal displacement of the base of the 2nd metatarsal with a 3 mm separation of the 1st and 2nd metatarsal bases. There is presence of a bony fragment in the Lisfranc joint space.

ASSESSMENT

Lisfranc fracture, left foot.

PLAN

I explained the nature of her injury in detail. Based on her exam and x-ray findings, she will most likely require surgery of the left foot, but I want to order an MRI to assess for any ligamentous injuries. We discussed the procedure and postoperative expectations, such as recovery time and restrictions, at length. We also discussed the complications associated with deferring surgical intervention including poor bone and ligament healing, pes planus deformation, and a high likelihood of developing arthritis in the foot. She will be unable to participate for the remainder of the soccer season, but should be able to play next season.

INSTRUCTIONS

We will see the patient on Monday, for surgery.
```

### With roles (gold_role) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** i'm doing alright aside from this foot pain that i have. i was playing in a soccer game yesterday and i was trying to steal the ball from another player and she ended up falling directly onto my right foot and i do n't know i i mean i was trying to get around her and my body ended up twisting around her and then i accidentally felt a pain in my foot. i've been keeping it elevated icing it the trainer wrapped it yesterday and taking ibuprofen as well. without ibuprofen i would say my pain is a three. with ibuprofen i would say my pain is a seven eight. i have not had a lot of injuries in soccer but never injured this foot. i had to stop playing right away and actually being helped off the field. i have been playing soccer since i was four five. i have experienced nothing like numbness or tingling or or any strange sensation.

**O.** blood pressure was one eighty one over seventy two heart rate was fifty eight respiratory rate was fourteen afebrile and oxygen saturation of ninety nine percent on room air. regular rate and rhythm no clicks rubs or murmurs no ectopic beats noted on auscultation lungs are clear and equal bilaterally. some bruising on the bottom of the foot and on the top of the foot. associated swelling. tenderness to palpation of the midfoot. positive for the piano key test. brisk capillary refill of less than three seconds. dorsalis pedis pulse is intact and strong. motor and sensation intact to light touch. subtle dorsal displacement of the base of the second metatarsal with a three millimeter separation of the first and second metatarsal bases. presence of a bony fragment in the lisfranc joint space.

**A.** right foot pain is due to a lisfranc fracture which is a fracture to one of your second metatarsal bones at the top of your foot where the metatarsals meet your cuboids. there are ligaments at the top of your foot so i'm gon na be ordering an mri to assess for injury to any of these ligaments. based on your exam and from what i'm seeing on your x-ray you're most likely going to need surgery of that foot. the surgery will place the bones back in their proper position and using plates and screws will hold them there while they heal and this is gon na allow those bones and ligaments to heal properly. it is a day surgery and you will be able to go home the same day and then i'm going to have you follow up with me here in the clinic you'll be in a cast and you will need to use crutches and you will not be able to use that left foot for about six to eight weeks. after that six to eight weeks you will gradually start walking on your foot based on how you tolerate it and we'll see how you do at that point. i do believe you're gon na need surgery i i'm recommending this because there are significant complications to your foot if we do not do this poor bone and ligament healing can lead to losing the arch of your foot and you're becoming flat-footed you also have a high likelihood of developing arthritis in that foot.

**P.** unfortunately you'll be out the rest of the season but we are gon na get you fixed up and ready for next season. i am having the nurse come in and get you started on your paperwork and then i will see you on monday morning and we will get your foot taken care of.

**Negation flags: 4**
- reference has *"without medication her pain is rated as 7-8/10"* → note says: _i'm doing alright aside from this foot pain that i have._
- reference has *"no numbness"* → note says: _i have experienced nothing like numbness or tingling or or any strange sensation._
- reference has *"denies left foot numbness or tingling"* → note says: _i'm doing alright aside from this foot pain that i have._
- reference has *"no ectopic beats noted on auscultation of the heart"* → note says: _blood pressure was one eighty one over seventy two heart rate was fifty eight respiratory rate was fourteen afebrile and oxygen saturation of ninety nine percent on room air._

Words absent from the reference (124): about, accidentally, actually, allow, alright, arch, around, aside, away, back, ball, because, becoming, believe, body, bon, bottom, bruising, can, care

### Without roles (None) — model: `Qwen/Qwen2.5-7B-Instruct`

**S.** Patient reports foot pain after a soccer injury where another player fell on his right foot. Pain level is 3 without ibuprofen and 7-8 with ibuprofen. Patient has no history of left foot injuries, has been playing soccer since childhood, and no numbness or tingling. Patient has a history of soccer injuries.

**O.** Vitals: BP 180/72, HR 58, RR 14, Afebrile, SpO2 99% on room air. Heart: Regular rate and rhythm, no clicks, rubs, or murmurs. Lungs: Clear and equal bilaterally. Left foot: Bruising, swelling, tenderness to palpation, positive piano key test, brisk capillary refill <3 sec, dorsalis pedis pulse intact and strong, motor and sensation intact to light touch. X-ray: Subtle dorsal displacement of the base of the second metatarsal, 3 mm separation of the first and second metatarsal bases, bony fragment in the Lisfranc joint space.

**A.** Lisfranc fracture of the second metatarsal at the top of the foot. Ligament injury suspected. Surgery recommended to place bones in proper position and use plates and screws for healing. Day surgery, cast, crutches, and non-weight-bearing for 6-8 weeks followed by gradual weight-bearing based on tolerance. Significant complications if untreated, including loss of arch and arthritis.

**P.** Order MRI to assess ligament injury. Schedule surgery. Provide paperwork. Follow up in clinic on Monday.

**Negation flags: 2**
- reference has *"without medication her pain is rated as 7-8/10"* → note says: _Patient reports foot pain after a soccer injury where another player fell on his right foot._
- reference has *"denies left foot numbness or tingling"* → note says: _Patient reports foot pain after a soccer injury where another player fell on his right foot._

Words absent from the reference (35): arch, bearing, bon, bruising, cast, childhood, crutch, day, fell, follow, followed, gradual, level, los, non, paperwork, place, plat, position, proper
