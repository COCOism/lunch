import streamlit as st
import pandas as pd
import json
import random

# 加載菜品數據
def load_recipes():
    try:
        with open("recipes.json", "r", encoding="utf-8") as file:
            recipes = json.load(file)
            for recipe in recipes:
                if "nutrition" not in recipe:
                    recipe["nutrition"] = {
                        "熱量 (kcal)": 0,
                        "蛋白質 (g)": 0,
                        "脂肪 (g)": 0,
                        "碳水化合物 (g)": 0
                    }
            return recipes
    except Exception as e:
        st.error(f"加載 recipes.json 時發生錯誤：{e}")
        st.stop()

# 計算菜單總營養
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

# 主程式
def main():
    st.title("週菜單生成器")
    recipes = load_recipes()

    if st.button("生成菜單"):
        menu = [
            {
                "category": "主食",
                "name": "白米飯",
                "nutrition": {
                    "熱量 (kcal)": 130,
                    "蛋白質 (g)": 2.7,
                    "脂肪 (g)": 0.3,
                    "碳水化合物 (g)": 28.2
                }
            }
        ]
        nutrition_table = build_nutrition_table(menu)
        st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
