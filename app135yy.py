import streamlit as st
import pandas as pd
import json
import random

# 午餐營養需求範圍
LUNCH_NUTRITION_REQUIREMENTS = {
    "熱量": {"min": 600, "max": 800},
    "蛋白質": {"min": 20, "max": 30},
    "脂肪": {"min": 15, "max": 25},
    "碳水化合物": {"min": 75, "max": 100},
}

# 計算單道菜的營養數據
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
    total_nutrition = {"熱量": 0, "蛋白質": 0, "脂肪": 0, "碳水化合物": 0}
    for item in menu:
        for key in total_nutrition:
            total_nutrition[key] += item["nutrition"].get(key, 0)
    return total_nutrition

# 檢查菜單是否符合營養需求
def check_nutrition_compliance(total_nutrition):
    compliance = {}
    for nutrient, range_values in LUNCH_NUTRITION_REQUIREMENTS.items():
        value = total_nutrition.get(nutrient, 0)
        compliance[nutrient] = range_values["min"] <= value <= range_values["max"]
    return compliance

# 構建菜單表格
def build_nutrition_table(menu, total_nutrition):
    rows = []
    for item in menu:
        row = {
            "類型": item["category"],
            "菜名": item["name"],
            "熱量 (kcal)": item["nutrition"]["熱量"],
            "蛋白質 (g)": item["nutrition"]["蛋白質"],
            "脂肪 (g)": item["nutrition"]["脂肪"],
            "碳水化合物 (g)": item["nutrition"]["碳水化合物"],
        }
        rows.append(row)

    # 添加總計行
    total_row = {
        "類型": "總計",
        "菜名": "",
        "熱量 (kcal)": total_nutrition["熱量"],
        "蛋白質 (g)": total_nutrition["蛋白質"],
        "脂肪 (g)": total_nutrition["脂肪"],
        "碳水化合物 (g)": total_nutrition["碳水化合物"],
    }
    rows.append(total_row)
    return pd.DataFrame(rows)

# 主程式
def main():
    st.title("週菜單生成器")

    # 加載食材營養數據
    nutrition_data = load_nutrition_data()

    # 加載菜品數據並計算營養
    recipes = load_recipes(nutrition_data)

    # 點擊按鈕生成菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = {}
        for day in range(1, 6):
            menu = random.sample(recipes, 4)  # 隨機選擇 4 道菜
            total_nutrition = calculate_total_nutrition(menu)
            compliance = check_nutrition_compliance(total_nutrition)
            weekly_menu[f"Day {day}"] = (menu, total_nutrition, compliance)

        for day, (menu, total_nutrition, compliance) in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            nutrition_table = build_nutrition_table(menu, total_nutrition)
            st.dataframe(nutrition_table)

            # 顯示營養是否符合需求
            st.write("營養需求對比：")
            for nutrient, is_compliant in compliance.items():
                if is_compliant:
                    st.success(f"{nutrient} 符合範圍")
                else:
                    range_values = LUNCH_NUTRITION_REQUIREMENTS[nutrient]
                    st.error(f"{nutrient} 未達標！需求範圍：{range_values['min']}-{range_values['max']}")

if __name__ == "__main__":
    main()
