from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.
class Party(models.Model):
    PARTY_TYPES = [
        ("PERSON", "person"),
        ("GROUP", "group")
    ]
    
    party_id = models.AutoField(primary_key = True)
    party_type = models.CharField(max_length = 20, choices = PARTY_TYPES, default = "PERSON")
    
    
    def __str__(self):
        return f"{self.party_id} - {self.party_type}"


class PartyRole(models.Model):
    ROLE_TYPES = [
        ("CUSTOMER", "Customer"),
        ("EMPLOYEE", "Employee"),
        ("ADMIN", "Admin"),
    ]
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="roles")
    role_type = models.CharField(max_length=30, choices=ROLE_TYPES)


    class Meta:
        unique_together = ("party", "role_type")


    def __str__(self):
        return f"{self.party} - {self.role_type}"


class UserLoginManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)

        # Ensure a party is created
        party = Party.objects.create(party_type="PERSON")

        user = self.model(email=email, party=party, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class UserLogin(AbstractBaseUser, PermissionsMixin):
    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name="user_login")
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserLoginManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email