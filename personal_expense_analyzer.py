import calendar
import csv
import math
import os
from datetime import date, datetime


PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_FILE = os.path.join(PROJECT_FOLDER, "transactions.csv")
SETTINGS_FILE = os.path.join(PROJECT_FOLDER, "settings.csv")
SAVINGS_GOAL_FILE = os.path.join(PROJECT_FOLDER, "savings_goal.csv")

DATE_FORMAT = "%Y-%m-%d"
TRANSACTION_FIELDS = ["date", "type", "category", "description", "amount"]

INCOME_CATEGORIES = ["Salary", "Allowance", "Freelance", "Other"]
EXPENSE_CATEGORIES = [ "Food", "Travel", "Shopping", "Bills", "Health", "Education", "Gifts", "Events", "Other",]

FESTIVAL_RULES = {
    1: ("Makar Sankranti / Pongal", ["Food", "Travel", "Gifts"]),
    3: ("Holi (date varies)", ["Food", "Events", "Shopping"]),
    8: ("Raksha Bandhan / Onam (dates vary)", ["Gifts", "Food", "Travel"]),
    9: ("Navratri / Durga Puja (dates vary)", ["Events", "Travel", "Shopping"]),
    10: ("Dussehra / Diwali (dates vary)", ["Gifts", "Food", "Shopping", "Travel"]),
    11: ("Diwali / Chhath (dates vary)", ["Gifts", "Food", "Travel"]),
    12: ("Christmas / New Year", ["Food", "Travel", "Gifts", "Events"]),
}


def format_money(amount):
    return f"Rs. {amount:,.2f}"


def read_amount(prompt, allow_zero=False):
    while True:
        entered_text = input(prompt).strip().replace(",", "")
        try:
            amount = float(entered_text)
            if not math.isfinite(amount):
                print("Please enter a regular number.")
            elif amount < 0 or (amount == 0 and not allow_zero):
                print("Please enter an amount greater than zero.")
            else:
                return amount
        except ValueError:
            print("Please enter a number, for example 250 or 250.50.")


def read_transaction_date():
    while True:
        entered_text = input(
            "Date (YYYY-MM-DD, press Enter for today): "
        ).strip()
        if entered_text == "":
            return date.today()
        try:
            return datetime.strptime(entered_text, DATE_FORMAT).date()
        except ValueError:
            print("That date was not valid. Please use YYYY-MM-DD.")


def read_month_and_year():
    while True:
        month_text = input("Month number (1-12): ").strip()
        year_text = input("Year (for example 2026): ").strip()
        try:
            month = int(month_text)
            year = int(year_text)
            if month < 1 or month > 12:
                print("The month must be between 1 and 12.")
                continue
            if year < 1:
                print("Please enter a valid year.")
                continue
            return month, year
        except ValueError:
            print("Please enter the month and year using numbers.")


def load_transactions():
    transactions = []
    skipped_rows = 0

    try:
        with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    transaction_date = datetime.strptime(
                        row.get("date", ""), DATE_FORMAT
                    ).date()
                    transaction_type = row.get("type", "")
                    amount = float(row.get("amount", ""))
                    category = (row.get("category") or "").strip()

                    if transaction_type not in ["Income", "Expense"]:
                        raise ValueError
                    if amount <= 0 or category == "":
                        raise ValueError

                    transactions.append(
                        {
                            "date": transaction_date.isoformat(),
                            "type": transaction_type,
                            "category": category,
                            "description": (row.get("description") or "").strip(),
                            "amount": amount,
                        }
                    )
                except (ValueError, TypeError, AttributeError):
                    skipped_rows += 1
    except FileNotFoundError:
        pass
    except (OSError, csv.Error):
        print("The transaction file could not be read. Starting with an empty list.")

    if skipped_rows > 0:
        print(f"Skipped {skipped_rows} invalid row(s) in the transaction file.")
    return transactions


def save_transactions(transactions):
    try:
        with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=TRANSACTION_FIELDS)
            writer.writeheader()
            writer.writerows(transactions)
        return True
    except OSError:
        print("The transaction file could not be saved.")
        return False


def load_settings():
    settings = {"monthly_budget": "0", "emergency_target": "0", "emergency_saved": "0",}
    try:
        with open(SETTINGS_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                setting_name = row.get("setting", "")
                setting_value = row.get("value", "")
                if setting_name in settings and setting_value != "":
                    settings[setting_name] = setting_value
    except FileNotFoundError:
        pass
    except (OSError, csv.Error):
        print("The settings file could not be read. Default values will be used.")

    return settings


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["setting", "value"])
            for setting_name in settings:
                writer.writerow([setting_name, settings[setting_name]])
        return True
    except OSError:
        print("The settings file could not be saved.")
        return False


def setting_amount(settings, setting_name):
    try:
        return max(0, float(settings.get(setting_name, "0")))
    except (ValueError, TypeError):
        return 0


def choose_category(transaction_type):
    if transaction_type == "Income":
        categories = INCOME_CATEGORIES
    else:
        categories = EXPENSE_CATEGORIES

    print("Choose a category:")
    for number, category in enumerate(categories, start=1):
        print(f"{number}. {category}")
    print(f"{len(categories) + 1}. Enter another category")

    while True:
        choice = input("Category number: ").strip()
        try:
            choice_number = int(choice)
            if 1 <= choice_number <= len(categories):
                return categories[choice_number - 1]
            if choice_number == len(categories) + 1:
                while True:
                    custom_category = input("Type the category name: ").strip()
                    if custom_category:
                        return custom_category.title()
                    print("The category name cannot be blank.")
        except ValueError:
            pass
        print("Please choose one of the numbers shown.")


def record_transaction(transactions, transaction_type):
    print(f"\nRecord {transaction_type.lower()}")
    transaction_date = read_transaction_date()
    amount = read_amount("Amount: ")
    category = choose_category(transaction_type)
    description = input("Short description (optional): ").strip()
    if description == "":
        description = "No description"

    transaction = { "date": transaction_date.isoformat(), "type": transaction_type, "category": category, "description": description,
        "amount": amount,
    }
    transactions.append(transaction)

    if save_transactions(transactions):
        print(f"{transaction_type} saved: {format_money(amount)}")
    else:
        transactions.pop()


def transactions_for_month(transactions, month, year):
    selected_transactions = []
    for transaction in transactions:
        transaction_date = datetime.strptime(transaction["date"], DATE_FORMAT).date()
        if transaction_date.month == month and transaction_date.year == year:
            selected_transactions.append(transaction)
    return selected_transactions


def show_monthly_summary(transactions, settings):
    print("\nMonthly spending summary")
    month, year = read_month_and_year()
    month_transactions = transactions_for_month(transactions, month, year)

    total_income = 0
    total_expenses = 0
    expense_by_category = {}

    for transaction in month_transactions:
        if transaction["type"] == "Income":
            total_income += transaction["amount"]
        else:
            total_expenses += transaction["amount"]
            category = transaction["category"]
            if category not in expense_by_category:
                expense_by_category[category] = 0
            expense_by_category[category] += transaction["amount"]

    balance = total_income - total_expenses
    budget = setting_amount(settings, "monthly_budget")

    print(f"\nSummary for {calendar.month_name[month]} {year}")
    print(f"Total income:   {format_money(total_income)}")
    print(f"Total expenses: {format_money(total_expenses)}")
    print(f"Monthly balance: {format_money(balance)}")

    if expense_by_category:
        print("\nExpenses by category:")
        for category, amount in expense_by_category.items():
            print(f"- {category}: {format_money(amount)}")
    else:
        print("\nNo expenses have been recorded for this month.")

    tips = []
    if not month_transactions:
        tips.append("Record income and expenses to build a useful monthly summary.")
    if budget <= 0:
        print("\nNo monthly budget is set yet.")
        tips.append("Set a monthly budget to see budget warnings.")
    else:
        amount_left = budget - total_expenses
        print(f"\nMonthly budget: {format_money(budget)}")
        if amount_left >= 0:
            print(f"Budget remaining: {format_money(amount_left)}")
        else:
            print(f"Over budget by: {format_money(abs(amount_left))}")

        if total_expenses >= budget:
            print("BUDGET ALERT: spending has reached or passed the budget.")
            tips.append("Review optional spending and adjust the next month's plan.")
        elif total_expenses >= budget * 0.8:
            print("Budget warning: spending has reached 80% of the budget.")
            tips.append("Keep an eye on remaining purchases for this month.")

    if balance < 0:
        tips.append("Expenses are higher than income for this month.")
    elif total_income > 0 and total_expenses == 0:
        tips.append("Keep recording expenses so the summary reflects your spending.")

    if expense_by_category:
        highest_category = ""
        highest_amount = -1
        for category, amount in expense_by_category.items():
            if amount > highest_amount:
                highest_category = category
                highest_amount = amount
        tips.append(
            f"Your highest spending category is {highest_category}; check whether it matches your plan."
        )

    print("\nSimple tips:")
    if tips:
        for tip in tips:
            print(f"- {tip}")
    else:
        print("- Your spending is within the current budget. Keep recording transactions.")


def set_monthly_budget(settings):
    print("\nSet monthly budget")
    current_budget = setting_amount(settings, "monthly_budget")
    if current_budget > 0:
        print(f"Current budget: {format_money(current_budget)}")

    budget = read_amount("New monthly budget (enter 0 to clear it): ", allow_zero=True)
    settings["monthly_budget"] = str(budget)
    if save_settings(settings):
        if budget == 0:
            print("Monthly budget cleared.")
        else:
            print(f"Monthly budget saved: {format_money(budget)}")


def show_future_expense_plan(transactions):
    print("\nFestival and future expense planner")
    month, year = read_month_and_year()
    print(f"\nPlanning notes for {calendar.month_name[month]} {year}:")

    if month in FESTIVAL_RULES:
        festival_name, suggested_categories = FESTIVAL_RULES[month]
        print(f"Calendar reminder: {festival_name}")
        print("Categories to consider: " + ", ".join(suggested_categories))
        print("These are planning hints. Check the local calendar for exact dates.")
    else:
        print("There is no special festival rule saved for this month.")

    past_category_totals = {}
    today = date.today()
    for transaction in transactions:
        transaction_date = datetime.strptime(transaction["date"], DATE_FORMAT).date()
        if (
            transaction["type"] == "Expense"
            and transaction_date.month == month
            and transaction_date < today
        ):
            category = transaction["category"]
            if category not in past_category_totals:
                past_category_totals[category] = 0
            past_category_totals[category] += transaction["amount"]

    if past_category_totals:
        print("\nRecorded spending in this month from earlier transactions:")
        for category, amount in past_category_totals.items():
            print(f"- {category}: {format_money(amount)}")
        print("Past spending is a reference, not a prediction of future costs.")
    else:
        print("\nThere is no earlier spending history for this month yet.")
        print("You can start by setting aside a small amount for the categories above.")


def plan_emergency_fund(settings):
    print("\nEmergency fund planner")
    old_target = setting_amount(settings, "emergency_target")
    old_saved = setting_amount(settings, "emergency_saved")

    if old_target > 0:
        print(f"Current target: {format_money(old_target)}")
        print(f"Current savings recorded: {format_money(old_saved)}")

    target = read_amount("Emergency-fund target: ", allow_zero=True)
    saved = read_amount("Amount already saved for emergencies: ", allow_zero=True)
    settings["emergency_target"] = str(target)
    settings["emergency_saved"] = str(saved)

    if not save_settings(settings):
        return

    remaining = max(0, target - saved)
    print(f"\nTarget: {format_money(target)}")
    print(f"Saved: {format_money(saved)}")
    print(f"Still needed: {format_money(remaining)}")

    if target == 0:
        print("Set a target above zero to calculate fund progress.")
    else:
        progress = min(saved / target * 100, 100)
        print(f"Progress: {progress:.1f}%")
        if saved >= target:
            print("Your emergency-fund target has been reached.")
        else:
            print("Tip: add a manageable amount regularly until the target is reached.")


def add_months(start_date, number_of_months):
    month_index = start_date.month - 1 + number_of_months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def load_savings_goal():
    try:
        with open(SAVINGS_GOAL_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                target = float(row.get("target", "0"))
                current = float(row.get("current", "0"))
                monthly_saving = float(row.get("monthly_saving", "0"))
                name = (row.get("name") or "").strip()
                if target > 0 and current >= 0 and monthly_saving > 0 and name:
                    return {
                        "name": name,
                        "target": target,
                        "current": current,
                        "monthly_saving": monthly_saving,
                    }
    except FileNotFoundError:
        pass
    except (OSError, csv.Error, ValueError, TypeError):
        print("The savings goal file could not be read.")
    return None


def save_savings_goal(goal):
    try:
        with open(SAVINGS_GOAL_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=["name", "target", "current", "monthly_saving"]
            )
            writer.writeheader()
            writer.writerow(goal)
        return True
    except OSError:
        print("The savings goal could not be saved.")
        return False


def show_savings_goal(goal):
    if goal is None:
        print("No savings goal has been saved yet.")
        return

    remaining = max(0, goal["target"] - goal["current"])
    print(f"\nSavings goal: {goal['name']}")
    print(f"Target: {format_money(goal['target'])}")
    print(f"Saved so far: {format_money(goal['current'])}")
    print(f"Monthly saving plan: {format_money(goal['monthly_saving'])}")
    print(f"Remaining: {format_money(remaining)}")

    if remaining == 0:
        print("Goal reached. Well done for following your plan.")
    else:
        months_needed = math.ceil(remaining / goal["monthly_saving"])
        target_date = add_months(date.today(), months_needed)
        print(f"Estimated time: {months_needed} month(s)")
        print(f"Estimated target date: {target_date.strftime('%B %Y')}")
        print("Tip: update the saved amount when you add more money to this goal.")


def set_savings_goal():
    print("\nSet or update a savings goal")
    name = input("What are you saving for? ").strip()
    while name == "":
        print("Please enter a short name for your goal.")
        name = input("What are you saving for? ").strip()

    target = read_amount("Goal target amount: ")
    current = read_amount("Amount saved so far: ", allow_zero=True)
    monthly_saving = read_amount("Planned saving per month: ")

    goal = {
        "name": name,
        "target": target,
        "current": current,
        "monthly_saving": monthly_saving,
    }

    if save_savings_goal(goal):
        print("Savings goal saved.")
        show_savings_goal(goal)


def show_recent_transactions(transactions):
    print("\nRecent transactions")
    if not transactions:
        print("No transactions have been recorded yet.")
        return

    recent_transactions = transactions[-10:]
    for transaction in reversed(recent_transactions):
        print(
            f"{transaction['date']} | {transaction['type']} | "
            f"{transaction['category']} | {format_money(transaction['amount'])} | "
            f"{transaction['description']}"
        )


def remove_expense(transactions):
    expenses = [
        (index, transaction)
        for index, transaction in enumerate(transactions)
        if transaction["type"] == "Expense"
    ]

    print("\nRemove an expense")
    if not expenses:
        print("No expenses have been recorded yet.")
        return

    print("Choose an expense to remove:")
    for number, (_, transaction) in enumerate(reversed(expenses), start=1):
        print(
            f"{number}. {transaction['date']} | {transaction['category']} | "
            f"{format_money(transaction['amount'])} | {transaction['description']}"
        )
    print("0. Cancel")

    while True:
        choice = input("Expense number: ").strip()
        try:
            choice_number = int(choice)
            if choice_number == 0:
                print("Removal cancelled.")
                return
            if 1 <= choice_number <= len(expenses):
                break
        except ValueError:
            pass
        print("Please choose one of the numbers shown.")

    index, transaction = list(reversed(expenses))[choice_number - 1]
    confirmation = input(
        f"Remove {transaction['date']} | {transaction['category']} | "
        f"{format_money(transaction['amount'])} | {transaction['description']}? (y/n): "
    ).strip().lower()
    if confirmation not in ["y", "yes"]:
        print("Removal cancelled.")
        return

    removed_transaction = transactions.pop(index)
    if save_transactions(transactions):
        print("Expense removed.")
    else:
        transactions.insert(index, removed_transaction)


def remove_all_data(transactions, settings):
    print("\nRemove all saved data")
    print(
        "This clears all income and expenses, resets budget and emergency-fund "
        "settings, and removes the savings goal."
    )
    confirmation = input("Type DELETE to confirm: ").strip()
    if confirmation != "DELETE":
        print("Removal cancelled.")
        return

    cleared_settings = {
        "monthly_budget": "0",
        "emergency_target": "0",
        "emergency_saved": "0",
    }

    if not save_transactions([]):
        return
    if not save_settings(cleared_settings):
        print("Could not finish clearing all data. Please try again.")
        return

    try:
        with open(SAVINGS_GOAL_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=["name", "target", "current", "monthly_saving"]
            )
            writer.writeheader()
    except OSError:
        print("Could not finish clearing all data. Please try again.")
        return

    transactions.clear()
    settings.clear()
    settings.update(cleared_settings)
    print("All saved data has been removed.")


def show_menu():
    print("\n" + "=" * 48)
    print("PERSONAL EXPENSES AND BUDGET ANALYZER")
    print("=" * 48)
    print("1. Record income")
    print("2. Record an expense")
    print("3. View monthly summary")
    print("4. Set monthly budget")
    print("5. Plan for a future month")
    print("6. Emergency fund planner")
    print("7. Set or update a savings goal")
    print("8. View savings goal")
    print("9. View recent transactions")
    print("10. Remove an expense")
    print("11. Remove all data")
    print("0. Save and exit")


def main():
    print("Welcome! Your records are saved in CSV files beside this program.")
    transactions = load_transactions()
    settings = load_settings()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            record_transaction(transactions, "Income")
        elif choice == "2":
            record_transaction(transactions, "Expense")
        elif choice == "3":
            show_monthly_summary(transactions, settings)
        elif choice == "4":
            set_monthly_budget(settings)
        elif choice == "5":
            show_future_expense_plan(transactions)
        elif choice == "6":
            plan_emergency_fund(settings)
        elif choice == "7":
            set_savings_goal()
        elif choice == "8":
            show_savings_goal(load_savings_goal())
        elif choice == "9":
            show_recent_transactions(transactions)
        elif choice == "10":
            remove_expense(transactions)
        elif choice == "11":
            remove_all_data(transactions, settings)
        elif choice == "0":
            save_transactions(transactions)
            save_settings(settings)
            print("Your information has been saved. see you later!")
            break
        else:
            print("Please choose a menu option from 0 to 11.")


if __name__ == "__main__":
    main()
