def main():
    st.title("週菜單生成器")

    # 加載菜譜和營養數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    # 側欄輸入用餐人數
    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    # 每個群體的午餐熱量範圍
    lunch_calorie_ranges = {
        "幼兒_男": (400, 560),
        "幼兒_女": (400, 560),
        "國小_男": (560, 880),
        "國小_女": (560, 880),
        "成人_男": (880, 1200),
        "成人_女": (720, 960),
    }

    # 動態計算有效群體的總熱量範圍
    min_total_calories = sum(lunch_calorie_ranges[group][0] * count 
                             for group, count in group_counts.items() if count > 0)
    max_total_calories = sum(lunch_calorie_ranges[group][1] * count 
                             for group, count in group_counts.items() if count > 0)

    # 每族群每日總熱量需求的40%作為午餐需求
    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    # 生成 5 天菜單
    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data, lunch_calorie_ranges)

        # 總熱量檢查
        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 計算每日總熱量
            total_calories = sum(item["calories"] for item in menu)

            # 檢查是否符合熱量範圍
            if total_calories < min_total_calories:
                st.warning(f"菜單總熱量 ({total_calories:.1f} kcal) 過低，不符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")
            elif total_calories > max_total_calories:
                st.warning(f"菜單總熱量 ({total_calories:.1f} kcal) 過高，不符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")
            else:
                st.success(f"菜單總熱量 ({total_calories:.1f} kcal) 符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")

            # 顯示菜單表格
            st.write(pd.DataFrame(menu))

if __name__ == "__main__":
    main()
