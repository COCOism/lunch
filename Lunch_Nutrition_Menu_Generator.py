def main():
    st.title("週菜單生成器")

    # 加載菜譜和營養數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=2),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=3),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=4),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=5),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=3),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=4),
    }

    lunch_calorie_ranges = {
        "幼兒_男": (400, 560),
        "幼兒_女": (400, 560),
        "國小_男": (560, 880),
        "國小_女": (560, 880),
        "成人_男": (880, 1200),
        "成人_女": (720, 960),
    }

    calories_per_day = {
        "幼兒_男": 1400, "幼兒_女": 1300,
        "國小_男": 1800, "國小_女": 1600,
        "成人_男": 2500, "成人_女": 2000
    }
    lunch_ratio = 0.4
    lunch_calories = {group: int(cal * lunch_ratio) for group, cal in calories_per_day.items()}

    min_total_calories = sum(lunch_calorie_ranges[group][0] * count for group, count in group_counts.items() if count > 0)
    max_total_calories = sum(lunch_calorie_ranges[group][1] * count for group, count in group_counts.items() if count > 0)

    if st.button("生成 5 天菜單"):
        weekly_menu = generate_weekly_menu(recipes, group_counts, lunch_calories, nutrition_data, lunch_calorie_ranges)

        for day, menu in weekly_menu.items():
            st.subheader(f"{day} 的菜單")
            if not menu:
                st.warning(f"{day} 的菜單未生成，請檢查菜品數據。")
                continue

            # 恢復表格格式
            formatted_menu = pd.DataFrame([
                {
                    "Unnamed: 0": i,
                    "name": item["name"],
                    "type": item["type"],
                    "calories": item["calories"],
                    "nutrition": item["nutrition"],
                    "portions": item["portions"],
                    "ingredients": item["ingredients"]
                }
                for i, item in enumerate(menu)
            ])

            # 熱量範圍檢查
            total_calories = sum(item["calories"] for item in menu)
            if total_calories < min_total_calories:
                st.warning(f"菜單總熱量 ({total_calories:.1f} kcal) 過低，不符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")
            elif total_calories > max_total_calories:
                st.warning(f"菜單總熱量 ({total_calories:.1f} kcal) 過高，不符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")
            else:
                st.success(f"菜單總熱量 ({total_calories:.1f} kcal) 符合需求範圍 ({min_total_calories}-{max_total_calories} kcal)")

            # 顯示恢復格式後的菜單
            st.write(formatted_menu)

if __name__ == "__main__":
    main()
