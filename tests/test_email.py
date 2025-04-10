from app.utils.formmaters import validate_email


def test_validate_email():
    """Тестовые сценарии для проверки валидации email"""
    тестовые_кейсы = [
        ("user@example.com", True),
        ("user.name@example.co.uk", True),
        ("user+tag@example.com", True),
        ("invalid.email", False),
        ("@invalid.com", False),
        ("user@.com", False),
        ("user@domain", False),
        ("", False),
        ("  user@example.com  ", True),
        ("USER@EXAMPLE.COM", True),
        ("a" * 65 + "@example.com", False),
    ]

    for email, ожидаемая_валидность in тестовые_кейсы:
        валиден, результат = validate_email(email)
        print(f"Email: {email}")
        print(f"Валиден: {валиден}")
        print(f"Результат: {результат}")
        print("---")
        assert валиден == ожидаемая_валидность, f"Ошибка для {email}"
