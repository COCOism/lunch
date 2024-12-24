def main():
    st.title("週菜單生成器")

    # 加載數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    # 用戶輸入用餐人數
    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    # 每日營養需求標準
    daily_nutrition_needs = {
        "熱量 (kcal)": 2000,
        "蛋白質 (g)": 75,
        "脂肪 (g)": 70,
        "碳水化合物 (g)": 260
    }
    lunch_nutrition_needs = {key: value * 0.4 for key, value in daily_nutrition_needs.items()}  # 午餐營養需求

    # 計算每組人數的午餐熱量需求
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4  # 午餐佔每日總熱量的比例
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    # 生成菜單按鈕
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue
            
            # 計算總營養
            total_nutrition = calculate_total_nutrition(menu)
            compliance = check_nutrition_compliance(total_nutrition, lunch_nutrition_needs)

            # 顯示菜單表格
            nutrition_table = build_nutrition_table_with_ingredients(menu)
            st.dataframe(nutrition_table)

            # 顯示營養是否符合標準
            st.write("總營養成分：", total_nutrition)
            if all(compliance.values()):
                st.success("此菜單符合午餐營養需求標準！")
            else:
                st.error("此菜單未滿足以下營養需求：")
                for key, is_compliant in compliance.items():
                    if not is_compliant:
                        st.write(f"- {key}：需求 {lunch_nutrition_needs[key]}，實際 {total_nutrition[key]}")

if __name__ == "__main__":
    main()
