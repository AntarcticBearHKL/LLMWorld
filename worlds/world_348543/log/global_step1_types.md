# [2026-08-24 19:41:09] global_step1_types

## Prompt

You are a demographic statistics expert. Based on the district description below, generate a list of the household types most likely to appear in this community.

## District Description (ABS 2021 census summary)

In the southeastern part of the Melbourne metropolitan area, the Clayton 3168 postcode district presents a distinctive demographic profile. According to the 2021 census, the district has a usual resident population of 21,880 — 11,681 males and 10,201 females, a slight male skew. The most striking feature is its extremely young age structure: the district's median age is only 28, well below the Australian national average. The 20-24 age group alone has 4,638 residents and the 25-34 group 6,640 — together more than half of the total population — making this an area dominated by young students and early-career professionals. By contrast, there are only 1,934 children aged 0-14 and about 1,486 residents aged 65 and over, a classic "large middle, small ends" structure.

This age structure deeply shapes the local household landscape. The district has 4,009 households with an average size of 2.5 people. Couple-only households are the largest group at 1,768, alongside 1,891 couples with children and 434 single-parent families. Because the population is young and student-heavy, living alone or sharing is very common: 1,893 households are one-person non-family dwellings and another 3,263 are non-family households, meaning many people do not live in traditional family units. Marital status reflects this too: among 25-34 year-olds, 2,838 men have never married and 1,183 women are unmarried.

Economically, Clayton shows a typical "student economy". The median personal weekly income is AUD 606 — below the Greater Melbourne level — reflecting the large number of full-time students and part-time workers. The median household weekly income is AUD 1,778 and the median family weekly income AUD 1,508. The unemployment rate is 9.3% and the labour force participation rate 60.7% (63.5% for men, 57.4% for women). Among employed residents, 5,386 work full-time and 4,761 part-time — a notably high part-time share. Education is one of the largest employers, with 1,216 people working in education and training, followed by health care and social assistance, and professional, scientific and technical services.

Housing in Clayton is diverse. Of the 8,606 private dwellings, 2,640 are separate houses, 2,703 are semi-detached, row or terrace houses, and 1,794 are flats or units. Home ownership rates are relatively low: only 1,358 households fully own their home, while 3,305 rent through a real estate agent and 618 rent from a private landlord. The median weekly rent is AUD 396 and the median monthly mortgage repayment AUD 2,000. On average 0.9 people live per bedroom — not especially crowded. Notably, 1,452 dwellings are unoccupied, likely including investor properties and short-term student rentals.

Education is the district's most defining feature. 4,797 residents hold a bachelor's degree, 3,485 a postgraduate qualification, and 1,577 an advanced diploma or diploma — an exceptionally dense concentration of highly educated people. Student numbers are striking: 3,337 residents aged 15-24 are enrolled in education and 2,517 aged 25 and over are still studying, confirming Clayton's identity as a university town adjacent to Monash University. The cultural diversity is equally marked: only 6,488 residents speak only English at home, while 13,724 speak a language other than English — including 5,406 of Chinese ancestry and about 2,800 of Indian ancestry, plus large numbers of migrants from Sri Lanka, Malaysia, Vietnam and elsewhere. 7,541 residents have no religious affiliation, 1,617 are Buddhists, 1,145 Orthodox Christians, and there is a substantial Hindu community. For commuting, driving dominates: 4,631 people drive to work alone, while close to 670 rely on trains and buses, with a notable number walking or cycling.

In summary, Clayton 3168 is a dynamic, multicultural community formed by international students, young professionals and newly arrived migrant families. It lacks the quiet ageing typical of traditional Australian suburbs; instead it is full of the bustle of study, work and mobility. High education levels, multilingualism, a high rental share and young residents clustering together are its defining traits — and its vitality. As a residential area it functions more like a "talent incubator" for the future: large numbers of young people receive higher education and start their careers here, continuously supplying fresh energy to Melbourne.

## Generation Requirements

1. Generate exactly **2** distinct household types (covering the most typical and most common household forms in this community)
2. For each household type provide: a type name, a detailed description, the typical member count, and a typical housing hint
3. Household types must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
4. Output language: all generated VALUES (type names, descriptions, housing hints) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple

Output JSON format (return ONLY the JSON, nothing else):

MANDATORY INSTRUCTIONS (must follow):
- Output only the JSON object itself in the format below. Never output markdown code fences (```), never output any explanatory text, never output lists or headings
- Use exactly the field names below: type, description, typical_members (must be an integer 1-8), housing_hint
- Generate exactly 2 types, no more and no fewer

{
  "household_types": [
    {
      "type": "household type name (in English)",
      "description": "detailed feature description (3-5 sentences: member composition, occupation/income, lifestyle, housing needs)",
      "typical_members": 3,
      "housing_hint": "typical housing type hint (e.g., two-bedroom apartment, three-bedroom townhouse, one-bedroom unit)"
    }
  ]
}


## Response

{
  "household_types": [
    {
      "type": "International Student Share House",
      "description": "Groups of young international students, largely from India, China and other Asian countries, sharing rented houses or apartments near the university. They work part-time in retail, hospitality or on campus, have modest incomes, and prioritise affordability and proximity to campus and public transport over space.",
      "typical_members": 4,
      "housing_hint": "Shared 3-4 bedroom house or apartment, often older rental stock near campus or the railway line"
    },
    {
      "type": "Young Professional Couple / Single",
      "description": "Early-career professionals and postgraduate students living alone or as a couple in compact dwellings. They are highly educated, often rent, and value easy access to the city, work and study, with low car dependence and modern amenities.",
      "typical_members": 2,
      "housing_hint": "One- or two-bedroom unit, apartment or townhouse, frequently rented"
    }
  ]
}
