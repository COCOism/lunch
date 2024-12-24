import streamlit as st
import pandas as pd
import json
import random

# 計算單道菜的營養數據
def calculate_recipe_nutrition(ingredients, nutrition_data):
    """
    根據食材營養數據和用量計算每道菜的營養數據。
    """
    total_nutrition = {"熱量 (kcal)": 0, "蛋白質 (g)": 0, "脂肪 (g)": 0, "碳水化合物 (g)": 0}
    for ingredient, weight in ingredients.items():
        if ingredient in nutrition_data:
            nutrient = nutrition_data[ingredient]
            total_nutrition["熱量 (kcal)"] += nutrient["calories"] * weight / 100
            total_nutrition["蛋白質 (g)"] += nutrient["protein"] * weight / 100
            total_nutrition["脂肪 (g)"] += nutrient["fat"] * weight / 100
            total_nutrition["碳水化合物 (g)"] += nutrient["carbs"] * weight / 100
    return {key: round(value, 1) for key, value in total_nutrition.items()}

# 加載菜品數據並計算營養
def load_recipes(nutrition_data):
    try:
        with open("recipes.json", "r", encoding="utf-8") as file:
            recipes = json.load(file)
            for recipe in recipes:
                if "nutrition" not in recipe or not recipe["nutrition"]:
                    recipe["nutrition"] = calculate_recipe_nutrition(recipe["ingredients"], nutrition_data)
            return recipes
    except FileNotFoundError:
        st.error("找不到 recipes.json 文件，請確保該文件存在於程式目錄中。")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"解析 recipes.json 時發生錯誤：{e}")
        st.stop()

# 加載食材營養數據
def load_nutrition_data():
    try:
        with open("ingredients_nutrition.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("找不到 ingredients_nutrition.json 文件，請確保該文件存在於程式目錄中。")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"解析 ingredients_nutrition.json 時發生錯誤：{e}")
        st.stop()

# 計算每日菜單總營養
def calculate_total_nutrition(menu):
    total_nutrition = {"熱量 (kcal)": 0, "蛋白質 (g)": 0, "脂肪 (g)": 0, "碳水化合物 (g)": 0}
    for item in menu:
        for key in total_nutrition:
            total_nutrition[key] += item["nutrition"].get(key, 0)
    return {key: round(value, 1) for key, value in total_nutrition.items()}

# 構建菜單表格
def build_nutrition_table(menu):
    rows = []
    for item in menu:
        row = {
            "類型": item["category"],
            "菜名": item["name"],
            "熱量 (kcal)": item["nutrition"].get("熱量 (kcal)", 0),
            "蛋白質 (g)": item["nutrition"].get("蛋白質 (g)", 0),
            "脂肪 (g)": item["nutrition"].get("脂肪 (g)", 0),
            "碳水化合物 (g)": item["nutrition"].get("碳水化合物 (g)", 0),
        }
        rows.append(row)
    return pd.DataFrame(rows)

# 計算單天的菜單
def calculate_menu_for_day(recipes, used_recipes):
    categorized_recipes = {"主食": [], "主菜": [], "副菜": [], "湯品": []}

    for recipe in recipes:
        if recipe["type"] in categorized_recipes:
            categorized_recipes[recipe["type"]].append(recipe)

    menu = []
    for category, options in categorized_recipes.items():
        if options:
            selected_recipe = random.choice(options)
            used_recipes.append(selected_recipe)
            menu.append({
                "category": category,
                "name": selected_recipe["name"],
                "nutrition": selected_recipe["nutrition"]
            })
    return menu

# 生成 5 天菜單
def generate_weekly_menu(recipes):
    weekly_menu = {}
    used_recipes = []  # 記錄已使用的菜品，避免重複
    for day in range(1, 6):  # 1 到 5 天
        daily_menu = calculate_menu_for_day(recipes, used_recipes)
        weekly_menu[f"Day {day}"] = daily_menu
    return weekly_menu

# 主程式
def main():
    st.title("週菜單生成器")

    # 加載食材營養數據
    nutrition_data = load_nutrition_data()

    # 加載菜品數據並計算營養
    recipes = load_recipes(nutrition_data)

    # 點擊按鈕生成菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 顯示菜單表格
            nutrition_table = build_nutrition_table(menu)
            st.dataframe(nutrition_table)

            # 計算總營養
            total_nutrition = calculate_total_nutrition(menu)
            st.write("菜單總營養成分：", total_nutrition)

if __name__ == "__main__":
    main()
