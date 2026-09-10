# step1_types  (attempt 1)

## 对话信息

- time: 2026-09-10 23:52:42
- seq: 1
- prefix: global_
- stage: step1_types
- attempt: 1
- ok: True

## 输入

```
You are a demographic statistics expert. Based on the district description below, generate a list of the household types most likely to appear in this community.

## District Description (ABS 2021 census summary)

In the southeastern part of the Melbourne metropolitan area, the Clayton 3168 postcode district presents a distinctive demographic profile. According to the 2021 census, the district has a usual resident population of 21,880 — 11,681 males and 10,201 females, a slight male skew. The most striking feature is its extremely young age structure: the district's median age is only 28, well below the Australian national average. The 20-24 age group alone has 4,638 residents and the 25-34 group 6,640 — together more than half of the total population — making this an area dominated by young students and early-career professionals. By contrast, there are only 1,934 children aged 0-14 and about 1,486 residents aged 65 and over, a classic "large middle, small ends" structure.

This age structure deeply shapes the local household landscape. The district has 4,009 households with an average size of 2.5 people. Couple-only households are the largest group at 1,768, alongside 1,891 couples with children and 434 single-parent families. Because the population is young and student-heavy, living alone or sharing is very common: 1,893 households are one-person non-family dwellings and another 3,263 are non-family households, meaning many people do not live in traditional family units. Marital status reflects this too: among 25-34 year-olds, 2,838 men have never married and 1,183 women are unmarried.

Economically, Clayton shows a typical "student economy". The median personal weekly income is AUD 606 — below the Greater Melbourne level — reflecting the large number of full-time students and part-time workers. The median household weekly income is AUD 1,778 and the median family weekly income AUD 1,508. The unemployment rate is 9.3% and the labour force participation rate 60.7% (63.5% for men, 57.4% for women). Among employed residents, 5,386 work full-time and 4,761 part-time — a notably high part-time share. Education is one of the largest employers, with 1,216 people working in education and training, followed by health care and social assistance, and professional, scientific and technical services.

Housing in Clayton is diverse. Of the 8,606 private dwellings, 2,640 are separate houses, 2,703 are semi-detached, row or terrace houses, and 1,794 are flats or units. Home ownership rates are relatively low: only 1,358 households fully own their home, while 3,305 rent through a real estate agent and 618 rent from a private landlord. The median weekly rent is AUD 396 and the median monthly mortgage repayment AUD 2,000. On average 0.9 people live per bedroom — not especially crowded. Notably, 1,452 dwellings are unoccupied, likely including investor properties and short-term student rentals.

Education is the district's most defining feature. 4,797 residents hold a bachelor's degree, 3,485 a postgraduate qualification, and 1,577 an advanced diploma or diploma — an exceptionally dense concentration of highly educated people. Student numbers are striking: 3,337 residents aged 15-24 are enrolled in education and 2,517 aged 25 and over are still studying, confirming Clayton's identity as a university town adjacent to Monash University. The cultural diversity is equally marked: only 6,488 residents speak only English at home, while 13,724 speak a language other than English — including 5,406 of Chinese ancestry and about 2,800 of Indian ancestry, plus large numbers of migrants from Sri Lanka, Malaysia, Vietnam and elsewhere. 7,541 residents have no religious affiliation, 1,617 are Buddhists, 1,145 Orthodox Christians, and there is a substantial Hindu community. For commuting, driving dominates: 4,631 people drive to work alone, while close to 670 rely on trains and buses, with a notable number walking or cycling.

In summary, Clayton 3168 is a dynamic, multicultural community formed by international students, young professionals and newly arrived migrant families. It lacks the quiet ageing typical of traditional Australian suburbs; instead it is full of the bustle of study, work and mobility. High education levels, multilingualism, a high rental share and young residents clustering together are its defining traits — and its vitality. As a residential area it functions more like a "talent incubator" for the future: large numbers of young people receive higher education and start their careers here, continuously supplying fresh energy to Melbourne.

## Generation Requirements

1. Generate exactly **3** distinct household types (covering the most typical and most common household forms in this community)
2. For each household type provide: a type name, a detailed description, the member count minimum and maximum, and a typical housing hint
3. Household types must match the district's age structure, income level, housing types, and cultural composition
   (e.g., a student area should feature share-house/student households, not large numbers of retired households)
4. Output language: all generated VALUES (type names, descriptions, housing hints) MUST be written in English, because the downstream system matches English tokens. Example type names: Young DINK Couple, Family with Children, International Student Share House, Single Professional Living Alone, Single-Parent Family, Multigenerational Household, Retired Couple
5. Return ONLY a valid JSON object matching the required schema (no markdown fences, no commentary).

```

## Schema

```json
{
  "type": "object",
  "required": [
    "household_types"
  ],
  "properties": {
    "household_types": {
      "type": "array",
      "minItems": 3,
      "maxItems": 3,
      "items": {
        "type": "object",
        "required": [
          "type",
          "description",
          "members_min",
          "members_max",
          "housing_hint"
        ],
        "properties": {
          "type": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "members_min": {
            "type": "integer",
            "minimum": 1,
            "maximum": 8
          },
          "members_max": {
            "type": "integer",
            "minimum": 1,
            "maximum": 8
          },
          "housing_hint": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

## 返回(原始)

```
{
  "household_types": [
    {
      "type": "International Student Share House",
      "description": "A group of university students, often international, sharing a rented dwelling to reduce costs. Typically aged 18-30, enrolled full-time at Monash University or other institutions, with part-time jobs. They come from diverse backgrounds, including Chinese, Indian, and Southeast Asian. High mobility, communal living, and shared expenses are common.",
      "members_min": 2,
      "members_max": 6,
      "housing_hint": "Rented apartment, flat, or semi-detached house with multiple bedrooms, often located near the university and public transport."
    },
    {
      "type": "Young Professional Couple (DINK)",
      "description": "A couple in their late 20s to early 30s, both employed in professional, scientific, technical, or healthcare sectors. They are university-educated, may be migrants or Australian-born, and have no children. They value career and lifestyle, often renting or buying a unit or townhouse. Dual income, no kids.",
      "members_min": 2,
      "members_max": 2,
      "housing_hint": "Modern apartment or townhouse, typically rented or recently purchased, with 1-2 bedrooms, close to amenities and transport."
    },
    {
      "type": "Family with Children (Migrant Family)",
      "description": "A couple with one or more children, often of Chinese, Indian, or Sri Lankan ancestry. Parents are typically aged 30-45, working in education, healthcare, or retail. They may be first- or second-generation migrants. Education is highly valued, and children attend local schools. Household income is modest to middle.",
      "members_min": 3,
      "members_max": 5,
      "housing_hint": "Separate house or semi-detached house with 3-4 bedrooms, often owner-occupied with a mortgage or rented, in a family-friendly neighbourhood."
    }
  ]
}
```

## 解析结果

```json
{
  "household_types": [
    {
      "type": "International Student Share House",
      "description": "A group of university students, often international, sharing a rented dwelling to reduce costs. Typically aged 18-30, enrolled full-time at Monash University or other institutions, with part-time jobs. They come from diverse backgrounds, including Chinese, Indian, and Southeast Asian. High mobility, communal living, and shared expenses are common.",
      "members_min": 2,
      "members_max": 6,
      "housing_hint": "Rented apartment, flat, or semi-detached house with multiple bedrooms, often located near the university and public transport."
    },
    {
      "type": "Young Professional Couple (DINK)",
      "description": "A couple in their late 20s to early 30s, both employed in professional, scientific, technical, or healthcare sectors. They are university-educated, may be migrants or Australian-born, and have no children. They value career and lifestyle, often renting or buying a unit or townhouse. Dual income, no kids.",
      "members_min": 2,
      "members_max": 2,
      "housing_hint": "Modern apartment or townhouse, typically rented or recently purchased, with 1-2 bedrooms, close to amenities and transport."
    },
    {
      "type": "Family with Children (Migrant Family)",
      "description": "A couple with one or more children, often of Chinese, Indian, or Sri Lankan ancestry. Parents are typically aged 30-45, working in education, healthcare, or retail. They may be first- or second-generation migrants. Education is highly valued, and children attend local schools. Household income is modest to middle.",
      "members_min": 3,
      "members_max": 5,
      "housing_hint": "Separate house or semi-detached house with 3-4 bedrooms, often owner-occupied with a mortgage or rented, in a family-friendly neighbourhood."
    }
  ]
}
```

