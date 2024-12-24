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

# 計算每日總熱量需求
def calculate_fixed_calories(fixed_group_counts, calorie_ranges):
    total_min_calories = 0
    total_max_calories = 0
    for group, count in fixed_group_counts.items():
        group_min, group_max = calorie_ranges[group]
        total_min_calories += group_min * count
        total_max_calories += group_max * count
    return total_min_calories, total_max_calories

# 為 5 天生成菜單
def generate_weekly_menu_fixed(recipes, total_calories, nutrition_data):
    weekly_menu = {}
    used_recipes = []  # 全局已使用菜品記錄
    
    for day in range(1, 6):  # 1 到 5 天
        daily_menu = calculate_menu_for_day_fixed(recipes, total_calories, nutrition_data, used_recipes)
        weekly_menu[f"Day {day}"] = daily_menu

    return weekly_menu

# 計算單天菜單（固定熱量）
def calculate_menu_for_day_fixed(recipes, total_calories, nutrition_data, used_recipes):
    category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
    category_calories = {category: total_calories * ratio for category, ratio in category_ratios.items()}

    categorized_recipes = {category: [] for category in category_ratios.keys()}
    for recipe in recipes:
        if recipe["type"] in categorized_recipes and recipe not in used_recipes:
            categorized_recipes[recipe["type"]].append(recipe)

    menu_summary = []

    for category, ratio in category_ratios.items():
        available_recipes = categorized_recipes.get(category, [])
        if not available_recipes:
            continue
        selected_recipe = random.choice(available_recipes)
        
        recipe_nutrition = calculate_recipe_nutrition(selected_recipe["ingredients"], nutrition_data)
        if recipe_nutrition["熱量"] == 0:
            continue
        portions = round(category_calories[category] / recipe_nutrition["熱量"], 1)

        total_ingredients = {ing: round(weight * portions, 1) for ing, weight in selected_recipe["ingredients"].items()}
        total_nutrition = {key: round(value * portions, 1) for key, value in recipe_nutrition.items()}

        menu_summary.append({
            "name": selected_recipe["name"],
            "type": selected_recipe["type"],
            "calories": total_nutrition["熱量"],
            "nutrition": total_nutrition,
            "portions": portions,
            "ingredients": total_ingredients
        })

        used_recipes.append(selected_recipe)

    return menu_summary

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

# 主應用
def main():
    st.title("固定人數週菜單生成器")

    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    fixed_group_counts = {
        "幼兒": 6,
        "國小": 48,
        "成年男性": 22,
        "成年女性": 0
    }

    calorie_ranges = {
        "幼兒": (400, 560),
        "國小": (560, 880),
        "成年男性": (880, 1200),
        "成年女性": (720, 960)
    }

    total_min_calories, total_max_calories = calculate_fixed_calories(fixed_group_counts, calorie_ranges)
    st.sidebar.write(f"每日固定熱量需求範圍: {total_min_calories} - {total_max_calories} 大卡")

    total_calories = (total_min_calories + total_max_calories) // 2  # 平均熱量需求

    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu_fixed(recipes, total_calories, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
