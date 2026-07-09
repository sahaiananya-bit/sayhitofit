# AI Body Composition Analysis API Documentation

## Overview
The AI analyzer module provides comprehensive body composition analysis and personalized fitness recommendations based on user metrics and goals.

## API Endpoints

### 1. POST `/api/analyze-body-composition`
Performs complete body composition analysis and provides personalized recommendations.

#### Request Body
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

#### Parameters
- **height_cm** (float, required): Height in centimeters
- **weight_kg** (float, required): Weight in kilograms
- **age** (int, required): Age in years
- **gender** (string, required): "male" or "female"
- **activity_level** (string, required): 
  - "sedentary" - Little or no exercise
  - "light" - 1-3 days/week light exercise
  - "moderate" - 3-5 days/week moderate exercise
  - "very_active" - 6-7 days/week intense exercise
  - "extra_active" - Physical job or training 2x/day
- **fitness_goal** (string, required): "weight_loss", "muscle_gain", or "maintenance"
- **waist_cm** (float, optional): Waist circumference for accurate body fat estimation
- **hip_cm** (float, optional): Hip circumference
- **neck_cm** (float, optional): Neck circumference

#### Response
```json
{
  "success": true,
  "data": {
    "bmi": 26.2,
    "bmi_category": "Overweight",
    "bmr": 1850.5,
    "tdee": 2867.75,
    "body_fat_percentage": 22.5,
    "lean_mass_kg": 65.8,
    "fat_mass_kg": 19.2,
    "caloric_recommendation": {
      "maintenance": 2868,
      "deficit_loss": 2368,
      "surplus_gain": 3368
    },
    "weight_suggestion": "increase",
    "target_weight_range": {
      "min": 60.5,
      "max": 81.3,
      "current": 85.0
    },
    "personalized_advice": "✓ Your BMI is healthy! Maintain with consistent training...",
    "weekly_targets": {
      "training_days": "4-5 days per week",
      "cardio": "150-300 min per week",
      "protein_daily": "215.5g",
      "water_intake": "2550ml per day (approx)"
    },
    "timeline": {
      "weekly_change_kg": 0.25,
      "weeks_to_goal": 21,
      "target_date": "2026-06-02"
    },
    "macro_breakdown": {
      "protein": {
        "grams": 215.5,
        "calories": 862,
        "percentage": 30.0
      },
      "carbs": {
        "grams": 322.7,
        "calories": 1290,
        "percentage": 45.0
      },
      "fats": {
        "grams": 79.6,
        "calories": 716,
        "percentage": 25.0
      }
    }
  }
}
```

### 2. POST `/api/bulk-vs-cut`
Provides specific recommendation for whether user should bulk (gain) or cut (lose) weight.

#### Request Body
Same as `/api/analyze-body-composition`

#### Response
```json
{
  "success": true,
  "recommendation": {
    "current_bmi": 26.2,
    "body_fat_percentage": 22.5,
    "recommendation": "BULK (Build Muscle)",
    "reasoning": [
      "Your lean body mass can support muscle gain",
      "Prioritize caloric surplus and strength training"
    ]
  }
}
```

### 3. GET `/api/health`
Health check endpoint to verify API is running.

#### Response
```json
{
  "status": "healthy",
  "version": "1.0"
}
```

## Key Metrics Explained

### BMI (Body Mass Index)
- Formula: weight(kg) / height(m)²
- Categories:
  - < 18.5: Underweight
  - 18.5-25: Normal Weight
  - 25-30: Overweight
  - > 30: Obese

### BMR (Basal Metabolic Rate)
- Calories your body burns at rest
- Calculated using Mifflin-St Jeor equation (most accurate)
- Accounts for age, gender, height, weight

### TDEE (Total Daily Energy Expenditure)
- BMR × Activity Multiplier
- Total calories burned in a day including exercise
- Used to calculate caloric needs for goals

### Body Fat Percentage
- Estimated from measurements (waist, hip, neck) if provided
- Fallback: BMI-based estimation (Deurenberg formula)
- Better body fat % than BMI alone for fitness assessment

### Macronutrient Breakdown
Personalized based on fitness goal:
- **Muscle Gain**: 30% protein, 45% carbs, 25% fat
- **Weight Loss**: 35% protein, 40% carbs, 25% fat
- **Maintenance**: 30% protein, 45% carbs, 25% fat

## Usage Examples

### Example 1: Overweight Person - Weight Loss Goal
```json
{
  "height_cm": 170,
  "weight_kg": 95,
  "age": 35,
  "gender": "female",
  "activity_level": "light",
  "fitness_goal": "weight_loss",
  "waist_cm": 92
}
```
**Expected Result**: Cut recommendation, 300-500 calorie deficit, high protein maintenance

### Example 2: Athletic Person - Muscle Gain Goal
```json
{
  "height_cm": 185,
  "weight_kg": 82,
  "age": 25,
  "gender": "male",
  "activity_level": "very_active",
  "fitness_goal": "muscle_gain",
  "waist_cm": 80,
  "hip_cm": 88,
  "neck_cm": 39
}
```
**Expected Result**: Bulk recommendation, 300-500 calorie surplus, high protein

### Example 3: Sedentary Person - Maintenance + Recomp
```json
{
  "height_cm": 175,
  "weight_kg": 75,
  "age": 40,
  "gender": "male",
  "activity_level": "sedentary",
  "fitness_goal": "maintenance",
  "waist_cm": 85
}
```
**Expected Result**: Increase activity, maintenance calories, focus on strength

## Recommendation Logic

### Weight Loss Suggestion
- BMI > 25 OR Body Fat > 25%
- Caloric Deficit: 300-500 calories/day
- Expected Loss: 0.5kg per week
- Focus: Preserve muscle, consistent cardio

### Muscle Gain Suggestion
- BMI < 18.5 OR Body Fat < 15%
- Caloric Surplus: 300-500 calories/day
- Expected Gain: 0.25-0.5kg per week
- Focus: Progressive overload, compound lifts

### Maintenance + Recomp
- BMI 18.5-25 AND Body Fat 15-25%
- Stay at maintenance calories
- Focus: Strength training, body composition improvement
- Expected: Muscle gain + slight fat loss over time

## Timeline Calculation

- **Weight Loss**: 0.5kg per week (conservative, sustainable)
- **Muscle Gain**: 0.25kg per week (quality gain, minimize fat)
- Automatically calculates weeks to goal and estimated target date

## Personalized Advice Includes

✓ BMI-based fitness level assessment
✓ Body composition feedback
✓ Activity level recommendations
✓ Age-appropriate training advice
✓ Goal-specific nutrition strategy
✓ Recovery and sleep recommendations
✓ Weekly training frequency targets

## Notes

- All body measurements should be taken accurately for best results
- Body fat percentage estimation is most accurate with all circumferences (waist, hip, neck)
- Timelines are conservative estimates; actual results depend on adherence
- Always consult healthcare professionals before starting new fitness programs
- AI provides data-driven recommendations, not medical advice
