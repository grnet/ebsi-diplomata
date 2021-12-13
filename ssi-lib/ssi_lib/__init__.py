"""Library providing SSI capabilities"""

from .app import SSIApp, SSIGenerationError, SSICreationError, \
    SSIRegistrationError, SSIResolutionError, SSIIssuanceError

__version__ = '0.0.1'

__all__ = (
    'SSIApp',
    'SSIGenerationError',
    'SSICreationError',
    'SSIRegistrationError',
    'SSIResolutionError',
    'SSIIssuanceError',
)
