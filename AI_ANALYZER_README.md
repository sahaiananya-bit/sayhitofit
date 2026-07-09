# SAYHITOFIT AI Body Composition Analyzer

## Overview

The AI Body Composition Analyzer is a sophisticated machine learning module that analyzes user body composition and provides personalized fitness recommendations. It calculates various metrics and delivers data-driven insights for weight loss, muscle gain, or maintenance goals.

## Features

✅ **Complete Body Composition Analysis**
- BMI calculation and classification
- Body fat percentage estimation (multiple algorithms)
- Lean mass and fat mass calculation
- BMR (Basal Metabolic Rate) calculation

✅ **Caloric Intelligence**
- TDEE (Total Daily Energy Expenditure) calculation
- Personalized caloric recommendations
- Macro nutrient breakdown (protein, carbs, fats)
- Activity level-based adjustments

✅ **AI-Driven Recommendations**
- Weight change suggestions (bulk, cut, or maintain)
- Target weight range calculation
- Timeline predictions with realistic goals
- Weekly training and nutrition targets

✅ **Personalized Fitness Advice**
- BMI-based assessments
- Body composition feedback
- Activity level suggestions
- Age-appropriate recommendations
- Goal-specific strategies

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Quick Start

### Test the Analyzer

```bash
python test_analyzer.py
```

This runs 4 test cases with different body types and goals.

### API Usage

Example cURL request:
```bash
curl -X POST "http://localhost:8000/api/analyze-body-composition" \
  -H "Content-Type: application/json" \
  -d '{
    "height_cm": 180,
    "weight_kg": 85,
    "age": 30,
    "gender": "male",
    "activity_level": "moderate",
    "fitness_goal": "muscle_gain",
    "waist_cm": 90,
    "hip_cm": 95,
    "neck_cm": 38
  }'
```

## Key Algorithms

### 1. BMR Calculation (Mifflin-St Jeor Equation)
Most accurate for modern populations
- **Male**: (10×weight) + (6.25×height) - (5×age) + 5
- **Female**: (10×weight) + (6.25×height) - (5×age) - 161

### 2. TDEE Calculation
TDEE = BMR × Activity Multiplier

**Activity Multipliers:**
- Sedentary: 1.2
- Light (1-3 days/week): 1.375
- Moderate (3-5 days/week): 1.55
- Very Active (6-7 days/week): 1.725
- Extra Active (training 2x/day): 1.9

### 3. Body Fat Percentage Estimation
Two methods available:

**Method 1: Circumference-based (Most Accurate)**
- Uses waist, hip, and neck measurements
- Jackson-Pollock formula for high accuracy
- Navy formula as alternative

**Method 2: BMI-based (Fallback)**
- Deurenberg formula
- Used when measurements unavailable
- Less accurate but still reasonable

### 4. Caloric Recommendations
- **Weight Loss**: TDEE - 500 cal (0.5kg/week loss)
- **Muscle Gain**: TDEE + 500 cal (0.25kg/week gain)
- **Maintenance**: TDEE (maintain weight)

### 5. Macro Distribution
**For Muscle Gain:**
- Protein: 30% of calories (higher protein for muscle synthesis)
- Carbs: 45%
- Fats: 25%

**For Weight Loss:**
- Protein: 35% of calories (preserve muscle during deficit)
- Carbs: 40%
- Fats: 25%

**For Maintenance:**
- Protein: 30%
- Carbs: 45%
- Fats: 25%

## API Endpoints

### POST /api/analyze-body-composition
Complete body composition analysis with all metrics and recommendations.

**Request:**
```json
{
  "height_cm": 180,
  "weight_kg": 85,
  "age": 30,
  "gender": "male",
  "activity_level": "moderate",
  "fitness_goal": "muscle_gain",
  "waist_cm": 90,
  "hip_cm": 95,
  "neck_cm": 38
}
```

**Response:** Returns all metrics, recommendations, timeline, and macro breakdown

### POST /api/bulk-vs-cut
Quick recommendation for bulk (gain) or cut (lose) phase.

**Request:** Same as above

**Response:** Simple bulk/cut recommendation with reasoning

### GET /api/health
Health check endpoint.

**Response:** `{"status": "healthy", "version": "1.0"}`

## Parameters Guide

### height_cm (float, required)
Height in centimeters. Example: 180

### weight_kg (float, required)
Weight in kilograms. Example: 85

### age (int, required)
Age in years. Example: 30

### gender (string, required)
Either "male" or "female"

### activity_level (string, required)
- **"sedentary"**: Little or no exercise, desk job
- **"light"**: 1-3 days per week light exercise
- **"moderate"**: 3-5 days per week moderate exercise (typical gym routine)
- **"very_active"**: 6-7 days per week intense exercise
- **"extra_active"**: Physical job or training twice per day

### fitness_goal (string, required)
- **"weight_loss"**: Lose fat, create caloric deficit
- **"muscle_gain"**: Build muscle, create caloric surplus
- **"maintenance"**: Maintain weight, focus on body recomposition

### waist_cm (float, optional)
Waist circumference at belly button level. Highly recommended for accuracy.

### hip_cm (float, optional)
Hip circumference at widest point. Improves body fat estimation.

### neck_cm (float, optional)
Neck circumference. Used in advanced body fat formulas.

## Response Structure

The analysis returns:
- **bmi**: Body Mass Index value
- **bmi_category**: "Underweight", "Normal Weight", "Overweight", or "Obese"
- **bmr**: Basal Metabolic Rate in calories
- **tdee**: Total Daily Energy Expenditure in calories
- **body_fat_percentage**: Estimated body fat percentage
- **lean_mass_kg**: Muscle + bone + organs weight
- **fat_mass_kg**: Total body fat weight
- **caloric_recommendation**: Maintenance, deficit, and surplus calories
- **weight_suggestion**: "increase", "decrease", or "maintain"
- **target_weight_range**: Min-max healthy weight range
- **personalized_advice**: Text-based recommendations
- **weekly_targets**: Training frequency, cardio, protein, water
- **timeline**: Weeks to goal and estimated target date
- **macro_breakdown**: Protein, carbs, fats in grams and percentages

## Example Scenarios

### Scenario 1: Overweight Person - Weight Loss
```json
{
  "height_cm": 170,
  "weight_kg": 95,
  "age": 35,
  "gender": "female",
  "activity_level": "light",
  "fitness_goal": "weight_loss"
}
```
**Result:** Cut recommendation, 300-500 calorie deficit, high protein for muscle preservation, realistic timeline to healthy weight

### Scenario 2: Athletic Person - Muscle Building
```json
{
  "height_cm": 185,
  "weight_kg": 82,
  "age": 25,
  "gender": "male",
  "activity_level": "very_active",
  "fitness_goal": "muscle_gain"
}
```
**Result:** Bulk recommendation, 300-500 calorie surplus, optimal macro split for muscle growth, progressive weight gain timeline

### Scenario 3: Average Person - Maintenance
```json
{
  "height_cm": 175,
  "weight_kg": 75,
  "age": 30,
  "gender": "male",
  "activity_level": "moderate",
  "fitness_goal": "maintenance"
}
```
**Result:** Maintenance calories with focus on body recomposition, strength training emphasis

## Measurement Guide

For best results, take measurements accurately:

**Height (cm):**
- Stand against wall
- Measure from ground to top of head
- No shoes

**Weight (kg):**
- Use reliable scale
- Weigh in morning, after bathroom, before eating
- Consistent timing weekly

**Waist (cm):**
- Relax abdomen
- Measure at naval level, horizontally
- Don't suck in

**Hip (cm):**
- Measure at widest point of hips
- Horizontal measurement

**Neck (cm):**
- Just below Adam's apple
- Horizontal measurement

## Timeline Accuracy

Timelines are **conservative estimates** based on:
- 0.5kg/week loss (sustainable, preserves muscle)
- 0.25kg/week gain (quality gains, minimizes excess fat)

**Actual results vary based on:**
- Diet adherence
- Training consistency
- Sleep quality
- Stress levels
- Genetics
- Starting metabolic rate

## Important Notes

⚠️ **AI provides data-driven recommendations, not medical advice**
- Always consult healthcare professionals before starting new programs
- These recommendations are for generally healthy adults
- Special populations (athletes, medical conditions) may need adjustments

⚠️ **Body fat estimation accuracy**
- Most accurate: With waist, hip, and neck measurements
- Moderate accuracy: With BMI-based estimation
- Measurements should be retaken consistently for progress tracking

⚠️ **Individual variation**
- Every person responds differently
- Adjust recommendations based on real results
- Track progress over 2-4 weeks before making changes

## Module Structure

```python
BodyCompositionAnalyzer
├── calculate_bmi()
├── calculate_bmr_mifflin_st_jeor()
├── calculate_tdee()
├── estimate_body_fat_percentage()
├── calculate_lean_mass()
├── calculate_caloric_recommendations()
├── calculate_target_weight_range()
├── generate_weight_suggestion()
├── generate_timeline()
├── generate_personalized_advice()
├── calculate_macro_breakdown()
└── analyze() [Main method]
```

## Future Enhancements

Potential additions for next versions:
- 📈 Progress tracking and predictions
- 🏋️ Workout recommendations based on goals
- 📊 Visual dashboards and charts
- 💾 User data persistence
- 🤖 Machine learning models for personalization
- 📱 Mobile app integration
- 🔄 Real-time metric comparisons

## Support

For issues or questions:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Review test cases in [test_analyzer.py](test_analyzer.py)
3. Refer to this README

---

**SAYHITOFIT AI Analyzer v1.0** | Helping you achieve your fitness goals with data-driven insights
