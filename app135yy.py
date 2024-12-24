import streamlit as st
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

# 計算單天菜單
def calculate_menu_for_day(recipes, group_counts, nutrition_data, day, used_recipes):
    categorized_recipes = {"主食": [], "主菜": [], "副菜": [], "湯品": []}

    for recipe in recipes:
        if recipe["type"] in categorized_recipes:
            categorized_recipes[recipe["type"]].append(recipe)

    menu = {}
    for category, options in categorized_recipes.items():
        if options:
            selected_recipe = random.choice(options)
            menu[category] = selected_recipe
            used_recipes.append(selected_recipe)

    return menu

# 生成 5 天菜單
def generate_weekly_menu(recipes, group_counts, nutrition_data):
    weekly_menu = {}
    used_recipes = []  # 記錄已使用的菜品，避免重複

    for day in range(1, 6):  # 1 到 5 天
        daily_menu = calculate_menu_for_day(
            recipes, group_counts, nutrition_data, day, used_recipes
        )
        weekly_menu[f"Day {day}"] = daily_menu

    return weekly_menu

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

    # 點擊按鈕生成菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 顯示每日菜單
            st.write(menu)

if __name__ == "__main__":
    main()
