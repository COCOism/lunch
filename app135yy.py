import streamlit as st
import pandas as pd
import json
import random
import matplotlib.pyplot as plt

# 加載菜譜數據
def load_recipes():
    try:
        with open("recipes.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"解析 recipes.json 時發生錯誤：{e}")
        st.stop()

# 加載食材營養數據
def load_nutrition_data():
    try:
        with open("ingredients_nutrition.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"解析 ingredients_nutrition.json 時發生錯誤：{e}")
        st.stop()

# 計算菜品營養成分
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

# 檢查每日營養比例
def validate_nutrition_ratio(menu_summary, total_calories):
    nutrition = {"蛋白質": 0, "脂肪": 0, "碳水化合物": 0}
    for item in menu_summary:
        nutrition["蛋白質"] += item["nutrition"]["蛋白質"]
        nutrition["脂肪"] += item["nutrition"]["脂肪"]
        nutrition["碳水化合物"] += item["nutrition"]["碳水化合物"]

    protein_ratio = (nutrition["蛋白質"] * 4) / total_calories * 100
    fat_ratio = (nutrition["脂肪"] * 9) / total_calories * 100
    carb_ratio = (nutrition["碳水化合物"] * 4) / total_calories * 100

    return {
        "蛋白質": round(protein_ratio, 1),
        "脂肪": round(fat_ratio, 1),
        "碳水化合物": round(carb_ratio, 1),
        "valid": 15 <= protein_ratio <= 25 and 20 <= fat_ratio <= 30 and 50 <= carb_ratio <= 60
    }

# 繪製營養比例圖表
def plot_nutrition_ratio(validation):
    labels = ["蛋白質", "脂肪", "碳水化合物"]
    values = [validation["蛋白質"], validation["脂肪"], validation["碳水化合物"]]
    plt.bar(labels, values, color=["#ff9999", "#66b3ff", "#99ff99"])
    plt.axhline(y=15, color='red', linestyle='--', label='蛋白質最低')
    plt.axhline(y=25, color='red', linestyle='--', label='蛋白質最高')
    plt.axhline(y=20, color='blue', linestyle='--', label='脂肪最低')
    plt.axhline(y=30, color='blue', linestyle='--', label='脂肪最高')
    plt.axhline(y=50, color='green', linestyle='--', label='碳水最低')
    plt.axhline(y=60, color='green', linestyle='--', label='碳水最高')
    plt.ylabel("比例 (%)")
    plt.title("每日營養成分比例")
    plt.legend()
    st.pyplot(plt)

# 為某一天生成菜單
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
    for category in category_ratios:
        available_recipes = categorized_recipes.get(category, [])
        if not available_recipes:
            continue

        selected_recipe = random.choice(available_recipes)
        recipe_nutrition = calculate_recipe_nutrition(selected_recipe["ingredients"], nutrition_data)
        if recipe_nutrition["熱量"] == 0:
            continue

        portions = round(category_calories[category] / recipe_nutrition["熱量"], 1)
        portions = min(portions, total_people)
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

# 構建營養表
def build_nutrition_table_with_ingredients(menu):
    rows = []
    for item in menu:
        row = {
            "菜品": item["name"],
            "類型": item["type"],
            "熱量 (kcal)": item["nutrition"]["熱量"],
            "蛋白質 (g)": item["nutrition"]["蛋白質"],
            "脂肪 (g)": item["脂肪"],
            "碳水化合物 (g)": item["碳水化合物"]
        }
        rows.append(row)
    return pd.DataFrame(rows)

# 主應用
def main():
    st.title("週菜單生成器 - 營養比例檢查")
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

    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000,
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    if st.button("生成 5 天菜單"):
        used_recipes = []
        for day in range(1, 6):
            st.subheader(f"第 {day} 天的菜單")
            daily_menu = calculate_menu_for_day(recipes, group_counts, lunch_calories, nutrition_data, day, used_recipes)
            
            total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
            validation = validate_nutrition_ratio(daily_menu, total_calories_needed)

            if not validation["valid"]:
                st.error(f"第 {day} 天的營養比例不符合要求，請調整菜單！")
            else:
                st.success(f"第 {day} 天的營養比例符合要求！")

            plot_nutrition_ratio(validation)

            if daily_menu:
                nutrition_table = build_nutrition_table_with_ingredients(daily_menu)
                st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
