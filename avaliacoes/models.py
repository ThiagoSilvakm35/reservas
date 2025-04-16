from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from reservas.models import Booking

class Review(models.Model):
    """Modelo para avaliações de reservas."""
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(
        _('nota'),
        validators=[
            MinValueValidator(1, _('A nota mínima é 1')),
            MaxValueValidator(5, _('A nota máxima é 5'))
        ]
    )
    comment = models.TextField(_('comentário'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('avaliação')
        verbose_name_plural = _('avaliações')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Avaliação: {self.booking.user.get_full_name()} - {self.booking.provider.service_name} - {self.rating} estrelas"

class ReviewResponse(models.Model):
    """Modelo para respostas às avaliações."""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    text = models.TextField(_('resposta'))
    responded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_responses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('resposta de avaliação')
        verbose_name_plural = _('respostas de avaliações')
    
    def __str__(self):
        return f"Resposta à avaliação: {self.review.booking.provider.service_name}"
