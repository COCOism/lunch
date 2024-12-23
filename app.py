import streamlit as st
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
    total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    for ingredient, weight in ingredients.items():
        if ingredient in nutrition_data:
            nutrient = nutrition_data[ingredient]
            total_nutrition["calories"] += nutrient["calories"] * weight / 100
            total_nutrition["protein"] += nutrient["protein"] * weight / 100
            total_nutrition["fat"] += nutrient["fat"] * weight / 100
            total_nutrition["carbs"] += nutrient["carbs"] * weight / 100
    return total_nutrition

# 計算菜單
def calculate_menu(recipes, group_counts, lunch_calories, nutrition_data):
    total_calories_needed = sum(count * lunch_calories[group] for group, count in group_counts.items())
    menu_summary = []

    for recipe in recipes:
        # 根據所需總熱量計算份量
        recipe_nutrition = calculate_recipe_nutrition(recipe["ingredients"], nutrition_data)
        portions = total_calories_needed // recipe_nutrition["calories"]

        # 總食材需求
        total_ingredients = {ing: weight * portions for ing, weight in recipe["ingredients"].items()}

        # 總營養數據
        total_nutrition = {
            key: value * portions for key, value in recipe_nutrition.items()
        }

        menu_summary.append({
            "name": recipe["name"],
            "type": recipe["type"],
            "calories": total_nutrition["calories"],
            "nutrition": total_nutrition,
            "portions": portions,
            "ingredients": total_ingredients
        })
    return menu_summary

# 主應用
def main():
    st.title("午餐菜單生成器")

    # 加載數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    # 人數輸入
    st.subheader("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.number_input("成人（女）人數", min_value=0, value=4),
    }

    # 計算午餐熱量需求
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    # 菜單生成
    if st.button("生成菜單"):
        menu = calculate_menu(recipes, group_counts, lunch_calories, nutrition_data)
        st.subheader("生成的菜單")
        for item in menu:
            st.write(f"### {item['name']} ({item['type']})")
            st.write(f"熱量: {item['calories']} kcal")
            st.write(f"份量: {item['portions']} 人份")
            st.write(f"營養成分: {item['nutrition']}")
            st.write(f"所需食材: {item['ingredients']}")

if __name__ == "__main__":
    main()
