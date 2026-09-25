from src.domain.value_objects.cpf import CPF
from src.domain.value_objects.cnpj import CNPJ
from src.domain.value_objects.email import Email
from src.domain.value_objects.phone_number import PhoneNumber


def test_cpf_sanitization():
    cpf = CPF.create("123.456.789-01")
    assert str(cpf) == "12345678901"
    assert cpf.is_valid_format is True

    # Com espaços e traços
    cpf2 = CPF.create("  098-765-432-10  ")
    assert str(cpf2) == "09876543210"

    # Nulo ou vazio
    assert str(CPF.create(None)) == ""


def test_cnpj_sanitization():
    cnpj = CNPJ.create("12.345.678/0001-90")
    assert str(cnpj) == "12345678000190"
    assert cnpj.is_valid_format is True

    # Nulo
    assert str(CNPJ.create(None)) == ""


def test_email_sanitization():
    email = Email.create("  Usuario.Teste@SE.SENAC.BR ")
    assert str(email) == "usuario.teste@se.senac.br"
    assert email.is_valid_format is True

    invalid = Email.create("invalid-email")
    assert invalid.is_valid_format is False


def test_phone_number_parsing():
    # Telefone com DDD e DDI
    phone1 = PhoneNumber.create("+55 (79) 99876-5432")
    assert phone1.ddi == "+55"
    assert phone1.ddd == "79"
    assert phone1.number == "998765432"

    # Telefone local sem DDI
    phone2 = PhoneNumber.create("79988776655")
    assert phone2.ddi == "+55"
    assert phone2.ddd == "79"
    assert phone2.number == "988776655"

    # Telefone nulo
    phone_null = PhoneNumber.create(None)
    assert phone_null.ddi == "+55"
    assert phone_null.ddd == "79"

