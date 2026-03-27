class AppError(Exception):
    """Base application error."""


class NotFoundError(AppError):
    """Raised when an entity could not be found."""


class ConflictError(AppError):
    """Raised when a unique constraint or state conflict occurs."""


class DomainValidationError(AppError):
    """Raised when a request violates a business rule."""
