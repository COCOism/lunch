def main():
    st.title("週菜單生成器")

    # 加載菜品數據和營養數據
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

    # 計算每組人數的午餐熱量需求
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4  # 午餐佔每日總熱量的比例
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    # 生成 5 天菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data)

        # 顯示 5 天的菜單
        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:  # 如果某一天的菜單未生成
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據或篩選條件。")
                continue
            # 顯示每一天的表格
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

if __name__ == "__main__":
    main()
