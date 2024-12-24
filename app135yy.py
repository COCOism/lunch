import streamlit as st
import pandas as pd
import json
import random

# 主程式
def main():
    st.title("週菜單生成器")

    # 加載菜品數據
    def load_recipes():
        try:
            with open("recipes.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            st.error(f"解析 recipes.json 時發生錯誤：{e}")
            st.stop()

    # 加載營養數據
    def load_nutrition_data():
        try:
            with open("ingredients_nutrition.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            st.error(f"解析 ingredients_nutrition.json 時發生錯誤：{e}")
            st.stop()

    # 計算單道菜的營養數據
    def calculate_recipe_nutrition(ingredients, nutrition_data):
        total_nutrition = {"熱量 (kcal)": 0, "蛋白質 (g)": 0, "脂肪 (g)": 0, "碳水化合物 (g)": 0}
        for ingredient, weight in ingredients.items():
            if ingredient in nutrition_data:
                nutrient = nutrition_data[ingredient]
                total_nutrition["熱量 (kcal)"] += nutrient["calories"] * weight / 100
                total_nutrition["蛋白質 (g)"] += nutrient["protein"] * weight / 100
                total_nutrition["脂肪 (g)"] += nutrient["fat"] * weight / 100
                total_nutrition["碳水化合物 (g)"] += nutrient["carbs"] * weight / 100
        return {key: round(value, 1) for key, value in total_nutrition.items()}

    # 計算單天菜單
    def calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes):
        total_people = sum(group_counts.values())
        total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
        category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
        category_calories = {category: total_calories_needed * ratio for category, ratio in category_ratios.items()}

        categorized_recipes = {category: [] for category in category_ratios.keys()}
        for recipe in recipes:
            if recipe["type"] in categorized_recipes and recipe not in used_recipes:
                categorized_recipes[recipe["type"]].append(recipe)

        menu_summary = []

        for category, ratio in category_ratios.items():
            if category == "主菜":
                if day in [1, 3, 5]:  # 豬肉主菜
                    available_recipes = [r for r in categorized_recipes[category] if "豬肉" in r["ingredients"]]
                elif day in [2, 4]:  # 雞肉主菜
                    available_recipes = [r for r in categorized_recipes[category] if "雞肉" in r["ingredients"]]
                else:
                    available_recipes = categorized_recipes[category]
                if not available_recipes:
                    available_recipes = categorized_recipes[category]
            else:
                available_recipes = categorized_recipes.get(category, [])

            if not available_recipes:
                continue
            selected_recipe = random.choice(available_recipes)

            recipe_nutrition = calculate_recipe_nutrition(selected_recipe["ingredients"], nutrition_data)
            portions = round(category_calories[category] / recipe_nutrition["熱量 (kcal)"], 1)
            portions = min(portions, total_people)

            total_ingredients = {ing: round(weight * portions, 1) for ing, weight in selected_recipe["ingredients"].items()}
            total_nutrition = {key: round(value * portions, 1) for key, value in recipe_nutrition.items()}

            menu_summary.append({
                "name": selected_recipe["name"],
                "type": selected_recipe["type"],
                "calories": total_nutrition["熱量 (kcal)"],
                "nutrition": total_nutrition,
                "portions": portions,
                "ingredients": total_ingredients
            })

            used_recipes.append(selected_recipe)

        return menu_summary

    # 生成 5 天菜單
    def generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data):
        weekly_menu = {}
        used_recipes = []
        for day in range(1, 6):
            daily_menu = calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes)
            weekly_menu[f"Day {day}"] = daily_menu
        return weekly_menu

    # 計算總營養
    def calculate_total_nutrition(menu):
        total_nutrition = {"熱量 (kcal)": 0, "蛋白質 (g)": 0, "脂肪 (g)": 0, "碳水化合物 (g)": 0}
        for item in menu:
            for key in total_nutrition:
                total_nutrition[key] += item["nutrition"].get(key, 0)
        return {key: round(value, 1) for key, value in total_nutrition.items()}

    # 檢查營養是否符合標準
    def check_nutrition_compliance(total_nutrition, lunch_nutrition_needs):
        compliance = {}
        for key in total_nutrition:
            compliance[key] = total_nutrition[key] >= lunch_nutrition_needs[key]
        return compliance

    # 顯示菜單的表格
    def build_nutrition_table_with_ingredients(menu):
        rows = []
        for item in menu:
            row = {
                "菜品": item["name"],
                "類型": item["type"],
                "熱量 (kcal)": item["nutrition"]["熱量 (kcal)"],
                "蛋白質 (g)": item["nutrition"]["蛋白質 (g)"],
                "脂肪 (g)": item["nutrition"]["脂肪 (g)"],
                "碳水化合物 (g)": item["nutrition"]["碳水化合物 (g)"],
            }
            rows.append(row)
        return pd.DataFrame(rows)

    # 加載數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    # 用戶輸入人數
    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    # 每日營養需求
    daily_nutrition_needs = {"熱量 (kcal)": 2000, "蛋白質 (g)": 75, "脂肪 (g)": 70, "碳水化合物 (g)": 260}
    lunch_nutrition_needs = {key: value * 0.4 for key, value in daily_nutrition_needs.items()}
    lunch_calories = {group: int(cal * 0.4) for group, cal in {"幼兒_男": 1400, "幼兒_女": 1300}.items()}

    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
