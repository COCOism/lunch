import streamlit as st
import pandas as pd
import json

# 加載菜譜數據
def load_recipes():
    with open("recipes.json", "r", encoding="utf-8") as file:
        return json.load(file)

# 加載食材營養數據
def load_nutrition_data():
    with open("ingredients_nutrition.json", "r", encoding="utf-8") as file:
        return json.load(file)

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

# 計算菜單
def calculate_menu(recipes, group_counts, lunch_calories, nutrition_data):
    total_people = sum(group_counts.values())
    total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
    category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
    category_calories = {category: total_calories_needed * ratio for category, ratio in category_ratios.items()}
    
    menu_summary = []

    for recipe in recipes:
        category = recipe["type"]
        if category not in category_calories:
            continue

        recipe_nutrition = calculate_recipe_nutrition(recipe["ingredients"], nutrition_data)
        if recipe_nutrition["熱量"] == 0:
            continue
        portions = round(category_calories[category] / recipe_nutrition["熱量"], 1)
        portions = min(portions, total_people)

        total_ingredients = {ing: round(weight * portions, 1) for ing, weight in recipe["ingredients"].items()}
        total_nutrition = {key: round(value * portions, 1) for key, value in recipe_nutrition.items()}

        menu_summary.append({
            "name": recipe["name"],
            "type": recipe["type"],
            "calories": total_nutrition["熱量"],
            "nutrition": total_nutrition,
            "portions": portions,
            "ingredients": total_ingredients
        })
    
    return menu_summary

# 構建營養成分和食材數量表格
def build_nutrition_table_with_ingredients(menu):
    rows = []
    for item in menu:
        ingredients = "; ".join([f"{ing}: {weight} 克" for ing, weight in item["ingredients"].items()])
        row = {
            "菜品": item["name"],
            "類型": item["type"],
            "熱量 (kcal)": item["nutrition"]["熱量"],
            "蛋白質 (g)": item["nutrition"]["蛋白質"],
            "脂肪 (g)": item["nutrition"]["脂肪"],
            "碳水化合物 (g)": item["nutrition"]["碳水化合物"],
            "食材": ingredients
        }
        rows.append(row)
    total_nutrition = {
        "熱量 (kcal)": sum(row["熱量 (kcal)"] for row in rows),
        "蛋白質 (g)": sum(row["蛋白質 (g)"] for row in rows),
        "脂肪 (g)": sum(row["脂肪 (g)"] for row in rows),
        "碳水化合物 (g)": sum(row["碳水化合物 (g)"] for row in rows),
    }
    rows.append({
        "菜品": "總計",
        "類型": "全部",
        "熱量 (kcal)": round(total_nutrition["熱量 (kcal)"], 1),
        "蛋白質 (g)": round(total_nutrition["蛋白質 (g)"], 1),
        "脂肪 (g)": round(total_nutrition["脂肪 (g)"], 1),
        "碳水化合物 (g)": round(total_nutrition["碳水化合物 (g)"], 1),
        "食材": "——"
    })
    return pd.DataFrame(rows)

# 主應用
def main():
    st.title("午餐菜單生成器")

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
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    if st.button("生成菜單"):
        menu = calculate_menu(recipes, group_counts, lunch_calories, nutrition_data)
        nutrition_table = build_nutrition_table_with_ingredients(menu)
        st.subheader("全餐營養成分與食材數量表")
        st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
