def main():
    st.title("週菜單生成器")

    # 加載菜譜和營養數據
    recipes = load_recipes()
    nutrition_data = load_nutrition_data()

    st.sidebar.header("輸入用餐人數")
    group_counts = {
        "幼兒_男": st.sidebar.number_input("幼兒（男）人數", min_value=0, value=6),
        "幼兒_女": st.sidebar.number_input("幼兒（女）人數", min_value=0, value=0),
        "國小_男": st.sidebar.number_input("國小（男）人數", min_value=0, value=48),
        "國小_女": st.sidebar.number_input("國小（女）人數", min_value=0, value=0),
        "成人_男": st.sidebar.number_input("成人（男）人數", min_value=0, value=20),
        "成人_女": st.sidebar.number_input("成人（女）人數", min_value=0, value=0),
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
                    "Unnamed: 0.1": i,
                    "Unnamed: 0": i,
                    "name": item["name"],
                    "type": item["type"],
                    "calories": item["calories"],
                    "nutrition": json.dumps(item["nutrition"], ensure_ascii=False),
                    "portions": item["portions"],
                    "ingredients": json.dumps(item["ingredients"], ensure_ascii=False),
                }
                for i, item in enumerate(menu)
            ])

            # 顯示恢復格式後的菜單
            st.write(formatted_menu)

if __name__ == "__main__":
    main()
