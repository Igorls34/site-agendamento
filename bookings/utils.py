"""
Utilitários diversos para o sistema de agendamento.
"""
from urllib.parse import quote
from django.conf import settings


def build_whatsapp_url(booking_or_message, phone_number=None):
    """
    Constrói URL do WhatsApp com mensagem pré-formatada.
    
    Args:
        booking_or_message: Instância do model Booking ou string com mensagem
        phone_number: Número do WhatsApp do profissional (com código do país)
                     Se None, usa settings.WHATSAPP_BUSINESS_NUMBER
    
    Returns:
        str: URL completa para redirecionamento ao WhatsApp
    """
    if phone_number is None:
        phone_number = getattr(settings, 'WHATSAPP_BUSINESS_NUMBER', '5524998190280')
    
    if isinstance(booking_or_message, str):
        message = booking_or_message
    else:
        message = booking_or_message.whatsapp_message()
    
    encoded_message = quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"


def normalize_phone(phone_str):
    """
    Normaliza telefone removendo caracteres especiais, mantendo apenas dígitos.
    
    Args:
        phone_str: String com telefone (ex: "(11) 99999-9999")
    
    Returns:
        str: Apenas dígitos (ex: "11999999999")
    """
    return ''.join(filter(str.isdigit, phone_str))


def format_phone_display(phone_digits):
    """
    Formata telefone para exibição amigável.
    
    Args:
        phone_digits: String apenas com dígitos
    
    Returns:
        str: Telefone formatado para exibição
    """
    if len(phone_digits) == 11:  # Celular com 9 dígitos
        return f"({phone_digits[:2]}) {phone_digits[2:7]}-{phone_digits[7:]}"
    elif len(phone_digits) == 10:  # Fixo
        return f"({phone_digits[:2]}) {phone_digits[2:6]}-{phone_digits[6:]}"
    else:
        return phone_digits  # Retorna como está se não conseguir formatar