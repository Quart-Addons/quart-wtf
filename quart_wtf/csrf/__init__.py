"""
quart_wtf.csrf
"""
from .extension import CSRFProtect, CSRFError

__all__ = ['CSRFProtect', 'CSRFError']
