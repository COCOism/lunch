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
def calculate_dynamic_calories(group_counts, calorie_ranges):
    total_min_calories = 0
    total_max_calories = 0
    for group, count in group_counts.items():
        group_min, group_max = calorie_ranges[group]
        total_min_calories += group_min * count
        total_max_calories += group_max * count
    return total_min_calories, total_max_calories

# 計算每日總蛋白質需求
def calculate_protein_requirements(group_counts, protein_ranges):
    total_min_protein = 0
    total_max_protein = 0
    for group, count in group_counts.items():
        group_min, group_max = protein_ranges[group]
        total_min_protein += group_min * count
        total_max_protein += group_max * count
    return total_min_protein, total_max_protein

# 為 5 天生成菜單
def generate_weekly_menu_dynamic(recipes, total_calories, total_protein, nutrition_data):
    weekly_menu = {}
    used_recipes = []  # 全局已使用菜品記錄

    for day in range(1, 6):  # 1 到 5 天
        daily_menu = calculate_menu_for_day_dynamic(
            recipes, total_calories, total_protein, nutrition_data, used_recipes, max_retries=10
        )
        if not daily_menu:
            st.error(f"Day {day} 的菜單未能在限制內滿足蛋白質需求。請檢查數據或調整菜單設置。")
        else:
            weekly_menu[f"Day {day}"] = daily_menu

    return weekly_menu

# 計算單天菜單（動態蛋白質和熱量）
def calculate_menu_for_day_dynamic(recipes, total_calories, total_protein, nutrition_data, used_recipes, max_retries=10):
    category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
    category_calories = {category: total_calories * ratio for category, ratio in category_ratios.items()}

    for _ in range(max_retries):
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
            if recipe_nutrition["熱量"] == 0 or recipe_nutrition["蛋白質"] == 0:
                continue
            portions = min(
                round(category_calories[category] / recipe_nutrition["熱量"], 1),
                round(total_protein / recipe_nutrition["蛋白質"], 1)
            )

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

        # 校驗每日總蛋白質是否符合範圍
        daily_total_protein = sum(item["nutrition"]["蛋白質"] for item in menu_summary)
        if total_protein * 0.9 <= daily_total_protein <= total_protein * 1.1:
            return menu_summary

    return []  # 如果達到最大嘗試次數，返回空菜單

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

# 構建營養成分和食材數量表格
def build_nutrition_table_with_ingredients(menu):
    all_ingredients = set()
    for item in menu:
        all_ingredients.update(item["ingredients"].keys())

    rows = []
    ingredient_totals = {ingredient: 0 for ingredient in all_ingredients}

    for item in menu:
        row = {
            "菜品": item["name"],
            "類型": item["type"],
            "熱量 (kcal)": item["nutrition"]["熱量"],
            "蛋白質 (g)": item["nutrition"]["蛋白質"],
            "脂肪 (g)": item["nutrition"]["脂肪"],
            "碳水化合物 (g)": item["nutrition"]["碳水化合物"],
        }
        for ingredient in all_ingredients:
            amount = item["ingredients"].get(ingredient, 0)
            row[f"{ingredient} (g)"] = f"{round(amount, 1)}" if amount > 0 else "0"
            ingredient_totals[ingredient] += amount
        rows.append(row)

    total_nutrition = {
        "熱量 (kcal)": sum(row["熱量 (kcal)"] for row in rows),
        "蛋白質 (g)": sum(row["蛋白質 (g)"] for row in rows),
        "脂肪 (g)": sum(row["脂肪 (g)"] for row in rows),
        "碳水化合物 (g)": sum(row["碳水化合物 (g)"] for row in rows),
    }
    total_row = {
        "菜品": "總計",
        "類型": "全部",
        "熱量 (kcal)": round(total_nutrition["熱量 (kcal)"], 1),
        "蛋白質 (g)": round(total_nutrition["蛋白質 (g)"], 1),
        "脂肪 (g)": round(total_nutrition["脂肪 (g)"], 1),
        "碳水化合物 (g)": round(total_nutrition["碳水化合物 (g)"], 1),
    }
    for ingredient, total_amount in ingredient_totals.items():
        total_row[f"{ingredient} (g)"] = f"{round(total_amount, 1)}"
    rows.append(total_row)

    return pd.DataFrame(rows)

# 主應用
def main():
    st.title("動態人數週菜單生成器（蛋白質與熱量平衡）")

    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    calorie_ranges = {
        "幼兒": (400, 560),
        "國小": (560, 880),
        "成年男性": (880, 1200),
        "成年女性": (720, 960)
    }

    protein_ranges = {
        "幼兒": (6, 8),
        "國小": (12, 20),
        "成年男性": (24, 32),
        "成年女性": (20, 28)
    }

    group_counts = {
        "幼兒": st.sidebar.number_input("幼兒人數", min_value=0, value=6),
        "國小": st.sidebar.number_input("國小人數", min_value=0, value=48),
        "成年男性": st.sidebar.number_input("成年男性人數", min_value=0, value=22),
        "成年女性": st.sidebar.number_input("成年女性人數", min_value=0, value=0),
    }
    total_min_calories, total_max_calories = calculate_dynamic_calories(group_counts, calorie_ranges)
    total_min_protein, total_max_protein = calculate_protein_requirements(group_counts, protein_ranges)

    st.sidebar.write(f"每日熱量需求範圍: {total_min_calories} - {total_max_calories} 大卡")
    st.sidebar.write(f"每日蛋白質需求範圍: {total_min_protein} - {total_max_protein} 克")

    total_calories = (total_min_calories + total_max_calories) // 2
    total_protein = (total_min_protein + total_max_protein) // 2

    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu_dynamic(recipes, total_calories, total_protein, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
