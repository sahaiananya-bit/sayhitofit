"""
AI Body Composition and Caloric Analysis Module
Analyzes client body composition and provides personalized fitness recommendations
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime, timedelta
import math

# Enums for activity levels and goals
class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"  # Little or no exercise
    LIGHT = "light"  # 1-3 days/week light exercise
    MODERATE = "moderate"  # 3-5 days/week moderate exercise
    VERY_ACTIVE = "very_active"  # 6-7 days/week intense exercise
    EXTRA_ACTIVE = "extra_active"  # Physical job or training twice per day

class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

# Request/Response Models
class BodyCompositionRequest(BaseModel):
    height_cm: float
    weight_kg: float
    age: int
    gender: Gender
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    # Optional physique photo as a data: URL (image/jpeg or image/png).
    # Analyzed by the vision model once, never stored. ~6 MB cap post-encoding.
    photo_data_url: Optional[str] = Field(default=None, max_length=6_000_000)

class CalorieRecommendation(BaseModel):
    maintenance: float
    deficit_loss: float  # For weight loss (500 cal deficit)
    surplus_gain: float  # For muscle gain (500 cal surplus)

class WeightTimeline(BaseModel):
    weekly_change_kg: float
    weeks_to_goal: Optional[int] = None
    target_date: Optional[str] = None

class WorkoutExercise(BaseModel):
    name: str
    sets: str
    reps: str
    rest: str

class WorkoutDay(BaseModel):
    day: str
    focus: str
    exercises: list[WorkoutExercise]

class WorkoutPlan(BaseModel):
    split_name: str
    weekly_schedule: list[WorkoutDay]

class MealItem(BaseModel):
    meal: str
    suggestions: list[str]

class NutritionPlan(BaseModel):
    template_name: str
    daily_meals: list[MealItem]
    pantry_staples: list[str]

class BodyCompositionResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    body_fat_percentage: Optional[float] = None
    lean_mass_kg: float
    fat_mass_kg: float
    caloric_recommendation: CalorieRecommendation
    weight_suggestion: str
    target_weight_range: Dict[str, float]
    personalized_advice: str
    weekly_targets: Dict[str, str]
    timeline: WeightTimeline
    macro_breakdown: Dict[str, Dict[str, float]]
    workout_plan: WorkoutPlan
    nutrition_plan: NutritionPlan
    plan_source: str = "rules"  # "ai" when plans come from the language model

class BodyCompositionAnalyzer:
    """AI analyzer for body composition and fitness recommendations"""
    
    # Activity level multipliers
    ACTIVITY_MULTIPLIERS = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTRA_ACTIVE: 1.9
    }
    
    # BMI Categories
    BMI_CATEGORIES = {
        (0, 18.5): "Underweight",
        (18.5, 25): "Normal Weight",
        (25, 30): "Overweight",
        (30, float('inf')): "Obese"
    }
    
    def __init__(self):
        pass
    
    def calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        """Calculate BMI (Body Mass Index)"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    
    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category based on BMI value"""
        for (min_val, max_val), category in self.BMI_CATEGORIES.items():
            if min_val <= bmi < max_val:
                return category
        return "Obese"
    
    def calculate_bmr_mifflin_st_jeor(
        self,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: Gender
    ) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
        More accurate for modern populations
        """
        if gender == Gender.MALE:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        return round(bmr, 1)
    
    def calculate_tdee(
        self,
        bmr: float,
        activity_level: ActivityLevel
    ) -> float:
        """Calculate Total Daily Energy Expenditure"""
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        tdee = bmr * multiplier
        return round(tdee, 1)
    
    def estimate_body_fat_percentage(
        self,
        age: int,
        gender: Gender,
        height_cm: float,
        waist_cm: Optional[float] = None,
        hip_cm: Optional[float] = None,
        neck_cm: Optional[float] = None,
        bmi: Optional[float] = None
    ) -> Optional[float]:
        """
        Estimate body fat percentage using available measurements
        Uses the US Navy circumference method when measurements allow,
        otherwise falls back to the Deurenberg BMI-based formula
        """
        if waist_cm and neck_cm and waist_cm > neck_cm:
            if gender == Gender.MALE:
                body_fat = 495 / (
                    1.0324
                    - 0.19077 * math.log10(waist_cm - neck_cm)
                    + 0.15456 * math.log10(height_cm)
                ) - 450
                return round(max(0, min(60, body_fat)), 1)
            elif hip_cm:
                # Navy formula for women requires the hip measurement
                body_fat = 495 / (
                    1.29579
                    - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm)
                    + 0.22100 * math.log10(height_cm)
                ) - 450
                return round(max(0, min(60, body_fat)), 1)
        
        # Fallback: Use BMI-based estimation (Deurenberg formula)
        if bmi:
            if gender == Gender.MALE:
                body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
            else:
                body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
            
            return round(max(0, min(60, body_fat)), 1)
        
        return None
    
    def calculate_lean_mass(
        self,
        weight_kg: float,
        body_fat_percentage: float
    ) -> tuple:
        """Calculate lean mass and fat mass"""
        fat_mass = weight_kg * (body_fat_percentage / 100)
        lean_mass = weight_kg - fat_mass
        return round(lean_mass, 1), round(fat_mass, 1)
    
    def calculate_caloric_recommendations(
        self,
        tdee: float,
        fitness_goal: FitnessGoal
    ) -> CalorieRecommendation:
        """Generate caloric recommendations based on fitness goal"""
        return CalorieRecommendation(
            maintenance=round(tdee, 0),
            deficit_loss=round(tdee - 500, 0),  # 500 cal deficit for ~0.5kg loss/week
            surplus_gain=round(tdee + 500, 0)   # 500 cal surplus for ~0.5kg gain/week
        )
    
    def calculate_target_weight_range(
        self,
        height_cm: float,
        gender: Gender,
        current_weight: float
    ) -> Dict[str, float]:
        """Calculate ideal weight range based on BMI"""
        height_m = height_cm / 100
        min_weight = 18.5 * (height_m ** 2)
        max_weight = 25 * (height_m ** 2)
        
        return {
            "min": round(min_weight, 1),
            "max": round(max_weight, 1),
            "current": round(current_weight, 1)
        }
    
    def generate_weight_suggestion(
        self,
        bmi: float,
        fitness_goal: FitnessGoal,
        body_fat_percentage: Optional[float] = None
    ) -> str:
        """Generate weight change suggestion"""
        if fitness_goal == FitnessGoal.WEIGHT_LOSS:
            return "decrease"
        elif fitness_goal == FitnessGoal.MUSCLE_GAIN:
            return "increase"
        else:
            if bmi < 18.5:
                return "increase"
            elif bmi > 25:
                return "decrease"
            else:
                return "maintain"
    
    def generate_timeline(
        self,
        current_weight: float,
        target_weight: float,
        fitness_goal: FitnessGoal
    ) -> WeightTimeline:
        """Calculate timeline to reach target weight"""
        weight_difference = abs(current_weight - target_weight)
        
        if fitness_goal == FitnessGoal.WEIGHT_LOSS:
            weekly_change = 0.5  # Conservative 0.5kg per week loss
            direction = "loss"
        elif fitness_goal == FitnessGoal.MUSCLE_GAIN:
            weekly_change = 0.25  # Conservative 0.25kg per week gain
            direction = "gain"
        else:
            return WeightTimeline(weekly_change_kg=0, weeks_to_goal=None, target_date=None)
        
        if weight_difference > 0:
            weeks = round(weight_difference / weekly_change)
            target_date = (datetime.now() + timedelta(weeks=weeks)).strftime("%Y-%m-%d")
        else:
            weeks = None
            target_date = None
        
        return WeightTimeline(
            weekly_change_kg=weekly_change,
            weeks_to_goal=weeks,
            target_date=target_date
        )
    
    def generate_personalized_advice(
        self,
        bmi: float,
        body_fat_percentage: Optional[float],
        fitness_goal: FitnessGoal,
        activity_level: ActivityLevel,
        age: int
    ) -> str:
        """Generate personalized fitness advice"""
        advice_lines = []
        
        # BMI-based advice
        bmi_category = self.get_bmi_category(bmi)
        if bmi_category == "Underweight":
            advice_lines.append("✓ You are underweight. Focus on progressive strength training with caloric surplus.")
            advice_lines.append("✓ Prioritize compound movements: squats, deadlifts, bench press.")
        elif bmi_category == "Normal Weight":
            advice_lines.append("✓ Your BMI is healthy! Maintain with consistent training.")
        elif bmi_category == "Overweight":
            advice_lines.append("✓ You are overweight. Combine moderate caloric deficit with strength training.")
            advice_lines.append("✓ Aim for 150-300 min of cardio per week.")
        elif bmi_category == "Obese":
            advice_lines.append("✓ Start with low-impact exercises: walking, swimming, cycling.")
            advice_lines.append("✓ Consult with healthcare professionals before starting intense training.")
        
        # Body fat-based advice
        if body_fat_percentage:
            if fitness_goal == FitnessGoal.MUSCLE_GAIN:
                if body_fat_percentage > 20:
                    advice_lines.append("✓ Consider cutting first to lower body fat before bulking.")
                else:
                    advice_lines.append("✓ Your body fat is optimal for muscle-building phase.")
            elif fitness_goal == FitnessGoal.WEIGHT_LOSS:
                advice_lines.append(f"✓ Current body fat: {body_fat_percentage}%. Target is 15-20% for men, 20-25% for women.")
        
        # Activity level advice
        if activity_level == ActivityLevel.SEDENTARY:
            advice_lines.append("✓ Increase daily movement: take stairs, walk more, add stretching.")
        elif activity_level == ActivityLevel.LIGHT:
            advice_lines.append("✓ Increase training frequency to 4-5 days per week for better results.")
        
        # Age-based advice
        if age > 40:
            advice_lines.append("✓ Focus on joint health: warm up properly and include mobility work.")
            advice_lines.append("✓ Prioritize recovery: ensure 7-9 hours of sleep daily.")
        
        # Goal-specific advice
        if fitness_goal == FitnessGoal.WEIGHT_LOSS:
            advice_lines.append("✓ Create a 300-500 calorie deficit through diet and exercise.")
            advice_lines.append("✓ Don't skip strength training - preserve muscle during fat loss.")
        elif fitness_goal == FitnessGoal.MUSCLE_GAIN:
            advice_lines.append("✓ Eat 300-500 calories above maintenance.")
            advice_lines.append("✓ Focus on progressive overload in your training.")
        
        return "\n".join(advice_lines)
    
    def calculate_macro_breakdown(
        self,
        daily_calories: float,
        fitness_goal: FitnessGoal,
        lean_mass_kg: float
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate macro nutrient breakdown
        Returns protein, carbs, and fat in grams and percentages
        """
        # Protein: 1.6-2.2g per kg lean mass for muscle gain, 1.6-2.4g for loss
        if fitness_goal == FitnessGoal.MUSCLE_GAIN:
            protein_ratio = 0.30  # 30% of calories
            fat_ratio = 0.25     # 25% of calories
            carbs_ratio = 0.45   # 45% of calories
        elif fitness_goal == FitnessGoal.WEIGHT_LOSS:
            protein_ratio = 0.35  # 35% of calories
            fat_ratio = 0.25     # 25% of calories
            carbs_ratio = 0.40   # 40% of calories
        else:
            protein_ratio = 0.30  # 30% of calories
            fat_ratio = 0.25     # 25% of calories
            carbs_ratio = 0.45   # 45% of calories
        
        protein_cals = daily_calories * protein_ratio
        carbs_cals = daily_calories * carbs_ratio
        fat_cals = daily_calories * fat_ratio
        
        return {
            "protein": {
                "grams": round(protein_cals / 4, 1),
                "calories": round(protein_cals, 0),
                "percentage": round(protein_ratio * 100, 1)
            },
            "carbs": {
                "grams": round(carbs_cals / 4, 1),
                "calories": round(carbs_cals, 0),
                "percentage": round(carbs_ratio * 100, 1)
            },
            "fats": {
                "grams": round(fat_cals / 9, 1),
                "calories": round(fat_cals, 0),
                "percentage": round(fat_ratio * 100, 1)
            }
        }

    def generate_workout_plan(self, goal: FitnessGoal, activity: ActivityLevel) -> WorkoutPlan:
        """Generate a weekly workout split based on goal and activity level"""
        if goal == FitnessGoal.WEIGHT_LOSS:
            split_name = "Metabolic Conditioning & Strength"
            days = [
                WorkoutDay(day="Monday", focus="Full Body Strength", exercises=[
                    WorkoutExercise(name="Goblet Squats", sets="3", reps="12-15", rest="60s"),
                    WorkoutExercise(name="Push-ups", sets="3", reps="max", rest="60s"),
                    WorkoutExercise(name="Dumbbell Rows", sets="3", reps="12", rest="60s")
                ]),
                WorkoutDay(day="Wednesday", focus="HIIT Cardio", exercises=[
                    WorkoutExercise(name="Burpees", sets="4", reps="30s", rest="30s"),
                    WorkoutExercise(name="Mountain Climbers", sets="4", reps="30s", rest="30s"),
                    WorkoutExercise(name="Jumping Jacks", sets="4", reps="60s", rest="30s")
                ]),
                WorkoutDay(day="Friday", focus="Full Body Circuit", exercises=[
                    WorkoutExercise(name="Lunges", sets="3", reps="15/side", rest="45s"),
                    WorkoutExercise(name="Plank", sets="3", reps="45s", rest="45s"),
                    WorkoutExercise(name="Kettlebell Swings", sets="3", reps="20", rest="45s")
                ])
            ]
        elif goal == FitnessGoal.MUSCLE_GAIN:
            split_name = "Hypertrophy Upper/Lower Split"
            days = [
                WorkoutDay(day="Monday", focus="Upper Body Power", exercises=[
                    WorkoutExercise(name="Bench Press", sets="4", reps="6-8", rest="120s"),
                    WorkoutExercise(name="Barbell Rows", sets="4", reps="6-8", rest="120s"),
                    WorkoutExercise(name="Overhead Press", sets="3", reps="8-10", rest="90s")
                ]),
                WorkoutDay(day="Tuesday", focus="Lower Body Power", exercises=[
                    WorkoutExercise(name="Back Squats", sets="4", reps="6-8", rest="120s"),
                    WorkoutExercise(name="Romanian Deadlifts", sets="4", reps="8-10", rest="120s"),
                    WorkoutExercise(name="Leg Press", sets="3", reps="10-12", rest="90s")
                ]),
                WorkoutDay(day="Thursday", focus="Upper Body Hypertrophy", exercises=[
                    WorkoutExercise(name="Incline DB Press", sets="3", reps="10-12", rest="90s"),
                    WorkoutExercise(name="Lat Pulldowns", sets="3", reps="10-12", rest="90s"),
                    WorkoutExercise(name="Lateral Raises", sets="3", reps="15", rest="60s")
                ]),
                WorkoutDay(day="Friday", focus="Lower Body Hypertrophy", exercises=[
                    WorkoutExercise(name="Leg Extensions", sets="3", reps="12-15", rest="90s"),
                    WorkoutExercise(name="Leg Curls", sets="3", reps="12-15", rest="90s"),
                    WorkoutExercise(name="Calf Raises", sets="4", reps="15-20", rest="60s")
                ])
            ]
        else:
            split_name = "Balanced Maintenance Split"
            days = [
                WorkoutDay(day="Monday", focus="Strength A", exercises=[
                    WorkoutExercise(name="Squats", sets="3", reps="8-10", rest="90s"),
                    WorkoutExercise(name="Bench Press", sets="3", reps="8-10", rest="90s")
                ]),
                WorkoutDay(day="Wednesday", focus="Active Recovery", exercises=[
                    WorkoutExercise(name="LISS Cardio (Walking)", sets="1", reps="45 min", rest="N/A"),
                    WorkoutExercise(name="Yoga/Flow", sets="1", reps="20 min", rest="N/A")
                ]),
                WorkoutDay(day="Friday", focus="Strength B", exercises=[
                    WorkoutExercise(name="Deadlifts", sets="3", reps="5", rest="120s"),
                    WorkoutExercise(name="Pull-ups", sets="3", reps="8-10", rest="90s")
                ])
            ]
        
        return WorkoutPlan(split_name=split_name, weekly_schedule=days)

    def generate_nutrition_plan(self, goal: FitnessGoal) -> NutritionPlan:
        """Generate a basic nutrition plan template based on goal"""
        pantry = ["Extra Virgin Olive Oil", "Pink Himalayan Salt", "Greek Yogurt", "Raw Honey", "Oats"]
        
        if goal == FitnessGoal.WEIGHT_LOSS:
            template = "High Protein / Low Carb (Fat Loss)"
            meals = [
                MealItem(meal="Breakfast", suggestions=["Egg white omelette with spinach", "Smoked salmon on keto toast"]),
                MealItem(meal="Lunch", suggestions=["Grilled chicken salad with apple cider vinaigrette", "Baked cod with steamed broccoli"]),
                MealItem(meal="Dinner", suggestions=["Grass-fed steak with asparagus", "Zucchini noodles with turkey meatballs"])
            ]
            pantry.extend(["Apple Cider Vinegar", "Green Tea", "Chia Seeds"])
        elif goal == FitnessGoal.MUSCLE_GAIN:
            template = "High Protein / High Carb (Muscle Building)"
            meals = [
                MealItem(meal="Breakfast", suggestions=["Protein oatmeal with banana and almond butter", "Egg scramble with sweet potato hash"]),
                MealItem(meal="Lunch", suggestions=["Ground beef with brown rice and bell peppers", "Chicken breast pasta with marinara"]),
                MealItem(meal="Dinner", suggestions=["Salmon with quinoa and avocado", "Lean turkey burger on whole grain bun"])
            ]
            pantry.extend(["Creatine Monohydrate", "Whey Protein", "Peanut Butter"])
        else:
            template = "Balanced Whole Foods (Maintenance)"
            meals = [
                MealItem(meal="Breakfast", suggestions=["Greek yogurt parfait with mixed berries", "Poached eggs on sourdough"]),
                MealItem(meal="Lunch", suggestions=["Turkey wrap with hummus and greens", "Quinoa bowl with chickpeas and roasted veg"]),
                MealItem(meal="Dinner", suggestions=["Air-fried chicken thighs with roasted potatoes", "Baked salmon with brown rice"])
            ]
            pantry.extend(["Mixed Nuts", "Quinoa", "Avocado Oil"])
            
        return NutritionPlan(template_name=template, daily_meals=meals, pantry_staples=pantry)

    def analyze(self, request: BodyCompositionRequest) -> BodyCompositionResponse:
        """
        Main analysis function - compiles all calculations
        """
        # Calculate basic metrics
        bmi = self.calculate_bmi(request.height_cm, request.weight_kg)
        bmi_category = self.get_bmi_category(bmi)
        bmr = self.calculate_bmr_mifflin_st_jeor(
            request.weight_kg,
            request.height_cm,
            request.age,
            request.gender
        )
        tdee = self.calculate_tdee(bmr, request.activity_level)
        
        # Calculate body composition
        body_fat_percentage = self.estimate_body_fat_percentage(
            request.age,
            request.gender,
            request.height_cm,
            request.waist_cm,
            request.hip_cm,
            request.neck_cm,
            bmi
        )
        
        lean_mass, fat_mass = self.calculate_lean_mass(
            request.weight_kg,
            body_fat_percentage if body_fat_percentage else 20
        )
        
        # Generate recommendations
        caloric_rec = self.calculate_caloric_recommendations(tdee, request.fitness_goal)
        target_weight_range = self.calculate_target_weight_range(
            request.height_cm,
            request.gender,
            request.weight_kg
        )
        weight_suggestion = self.generate_weight_suggestion(
            bmi,
            request.fitness_goal,
            body_fat_percentage
        )
        
        # Determine target weight
        if weight_suggestion == "decrease":
            target_weight = target_weight_range["min"]
        elif weight_suggestion == "increase":
            target_weight = target_weight_range["max"]
        else:
            target_weight = request.weight_kg
        
        timeline = self.generate_timeline(
            request.weight_kg,
            target_weight,
            request.fitness_goal
        )
        
        personalized_advice = self.generate_personalized_advice(
            bmi,
            body_fat_percentage,
            request.fitness_goal,
            request.activity_level,
            request.age
        )
        
        macro_breakdown = self.calculate_macro_breakdown(
            caloric_rec.maintenance,
            request.fitness_goal,
            lean_mass
        )
        
        # Weekly targets
        weekly_targets = {
            "training_days": "4-5 days per week",
            "cardio": "150-300 min per week",
            "protein_daily": f"{macro_breakdown['protein']['grams']}g",
            "water_intake": f"{request.weight_kg * 30}ml per day (approx)"
        }
        
        return BodyCompositionResponse(
            bmi=bmi,
            bmi_category=bmi_category,
            bmr=bmr,
            tdee=tdee,
            body_fat_percentage=body_fat_percentage,
            lean_mass_kg=lean_mass,
            fat_mass_kg=fat_mass,
            caloric_recommendation=caloric_rec,
            weight_suggestion=weight_suggestion,
            target_weight_range=target_weight_range,
            personalized_advice=personalized_advice,
            weekly_targets=weekly_targets,
            timeline=timeline,
            macro_breakdown=macro_breakdown,
            workout_plan=self.generate_workout_plan(request.fitness_goal, request.activity_level),
            nutrition_plan=self.generate_nutrition_plan(request.fitness_goal)
        )

# Create a singleton instance
analyzer = BodyCompositionAnalyzer()
