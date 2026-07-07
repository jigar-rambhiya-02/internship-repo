from constants import APP_NAME, VERSION
import operations 
import history 



def calling_operation():
    try:
        num1 = int(input('Enter 1st Number: '))   # allow decimals
        num2 = int(input('Enter 2nd Number: '))
    except ValueError:
        print("Invalid number. Please try again.")
        return False

    operation = input('Operation: add(+), sub(-), multiply(*), divide(/)\nEnter Operator: ')

    if operation == '+':
        result = operations.add(num1, num2)
    elif operation == '-':
        result = operations.subtract(num1, num2)
    elif operation == '*':
        result = operations.multiply(num1, num2)
    elif operation == '/':
        result = operations.divide(num1, num2)
    else:
        print('Invalid operation. Use +, -, *, or /.')
        return False

    # Show result to user
    print(f'{num1} {operation} {num2} = {result}')
    history.save_result(num1, num2, operation, result)
    return True


def options():
    while True:
        try:
            opt = int(input('\nPlease Pick an Option:\n(1.) Calculator\n(2.) Show History\n(3.) Exit\nChoose your option: '))
        except ValueError:
            print("Please enter a number (1, 2, or 3).")
            continue
        if opt == 1:
            calling_operation()
        elif opt == 2:
            history.show_history()
        elif opt == 3:
            print("Goodbye!")
            break
        else:
            print("Invalid option, choose 1, 2, or 3.")

def main():
    print('\n\n\n')
    print('='*45)
    print(f'APP_NAME : {APP_NAME}')
    print(f'VERSION : {VERSION}')
    print('='*45)
    # print('\n\n\n')

    options()


if __name__ == '__main__':
    main()