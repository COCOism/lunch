import streamlit as st
import pandas as pd
import json
import random

# 加載菜譜數據
def load_recipes():
    try:
        with open("recipes.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        st.error(f"解析 recipes.json 時發生錯誤：{e}")
        st.stop()

# 加載食材營養數據
def load_nutrition_data():
    try:
        with open("ingredients_nutrition.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        st.error(f"解析 ingredients_nutrition.json 時發生錯誤：{e}")
        st.stop()

# 計算營養成分
def calculate_recipe_nutrition(ingredients, nutrition_data):
    total_nutrition = {"熱量": 0, "蛋白質": 0, "脂肪": 0, "碳水化合物": 0}
    for ingredient, weight in ingredients.items():
        if ingredient in nutrition_data:
            nutrient = nutrition_data[ingredient]
            total_nutrition["熱量"] += nutrient["calories"] * weight / 100
            total_nutrition["蛋白質"] += nutrient["protein"] * weight / 100
            total_nutrition["脂肪"] += nutrient["fat"] * weight / 100
            total_nutrition["碳水化合物"] += nutrient["carbs"] * weight / 100
    return {key: round(value, 1) for key, value in total_nutrition.items()}

# 計算單天菜單
def calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes, lunch_calorie_ranges):
    total_people = sum(group_counts.values())
    total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
    category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
    category_calories = {category: total_calories_needed * ratio for category, ratio in category_ratios.items()}

    categorized_recipes = {category: [] for category in category_ratios.keys()}
    for recipe in recipes:
        if recipe["type"] in categorized_recipes and recipe not in used_recipes:
            categorized_recipes[recipe["type"]].append(recipe)

    menu_summary = []
    total_calories_actual = {group: 0 for group in group_counts.keys()}

    for category, ratio in category_ratios.items():
        available_recipes = categorized_recipes.get(category, [])
        if not available_recipes:
            continue
        selected_recipe = random.choice(available_recipes)
        recipe_nutrition = calculate_recipe_nutrition(selected_recipe["ingredients"], nutrition_data)
        if recipe_nutrition["熱量"] == 0:
            continue

        portions = round(category_calories[category] / recipe_nutrition["熱量"], 1)
        portions = min(portions, total_people)

        for group, count in group_counts.items():
            group_calories = recipe_nutrition["熱量"] * portions / total_people * count
            total_calories_actual[group] += group_calories

        menu_summary.append({
            "name": selected_recipe["name"],
            "type": selected_recipe["type"],
            "calories": recipe_nutrition["熱量"],
            "nutrition": recipe_nutrition,
            "portions": portions,
            "ingredients": {ing: round(weight * portions, 1) for ing, weight in selected_recipe["ingredients"].items()},
        })
        used_recipes.append(selected_recipe)

    for group, (min_cal, max_cal) in lunch_calorie_ranges.items():
        actual_calories = total_calories_actual[group]
        if actual_calories < min_cal:
            st.warning(f"{group} 的實際熱量 ({actual_calories:.1f} kcal) 低於需求範圍 ({min_cal}-{max_cal} kcal)")
        elif actual_calories > max_cal:
            st.warning(f"{group} 的實際熱量 ({actual_calories:.1f} kcal) 高於需求範圍 ({min_cal}-{max_cal} kcal)")
        else:
            st.success(f"{group} 的實際熱量 ({actual_calories:.1f} kcal) 符合需求範圍 ({min_cal}-{max_cal} kcal)")

    return menu_summary

# 為 5 天生成菜單
def generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data, lunch_calorie_ranges):
    weekly_menu = {}
    used_recipes = []

    for day in range(1, 6):
        daily_menu = calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes, lunch_calorie_ranges)
        weekly_menu[f"Day {day}"] = daily_menu

    return weekly_menu

# 主應用
def main():
    st.title("週菜單生成器")

    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    lunch_calorie_ranges = {
        "幼兒_男": (400, 560),
        "幼兒_女": (400, 560),
        "國小_男": (560, 880),
        "國小_女": (560, 880),
        "成人_男": (880, 1200),
        "成人_女": (720, 960),
    }

    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data, lunch_calorie_ranges)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue
            st.write(menu)

if __name__ == "__main__":
    main()
