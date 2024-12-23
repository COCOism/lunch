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
    # 四捨五入到小數點後一位
    return {key: round(value, 1) for key, value in total_nutrition.items()}

# 計算菜單
def calculate_menu(recipes, group_counts, lunch_calories, nutrition_data):
    # 總用餐人數
    total_people = sum(group_counts.values())

    # 確保熱量按比例分配
    total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
    category_ratios = {"主食": 0.3, "主菜": 0.4, "副菜": 0.2, "湯品": 0.1}
    category_calories = {category: total_calories_needed * ratio for category, ratio in category_ratios.items()}
    
    menu_summary = []

    for recipe in recipes:
        category = recipe["type"]
        if category not in category_calories:
            continue

        # 計算該道菜需要的份量
        recipe_nutrition = calculate_recipe_nutrition(recipe["ingredients"], nutrition_data)
        if recipe_nutrition["熱量"] == 0:  # 避免除以零
            continue
        portions = round(category_calories[category] / recipe_nutrition["熱量"], 1)

        # 確保份量不超過總人數
        portions = min(portions, total_people)

        # 總食材需求
        total_ingredients = {ing: round(weight * portions, 1) for ing, weight in recipe["ingredients"].items()}

        # 總營養數據
        total_nutrition = {
            key: round(value * portions, 1) for key, value in recipe_nutrition.items()
        }

        menu_summary.append({
            "name": recipe["name"],
            "type": recipe["type"],
            "calories": total_nutrition["熱量"],
            "nutrition": total_nutrition,
            "portions": portions,
            "ingredients": total_ingredients
        })
    
    return menu_summary

# 構建營養成分表格
def build_nutrition_table(menu):
    rows = []
    for item in menu:
        row = {
            "菜品": item["name"],
            "類型": item["type"],
            "熱量 (kcal)": item["nutrition"]["熱量"],
            "蛋白質 (g)": item["nutrition"]["蛋白質"],
            "脂肪 (g)": item["nutrition"]["脂肪"],
            "碳水化合物 (g)": item["nutrition"]["碳水化合物"],
        }
        rows.append(row)
    # 添加總營養行
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
    })
    return pd.DataFrame(rows)

# 主應用
def main():
    st.title("午餐菜單生成器")

    # 加載數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    # 人數輸入（左側欄）
    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    # 計算午餐熱量需求
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    # 動態更新菜單
    if st.button("生成菜單"):
        menu = calculate_menu(recipes, group_counts, lunch_calories, nutrition_data)
        nutrition_table = build_nutrition_table(menu)
        st.subheader("全餐營養成分表")
        st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
