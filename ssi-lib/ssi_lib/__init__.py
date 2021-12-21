"""Library providing SSI capabilities"""

from .app import SSIApp, \
    SSIGenerationError, \
    SSIRegistrationError, \
    SSIResolutionError, \
    SSIIssuanceError, \
    SSIVerificationError, \
    SSIContentError

__version__ = '0.0.1'

__all__ = (
    'SSIApp',
    'SSIGenerationError',
    'SSIRegistrationError',
    'SSIResolutionError',
    'SSIIssuanceError',
    'SSIVerificationError',
    'SSIContentError',
)
