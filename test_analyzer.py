"""
Test script for AI Body Composition Analyzer
Run this to verify the analyzer is working correctly
"""

from ai_analyzer import (
    BodyCompositionAnalyzer,
    BodyCompositionRequest,
    Gender,
    ActivityLevel,
    FitnessGoal
)

def test_analyzer():
    """Test the body composition analyzer with sample data"""
    
    analyzer = BodyCompositionAnalyzer()
    
    print("=" * 80)
    print("SAYHITOFIT AI BODY COMPOSITION ANALYZER - TEST SUITE")
    print("=" * 80)
    
    # Test Case 1: Overweight male - Weight Loss Goal
    print("\n📊 TEST 1: Overweight Male - Weight Loss Goal")
    print("-" * 80)
    
    request1 = BodyCompositionRequest(
        height_cm=175,
        weight_kg=95,
        age=35,
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATE,
        fitness_goal=FitnessGoal.WEIGHT_LOSS,
        waist_cm=100,
        hip_cm=105,
        neck_cm=40
    )
    
    result1 = analyzer.analyze(request1)
    print(f"BMI: {result1.bmi} ({result1.bmi_category})")
    print(f"Body Fat: {result1.body_fat_percentage}%")
    print(f"Lean Mass: {result1.lean_mass_kg}kg | Fat Mass: {result1.fat_mass_kg}kg")
    print(f"BMR: {result1.bmr} cal | TDEE: {result1.tdee} cal")
    print(f"Daily Calories: Maintenance={result1.caloric_recommendation.maintenance}, Loss={result1.caloric_recommendation.deficit_loss}")
    print(f"Weight Suggestion: {result1.weight_suggestion}")
    print(f"Target Weight: {result1.target_weight_range['min']} - {result1.target_weight_range['max']} kg")
    print(f"Timeline: {result1.timeline.weeks_to_goal} weeks to target ({result1.timeline.target_date})")
    print(f"Protein Daily: {result1.macro_breakdown['protein']['grams']}g")
    
    # Test Case 2: Lean male - Muscle Gain Goal
    print("\n📊 TEST 2: Lean Male - Muscle Gain Goal")
    print("-" * 80)
    
    request2 = BodyCompositionRequest(
        height_cm=185,
        weight_kg=78,
        age=26,
        gender=Gender.MALE,
        activity_level=ActivityLevel.VERY_ACTIVE,
        fitness_goal=FitnessGoal.MUSCLE_GAIN,
        waist_cm=80,
        hip_cm=88,
        neck_cm=38
    )
    
    result2 = analyzer.analyze(request2)
    print(f"BMI: {result2.bmi} ({result2.bmi_category})")
    print(f"Body Fat: {result2.body_fat_percentage}%")
    print(f"Lean Mass: {result2.lean_mass_kg}kg | Fat Mass: {result2.fat_mass_kg}kg")
    print(f"BMR: {result2.bmr} cal | TDEE: {result2.tdee} cal")
    print(f"Daily Calories: Maintenance={result2.caloric_recommendation.maintenance}, Gain={result2.caloric_recommendation.surplus_gain}")
    print(f"Weight Suggestion: {result2.weight_suggestion}")
    print(f"Target Weight: {result2.target_weight_range['min']} - {result2.target_weight_range['max']} kg")
    print(f"Timeline: {result2.timeline.weeks_to_goal} weeks to target ({result2.timeline.target_date})")
    print(f"Protein Daily: {result2.macro_breakdown['protein']['grams']}g")
    
    # Test Case 3: Normal weight female - Maintenance + Recomp
    print("\n📊 TEST 3: Normal Weight Female - Maintenance Goal")
    print("-" * 80)
    
    request3 = BodyCompositionRequest(
        height_cm=165,
        weight_kg=62,
        age=28,
        gender=Gender.FEMALE,
        activity_level=ActivityLevel.LIGHT,
        fitness_goal=FitnessGoal.MAINTENANCE,
        waist_cm=75,
        hip_cm=88,
        neck_cm=32
    )
    
    result3 = analyzer.analyze(request3)
    print(f"BMI: {result3.bmi} ({result3.bmi_category})")
    print(f"Body Fat: {result3.body_fat_percentage}%")
    print(f"Lean Mass: {result3.lean_mass_kg}kg | Fat Mass: {result3.fat_mass_kg}kg")
    print(f"BMR: {result3.bmr} cal | TDEE: {result3.tdee} cal")
    print(f"Daily Calories: Maintenance={result3.caloric_recommendation.maintenance}")
    print(f"Weight Suggestion: {result3.weight_suggestion}")
    print(f"Protein Daily: {result3.macro_breakdown['protein']['grams']}g")
    
    # Test Case 4: Underweight person - Need to gain
    print("\n📊 TEST 4: Underweight Person - Need to Gain")
    print("-" * 80)
    
    request4 = BodyCompositionRequest(
        height_cm=180,
        weight_kg=65,
        age=22,
        gender=Gender.MALE,
        activity_level=ActivityLevel.MODERATE,
        fitness_goal=FitnessGoal.MUSCLE_GAIN,
        waist_cm=75,
        hip_cm=82,
        neck_cm=35
    )
    
    result4 = analyzer.analyze(request4)
    print(f"BMI: {result4.bmi} ({result4.bmi_category})")
    print(f"Body Fat: {result4.body_fat_percentage}%")
    print(f"Lean Mass: {result4.lean_mass_kg}kg | Fat Mass: {result4.fat_mass_kg}kg")
    print(f"BMR: {result4.bmr} cal | TDEE: {result4.tdee} cal")
    print(f"Daily Calories: Maintenance={result4.caloric_recommendation.maintenance}, Gain={result4.caloric_recommendation.surplus_gain}")
    print(f"Weight Suggestion: {result4.weight_suggestion}")
    print(f"Target Weight: {result4.target_weight_range['min']} - {result4.target_weight_range['max']} kg")
    print(f"Timeline: {result4.timeline.weeks_to_goal} weeks to target ({result4.timeline.target_date})")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    # Print sample advice
    print("\n📝 SAMPLE PERSONALIZED ADVICE (Test 1):")
    print("-" * 80)
    print(result1.personalized_advice)
    
    print("\n📊 MACRO BREAKDOWN (Test 1):")
    print("-" * 80)
    macros = result1.macro_breakdown
    print(f"Protein: {macros['protein']['grams']}g ({macros['protein']['percentage']}%)")
    print(f"Carbs:   {macros['carbs']['grams']}g ({macros['carbs']['percentage']}%)")
    print(f"Fats:    {macros['fats']['grams']}g ({macros['fats']['percentage']}%)")

if __name__ == "__main__":
    try:
        test_analyzer()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
