import streamlit as st
import pandas as pd
import json
import random

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
    for day in range(1, 6):  # 1 到 5 天
        daily_menu = calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes)
        weekly_menu[f"Day {day}"] = daily_menu
    return weekly_menu

# 構建菜單表格，包含營養成分加總和食材總量
def build_nutrition_table_with_ingredients(menu):
    all_ingredients = set()  # 收集所有食材
    for item in menu:
        all_ingredients.update(item["ingredients"].keys())

    rows = []  # 每道菜的數據
    ingredient_totals = {ingredient: 0 for ingredient in all_ingredients}  # 初始化每種食材的總量

    # 填充每道菜的營養成分和食材
    for item in menu:
        row = {
            "菜品": item["name"],
            "類型": item["type"],
            "熱量 (kcal)": item["nutrition"]["熱量 (kcal)"],
            "蛋白質 (g)": item["nutrition"]["蛋白質 (g)"],
            "脂肪 (g)": item["nutrition"]["脂肪 (g)"],
            "碳水化合物 (g)": item["nutrition"]["碳水化合物 (g)"],
        }
        for ingredient in all_ingredients:
            amount = item["ingredients"].get(ingredient, 0)
            row[ingredient] = f"{amount} 克" if amount > 0 else "——"
            ingredient_totals[ingredient] += amount
        rows.append(row)

    # 營養總計
    total_nutrition = {
        "熱量 (kcal)": sum(row["熱量 (kcal)"] for row in rows),
        "蛋白質 (g)": sum(row["蛋白質 (g)"] for row in rows),
        "脂肪 (g)": sum(row["脂肪 (g)"] for row in rows),
        "碳水化合物 (g)": sum(row["碳水化合物 (g)"] for row in rows),
    }

    # 添加總計行
    total_row = {
        "菜品": "總計",
        "類型": "全部",
        "熱量 (kcal)": round(total_nutrition["熱量 (kcal)"], 1),
        "蛋白質 (g)": round(total_nutrition["蛋白質 (g)"], 1),
        "脂肪 (g)": round(total_nutrition["脂肪 (g)"], 1),
        "碳水化合物 (g)": round(total_nutrition["碳水化合物 (g)"], 1),
    }
    for ingredient, total_amount in ingredient_totals.items():
        total_row[ingredient] = f"{round(total_amount, 1)} 克" if total_amount > 0 else "——"

    rows.append(total_row)  # 添加總計行到表格中

    return pd.DataFrame(rows)  # 返回表格作為 DataFrame

# 主程式
def main():
    st.title("週菜單生成器")

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
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(calories_per_day.get(group, 0) * lunch_ratio) for group in group_counts}

    # 鍵一致性檢查
    if set(group_counts.keys()) != set(lunch_calories.keys()):
        st.error("用餐人數的鍵與午餐熱量計算的鍵不匹配，請檢查配置！")
        st.stop()

    # 點擊按鈕生成菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data)
        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 顯示菜單表格
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
