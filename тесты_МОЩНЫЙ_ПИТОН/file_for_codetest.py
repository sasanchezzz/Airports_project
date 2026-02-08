# def gen_extra_nums():
#     n = 0
#     while n < 4:
#         yield n
#         n += 1
#     yield 42

# for num in gen_extra_nums():
#     print(num)


# def gen_squares(max_number: int):
#     for num in range(max_number):
#         yield num**2

# deposit = 10000
# monthly_rate = 1.005  # 0.5% в месяц
# deposit *= monthly_rate
# print(f"Сумма через месяц: {deposit:.2f}")

# user_input = input("Введите что-нибудь: ")
# if len(user_input) > 5:
#     print(f"Длинная строка: {user_input}")

# if (length := len(input("Введите что-нибудь: "))) > 5:
#     print(f"Длина строки: {length}")

data = [1, 4, 9, 16, 25, 36, 49, 64]
while (current := data.pop()) > 10:
    print(f"Большое число: {current}")