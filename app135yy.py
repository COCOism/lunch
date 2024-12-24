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

    # 其他函數（如 calculate_recipe_nutrition、calculate_menu_for_day 等，保持不變）

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

    # 定義每日總熱量需求（每類群體）
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4  # 午餐佔每日總熱量的比例

    # 修正：生成 lunch_calories 並確保與 group_counts 鍵一致
    lunch_calories = {group: int(calories_per_day.get(group, 0) * lunch_ratio) for group in group_counts}

    # 修正：檢查鍵的一致性，避免 KeyError
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
