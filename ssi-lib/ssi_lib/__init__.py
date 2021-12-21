"""Library providing SSI capabilities"""

from .ssi import \
    SSIApp, \
    SSIGenerationError, \
    SSIRegistrationError, \
    SSIResolutionError, \
    SSIIssuanceError, \
    SSIVerificationError, \
    SSIVcContentError, \
    Template, \
    Vc

__version__ = '0.1.0'

__all__ = (
    'SSIApp',
    'SSIGenerationError',
    'SSIRegistrationError',
    'SSIResolutionError',
    'SSIIssuanceError',
    'SSIVerificationError',
    'SSIVcContentError',
    'Template',
    'Vc',
)
