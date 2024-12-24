import streamlit as st
import pandas as pd
import json
import random

# 加載菜品數據
def load_recipes():
    try:
        with open("recipes.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("找不到 recipes.json 文件，請確保該文件存在於程式目錄中。")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"解析 recipes.json 時發生錯誤：{e}")
        st.stop()

# 加載營養數據
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

# 計算總需求範圍
def calculate_total_needs(group_counts):
    lunch_needs_per_person = {
        "幼兒": {"熱量 (kcal)": (360, 600), "蛋白質 (g)": (7.5, 14), "脂肪 (g)": (10.5, 18), "碳水化合物 (g)": (39, 80)},
        "國小": {"熱量 (kcal)": (480, 800), "蛋白質 (g)": (15, 28), "脂肪 (g)": (13.5, 24), "碳水化合物 (g)": (60, 120)},
        "成人": {"熱量 (kcal)": (600, 1000), "蛋白質 (g)": (18, 32), "脂肪 (g)": (15, 32), "碳水化合物 (g)": (75, 140)},
    }

    total_needs = {"熱量 (kcal)": [0, 0], "蛋白質 (g)": [0, 0], "脂肪 (g)": [0, 0], "碳水化合物 (g)": [0, 0]}
    for group, count in group_counts.items():
        if group.startswith("幼兒"):
            needs = lunch_needs_per_person["幼兒"]
        elif group.startswith("國小"):
            needs = lunch_needs_per_person["國小"]
        elif group.startswith("成人"):
            needs = lunch_needs_per_person["成人"]
        else:
            continue
        for key, (min_val, max_val) in needs.items():
            total_needs[key][0] += min_val * count
            total_needs[key][1] += max_val * count

    return {key: (round(min_val, 1), round(max_val, 1)) for key, (min_val, max_val) in total_needs.items()}

# 計算菜單的總營養成分
def calculate_total_nutrition(menu):
    total_nutrition = {"熱量 (kcal)": 0, "蛋白質 (g)": 0, "脂肪 (g)": 0, "碳水化合物 (g)": 0}
    for item in menu:
        for key in total_nutrition:
            total_nutrition[key] += item["nutrition"].get(key, 0)
    return {key: round(value, 1) for key, value in total_nutrition.items()}

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

    # 計算總需求範圍
    total_needs = calculate_total_needs(group_counts)

    # 點擊按鈕生成菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 計算總營養
            total_nutrition = calculate_total_nutrition(menu)

            # 對比是否符合總需求
            compliance = {key: total_needs[key][0] <= total_nutrition[key] <= total_needs[key][1] for key in total_needs}
            st.write("營養總需求：", total_needs)
            st.write("菜單總營養：", total_nutrition)

            if all(compliance.values()):
                st.success("此菜單符合午餐需求範圍！")
            else:
                st.error("此菜單未達到以下營養需求：")
                for key, is_compliant in compliance.items():
                    if not is_compliant:
                        st.write(f"- {key}：需求 {total_needs[key][0]}-{total_needs[key][1]}，實際 {total_nutrition[key]}")

if __name__ == "__main__":
    main()
